use crate::ops::{finish_call, utc_now};
use crate::routes::models::search_results_probe;
use crate::AppState;
use axum::{
    extract::{Query, State},
    http::HeaderMap,
    Json,
};
use reqwest::Url;
use serde::Deserialize;
use serde_json::Value;
use std::time::Instant;

#[derive(Deserialize)]
pub struct params {
    limit: i32,
    filters: String,
}

pub async fn probe_search(
    State(app_state): State<AppState>,
    Query(search_paramas): Query<params>,
    headers: HeaderMap,
) -> Result<Json<search_results_probe>, String> {
    let start = Instant::now();
    let start_ts = utc_now();
    let api_key = app_state.probe_key_value();
    let client = app_state.reqwest_client.clone();

    let limit = search_paramas.limit;
    let filters = search_paramas.filters;
    let mut url = Url::parse("https://api.probe42.in/probe_pro_sandbox/entities")
        .map_err(|e| format!("invalid probe URL: {e}"))?;

    url.query_pairs_mut()
        .append_pair("limit", &limit.to_string())
        .append_pair("filters", &filters);

    println!("sending probe request: {}", url);

    let result = async {
        let response = client
            .get(url)
            .header("x-api-key", api_key)
            .header("Accept", "application/json")
            .header("x-api-version", "1.3")
            .send()
            .await
            .map_err(|e| format!("error sending to probe42 {e}"))?;

        println!("status: {}", response.status());

        let resp: search_results_probe = response
            .json()
            .await
            .map_err(|e| format!("error getting from probe42 {e}"))?;
        Ok(Json(resp))
    }
    .await;

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
    let api_key = app_state.probe_key_value();
    let client = app_state.reqwest_client.clone();

    let cin = params.cin;
    let url =
        format!("https://api.probe42.in/probe_pro_sandbox/companies/{cin}/comprehensive-details");

    let result = async {
        let resp: Value = client
            .get(url)
            .header("x-api-key", api_key)
            .header("Accept", "application/json")
            .header("x-api-version", "1.3")
            .send()
            .await
            .map_err(|e| format!("error sending to probe42 {e}"))?
            .json()
            .await
            .map_err(|e| format!("error unmarshaling comp details {e}"))?;
        Ok(Json(resp))
    }
    .await;

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
