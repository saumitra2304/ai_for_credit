use std::collections::HashMap;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use axum::http::HeaderMap;
use chrono::{SecondsFormat, Utc};
use rusqlite::Connection;

static SPAN_SEQ: AtomicU64 = AtomicU64::new(1);
static TRIM_TICK: AtomicU64 = AtomicU64::new(0);

struct KeyOverlay {
    mtime_secs: u64,
    probe: String,
    insta: String,
}

static KEY_OVERLAY: Mutex<Option<KeyOverlay>> = Mutex::new(None);

fn file_mtime_secs(path: &Path) -> u64 {
    std::fs::metadata(path)
        .and_then(|meta| meta.modified())
        .ok()
        .and_then(|modified| modified.duration_since(UNIX_EPOCH).ok())
        .map(|duration| duration.as_secs())
        .unwrap_or(0)
}

pub fn utc_now() -> String {
    Utc::now().to_rfc3339_opts(SecondsFormat::Millis, true)
}

pub fn new_id() -> String {
    let n = SPAN_SEQ.fetch_add(1, Ordering::Relaxed);
    let t = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    format!("{t:x}{n:x}")
}

pub fn sqlite_path() -> PathBuf {
    match std::env::var("SQLITE_PATH") {
        Ok(value) if !value.is_empty() => PathBuf::from(value),
        _ => PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("reasoning_layer/credit_ai_db.db"),
    }
}

pub fn overlay_keys(path: &Path, probe: &mut String, insta: &mut String) {
    let mtime = file_mtime_secs(path);
    if let Ok(guard) = KEY_OVERLAY.lock() {
        if let Some(cached) = guard.as_ref() {
            if cached.mtime_secs == mtime && mtime != 0 {
                if !cached.probe.is_empty() {
                    *probe = cached.probe.clone();
                }
                if !cached.insta.is_empty() {
                    *insta = cached.insta.clone();
                }
                return;
            }
        }
    }

    let Ok(conn) = Connection::open(path) else {
        return;
    };
    let _ = conn.busy_timeout(Duration::from_millis(3000));
    let mut overlay = KeyOverlay {
        mtime_secs: mtime,
        probe: String::new(),
        insta: String::new(),
    };
    if let Ok(value) = conn.query_row(
        "SELECT value FROM app_settings WHERE key = 'probe_api_key'",
        [],
        |row| row.get::<_, String>(0),
    ) {
        if !value.is_empty() {
            overlay.probe = value;
            *probe = overlay.probe.clone();
        }
    }
    if let Ok(value) = conn.query_row(
        "SELECT value FROM app_settings WHERE key = 'INSTA_API_KEY'",
        [],
        |row| row.get::<_, String>(0),
    ) {
        if !value.is_empty() {
            overlay.insta = value;
            *insta = overlay.insta.clone();
        }
    }
    if let Ok(mut guard) = KEY_OVERLAY.lock() {
        *guard = Some(overlay);
    }
}

#[derive(Default)]
pub struct SmeMetrics {
    inner: Mutex<Inner>,
}

#[derive(Default)]
struct Inner {
    counts: HashMap<(String, String), u64>,
    duration_sum: HashMap<String, f64>,
    duration_count: HashMap<String, u64>,
}

impl SmeMetrics {
    pub fn observe(&self, route: &str, status: &str, elapsed: Duration) {
        let Ok(mut guard) = self.inner.lock() else {
            return;
        };
        *guard
            .counts
            .entry((route.to_string(), status.to_string()))
            .or_insert(0) += 1;
        *guard.duration_sum.entry(route.to_string()).or_insert(0.0) += elapsed.as_secs_f64();
        *guard.duration_count.entry(route.to_string()).or_insert(0) += 1;
    }

