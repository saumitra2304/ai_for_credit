use axum::{
    body::Body,
    extract::Json,
    http::StatusCode,
    response::{IntoResponse, Response},
};
use serde::Deserialize;
use serde_json::{json, Value};
use std::env;
use std::net::SocketAddr;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::time::Duration;

const OLLAMA: &str = "http://127.0.0.1:11434";

static MANAGED: Mutex<Option<Child>> = Mutex::new(None);

fn expected_model() -> String {
    env::var("OPENAI_MODEL_NAME").unwrap_or_else(|_| "qwen3:8b".to_string())
}

fn apply_serve_env(cmd: &mut Command) {
    cmd.env("OLLAMA_HOST", "127.0.0.1:11434")
        .env("OLLAMA_CONTEXT_LENGTH", "32768")
        .env("OLLAMA_FLASH_ATTENTION", "1")
        .env("OLLAMA_KV_CACHE_TYPE", "q8_0");
}

fn hide_window(cmd: &mut Command) {
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }
    let _ = cmd;
}

fn which_named(name: &str) -> Option<PathBuf> {
    let path = env::var_os("PATH")?;
    for dir in env::split_paths(&path) {
        let plain = dir.join(name);
        if plain.is_file() {
            return Some(plain);
        }
        #[cfg(windows)]
        {
            let exe = dir.join(format!("{name}.exe"));
            if exe.is_file() {
                return Some(exe);
            }
        }
    }
    None
}

fn find_ollama() -> Option<PathBuf> {
    if let Ok(explicit) = env::var("OLLAMA_PATH") {
        let path = PathBuf::from(explicit);
        if path.is_file() {
            return Some(path);
        }
    }
    if let Some(found) = which_named("ollama") {
        return Some(found);
    }

    let mut candidates = Vec::new();
    if let Some(home) = env::var_os("HOME") {
        let home = PathBuf::from(home);
        candidates.push(home.join(".local/bin/ollama"));
        candidates.push(home.join("bin/ollama"));
    }
    candidates.push(PathBuf::from("/opt/homebrew/bin/ollama"));
    candidates.push(PathBuf::from("/usr/local/bin/ollama"));
    candidates.push(PathBuf::from(
        "/Applications/Ollama.app/Contents/Resources/ollama",
    ));

    if let Some(local) = env::var_os("LOCALAPPDATA") {
        candidates.push(PathBuf::from(local).join("Programs/Ollama/ollama.exe"));
    }
    if let Some(pf) = env::var_os("ProgramFiles") {
        candidates.push(PathBuf::from(pf).join("Ollama/ollama.exe"));
    }
    if let Some(user) = env::var_os("USERPROFILE") {
        candidates.push(
            PathBuf::from(user).join("AppData/Local/Programs/Ollama/ollama.exe"),
        );
    }
    candidates.push(PathBuf::from(r"C:\Program Files\Ollama\ollama.exe"));

    candidates.into_iter().find(|path| path.is_file())
}

async fn ollama_tags() -> Option<Value> {
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(3))
        .build()
        .ok()?;
    let resp = client.get(format!("{OLLAMA}/api/tags")).send().await.ok()?;
    if !resp.status().is_success() {
        return None;
    }
    resp.json().await.ok()
}

fn models_from_tags(payload: &Value) -> Vec<String> {
    payload
        .get("models")
        .and_then(|m| m.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|item| item.get("name").and_then(|n| n.as_str()).map(str::to_string))
                .collect()
        })
        .unwrap_or_default()
}

fn model_installed(models: &[String], model: &str) -> bool {
    models.iter().any(|name| {
        name == model || name.starts_with(&format!("{model}:")) || model.starts_with(name)
    })
}

fn port_open() -> bool {
    let addr: SocketAddr = "127.0.0.1:11434".parse().expect("static ollama addr");
    std::net::TcpStream::connect_timeout(&addr, Duration::from_millis(250)).is_ok()
}

async fn wait_running(seconds: u64) -> bool {
    let attempts = seconds.saturating_mul(4).max(1);
    for _ in 0..attempts {
        if ollama_tags().await.is_some() {
            return true;
        }
        tokio::time::sleep(Duration::from_millis(250)).await;
    }
    false
}

