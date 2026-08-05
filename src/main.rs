use axum::{
    extract::State,
    routing::get,
    Router,
};
use reqwest::Client;
use std::sync::Arc;
mod routes;
use routes::finacial_summary;

use crate::routes::finacial_summary::{brisk_all, insta_summary};

// 1. Define your shared state struct
#[derive(Clone)]
struct AppState {
    api_key: String,
    reqwest_client:Client,
   
}

#[tokio::main]
async fn main() {

    let client=reqwest::Client::new();


    // 2. Instantiate your state wrapped in Arc
    let state = AppState {
        api_key: String::from("koHNEOKWX6/1KMOIiUDMzrWAxS9rvh8rHvzZtQWcfj+BTb5vA0lSiw=="),
        reqwest_client:client
        
    };

    // 3. Attach state using `.with_state()`
    let app = Router::new()
        .route("/insta_summary", get(insta_summary))
        .with_state(state.clone())
        .route("/brisk_all", get(brisk_all)).with_state(state.clone());

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000")
        .await
        .unwrap();
    
    axum::serve(listener, app).await.unwrap();
}

// 4. Extract state in your handler
