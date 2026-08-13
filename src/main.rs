use axum::{
    extract::State,
    routing::get,
    Router,
};
use reqwest::Client;
use std::sync::Arc;
mod routes;
use routes::finacial_summary;
use routes::probe_router::{probe_search,company_comprehensive_details};

use std::env;

use crate::routes::finacial_summary::{brisk_all, insta_summary};

// 1. Define your shared state struct
#[derive(Clone)]
struct AppState {
    api_key: String,
    reqwest_client:Client,
    probe_key:String,
   
}

#[tokio::main]
async fn main() {

    let client=reqwest::Client::new();

    let probe_key=extract_en();


    // 2. Instantiate your state wrapped in Arc
    let state = AppState {
        api_key: String::from("koHNEOKWX6/1KMOIiUDMzrWAxS9rvh8rHvzZtQWcfj+BTb5vA0lSiw=="),
        reqwest_client:client,
        probe_key:probe_key
        
    };

    // 3. Attach state using `.with_state()`
    let app = Router::new()
        .route("/insta_summary", get(insta_summary))
        .with_state(state.clone())
        .route("/brisk_all", get(brisk_all)).with_state(state.clone())
        .route("/search_company", get(probe_search)).with_state(state.clone())
        .route("/company_details",get(company_comprehensive_details).with_state(state.clone()));

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000")
        .await
        .unwrap();
    
    axum::serve(listener, app).await.unwrap();
}

fn extract_en()->String{
    dotenvy::dotenv().ok();

    // 2. Read environment variables
    
    // Method A: Using unwrap or expect (panics if variable isn't set)
    let probe_key = env::var("probe_api_key")
        .expect("probe_api_key must be set in .env or environment");

    return probe_key;
}

// 4. Extract state in your handler
