#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use sme_financial_apis::{
    bind_local, load_env_files, load_state, serve, with_internal_token, with_python_origin,
};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use std::time::Duration;
use tauri::Manager;
use tokio::net::TcpListener;

struct PythonSidecar(Mutex<Option<Child>>);

impl Drop for PythonSidecar {
    fn drop(&mut self) {
        if let Ok(mut slot) = self.0.lock() {
            if let Some(child) = slot.as_mut() {
                terminate_child(child);
            }
        }
    }
}

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn reasoning_dir() -> PathBuf {
    repo_root().join("reasoning_layer")
}

fn load_desktop_env(app: &tauri::AppHandle) {
    let mut candidates = Vec::new();

    if let Ok(dir) = app.path().resource_dir() {
        candidates.push(dir.join("bundled.env"));
        candidates.push(dir.join(".env"));
        candidates.push(dir.join("_up_").join("bundled.env"));
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(dir) = exe.parent() {
            candidates.push(dir.join("bundled.env"));
            candidates.push(dir.join(".env"));
            candidates.push(dir.join("../Resources/bundled.env"));
            candidates.push(dir.join("resources/bundled.env"));
        }
    }
    let root = repo_root();
    candidates.push(root.join(".env"));
    candidates.push(root.join("reasoning_layer/.env"));
    candidates.push(root.join("credit_ai_frontend/src-tauri/bundled.env"));

    for path in candidates {
        if path.exists() {
            let _ = dotenvy::from_path(&path);
        }
    }
    load_env_files();
    eprintln!(
        "env: probe_api_key={} INSTA_API_KEY={} OPENAI_MODEL_NAME={}",
        env_flag("probe_api_key"),
        env_flag("INSTA_API_KEY"),
        std::env::var("OPENAI_MODEL_NAME").unwrap_or_else(|_| "qwen3:8b".into()),
    );
}

fn env_flag(name: &str) -> &'static str {
    if std::env::var(name).ok().filter(|s| !s.is_empty()).is_some() {
        "set"
    } else {
        "missing"
    }
}

fn random_token() -> String {
    format!(
        "{}{}",
        uuid::Uuid::new_v4().as_simple(),
        uuid::Uuid::new_v4().as_simple()
    )
}

fn port_open(port: u16) -> bool {
    std::net::TcpStream::connect(("127.0.0.1", port)).is_ok()
}

fn reserve_port() -> std::io::Result<u16> {
    let listener = std::net::TcpListener::bind("127.0.0.1:0")?;
    let port = listener.local_addr()?.port();
    drop(listener);
    Ok(port)
}

fn sidecar_binary(app: &tauri::AppHandle) -> Option<PathBuf> {
    let mut dirs = Vec::new();
    if let Ok(res) = app.path().resource_dir() {
        dirs.push(res.join("binaries"));
        dirs.push(res);
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(dir) = exe.parent() {
            dirs.push(dir.join("../Resources/binaries"));
            dirs.push(dir.join("resources/binaries"));
            dirs.push(dir.join("binaries"));
            dirs.push(dir.to_path_buf());
        }
    }
    dirs.push(PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("binaries"));

    let names = [
        "reasoning-layer",
        "reasoning-layer.exe",
        "reasoning-layer-aarch64-apple-darwin",
        "reasoning-layer-x86_64-apple-darwin",
        "reasoning-layer-x86_64-pc-windows-msvc.exe",
    ];
    for dir in dirs {
        for name in names {
            let path = dir.join(name);
            if path.is_file() {
                return Some(path);
            }
        }
    }
    None
}

fn spawn_python(
    app: &tauri::AppHandle,
    port: u16,
    rust_port: u16,
    token: &str,
    sqlite: &Path,
) -> std::io::Result<Child> {
    let reasoning = reasoning_dir();
    let sidecar = sidecar_binary(app).ok_or_else(|| {
        std::io::Error::new(
            std::io::ErrorKind::NotFound,
            "bundled reasoning-layer sidecar is missing",
        )
    })?;
    eprintln!("using Python sidecar {}", sidecar.display());

    let work_dir = sqlite.parent().filter(|p| p.exists()).unwrap_or(&reasoning);
    let log = std::fs::File::create(work_dir.join("python.log"))?;
    let log_err = log.try_clone()?;

    let mut cmd = Command::new(sidecar);
    cmd.current_dir(work_dir)
        .env("HOST", "127.0.0.1")
        .env("PORT", port.to_string())
        .env("SME_API_BASE", format!("http://127.0.0.1:{rust_port}"))
        .env("INTERNAL_TOKEN", token)
        .env("SQLITE_PATH", sqlite)
        .env("PYTHONUNBUFFERED", "1")
        .stdin(Stdio::null())
        .stdout(Stdio::from(log))
        .stderr(Stdio::from(log_err));

    #[cfg(unix)]
    {
        use std::os::unix::process::CommandExt;
        cmd.process_group(0);
    }
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        const CREATE_NO_WINDOW: u32 = 0x0800_0000;
        cmd.creation_flags(CREATE_NO_WINDOW);
    }

    cmd.spawn()
}

