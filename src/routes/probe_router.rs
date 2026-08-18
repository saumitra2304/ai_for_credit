use crate::AppState;
use crate::routes::models::search_results_probe;
use axum::{
    Json,
    extract::{Query, State},
};
use reqwest::{Client, Url};
use serde::Deserialize;
use serde_json::Value;
use serde_json::json;

use crate::routes::probe_models::CompanyDetails;

#[derive(Deserialize)]
pub struct params {
    limit: i32,
    filters: String,
}

// curl --location 'https://api.probe42.in/probe_pro_sandbox/entities?limit=25&filters=%7B%22nameStartsWith%22%3A%22Probe%22%2C%22entityType%22%3A%5B%22company%22%2C%22llp%22%5D%7D' \
// --header 'x-api-key: Replace this with your API Key' \
// --header 'Accept: application/json' \
// --header 'x-api-version: 1.3'

pub async fn probe_search(
    State(app_state): State<AppState>,
    Query(search_paramas): Query<params>,
) -> Result<Json<search_results_probe>, String> {
    let api_key = app_state.probe_key;
    let client = app_state.reqwest_client;

    let limit = search_paramas.limit;
    let filters = search_paramas.filters;
    let mut url = Url::parse("https://api.probe42.in/probe_pro_sandbox/entities")
        .map_err(|e| format!("invalid probe URL: {e}"))?;

    url.query_pairs_mut()
        .append_pair("limit", &limit.to_string())
        .append_pair("filters", &filters);

    println!("sending probe request: {}", url);

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
// curl --location 'https://api.probe42.in/probe_pro_sandbox/companies/U15549PN1992FTC065522/comprehensive-details' --header 'x-api-key: Replace this with your API Key' --header 'Accept: application/json' --header 'x-api-version: 1.3'

#[derive(Debug, Deserialize)]
pub struct company_details_params {
    cin: String,
}
pub async fn company_comprehensive_details(
    State(app_state): State<AppState>,
    Query(params): Query<company_details_params>,
) -> Result<Json<Value>, String> {
    let api_key = app_state.probe_key;
    let client = app_state.reqwest_client;

    let cin = params.cin;

    let url =
        format!("https://api.probe42.in/probe_pro_sandbox/companies/{cin}/comprehensive-details");

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