    pub fn render(&self) -> String {
        let Ok(guard) = self.inner.lock() else {
            return String::new();
        };
        let mut out = String::from(
            "# HELP kuber_sme_http_requests_total SME API requests\n# TYPE kuber_sme_http_requests_total counter\n",
        );
        for ((route, status), count) in &guard.counts {
            out.push_str(&format!(
                "kuber_sme_http_requests_total{{route=\"{route}\",status=\"{status}\"}} {count}\n"
            ));
        }
        out.push_str(
            "# HELP kuber_sme_http_request_duration_seconds SME API request duration\n# TYPE kuber_sme_http_request_duration_seconds summary\n",
        );
        for (route, sum) in &guard.duration_sum {
            let count = guard.duration_count.get(route).copied().unwrap_or(0);
            out.push_str(&format!(
                "kuber_sme_http_request_duration_seconds_sum{{route=\"{route}\"}} {sum}\n"
            ));
            out.push_str(&format!(
                "kuber_sme_http_request_duration_seconds_count{{route=\"{route}\"}} {count}\n"
            ));
        }
        out
    }
}

pub fn headers_trace(headers: &HeaderMap) -> (String, Option<String>) {
    let trace = headers
        .get("x-request-id")
        .and_then(|value| value.to_str().ok())
        .filter(|value| !value.is_empty())
        .map(|value| value.to_string())
        .unwrap_or_else(new_id);
    let parent = headers
        .get("x-parent-span-id")
        .and_then(|value| value.to_str().ok())
        .filter(|value| !value.is_empty())
        .map(|value| value.to_string());
    (trace, parent)
}

fn maybe_trim(conn: &Connection) {
    if TRIM_TICK.fetch_add(1, Ordering::Relaxed) % 64 != 0 {
        return;
    }
    let _ = conn.execute(
        "DELETE FROM app_spans WHERE id NOT IN (SELECT id FROM app_spans ORDER BY id DESC LIMIT 10000)",
        [],
    );
    let _ = conn.execute(
        "DELETE FROM app_logs WHERE id NOT IN (SELECT id FROM app_logs ORDER BY id DESC LIMIT 20000)",
        [],
    );
}

fn record_span(
    path: &Path,
    trace_id: &str,
    span_id: &str,
    parent_id: Option<&str>,
    name: &str,
    start_ts: &str,
    end_ts: &str,
    status: &str,
    attrs_json: Option<&str>,
) {
    let Ok(conn) = Connection::open(path) else {
        return;
    };
    let _ = conn.busy_timeout(Duration::from_millis(3000));
    let _ = conn.execute(
        "INSERT INTO app_spans (trace_id, span_id, parent_id, name, start_ts, end_ts, status, attrs_json)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
        rusqlite::params![
            trace_id,
            span_id,
            parent_id,
            name,
            start_ts,
            end_ts,
            status,
            attrs_json
        ],
    );
    maybe_trim(&conn);
}

fn record_log(path: &Path, level: &str, message: &str, request_id: Option<&str>) {
    let Ok(conn) = Connection::open(path) else {
        return;
    };
    let _ = conn.busy_timeout(Duration::from_millis(3000));
    let clipped = if message.len() > 2000 {
        format!("{}…", &message[..2000])
    } else {
        message.to_string()
    };
    let _ = conn.execute(
        "INSERT INTO app_logs (ts, level, source, message, request_id, extra_json)
         VALUES (?1, ?2, 'rust', ?3, ?4, NULL)",
        rusqlite::params![utc_now(), level, clipped, request_id],
    );
    maybe_trim(&conn);
}

pub fn finish_call(
    sqlite: PathBuf,
    metrics: Arc<SmeMetrics>,
    headers: HeaderMap,
    route: &'static str,
    start: Instant,
    start_ts: String,
    ok: bool,
    err: Option<String>,
) {
    let status_http = if ok { "200" } else { "500" };
    metrics.observe(route, status_http, start.elapsed());
    let (trace, parent) = headers_trace(&headers);
    let span_id = new_id();
    let end_ts = utc_now();
    let status = if ok { "ok" } else { "error" };
    let attrs = err.as_ref().map(|message| {
        serde_json::json!({ "error": message }).to_string()
    });
    let log_message = if ok {
        None
    } else {
        Some(format!("{route} failed: {}", err.unwrap_or_default()))
    };
    tokio::task::spawn_blocking(move || {
        record_span(
            &sqlite,
            &trace,
            &span_id,
            parent.as_deref(),
            route,
            &start_ts,
            &end_ts,
            status,
            attrs.as_deref(),
        );
        if let Some(message) = log_message {
            record_log(&sqlite, "error", &message, Some(&trace));
        }
    });
}
