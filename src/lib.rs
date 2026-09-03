use axum::{
    Router,
    extract::State,
    http::{HeaderMap, HeaderValue, Method, StatusCode, header},
    middleware::{self, Next},
    response::{IntoResponse, Response},
    routing::{any, get, post},
};
use reqwest::Client;
use std::env;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::net::TcpListener;
use tower_http::cors::{Any, CorsLayer};

mod ollama;
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
    pub python_origin: Option<String>,
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
    let _ = dotenvy::from_path(crate_root.join(".env"));
    let _ = dotenvy::from_path(crate_root.join("reasoning_layer/.env"));
}

pub fn load_state() -> AppState {
    load_env_files();

    let python_origin = env::var("PYTHON_ORIGIN")
        .ok()
        .map(|s| s.trim().trim_end_matches('/').to_string())
        .filter(|s| !s.is_empty());

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
        python_origin,
        sqlite_path: crate::ops::sqlite_path(),
        metrics: Arc::new(SmeMetrics::default()),
    }
}

pub fn with_python_origin(mut state: AppState, origin: impl Into<String>) -> AppState {
    state.python_origin = Some(origin.into().trim().trim_end_matches('/').to_string());
    state
}

pub fn with_internal_token(mut state: AppState, token: impl Into<String>) -> AppState {
    state.internal_token = token.into();
    state
}

pub fn router(state: AppState) -> Router {
    let mut app = Router::new()
        .route("/insta_summary", get(insta_summary))
        .route("/brisk_all", get(brisk_all))
        .route("/search_company", get(probe_search))
        .route("/company_details", get(company_comprehensive_details))
        .route("/api/search/search_company", get(probe_search))
        .route("/api/search/company_details", get(company_comprehensive_details))
        .route("/api/ollama/status", get(ollama::status))
        .route("/api/ollama/start", post(ollama::start))
        .route("/api/ollama/warmup", post(ollama::warmup))
        .route("/api/ollama/pull", post(ollama::pull))
        .route("/internal/reload-settings", post(reload_settings));

    if state.python_origin.is_some() {
        app = app
            .route("/api/chat", any(proxy_python))
            .route("/api/chat_history", any(proxy_python))
            .route("/api/chat_history/{*path}", any(proxy_python))
            .route("/api/auth", any(proxy_python))
            .route("/api/auth/{*path}", any(proxy_python))
            .route("/api/admin", any(proxy_python))
            .route("/api/admin/{*path}", any(proxy_python));
    }

    app.layer(middleware::from_fn_with_state(
        state.clone(),
        internal_token_middleware,
    ))
    .layer(
        CorsLayer::new()
            .allow_origin(Any)
            .allow_methods(Any)
            .allow_headers(Any),
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

async fn proxy_python(
    State(state): State<AppState>,
    request: axum::http::Request<axum::body::Body>,
) -> Response {
    let Some(origin) = state.python_origin.as_deref() else {
        return (StatusCode::BAD_GATEWAY, "python origin not configured").into_response();
    };

    let path = request.uri().path();
    let forwarded = path.strip_prefix("/api").unwrap_or(path);
    let query = request
        .uri()
        .query()
        .map(|q| format!("?{q}"))
        .unwrap_or_default();
    let url = format!("{origin}{forwarded}{query}");

    let method = match reqwest::Method::from_bytes(request.method().as_str().as_bytes()) {
        Ok(method) => method,
        Err(_) => return (StatusCode::METHOD_NOT_ALLOWED, "unsupported method").into_response(),
    };

    let headers = request.headers().clone();
    let body = match axum::body::to_bytes(request.into_body(), 32 * 1024 * 1024).await {
        Ok(bytes) => bytes,
        Err(err) => {
            return (
                StatusCode::BAD_REQUEST,
                format!("failed to read request body: {err}"),
            )
                .into_response();
        }
    };

    let mut builder = state.reqwest_client.request(method, url);
    for (name, value) in headers.iter() {
        if name == header::HOST || name == header::CONTENT_LENGTH {
            continue;
        }
        builder = builder.header(name, value);
    }
    if !state.internal_token.is_empty() {
        builder = builder.header("X-Internal-Token", &state.internal_token);
    }

    let upstream = match builder.body(body).send().await {
        Ok(resp) => resp,
        Err(err) => {
            return (
                StatusCode::BAD_GATEWAY,
                format!("python proxy failed: {err}"),
            )
                .into_response();
        }
    };

    let status =
        StatusCode::from_u16(upstream.status().as_u16()).unwrap_or(StatusCode::BAD_GATEWAY);
    let mut response_headers = HeaderMap::new();
    for (name, value) in upstream.headers() {
        if name == header::TRANSFER_ENCODING || name == header::CONTENT_LENGTH {
            continue;
        }
        if let (Ok(name), Ok(value)) = (
            axum::http::HeaderName::from_bytes(name.as_str().as_bytes()),
            HeaderValue::from_bytes(value.as_bytes()),
        ) {
            response_headers.append(name, value);
        }
    }

    let stream = upstream.bytes_stream();
    let body = axum::body::Body::from_stream(stream);
    (status, response_headers, body).into_response()
}
