use serde::Deserialize;
use serde::Serialize;
use serde_json::Value;

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CompanyDetails {
    pub metadata: Metadata,
    pub data: Data,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Metadata {
    #[serde(rename = "api_version")]
    pub api_version: String,
    #[serde(rename = "last_updated")]
    pub last_updated: String,
    #[serde(rename = "identifier_changed")]
    pub identifier_changed: bool,
    #[serde(rename = "document_list_token")]
    pub document_list_token: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Data {
    pub company: Company,
    pub description: Description,
    #[serde(rename = "name_history")]
    pub name_history: Vec<NameHistory>,
    #[serde(rename = "authorized_signatories")]
    pub authorized_signatories: Vec<AuthorizedSignatory>,
    #[serde(rename = "director_network")]
    pub director_network: Vec<DirectorNetwork>,
    #[serde(rename = "contact_details")]
    pub contact_details: ContactDetails,
    #[serde(rename = "open_charges")]
    pub open_charges: Vec<Value>,
    #[serde(rename = "open_charges_latest_event")]
    pub open_charges_latest_event: Vec<Value>,
    #[serde(rename = "charge_sequence")]
    pub charge_sequence: Vec<Value>,
    pub financials: Vec<Financial>,
    #[serde(rename = "nbfc_financials")]
    pub nbfc_financials: Vec<Value>,
    #[serde(rename = "financial_parameters")]
    pub financial_parameters: Vec<FinancialParameter>,
    #[serde(rename = "industry_segments")]
    pub industry_segments: Vec<IndustrySegment>,
    #[serde(rename = "principal_business_activities")]
    pub principal_business_activities: Vec<PrincipalBusinessActivity>,
    #[serde(rename = "related_party_transactions")]
    pub related_party_transactions: Vec<RelatedPartyTransaction>,
    #[serde(rename = "establishments_registered_with_epfo")]
    pub establishments_registered_with_epfo: Vec<EstablishmentsRegisteredWithEpfo>,
    pub shareholdings: Vec<Shareholding>,
    #[serde(rename = "shareholdings_more_than_five_percent")]
    pub shareholdings_more_than_five_percent: Vec<ShareholdingsMoreThanFivePercent>,
    #[serde(rename = "shareholdings_summary")]
    pub shareholdings_summary: Vec<ShareholdingsSummary>,
    #[serde(rename = "director_shareholdings")]
    pub director_shareholdings: Vec<DirectorShareholding>,
    #[serde(rename = "bifr_history")]
    pub bifr_history: Vec<Value>,
    #[serde(rename = "cdr_history")]
    pub cdr_history: Vec<Value>,
    #[serde(rename = "defaulter_list")]
    pub defaulter_list: Vec<Value>,
    #[serde(rename = "legal_history")]
    pub legal_history: Vec<LegalHistory>,
    #[serde(rename = "credit_ratings")]
    pub credit_ratings: Vec<Value>,
    #[serde(rename = "credit_rating_rationale")]
    pub credit_rating_rationale: Vec<Value>,
    #[serde(rename = "unaccepted_rating")]
    pub unaccepted_rating: Value,
    #[serde(rename = "holding_entities")]
    pub holding_entities: HoldingEntities,
    #[serde(rename = "subsidiary_entities")]
    pub subsidiary_entities: SubsidiaryEntities,
    #[serde(rename = "associate_entities")]
    pub associate_entities: Value,
    #[serde(rename = "joint_ventures")]
    pub joint_ventures: Value,
    #[serde(rename = "securities_allotment")]
    pub securities_allotment: Vec<Value>,
    #[serde(rename = "peer_comparison")]
    pub peer_comparison: Vec<PeerComparison>,
    #[serde(rename = "gst_details")]
    pub gst_details: Vec<GstDetail>,
    #[serde(rename = "struckoff248_details")]
    pub struckoff248_details: Struckoff248Details,
    #[serde(rename = "msme_supplier_payment_delays")]
    pub msme_supplier_payment_delays: MsmeSupplierPaymentDelays,
    #[serde(rename = "legal_cases_of_financial_disputes")]
    pub legal_cases_of_financial_disputes: Vec<Value>,
    #[serde(rename = "probe_financial_score")]
    pub probe_financial_score: ProbeFinancialScore,
    #[serde(rename = "key_indicators")]
    pub key_indicators: KeyIndicators,
    #[serde(rename = "filing_dates")]
    pub filing_dates: FilingDates,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Company {
    pub cin: String,
    #[serde(rename = "legal_name")]
    pub legal_name: String,
    #[serde(rename = "efiling_status")]
    pub efiling_status: String,
    #[serde(rename = "incorporation_date")]
    pub incorporation_date: String,
    #[serde(rename = "paid_up_capital")]
    pub paid_up_capital: i64,
    #[serde(rename = "sum_of_charges")]
    pub sum_of_charges: i64,
    #[serde(rename = "authorized_capital")]
    pub authorized_capital: i64,
    #[serde(rename = "active_compliance")]
    pub active_compliance: String,
    #[serde(rename = "cirp_status")]
    pub cirp_status: Value,
    pub lei: Lei,
    #[serde(rename = "registered_address")]
    pub registered_address: RegisteredAddress,
    #[serde(rename = "business_address")]
    pub business_address: BusinessAddress,
    pub pan: String,
    pub website: String,
    pub classification: String,
    pub status: String,
    #[serde(rename = "next_cin")]
    pub next_cin: Value,
    #[serde(rename = "last_agm_date")]
    pub last_agm_date: String,
    #[serde(rename = "last_filing_date")]
    pub last_filing_date: String,
    pub email: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Lei {
    pub number: String,
    pub status: String,
    #[serde(rename = "registration_date")]
    pub registration_date: String,
    #[serde(rename = "last_updated_date")]
    pub last_updated_date: String,
    #[serde(rename = "next_renewal_date")]
    pub next_renewal_date: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RegisteredAddress {
    #[serde(rename = "full_address")]
    pub full_address: String,
    #[serde(rename = "address_line1")]
    pub address_line1: String,
    #[serde(rename = "address_line2")]
    pub address_line2: String,
    pub city: String,
    pub pincode: String,
    pub state: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BusinessAddress {
    #[serde(rename = "address_line1")]
    pub address_line1: String,
    #[serde(rename = "address_line2")]
    pub address_line2: String,
    pub city: String,
    pub pincode: i64,
    pub state: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Description {
    #[serde(rename = "desc_thousand_char")]
    pub desc_thousand_char: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NameHistory {
    pub name: String,
    pub date: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AuthorizedSignatory {
    pub pan: Option<String>,
    pub din: Option<String>,
    pub name: String,
    pub designation: String,
    #[serde(rename = "din_status")]
    pub din_status: Option<String>,
    pub gender: Option<String>,
    #[serde(rename = "date_of_birth")]
    pub date_of_birth: Option<String>,
    pub age: i64,
    #[serde(rename = "date_of_appointment")]
    pub date_of_appointment: Option<String>,
    #[serde(rename = "date_of_appointment_for_current_designation")]
    pub date_of_appointment_for_current_designation: Option<String>,
    #[serde(rename = "date_of_cessation")]
    pub date_of_cessation: Option<String>,
    pub nationality: Option<String>,
    #[serde(rename = "dsc_status")]
    pub dsc_status: Value,
    #[serde(rename = "dsc_expiry_date")]
    pub dsc_expiry_date: Value,
    #[serde(rename = "father_name")]
    pub father_name: Value,
    pub address: Address,
    #[serde(rename = "association_history")]
    pub association_history: Vec<AssociationHistory>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Address {
    #[serde(rename = "address_line1")]
    pub address_line1: Value,
    #[serde(rename = "address_line2")]
    pub address_line2: Value,
    pub city: Value,
    pub state: Value,
    pub pincode: Value,
    pub country: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AssociationHistory {
    pub event: Value,
    #[serde(rename = "designation_after_event")]
    pub designation_after_event: String,
    #[serde(rename = "event_date")]
    pub event_date: String,
    #[serde(rename = "filing_date")]
    pub filing_date: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DirectorNetwork {
    pub name: String,
    pub pan: Option<String>,
    pub din: String,
    pub network: Network,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Network {
    pub companies: Vec<Company2>,
    pub llps: Vec<Llp>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Company2 {
    pub cin: String,
    #[serde(rename = "legal_name")]
    pub legal_name: String,
    #[serde(rename = "company_status")]
    pub company_status: String,
    #[serde(rename = "incorporation_date")]
    pub incorporation_date: String,
    #[serde(rename = "paid_up_capital")]
    pub paid_up_capital: i64,
    #[serde(rename = "sum_of_charges")]
    pub sum_of_charges: i64,
    pub city: String,
    #[serde(rename = "active_compliance")]
    pub active_compliance: Option<String>,
    #[serde(rename = "cirp_status")]
    pub cirp_status: Value,
    pub designation: String,
    #[serde(rename = "date_of_appointment")]
    pub date_of_appointment: String,
    #[serde(rename = "date_of_appointment_for_current_designation")]
    pub date_of_appointment_for_current_designation: String,
    #[serde(rename = "date_of_cessation")]
    pub date_of_cessation: Option<String>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Llp {
    pub llpin: String,
    #[serde(rename = "legal_name")]
    pub legal_name: String,
    pub status: String,
    #[serde(rename = "incorporation_date")]
    pub incorporation_date: String,
    #[serde(rename = "total_obligation_of_contribution")]
    pub total_obligation_of_contribution: i64,
    #[serde(rename = "sum_of_charges")]
    pub sum_of_charges: i64,
    pub city: String,
    #[serde(rename = "cirp_status")]
    pub cirp_status: Value,
    pub designation: String,
    #[serde(rename = "date_of_appointment")]
    pub date_of_appointment: String,
    #[serde(rename = "date_of_appointment_for_current_designation")]
    pub date_of_appointment_for_current_designation: String,
    #[serde(rename = "date_of_cessation")]
    pub date_of_cessation: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ContactDetails {
    pub email: Vec<Email>,
    pub phone: Vec<Phone>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Email {
    pub email_id: String,
    pub status: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Phone {
    pub phone_number: String,
    pub status: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Financial {
    pub year: String,
    pub nature: String,
    #[serde(rename = "stated_on")]
    pub stated_on: String,
    #[serde(rename = "filing_type")]
    pub filing_type: String,
    #[serde(rename = "start_date")]
    pub start_date: String,
    #[serde(rename = "filing_standard")]
    pub filing_standard: String,
    pub ratios: Ratios,
    pub bs: Bs,
    pub pnl: Pnl,
    #[serde(rename = "cash_flow")]
    pub cash_flow: CashFlow,
    #[serde(rename = "pnl_key_schedule")]
    pub pnl_key_schedule: PnlKeySchedule,
    pub auditor: Option<Auditor>,
    #[serde(rename = "auditor_comments")]
    pub auditor_comments: Option<AuditorComments>,
    #[serde(rename = "auditor_additional")]
    pub auditor_additional: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Ratios {
    #[serde(rename = "revenue_growth")]
    pub revenue_growth: Option<f64>,
    #[serde(rename = "gross_profit_margin")]
    pub gross_profit_margin: f64,
    #[serde(rename = "net_margin")]
    pub net_margin: f64,
    #[serde(rename = "ebitda_margin")]
    pub ebitda_margin: f64,
    #[serde(rename = "return_on_equity")]
    pub return_on_equity: f64,
    #[serde(rename = "return_on_capital_employed")]
    pub return_on_capital_employed: f64,
    #[serde(rename = "debt_ratio")]
    pub debt_ratio: i64,
    #[serde(rename = "debt_by_equity")]
    pub debt_by_equity: i64,
    #[serde(rename = "interest_coverage_ratio")]
    pub interest_coverage_ratio: Option<f64>,
    #[serde(rename = "current_ratio")]
    pub current_ratio: f64,
    #[serde(rename = "quick_ratio")]
    pub quick_ratio: f64,
    #[serde(rename = "inventory_by_sales_days")]
    pub inventory_by_sales_days: f64,
    #[serde(rename = "debtors_by_sales_days")]
    pub debtors_by_sales_days: f64,
    #[serde(rename = "payables_by_sales_days")]
    pub payables_by_sales_days: f64,
    #[serde(rename = "cash_conversion_cycle")]
    pub cash_conversion_cycle: f64,
    #[serde(rename = "sales_by_net_fixed_assets")]
    pub sales_by_net_fixed_assets: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Bs {
    pub assets: Assets,
    pub liabilities: Liabilities,
    pub sub_totals: SubTotals,
    pub metadata: Metadata2,
    pub notes: Option<Notes>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Assets {
    #[serde(rename = "tangible_assets")]
    pub tangible_assets: i64,
    #[serde(rename = "producing_properties")]
    pub producing_properties: Value,
    #[serde(rename = "intangible_assets")]
    pub intangible_assets: i64,
    #[serde(rename = "preproducing_properties")]
    pub preproducing_properties: Value,
    #[serde(rename = "tangible_assets_capital_work_in_progress")]
    pub tangible_assets_capital_work_in_progress: i64,
    #[serde(rename = "intangible_assets_under_development")]
    pub intangible_assets_under_development: Value,
    #[serde(rename = "noncurrent_investments")]
    pub noncurrent_investments: i64,
    #[serde(rename = "deferred_tax_assets_net")]
    pub deferred_tax_assets_net: i64,
    #[serde(rename = "foreign_curr_monetary_item_trans_diff_asset_account")]
    pub foreign_curr_monetary_item_trans_diff_asset_account: Value,
    #[serde(rename = "long_term_loans_and_advances")]
    pub long_term_loans_and_advances: i64,
    #[serde(rename = "other_noncurrent_assets")]
    pub other_noncurrent_assets: Option<i64>,
    #[serde(rename = "current_investments")]
    pub current_investments: i64,
    pub inventories: i64,
    #[serde(rename = "trade_receivables")]
    pub trade_receivables: i64,
    #[serde(rename = "cash_and_bank_balances")]
    pub cash_and_bank_balances: i64,
    #[serde(rename = "short_term_loans_and_advances")]
    pub short_term_loans_and_advances: i64,
    #[serde(rename = "other_current_assets")]
    pub other_current_assets: i64,
    #[serde(rename = "given_assets_total")]
    pub given_assets_total: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Liabilities {
    #[serde(rename = "share_capital")]
    pub share_capital: i64,
    #[serde(rename = "reserves_and_surplus")]
    pub reserves_and_surplus: i64,
    #[serde(rename = "money_received_against_share_warrants")]
    pub money_received_against_share_warrants: Value,
    #[serde(rename = "share_application_money_pending_allotment")]
    pub share_application_money_pending_allotment: Option<i64>,
    #[serde(rename = "deferred_government_grants")]
    pub deferred_government_grants: Value,
    #[serde(rename = "minority_interest")]
    pub minority_interest: Option<i64>,
    #[serde(rename = "long_term_borrowings")]
    pub long_term_borrowings: i64,
    #[serde(rename = "deferred_tax_liabilities_net")]
    pub deferred_tax_liabilities_net: Value,
    #[serde(rename = "foreign_curr_monetary_item_trans_diff_liability_account")]
    pub foreign_curr_monetary_item_trans_diff_liability_account: Value,
    #[serde(rename = "other_long_term_liabilities")]
    pub other_long_term_liabilities: Option<i64>,
    #[serde(rename = "long_term_provisions")]
    pub long_term_provisions: i64,
    #[serde(rename = "short_term_borrowings")]
    pub short_term_borrowings: i64,
    #[serde(rename = "trade_payables")]
    pub trade_payables: i64,
    #[serde(rename = "other_current_liabilities")]
    pub other_current_liabilities: i64,
    #[serde(rename = "short_term_provisions")]
    pub short_term_provisions: i64,
    #[serde(rename = "given_liabilities_total")]
    pub given_liabilities_total: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SubTotals {
    #[serde(rename = "total_equity")]
    pub total_equity: i64,
    #[serde(rename = "total_non_current_liabilities")]
    pub total_non_current_liabilities: i64,
    #[serde(rename = "total_current_liabilities")]
    pub total_current_liabilities: i64,
    #[serde(rename = "net_fixed_assets")]
    pub net_fixed_assets: i64,
    #[serde(rename = "total_current_assets")]
    pub total_current_assets: i64,
    #[serde(rename = "capital_wip")]
    pub capital_wip: i64,
    #[serde(rename = "total_debt")]
    pub total_debt: i64,
    #[serde(rename = "total_other_non_current_assets")]
    pub total_other_non_current_assets: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Metadata2 {
    #[serde(rename = "doc_id")]
    pub doc_id: Option<String>,
    #[serde(rename = "xml_to_pdf_converted_doc_id")]
    pub xml_to_pdf_converted_doc_id: Option<String>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Notes {
    #[serde(rename = "gross_fixed_assets")]
    pub gross_fixed_assets: Option<i64>,
    #[serde(rename = "trade_receivable_exceeding_six_months")]
    pub trade_receivable_exceeding_six_months: Option<i64>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Pnl {
    pub line_items: LineItems,
    pub sub_totals: SubTotals2,
    #[serde(rename = "revenue_breakup")]
    pub revenue_breakup: RevenueBreakup,
    #[serde(rename = "depreciation_breakup")]
    pub depreciation_breakup: DepreciationBreakup,
    pub metadata: Metadata3,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LineItems {
    #[serde(rename = "net_revenue")]
    pub net_revenue: i64,
    #[serde(rename = "total_cost_of_materials_consumed")]
    pub total_cost_of_materials_consumed: i64,
    #[serde(rename = "total_purchases_of_stock_in_trade")]
    pub total_purchases_of_stock_in_trade: i64,
    #[serde(rename = "total_changes_in_inventories_or_finished_goods")]
    pub total_changes_in_inventories_or_finished_goods: i64,
    #[serde(rename = "total_employee_benefit_expense")]
    pub total_employee_benefit_expense: i64,
    #[serde(rename = "total_other_expenses")]
    pub total_other_expenses: i64,
    #[serde(rename = "operating_profit")]
    pub operating_profit: i64,
    #[serde(rename = "other_income")]
    pub other_income: i64,
    pub depreciation: i64,
    #[serde(rename = "profit_before_interest_and_tax")]
    pub profit_before_interest_and_tax: i64,
    pub interest: i64,
    #[serde(rename = "profit_before_tax_and_exceptional_items_before_tax")]
    pub profit_before_tax_and_exceptional_items_before_tax: i64,
    #[serde(rename = "exceptional_items_before_tax")]
    pub exceptional_items_before_tax: Option<i64>,
    #[serde(rename = "profit_before_tax")]
    pub profit_before_tax: i64,
    #[serde(rename = "income_tax")]
    pub income_tax: i64,
    #[serde(rename = "profit_for_period_from_continuing_operations")]
    pub profit_for_period_from_continuing_operations: i64,
    #[serde(rename = "profit_from_discontinuing_operation_after_tax")]
    pub profit_from_discontinuing_operation_after_tax: Option<i64>,
    #[serde(rename = "minority_interest_and_profit_from_associates_and_joint_ventures")]
    pub minority_interest_and_profit_from_associates_and_joint_ventures: Option<i64>,
    #[serde(rename = "profit_after_tax")]
    pub profit_after_tax: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SubTotals2 {
    #[serde(rename = "total_operating_cost")]
    pub total_operating_cost: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RevenueBreakup {
    #[serde(rename = "revenue_from_operations")]
    pub revenue_from_operations: Option<i64>,
    #[serde(rename = "revenue_from_interest")]
    pub revenue_from_interest: Value,
    #[serde(rename = "revenue_from_other_financial_services")]
    pub revenue_from_other_financial_services: Value,
    #[serde(rename = "revenue_from_sale_of_products")]
    pub revenue_from_sale_of_products: Option<i64>,
    #[serde(rename = "revenue_from_sale_of_services")]
    pub revenue_from_sale_of_services: Option<i64>,
    #[serde(rename = "other_operating_revenues")]
    pub other_operating_revenues: Option<i64>,
    #[serde(rename = "excise_duty")]
    pub excise_duty: Option<i64>,
    #[serde(rename = "service_tax_collected")]
    pub service_tax_collected: Value,
    #[serde(rename = "other_duties_taxes_collected")]
    pub other_duties_taxes_collected: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DepreciationBreakup {
    pub depreciation: i64,
    pub amortisation: Value,
    pub depletion: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Metadata3 {
    pub doc_id: Option<String>,
    #[serde(rename = "xml_to_pdf_converted_doc_id")]
    pub xml_to_pdf_converted_doc_id: Option<String>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CashFlow {
    #[serde(rename = "profit_before_tax")]
    pub profit_before_tax: i64,
    #[serde(rename = "adjustment_for_finance_cost_and_depreciation")]
    pub adjustment_for_finance_cost_and_depreciation: i64,
    #[serde(rename = "adjustment_for_current_and_non_current_assets")]
    pub adjustment_for_current_and_non_current_assets: i64,
    #[serde(rename = "adjustment_for_current_and_non_current_liabilities")]
    pub adjustment_for_current_and_non_current_liabilities: i64,
    #[serde(rename = "other_adjustments_in_operating_activities")]
    pub other_adjustments_in_operating_activities: i64,
    #[serde(rename = "cash_flows_from_used_in_operating_activities")]
    pub cash_flows_from_used_in_operating_activities: i64,
    #[serde(rename = "cash_outflow_from_purchase_of_assets")]
    pub cash_outflow_from_purchase_of_assets: i64,
    #[serde(rename = "cash_inflow_from_sale_of_assets")]
    pub cash_inflow_from_sale_of_assets: i64,
    #[serde(rename = "income_from_assets")]
    pub income_from_assets: i64,
    #[serde(rename = "other_adjustments_in_investing_activities")]
    pub other_adjustments_in_investing_activities: Option<i64>,
    #[serde(rename = "cash_flows_from_used_in_investing_activities")]
    pub cash_flows_from_used_in_investing_activities: i64,
    #[serde(rename = "cash_outflow_from_repayment_of_capital_and_borrowings")]
    pub cash_outflow_from_repayment_of_capital_and_borrowings: Option<i64>,
    #[serde(rename = "cash_inflow_from_raisng_capital_and_borrowings")]
    pub cash_inflow_from_raisng_capital_and_borrowings: Option<i64>,
    #[serde(rename = "interest_and_dividends_paid")]
    pub interest_and_dividends_paid: i64,
    #[serde(rename = "other_adjustments_in_financing_activities")]
    pub other_adjustments_in_financing_activities: Option<i64>,
    #[serde(rename = "cash_flows_from_used_in_financing_activities")]
    pub cash_flows_from_used_in_financing_activities: i64,
    #[serde(rename = "incr_decr_in_cash_cash_equv_before_effect_of_excg_rate_changes")]
    pub incr_decr_in_cash_cash_equv_before_effect_of_excg_rate_changes: i64,
    #[serde(rename = "adjustments_to_cash_and_cash_equivalents")]
    pub adjustments_to_cash_and_cash_equivalents: Value,
    #[serde(rename = "incr_decr_in_cash_cash_equv")]
    pub incr_decr_in_cash_cash_equv: i64,
    #[serde(rename = "cash_flow_statement_at_end_of_period")]
    pub cash_flow_statement_at_end_of_period: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PnlKeySchedule {
    #[serde(rename = "managerial_remuneration")]
    pub managerial_remuneration: i64,
    #[serde(rename = "payment_to_auditors")]
    pub payment_to_auditors: i64,
    #[serde(rename = "insurance_expenses")]
    pub insurance_expenses: i64,
    #[serde(rename = "power_and_fuel")]
    pub power_and_fuel: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Auditor {
    #[serde(rename = "auditor_name")]
    pub auditor_name: String,
    #[serde(rename = "auditor_firm_name")]
    pub auditor_firm_name: String,
    pub pan: String,
    #[serde(rename = "membership_number")]
    pub membership_number: String,
    #[serde(rename = "firm_registration_number")]
    pub firm_registration_number: String,
    pub address: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AuditorComments {
    #[serde(rename = "report_has_adverse_remarks")]
    pub report_has_adverse_remarks: bool,
    #[serde(rename = "disclosures_auditor_report")]
    pub disclosures_auditor_report: Vec<Value>,
    #[serde(rename = "disclosures_director_report")]
    pub disclosures_director_report: Vec<Value>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FinancialParameter {
    pub year: String,
    pub nature: String,
    #[serde(rename = "earning_fc")]
    pub earning_fc: Option<i64>,
    #[serde(rename = "expenditure_fc")]
    pub expenditure_fc: Option<i64>,
    #[serde(rename = "transaction_related_parties_as_18")]
    pub transaction_related_parties_as_18: Option<i64>,
    #[serde(rename = "employee_benefit_expense")]
    pub employee_benefit_expense: Option<i64>,
    #[serde(rename = "number_of_employees")]
    pub number_of_employees: Value,
    #[serde(rename = "prescribed_csr_expenditure")]
    pub prescribed_csr_expenditure: Option<f64>,
    #[serde(rename = "total_amount_csr_spent_for_financial_year")]
    pub total_amount_csr_spent_for_financial_year: Option<i64>,
    #[serde(rename = "gross_fixed_assets")]
    pub gross_fixed_assets: Option<i64>,
    #[serde(rename = "trade_receivable_exceeding_six_months")]
    pub trade_receivable_exceeding_six_months: Option<i64>,
    #[serde(rename = "proposed_dividend")]
    pub proposed_dividend: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct IndustrySegment {
    pub industry: String,
    pub segments: Vec<String>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PrincipalBusinessActivity {
    pub year: String,
    #[serde(rename = "main_activity_group_code")]
    pub main_activity_group_code: String,
    #[serde(rename = "main_activity_group_description")]
    pub main_activity_group_description: String,
    #[serde(rename = "business_activity_code")]
    pub business_activity_code: String,
    #[serde(rename = "business_activity_description")]
    pub business_activity_description: String,
    #[serde(rename = "percentage_of_turnover")]
    pub percentage_of_turnover: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RelatedPartyTransaction {
    #[serde(rename = "financial_year")]
    pub financial_year: String,
    pub company: Vec<Company3>,
    pub llp: Vec<Value>,
    pub individual: Vec<Individual>,
    pub others: Vec<Other>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Company3 {
    pub name: String,
    #[serde(rename = "legal_name")]
    pub legal_name: String,
    pub relationship: String,
    #[serde(rename = "type_of_transaction")]
    pub type_of_transaction: String,
    pub amount: i64,
    pub cin: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Individual {
    pub name: String,
    #[serde(rename = "legal_name")]
    pub legal_name: String,
    pub relationship: String,
    #[serde(rename = "type_of_transaction")]
    pub type_of_transaction: String,
    pub amount: String,
    pub din: Option<String>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Other {
    pub name: String,
    #[serde(rename = "legal_name")]
    pub legal_name: String,
    pub relationship: String,
    #[serde(rename = "type_of_transaction")]
    pub type_of_transaction: String,
    pub amount: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EstablishmentsRegisteredWithEpfo {
    #[serde(rename = "establishment_id")]
    pub establishment_id: String,
    #[serde(rename = "establishment_name")]
    pub establishment_name: String,
    #[serde(rename = "working_status")]
    pub working_status: String,
    #[serde(rename = "principal_business_activities")]
    pub principal_business_activities: String,
    #[serde(rename = "date_of_setup")]
    pub date_of_setup: String,
    pub address: String,
    pub city: String,
    #[serde(rename = "exemption_status_edli")]
    pub exemption_status_edli: String,
    #[serde(rename = "exemption_status_pension")]
    pub exemption_status_pension: String,
    #[serde(rename = "exemption_status_pf")]
    pub exemption_status_pf: String,
    #[serde(rename = "latest_wage_month")]
    pub latest_wage_month: String,
    #[serde(rename = "latest_date_of_credit")]
    pub latest_date_of_credit: Value,
    #[serde(rename = "no_of_employees")]
    pub no_of_employees: i64,
    pub amount: i64,
    #[serde(rename = "payment_timeliness")]
    pub payment_timeliness: String,
    #[serde(rename = "filing_details")]
    pub filing_details: Vec<FilingDetail>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FilingDetail {
    #[serde(rename = "wage_month")]
    pub wage_month: String,
    pub trrn: String,
    #[serde(rename = "date_of_credit")]
    pub date_of_credit: String,
    #[serde(rename = "payment_due_date")]
    pub payment_due_date: String,
    #[serde(rename = "no_of_employees")]
    pub no_of_employees: i64,
    pub amount: i64,
    #[serde(rename = "payment_timeliness")]
    pub payment_timeliness: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Shareholding {
    pub shareholders: String,
    pub year: String,
    #[serde(rename = "financial_year")]
    pub financial_year: String,
    pub category: String,
    #[serde(rename = "indian_held_no_of_shares")]
    pub indian_held_no_of_shares: i64,
    #[serde(rename = "indian_held_percentage_of_shares")]
    pub indian_held_percentage_of_shares: i64,
    #[serde(rename = "nri_held_no_of_shares")]
    pub nri_held_no_of_shares: i64,
    #[serde(rename = "nri_held_percentage_of_shares")]
    pub nri_held_percentage_of_shares: i64,
    #[serde(rename = "foreign_held_other_than_nri_no_of_shares")]
    pub foreign_held_other_than_nri_no_of_shares: i64,
    #[serde(rename = "foreign_held_other_than_nri_percentage_of_shares")]
    pub foreign_held_other_than_nri_percentage_of_shares: i64,
    #[serde(rename = "central_government_held_no_of_shares")]
    pub central_government_held_no_of_shares: i64,
    #[serde(rename = "central_government_held_percentage_of_shares")]
    pub central_government_held_percentage_of_shares: i64,
    #[serde(rename = "state_government_held_no_of_shares")]
    pub state_government_held_no_of_shares: i64,
    #[serde(rename = "state_government_held_percentage_of_shares")]
    pub state_government_held_percentage_of_shares: i64,
    #[serde(rename = "government_company_held_no_shares")]
    pub government_company_held_no_shares: i64,
    #[serde(rename = "government_company_held_percentage_of_shares")]
    pub government_company_held_percentage_of_shares: i64,
    #[serde(rename = "insurance_company_held_no_of_shares")]
    pub insurance_company_held_no_of_shares: i64,
    #[serde(rename = "insurance_company_held_percentage_of_shares")]
    pub insurance_company_held_percentage_of_shares: i64,
    #[serde(rename = "bank_held_no_of_shares")]
    pub bank_held_no_of_shares: i64,
    #[serde(rename = "bank_held_percentage_of_shares")]
    pub bank_held_percentage_of_shares: i64,
    #[serde(rename = "financial_institutions_held_no_of_shares")]
    pub financial_institutions_held_no_of_shares: i64,
    #[serde(rename = "financial_institutions_held_percentage_of_shares")]
    pub financial_institutions_held_percentage_of_shares: i64,
    #[serde(rename = "financial_institutions_investors_held_no_of_shares")]
    pub financial_institutions_investors_held_no_of_shares: i64,
    #[serde(rename = "financial_institutions_investors_held_percentage_of_shares")]
    pub financial_institutions_investors_held_percentage_of_shares: i64,
    #[serde(rename = "mutual_funds_held_no_of_shares")]
    pub mutual_funds_held_no_of_shares: i64,
    #[serde(rename = "mutual_funds_held_percentage_of_shares")]
    pub mutual_funds_held_percentage_of_shares: i64,
    #[serde(rename = "venture_capital_held_no_of_shares")]
    pub venture_capital_held_no_of_shares: i64,
    #[serde(rename = "venture_capital_held_percentage_of_shares")]
    pub venture_capital_held_percentage_of_shares: i64,
    #[serde(rename = "body_corporate_held_no_of_shares")]
    pub body_corporate_held_no_of_shares: i64,
    #[serde(rename = "body_corporate_held_percentage_of_shares")]
    pub body_corporate_held_percentage_of_shares: i64,
    #[serde(rename = "others_held_no_of_shares")]
    pub others_held_no_of_shares: i64,
    #[serde(rename = "others_held_percentage_of_shares")]
    pub others_held_percentage_of_shares: i64,
    #[serde(rename = "total_no_of_shares")]
    pub total_no_of_shares: i64,
    #[serde(rename = "total_percentage_of_shares")]
    pub total_percentage_of_shares: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ShareholdingsMoreThanFivePercent {
    pub company: Vec<Value>,
    pub llp: Vec<Value>,
    pub individual: Vec<Value>,
    pub others: Vec<Other2>,
    #[serde(rename = "financial_year")]
    pub financial_year: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Other2 {
    pub name: String,
    #[serde(rename = "shareholding_percentage")]
    pub shareholding_percentage: i64,
    #[serde(rename = "no_of_shares")]
    pub no_of_shares: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ShareholdingsSummary {
    pub year: String,
    #[serde(rename = "financial_year")]
    pub financial_year: String,
    #[serde(rename = "total_equity_shares")]
    pub total_equity_shares: i64,
    #[serde(rename = "total_preference_shares")]
    pub total_preference_shares: i64,
    pub promoter: i64,
    pub public: Value,
    pub total: i64,
    pub metadata: Metadata4,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Metadata4 {
    #[serde(rename = "doc_id")]
    pub doc_id: String,
    #[serde(rename = "xml_to_pdf_converted_doc_id")]
    pub xml_to_pdf_converted_doc_id: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DirectorShareholding {
    pub year: String,
    #[serde(rename = "financial_year")]
    pub financial_year: String,
    #[serde(rename = "din_pan")]
    pub din_pan: String,
    #[serde(rename = "full_name")]
    pub full_name: String,
    pub designation: String,
    #[serde(rename = "date_of_cessation")]
    pub date_of_cessation: Value,
    #[serde(rename = "no_of_shares")]
    pub no_of_shares: i64,
    #[serde(rename = "percentage_holding")]
    pub percentage_holding: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LegalHistory {
    pub petitioner: String,
    pub respondent: String,
    pub court: String,
    pub date: Option<String>,
    #[serde(rename = "case_status")]
    pub case_status: String,
    #[serde(rename = "case_number")]
    pub case_number: String,
    #[serde(rename = "case_type")]
    pub case_type: String,
    #[serde(rename = "case_category")]
    pub case_category: String,
    pub severity: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct HoldingEntities {
    #[serde(rename = "financial_year")]
    pub financial_year: String,
    pub company: Vec<Value>,
    pub llp: Vec<Value>,
    pub others: Vec<Other3>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Other3 {
    #[serde(rename = "legal_name")]
    pub legal_name: String,
    #[serde(rename = "share_holding_percentage")]
    pub share_holding_percentage: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SubsidiaryEntities {
    #[serde(rename = "financial_year")]
    pub financial_year: String,
    pub company: Vec<Company4>,
    pub llp: Vec<Value>,
    pub others: Vec<Value>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Company4 {
    pub cin: String,
    #[serde(rename = "legal_name")]
    pub legal_name: String,
    #[serde(rename = "paid_up_capital")]
    pub paid_up_capital: i64,
    #[serde(rename = "sum_of_charges")]
    pub sum_of_charges: i64,
    #[serde(rename = "incorporation_date")]
    pub incorporation_date: String,
    #[serde(rename = "share_holding_percentage")]
    pub share_holding_percentage: i64,
    pub city: String,
    pub status: String,
    #[serde(rename = "active_compliance")]
    pub active_compliance: String,
    #[serde(rename = "cirp_status")]
    pub cirp_status: Value,
    #[serde(rename = "next_cin")]
    pub next_cin: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PeerComparison {
    pub biz_industry: String,
    pub biz_segment: String,
    pub ref_year: String,
    pub peers: Vec<Peer>,
    pub bench_marks: Vec<BenchMark>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Peer {
    pub cin: String,
    pub legal_name: String,
    pub revenue: i64,
    pub city: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BenchMark {
    pub year: String,
    #[serde(rename = "no_of_peers_in_sample")]
    pub no_of_peers_in_sample: i64,
    pub revenue: f64,
    #[serde(rename = "revenue_growth")]
    pub revenue_growth: f64,
    #[serde(rename = "net_margin")]
    pub net_margin: f64,
    #[serde(rename = "ebitda_margin")]
    pub ebitda_margin: f64,
    #[serde(rename = "return_on_equity")]
    pub return_on_equity: f64,
    #[serde(rename = "sales_by_net_fixed_assets")]
    pub sales_by_net_fixed_assets: f64,
    #[serde(rename = "inventory_holding_period")]
    pub inventory_holding_period: f64,
    #[serde(rename = "debtor_days_outstanding")]
    pub debtor_days_outstanding: f64,
    #[serde(rename = "trade_payable_days")]
    pub trade_payable_days: f64,
    #[serde(rename = "cash_conversion_cycle")]
    pub cash_conversion_cycle: f64,
    #[serde(rename = "debt_by_equity")]
    pub debt_by_equity: i64,
    #[serde(rename = "gross_profit_margin")]
    pub gross_profit_margin: f64,
    #[serde(rename = "return_on_capital_employed")]
    pub return_on_capital_employed: f64,
    #[serde(rename = "interest_coverage_ratio")]
    pub interest_coverage_ratio: f64,
    #[serde(rename = "debt_ratio")]
    pub debt_ratio: i64,
    #[serde(rename = "current_ratio")]
    pub current_ratio: f64,
    #[serde(rename = "quick_ratio")]
    pub quick_ratio: f64,
    #[serde(rename = "median_revenue")]
    pub median_revenue: f64,
    #[serde(rename = "median_revenue_growth")]
    pub median_revenue_growth: f64,
    #[serde(rename = "median_net_margin")]
    pub median_net_margin: f64,
    #[serde(rename = "median_ebitda_margin")]
    pub median_ebitda_margin: f64,
    #[serde(rename = "median_return_on_equity")]
    pub median_return_on_equity: f64,
    #[serde(rename = "median_sales_by_net_fixed_assets")]
    pub median_sales_by_net_fixed_assets: f64,
    #[serde(rename = "median_inventory_holding_period")]
    pub median_inventory_holding_period: f64,
    #[serde(rename = "median_debtor_days_outstanding")]
    pub median_debtor_days_outstanding: f64,
    #[serde(rename = "median_trade_payable_days")]
    pub median_trade_payable_days: f64,
    #[serde(rename = "median_cash_conversion_cycle")]
    pub median_cash_conversion_cycle: f64,
    #[serde(rename = "median_debt_by_equity")]
    pub median_debt_by_equity: f64,
    #[serde(rename = "median_gross_profit_margin")]
    pub median_gross_profit_margin: f64,
    #[serde(rename = "median_return_on_capital_employed")]
    pub median_return_on_capital_employed: f64,
    #[serde(rename = "median_interest_coverage_ratio")]
    pub median_interest_coverage_ratio: f64,
    #[serde(rename = "median_debt_ratio")]
    pub median_debt_ratio: f64,
    #[serde(rename = "median_current_ratio")]
    pub median_current_ratio: f64,
    #[serde(rename = "median_quick_ratio")]
    pub median_quick_ratio: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GstDetail {
    pub gstin: String,
    pub status: String,
    #[serde(rename = "company_name")]
    pub company_name: String,
    #[serde(rename = "trade_name")]
    pub trade_name: Option<String>,
    pub state: String,
    #[serde(rename = "state_jurisdiction")]
    pub state_jurisdiction: Option<String>,
    #[serde(rename = "centre_jurisdiction")]
    pub centre_jurisdiction: Option<String>,
    #[serde(rename = "date_of_registration")]
    pub date_of_registration: String,
    #[serde(rename = "taxpayer_type")]
    pub taxpayer_type: String,
    #[serde(rename = "nature_of_business_activities")]
    pub nature_of_business_activities: Option<String>,
    #[serde(rename = "filing_timeliness")]
    pub filing_timeliness: Option<String>,
    pub filings: Vec<Filing>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Filing {
    #[serde(rename = "return_type")]
    pub return_type: String,
    #[serde(rename = "date_of_filing")]
    pub date_of_filing: String,
    #[serde(rename = "filing_due_date")]
    pub filing_due_date: Option<String>,
    #[serde(rename = "financial_year")]
    pub financial_year: String,
    #[serde(rename = "tax_period")]
    pub tax_period: String,
    pub status: String,
    #[serde(rename = "filing_timeliness")]
    pub filing_timeliness: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Struckoff248Details {
    #[serde(rename = "struck_off_status")]
    pub struck_off_status: String,
    #[serde(rename = "restored_status")]
    pub restored_status: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MsmeSupplierPaymentDelays {
    pub trend: Vec<Trend>,
    #[serde(rename = "delays_for_period")]
    pub delays_for_period: DelaysForPeriod,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Trend {
    pub period: String,
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DelaysForPeriod {
    #[serde(rename = "latest_period")]
    pub latest_period: String,
    #[serde(rename = "total_amount_due_for_period")]
    pub total_amount_due_for_period: i64,
    pub delays: Vec<Delay>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Delay {
    #[serde(rename = "supplier_name")]
    pub supplier_name: String,
    #[serde(rename = "supplier_pan")]
    pub supplier_pan: String,
    #[serde(rename = "amount_due")]
    pub amount_due: i64,
    #[serde(rename = "amount_due_from_date")]
    pub amount_due_from_date: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProbeFinancialScore {
    #[serde(rename = "overall_financial_score")]
    pub overall_financial_score: i64,
    #[serde(rename = "growth_score")]
    pub growth_score: i64,
    #[serde(rename = "profitability_score")]
    pub profitability_score: i64,
    #[serde(rename = "liquidity_score")]
    pub liquidity_score: i64,
    #[serde(rename = "solvency_score")]
    pub solvency_score: i64,
    #[serde(rename = "efficiency_score")]
    pub efficiency_score: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct KeyIndicators {
    pub revenue: String,
    pub profit: String,
    #[serde(rename = "employee_count")]
    pub employee_count: String,
    #[serde(rename = "pending_cases_filed_against_this_corporate")]
    pub pending_cases_filed_against_this_corporate: bool,
    #[serde(rename = "bureau_defaults")]
    pub bureau_defaults: bool,
    #[serde(rename = "gst_filing_delay")]
    pub gst_filing_delay: bool,
    #[serde(rename = "epf_payment_delay")]
    pub epf_payment_delay: Value,
    #[serde(rename = "severe_pending_cases_filed_against_this_corporate")]
    pub severe_pending_cases_filed_against_this_corporate: bool,
    #[serde(rename = "credit_rating")]
    pub credit_rating: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FilingDates {
    #[serde(rename = "aoc_4")]
    pub aoc_4: Aoc4,
    #[serde(rename = "mgt_7")]
    pub mgt_7: Mgt7,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Aoc4 {
    #[serde(rename = "financial_year")]
    pub financial_year: String,
    #[serde(rename = "filing_date")]
    pub filing_date: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Mgt7 {
    #[serde(rename = "financial_year")]
    pub financial_year: String,
    #[serde(rename = "filing_date")]
    pub filing_date: String,
}