fn spawn_serve(bin: &Path) -> Result<(), String> {
    let log_path = env::temp_dir().join("kuber-ollama.log");
    let log = std::fs::File::create(&log_path)
        .map_err(|err| format!("could not write {}: {err}", log_path.display()))?;
    let log_err = log
        .try_clone()
        .map_err(|err| format!("could not clone ollama log: {err}"))?;

    let mut cmd = Command::new(bin);
    cmd.arg("serve")
        .stdin(Stdio::null())
        .stdout(Stdio::from(log))
        .stderr(Stdio::from(log_err));
    apply_serve_env(&mut cmd);
    hide_window(&mut cmd);

    let child = cmd
        .spawn()
        .map_err(|err| format!("failed to start {}: {err}", bin.display()))?;

    if let Ok(mut slot) = MANAGED.lock() {
        if let Some(mut previous) = slot.take() {
            let _ = previous.kill();
        }
        *slot = Some(child);
    }
    Ok(())
}

fn status_payload(running: bool, tags: Option<&Value>) -> Value {
    let model = expected_model();
    let models = tags.map(models_from_tags).unwrap_or_default();
    let installed = model_installed(&models, &model);
    let binary = find_ollama();
    json!({
        "ok": running,
        "running": running,
        "model": model,
        "installed": installed,
        "models": models,
        "binary_found": binary.is_some(),
        "binary": binary.as_ref().map(|path| path.display().to_string()),
        "managed": MANAGED.lock().ok().is_some_and(|slot| slot.is_some()),
    })
}

pub async fn status() -> Json<Value> {
    match ollama_tags().await {
        Some(payload) => Json(status_payload(true, Some(&payload))),
        None => Json(status_payload(false, None)),
    }
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

pub async fn start() -> Response {
    if let Some(payload) = ollama_tags().await {
        return (StatusCode::OK, Json(status_payload(true, Some(&payload)))).into_response();
    }

    let Some(bin) = find_ollama() else {
        return (
            StatusCode::PRECONDITION_FAILED,
            Json(json!({
                "ok": false,
                "running": false,
                "binary_found": false,
                "model": expected_model(),
                "installed": false,
                "error": "Ollama is not installed. Install it from https://ollama.com/download then click Start LLM.",
                "download_url": "https://ollama.com/download",
            })),
        )
            .into_response();
    };

    if let Err(err) = spawn_serve(&bin) {
        return (
            StatusCode::BAD_GATEWAY,
            Json(json!({
                "ok": false,
                "running": false,
                "binary_found": true,
                "binary": bin.display().to_string(),
                "model": expected_model(),
                "error": err,
            })),
        )
            .into_response();
    }

    if !wait_running(40).await {
        let extra = if port_open() {
            "Ollama opened a port but did not become ready."
        } else {
            "Ollama did not start. Check kuber-ollama.log in the temp folder."
        };
        return (
            StatusCode::GATEWAY_TIMEOUT,
            Json(json!({
                "ok": false,
                "running": false,
                "binary_found": true,
                "binary": bin.display().to_string(),
                "model": expected_model(),
                "error": extra,
            })),
        )
            .into_response();
    }

    let tags = ollama_tags().await;
    (
        StatusCode::OK,
        Json(status_payload(true, tags.as_ref())),
    )
        .into_response()
}

pub async fn warmup() -> Response {
    let model = expected_model();
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(180))
        .build()
        .unwrap_or_else(|_| reqwest::Client::new());

    let result = client
        .post(format!("{OLLAMA}/api/generate"))
        .json(&json!({
            "model": model,
            "prompt": "Ready.",
            "stream": false,
            "keep_alive": "30m",
            "options": { "num_predict": 8 }
        }))
        .send()
        .await;

    match result {
        Ok(resp) if resp.status().is_success() => {
            (StatusCode::OK, Json(json!({ "ok": true, "model": model }))).into_response()
        }
        Ok(resp) => {
            let status = StatusCode::from_u16(resp.status().as_u16())
                .unwrap_or(StatusCode::BAD_GATEWAY);
            let text = resp.text().await.unwrap_or_default();
            (status, Json(json!({ "ok": false, "error": text }))).into_response()
        }
        Err(err) => (
            StatusCode::BAD_GATEWAY,
            Json(json!({
                "ok": false,
                "error": format!("Warm-up failed: {err}"),
            })),
        )
            .into_response(),
    }
}
