use axum::{
    Router,
    extract::State,
    http::{header, HeaderName, Method, StatusCode},
    middleware::{self, Next},
    response::{IntoResponse, Response},
    routing::{get, post},
};
use reqwest::Client;
use std::env;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::net::TcpListener;
use tower_http::cors::{AllowOrigin, CorsLayer};

mod ops;
mod routes;

use ops::SmeMetrics;
use routes::finacial_summary::{brisk_all, insta_summary};
use routes::probe_router::{company_comprehensive_details, probe_search};

#[derive(Clone)]
pub struct AppState {
    pub api_key: String,
    pub reqwest_client: Client,
    pub probe_key: String,
    pub internal_token: String,
    pub sqlite_path: PathBuf,
    pub metrics: Arc<SmeMetrics>,
}

impl AppState {
    pub fn probe_key_value(&self) -> String {
        let mut probe = self.probe_key.clone();
        let mut insta = self.api_key.clone();
        ops::overlay_keys(&self.sqlite_path, &mut probe, &mut insta);
        probe
    }

    pub fn api_key_value(&self) -> String {
        let mut probe = self.probe_key.clone();
        let mut insta = self.api_key.clone();
        ops::overlay_keys(&self.sqlite_path, &mut probe, &mut insta);
        insta
    }
}

pub fn load_env_files() {
    let crate_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let _ = dotenvy::dotenv();
    let _ = dotenvy::from_path(PathBuf::from("/app/.env"));
    let _ = dotenvy::from_path(crate_root.join(".env"));
    let _ = dotenvy::from_path(crate_root.join("reasoning_layer/.env"));
}

pub fn load_state() -> AppState {
    load_env_files();

    AppState {
        api_key: env::var("INSTA_API_KEY")
            .or_else(|_| env::var("insta_api_key"))
            .unwrap_or_default(),
        reqwest_client: Client::new(),
        probe_key: env::var("probe_api_key").unwrap_or_else(|_| {
            eprintln!("probe_api_key is not set; company search will fail until it is in .env");
            String::new()
        }),
        internal_token: env::var("INTERNAL_TOKEN").unwrap_or_default(),
        sqlite_path: crate::ops::sqlite_path(),
        metrics: Arc::new(SmeMetrics::default()),
    }
}

pub fn router(state: AppState) -> Router {
    Router::new()
        .route("/insta_summary", get(insta_summary))
        .route("/brisk_all", get(brisk_all))
        .route("/search_company", get(probe_search))
        .route("/company_details", get(company_comprehensive_details))
        .route("/api/search/search_company", get(probe_search))
        .route(
            "/api/search/company_details",
            get(company_comprehensive_details),
        )
        .route("/internal/reload-settings", post(reload_settings))
        .layer(middleware::from_fn_with_state(
            state.clone(),
            internal_token_middleware,
        ))
        .layer(
            CorsLayer::new()
                .allow_origin(AllowOrigin::mirror_request())
                .allow_credentials(true)
                .allow_methods([Method::GET, Method::POST, Method::OPTIONS])
                .allow_headers([
                    header::AUTHORIZATION,
                    header::CONTENT_TYPE,
                    HeaderName::from_static("x-request-id"),
                ]),
        )
        .with_state(state)
}

pub async fn bind_local(port: u16) -> std::io::Result<(TcpListener, u16)> {
    let listener = TcpListener::bind(("127.0.0.1", port)).await?;
    let bound = listener.local_addr()?.port();
    Ok((listener, bound))
}

pub async fn serve(listener: TcpListener, state: AppState) {
    axum::serve(listener, router(state)).await.unwrap();
}

pub async fn run_standalone() {
    let port: u16 = env::var("SME_API_PORT")
        .ok()
        .and_then(|s| s.parse().ok())
        .unwrap_or(3000);
    let state = load_state();
    let (listener, bound) = bind_local(port)
        .await
        .unwrap_or_else(|err| panic!("failed to bind 127.0.0.1:{port}: {err}"));
    eprintln!("SME API listening on http://127.0.0.1:{bound}");
    serve(listener, state).await;
}

fn token_matches(got: &str, expected: &str) -> bool {
    let a = got.as_bytes();
    let b = expected.as_bytes();
    if a.len() != b.len() {
        let mut acc = 0u8;
        for byte in b {
            acc |= *byte;
        }
        let _ = acc;
        return false;
    }
    a.iter().zip(b.iter()).fold(0u8, |acc, (x, y)| acc | (x ^ y)) == 0
}

async fn reload_settings() -> &'static str {
    "ok"
}

async fn internal_token_middleware(
    State(state): State<AppState>,
    request: axum::http::Request<axum::body::Body>,
    next: Next,
) -> Response {
    if state.internal_token.is_empty() || request.method() == Method::OPTIONS {
        return next.run(request).await;
    }
    let ok = request
        .headers()
        .get("x-internal-token")
        .and_then(|value| value.to_str().ok())
        .is_some_and(|got| token_matches(got, &state.internal_token));
    if !ok {
        return (StatusCode::UNAUTHORIZED, "invalid internal token").into_response();
    }
    next.run(request).await
}
