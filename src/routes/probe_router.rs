use crate::ops::{finish_call, utc_now};
use crate::routes::models::search_results_probe;
use crate::AppState;
use axum::{
    extract::{Query, State},
    http::HeaderMap,
    Json,
};
use reqwest::{Client, Url};
use serde::Deserialize;
use serde_json::Value;
use std::time::{Duration, Instant};
use tokio::time::sleep;

#[derive(Deserialize)]
pub struct params {
    limit: i32,
    filters: String,
}

async fn probe_get_json<T: serde::de::DeserializeOwned>(
    client: &Client,
    url: String,
    api_key: &str,
    metrics: &crate::ops::SmeMetrics,
) -> Result<T, String> {
    let mut last = String::from("probe request failed");
    for attempt in 0..3 {
        let response = client
            .get(&url)
            .header("x-api-key", api_key)
            .header("Accept", "application/json")
            .header("x-api-version", "1.3")
            .send()
            .await;
        match response {
            Ok(resp) => {
                let status = resp.status();
                if status.is_success() {
                    return resp
                        .json()
                        .await
                        .map_err(|err| format!("error getting from probe42 {err}"));
                }
                last = format!("probe HTTP {status}");
                if status.is_server_error() && attempt < 2 {
                    metrics.inc_retry();
                    sleep(Duration::from_millis(250 * (attempt as u64 + 1))).await;
                    continue;
                }
                return Err(last);
            }
            Err(err) => {
                last = format!("error sending to probe42 {err}");
                if attempt < 2 {
                    metrics.inc_retry();
                    sleep(Duration::from_millis(250 * (attempt as u64 + 1))).await;
                    continue;
                }
            }
        }
    }
    Err(last)
}

pub async fn probe_search(
    State(app_state): State<AppState>,
    Query(search_paramas): Query<params>,
    headers: HeaderMap,
) -> Result<Json<search_results_probe>, String> {
    let start = Instant::now();
    let start_ts = utc_now();
    let api_key = crate::probe_key_value(&app_state);
    let client = app_state.reqwest_client.clone();

    let limit = search_paramas.limit;
    let filters = search_paramas.filters;
    let mut url = Url::parse("https://api.probe42.in/probe_pro_sandbox/entities")
        .map_err(|e| format!("invalid probe URL: {e}"))?;

    url.query_pairs_mut()
        .append_pair("limit", &limit.to_string())
        .append_pair("filters", &filters);

    println!("sending probe request: {}", url);

    let permit = app_state
        .probe_limit
        .clone()
        .acquire_owned()
        .await
        .map_err(|err| format!("probe limiter: {err}"))?;
    app_state.metrics.inc_in_flight();
    let result = probe_get_json::<search_results_probe>(
        &client,
        url.to_string(),
        &api_key,
        &app_state.metrics,
    )
    .await
    .map(Json);
    app_state.metrics.dec_in_flight();
    drop(permit);

    finish_call(
        app_state.sqlite_path.clone(),
        app_state.metrics.clone(),
        headers,
        "probe_search",
        start,
        start_ts,
        result.is_ok(),
        result.as_ref().err().cloned(),
    );
    result
}

#[derive(Debug, Deserialize)]
pub struct company_details_params {
    cin: String,
}

pub async fn company_comprehensive_details(
    State(app_state): State<AppState>,
    Query(params): Query<company_details_params>,
    headers: HeaderMap,
) -> Result<Json<Value>, String> {
    let start = Instant::now();
    let start_ts = utc_now();
    let api_key = crate::probe_key_value(&app_state);
    let client = app_state.reqwest_client.clone();

    let cin = params.cin;
    let url =
        format!("https://api.probe42.in/probe_pro_sandbox/companies/{cin}/comprehensive-details");

    let permit = app_state
        .probe_limit
        .clone()
        .acquire_owned()
        .await
        .map_err(|err| format!("probe limiter: {err}"))?;
    app_state.metrics.inc_in_flight();
    let result = probe_get_json::<Value>(&client, url, &api_key, &app_state.metrics)
        .await
        .map(Json);
    app_state.metrics.dec_in_flight();
    drop(permit);

    finish_call(
        app_state.sqlite_path.clone(),
        app_state.metrics.clone(),
        headers,
        "company_details",
        start,
        start_ts,
        result.is_ok(),
        result.as_ref().err().cloned(),
    );
    result
}