fn terminate_child(child: &mut Child) {
    #[cfg(unix)]
    {
        let pid = child.id() as i32;
        unsafe {
            libc::kill(-pid, libc::SIGTERM);
        }
        std::thread::sleep(Duration::from_millis(300));
        unsafe {
            libc::kill(-pid, libc::SIGKILL);
        }
    }
    let _ = child.kill();
    let _ = child.wait();
}

async fn wait_healthy(origin: &str, token: &str) -> bool {
    let client = reqwest::Client::new();
    for _ in 0..120 {
        let mut req = client.get(format!("{origin}/health"));
        if !token.is_empty() {
            req = req.header("X-Internal-Token", token);
        }
        if let Ok(resp) = req.send().await {
            if resp.status().is_success() {
                return true;
            }
        }
        tokio::time::sleep(Duration::from_millis(250)).await;
    }
    false
}

fn injection_script(api_origin: &str, token: &str) -> String {
    format!(
        r#"Object.defineProperty(window, "__CREDIT_AI__", {{
  configurable: false,
  enumerable: false,
  writable: false,
  value: Object.freeze({{
    apiOrigin: "{api_origin}",
    token: "{token}",
    desktop: true
  }})
}});"#
    )
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            load_desktop_env(app.handle());

            let sqlite = if cfg!(debug_assertions) {
                reasoning_dir().join("credit_ai_db.db")
            } else {
                let dir = app.path().app_data_dir()?;
                std::fs::create_dir_all(&dir)?;
                dir.join("credit_ai.db")
            };

            let use_ephemeral = !cfg!(debug_assertions);
            let token = if use_ephemeral {
                random_token()
            } else {
                String::new()
            };

            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                if let Err(err) = start_backends(handle, sqlite, token, use_ephemeral).await {
                    eprintln!("failed to start backends: {err}");
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

async fn start_backends(
    app: tauri::AppHandle,
    sqlite: PathBuf,
    token: String,
    use_ephemeral: bool,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let rust_preferred: u16 = if use_ephemeral { 0 } else { 3000 };
    let python_port: u16 = if use_ephemeral { reserve_port()? } else { 8001 };

    let rust_listener: Option<TcpListener>;
    let rust_port: u16;
    if rust_preferred != 0 && port_open(rust_preferred) {
        eprintln!("SME API already listening on {rust_preferred}");
        rust_listener = None;
        rust_port = rust_preferred;
    } else {
        let (listener, bound) = bind_local(rust_preferred).await?;
        rust_listener = Some(listener);
        rust_port = bound;
        eprintln!("SME API listening on http://127.0.0.1:{rust_port}");
    }

    let python_child = if port_open(python_port) {
        eprintln!("Python already listening on {python_port}");
        None
    } else {
        match spawn_python(&app, python_port, rust_port, &token, &sqlite) {
            Ok(child) => Some(child),
            Err(err) => {
                eprintln!("failed to spawn Python sidecar: {err}");
                None
            }
        }
    };
    app.manage(PythonSidecar(Mutex::new(python_child)));

    let python_origin = format!("http://127.0.0.1:{python_port}");
    if !wait_healthy(&python_origin, &token).await {
        eprintln!("Python sidecar did not become healthy on {python_origin}");
    }

    if let Some(listener) = rust_listener {
        let mut state = load_state();
        if !token.is_empty() {
            state = with_internal_token(state, token.clone());
        }
        state = with_python_origin(state, python_origin);
        tauri::async_runtime::spawn(async move {
            serve(listener, state).await;
        });
    }

    if use_ephemeral {
        let api_origin = format!("http://127.0.0.1:{rust_port}");
        let script = injection_script(&api_origin, &token);
        if let Some(window) = app.get_webview_window("main") {
            let _ = window.eval(&script);
        }
    }

    Ok(())
}
