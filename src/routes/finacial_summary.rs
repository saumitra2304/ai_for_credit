use std::time::Duration;
use axum::{
    extract::{Query, State},
    http::StatusCode,
    Json,
};
use reqwest::Client;
use serde::de::DeserializeOwned;
use serde_json::Value;
use tokio::time::sleep;

use crate::{
    routes::models::{final_json_brisk, order_details_briskall, SummaryParams},
    AppState,
};

/// Helper function to perform GET requests with automatic retries for transient network errors.
/// Also validates HTTP status codes and produces detailed error outputs if deserialization fails.
async fn fetch_json<T: DeserializeOwned>(
    client: &Client,
    url: &str,
    api_key: &str,
) -> Result<T, (StatusCode, String)> {
    let mut retries = 3;

    loop {
        let response = client
            .get(url)
            .header("user-key", api_key)
            .send()
            .await;

        match response {
            Ok(resp) => {
                // 1. Check for HTTP 4xx/5xx status codes
                let status = resp.status();
                if !status.is_success() {
                    let error_body = resp
                        .text()
                        .await
                        .unwrap_or_else(|_| "<failed to read error body>".to_string());

                    return Err((
                        StatusCode::BAD_GATEWAY,
                        format!(
                            "Upstream API returned HTTP status {status} for URL ({url}). Response body: {error_body}"
                        ),
                    ));
                }

                // 2. Read raw response text
                let raw_text = resp.text().await.map_err(|err| {
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        format!("Failed to read response body text from ({url}): {err}"),
                    )
                })?;

                // 3. Deserialize JSON with descriptive context
                return serde_json::from_str::<T>(&raw_text).map_err(|err| {
                    (
                        StatusCode::UNPROCESSABLE_ENTITY,
                        format!(
                            "JSON deserialization failed for URL ({url}). Error: {err}. Raw response was: {raw_text}"
                        ),
                    )
                });
            }
            Err(err) => {
                retries -= 1;
                if retries == 0 {
                    return Err((
                        StatusCode::GATEWAY_TIMEOUT,
                        format!("Network request failed after retries for URL ({url}): {err}"),
                    ));
                }
                // Wait 2 seconds before retrying a dropped connection
                sleep(Duration::from_secs(2)).await;
            }
        }
    }
}

async fn fetch_json_post<T: DeserializeOwned>(
    client: &Client,
    url: &str,
    api_key: &str,
) -> Result<T, (StatusCode, String)> {
    let mut retries = 3;

    loop {
        let response = client
            .post(url)
            .header("user-key", api_key)
            .send()
            .await;

        match response {
            Ok(resp) => {
                // 1. Check for HTTP 4xx/5xx status codes
                let status = resp.status();
                if !status.is_success() {
                    let error_body = resp
                        .text()
                        .await
                        .unwrap_or_else(|_| "<failed to read error body>".to_string());

                    return Err((
                        StatusCode::BAD_GATEWAY,
                        format!(
                            "Upstream API returned HTTP status {status} for URL ({url}). Response body: {error_body}"
                        ),
                    ));
                }

                // 2. Read raw response text
                let raw_text = resp.text().await.map_err(|err| {
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        format!("Failed to read response body text from ({url}): {err}"),
                    )
                })?;

                // 3. Deserialize JSON with descriptive context
                return serde_json::from_str::<T>(&raw_text).map_err(|err| {
                    (
                        StatusCode::UNPROCESSABLE_ENTITY,
                        format!(
                            "JSON deserialization failed for URL ({url}). Error: {err}. Raw response was: {raw_text}"
                        ),
                    )
                });
            }
            Err(err) => {
                retries -= 1;
                if retries == 0 {
                    return Err((
                        StatusCode::GATEWAY_TIMEOUT,
                        format!("Network request failed after retries for URL ({url}): {err}"),
                    ));
                }
                // Wait 2 seconds before retrying a dropped connection
                sleep(Duration::from_secs(2)).await;
            }
        }
    }
}

pub async fn insta_summary(
    State(state): State<AppState>,
    Query(params): Query<SummaryParams>,
) -> Result<Json<Value>, (StatusCode, String)> {
    let url = format!(
        "https://instafinancials.com/api/InstaSummary/v1/json/CompanyCIN/{}",
        params.cin
    );

    let json_body: Value = fetch_json(&state.reqwest_client, &url, &state.api_key).await?;
    Ok(Json(json_body))
}

pub async fn brisk_all(
    Query(params): Query<SummaryParams>,
    State(state): State<AppState>,
) -> Result<Json<final_json_brisk>, (StatusCode, String)> {
    let client = &state.reqwest_client;
    let api_key = &state.api_key;

    // Step 1: Order Report
    let order_url = format!(
        "https://api.instafinancials.com/InstaReports/v1/BRisk/CompanyCIN/{}/OrderReport",
        params.cin
    );
    let order_resp: order_details_briskall = fetch_json_post(client, &order_url, api_key).await?;

    // Step 2: Poll status until complete
    let order_status_url = format!(
        "https://api.instafinancials.com/InstaReports/v1/BRisk/OrderID/{}/GetStatus",
        order_resp.order_id
    );

    loop {
        let resp_status: order_details_briskall = fetch_json(client, &order_status_url, api_key).await?;

        if resp_status.order_status == "Order Completed" {
            break;
        }

        sleep(Duration::from_secs(60)).await;
    }

    // Step 3: Download Report
    let download_url = format!(
        "https://api.instafinancials.com/InstaReports/v1/BRisk/OrderID/{}/DownloadReport",
        order_resp.order_id
    );
    let final_report: final_json_brisk = fetch_json(client, &download_url, api_key).await?;

    Ok(Json(final_report))
}