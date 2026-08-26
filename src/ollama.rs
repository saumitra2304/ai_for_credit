use axum::{
    body::Body,
    extract::Json,
    http::StatusCode,
    response::{IntoResponse, Response},
};
use serde::Deserialize;
use serde_json::{json, Value};
use std::env;

const OLLAMA: &str = "http://127.0.0.1:11434";

fn expected_model() -> String {
    env::var("OPENAI_MODEL_NAME").unwrap_or_else(|_| "qwen3:8b".to_string())
}

pub async fn status() -> Json<Value> {
    let model = expected_model();
    let client = reqwest::Client::new();
    let Ok(resp) = client.get(format!("{OLLAMA}/api/tags")).send().await else {
        return Json(json!({
            "ok": false,
            "running": false,
            "model": model,
            "installed": false,
            "models": [],
        }));
    };

    if !resp.status().is_success() {
        return Json(json!({
            "ok": false,
            "running": false,
            "model": model,
            "installed": false,
            "models": [],
        }));
    }

    let payload: Value = resp.json().await.unwrap_or_else(|_| json!({}));
    let models: Vec<String> = payload
        .get("models")
        .and_then(|m| m.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|item| item.get("name").and_then(|n| n.as_str()).map(str::to_string))
                .collect()
        })
        .unwrap_or_default();

    let installed = models.iter().any(|name| {
        name == &model || name.starts_with(&format!("{model}:")) || model.starts_with(name)
    });

    Json(json!({
        "ok": true,
        "running": true,
        "model": model,
        "installed": installed,
        "models": models,
    }))
}

#[derive(Deserialize, Default)]
pub struct PullBody {
    pub name: Option<String>,
}

pub async fn pull(Json(body): Json<PullBody>) -> Response {
    let model = body.name.unwrap_or_else(expected_model);
    let client = reqwest::Client::new();
    let upstream = client
        .post(format!("{OLLAMA}/api/pull"))
        .json(&json!({ "name": model, "stream": true }))
        .send()
        .await;

    match upstream {
        Ok(resp) if resp.status().is_success() => {
            let stream = resp.bytes_stream();
            (
                StatusCode::OK,
                [("content-type", "application/x-ndjson")],
                Body::from_stream(stream),
            )
                .into_response()
        }
        Ok(resp) => {
            let status = StatusCode::from_u16(resp.status().as_u16())
                .unwrap_or(StatusCode::BAD_GATEWAY);
            let text = resp.text().await.unwrap_or_default();
            (status, text).into_response()
        }
        Err(err) => (
            StatusCode::BAD_GATEWAY,
            format!("Ollama is not reachable: {err}"),
        )
            .into_response(),
    }
}
