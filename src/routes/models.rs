use serde::Deserialize; 
use serde::Serialize;

#[derive(Deserialize)] // 1. Allow serde to parse query string into this struct
pub struct SummaryParams {
    pub cin: String,    // 2. Make the field public so the handler can access it
}


#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct order_details_briskall {
    #[serde(rename = "Input")]
    pub input: String,
    #[serde(rename = "IsBillable")]
    pub is_billable: bool,
    #[serde(rename = "OrderID")]
    pub order_id: i64,
    #[serde(rename = "OrderRemarks")]
    pub order_remarks: String,
    #[serde(rename = "OrderStatus")]
    pub order_status: String,
    #[serde(rename = "OrderedOn")]
    pub ordered_on: String,
    #[serde(rename = "Product")]
    pub product: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OrderStatus {
    #[serde(rename = "IsBillable")]
    pub is_billable: bool,
    #[serde(rename = "OrderID")]
    pub order_id: i64,
    #[serde(rename = "OrderedOn")]
    pub ordered_on: String,
    #[serde(rename = "Product")]
    pub product: String,
    #[serde(rename = "Input")]
    pub input: String,
    #[serde(rename = "OrderStatus")]
    pub order_status: String,
    #[serde(rename = "OrderRemarks")]
    pub order_remarks: String,
}

use serde_json::Value;

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct final_json_brisk {
    #[serde(rename = "CompanyHighlightsForLatestFinancialYear")]
    pub company_highlights_for_latest_financial_year: CompanyHighlightsForLatestFinancialYear,
    #[serde(rename = "CorporateDirectory")]
    pub corporate_directory: CorporateDirectory,
    #[serde(rename = "ProductAndServices")]
    pub product_and_services: ProductAndServices,
    #[serde(rename = "OwnershipDetails")]
    pub ownership_details: Vec<OwnershipDetail>,
    #[serde(rename = "ComparativeFinancialsStandalone")]
    pub comparative_financials_standalone: ComparativeFinancialsStandalone,
    #[serde(rename = "SchedulesAndDisclosuresFinancialsInfo")]
    pub schedules_and_disclosures_financials_info: SchedulesAndDisclosuresFinancialsInfo,
    #[serde(rename = "RiskReport")]
    pub risk_report: RiskReport,
    #[serde(rename = "ComparativeFinancialsConsolidated")]
    pub comparative_financials_consolidated: ComparativeFinancialsConsolidated,
    #[serde(rename = "StandaloneVsConsolidatedFinancials")]
    pub standalone_vs_consolidated_financials: StandaloneVsConsolidatedFinancials,
    #[serde(rename = "AuditorDetailsAndCAROReport")]
    pub auditor_details_and_caroreport: AuditorDetailsAndCaroreport,
    #[serde(rename = "GroupCompaniesAndRelatedPartyInformation")]
    pub group_companies_and_related_party_information: GroupCompaniesAndRelatedPartyInformation,
    #[serde(rename = "OtherRelatedCompanies")]
    pub other_related_companies: OtherRelatedCompanies,
    #[serde(rename = "CreditRatings")]
    pub credit_ratings: CreditRatings,
    #[serde(rename = "ITATCases")]
    pub itatcases: Vec<Itatcase>,
    #[serde(rename = "SuitFiledCasesAndWillfulDefaulter_Historical")]
    pub suit_filed_cases_and_willful_defaulter_historical: Vec<Value>,
    #[serde(rename = "MCASeriousComplaints")]
    pub mcaserious_complaints: Vec<McaseriousComplaint>,
    #[serde(rename = "ComplianceAndDelays")]
    pub compliance_and_delays: ComplianceAndDelays,
    #[serde(rename = "EstablishmentAndEPFDetails")]
    pub establishment_and_epfdetails: EstablishmentAndEpfdetails,
    #[serde(rename = "ChargeSearchReport")]
    pub charge_search_report: ChargeSearchReport,
    #[serde(rename = "ChargesProfileReport")]
    pub charges_profile_report: ChargesProfileReport,
    #[serde(rename = "DirectorKYCAndNetworks")]
    pub director_kycand_networks: DirectorKycandNetworks,
    #[serde(rename = "LegalInformation")]
    pub legal_information: LegalInformation,
    #[serde(rename = "CompanyNewsAndSentimentAnalysis")]
    pub company_news_and_sentiment_analysis: Value,
    #[serde(rename = "BRiskDocuments")]
    pub brisk_documents: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CompanyHighlightsForLatestFinancialYear {
    #[serde(rename = "LatestFinancialYear")]
    pub latest_financial_year: i64,
    #[serde(rename = "FinancialHighlights")]
    pub financial_highlights: Vec<FinancialHighlight>,
    #[serde(rename = "NonFinancialHighlights")]
    pub non_financial_highlights: Vec<NonFinancialHighlight>,
    #[serde(rename = "RiskHighlights")]
    pub risk_highlights: Vec<RiskHighlight>,
    #[serde(rename = "NewsHighlights")]
    pub news_highlights: Value,
    #[serde(rename = "ComplianceHighlights")]
    pub compliance_highlights: Vec<ComplianceHighlight>,
    #[serde(rename = "EventHighlights")]
    pub event_highlights: Vec<EventHighlight>,
    #[serde(rename = "LegalHighlights")]
    pub legal_highlights: LegalHighlights,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FinancialHighlight {
    #[serde(rename = "HighlightName")]
    pub highlight_name: String,
    #[serde(rename = "Value")]
    pub value: String,
    #[serde(rename = "ChangePercentage")]
    pub change_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NonFinancialHighlight {
    #[serde(rename = "HighlightName")]
    pub highlight_name: String,
    #[serde(rename = "HighlightValue")]
    pub highlight_value: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RiskHighlight {
    #[serde(rename = "RiskTest")]
    pub risk_test: String,
    #[serde(rename = "Result")]
    pub result: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ComplianceHighlight {
    #[serde(rename = "Compliance")]
    pub compliance: String,
    #[serde(rename = "Status")]
    pub status: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EventHighlight {
    #[serde(rename = "EventName")]
    pub event_name: String,
    #[serde(rename = "EventCount")]
    pub event_count: i64,
    #[serde(rename = "EventValue")]
    pub event_value: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LegalHighlights {
    #[serde(rename = "TotalOpenCasesCount")]
    pub total_open_cases_count: i64,
    #[serde(rename = "SupremeCourtAndHighCourtPercentage")]
    pub supreme_court_and_high_court_percentage: f64,
    #[serde(rename = "TribunalPercentage")]
    pub tribunal_percentage: f64,
    #[serde(rename = "OtherCasesPercentage")]
    pub other_cases_percentage: f64,
    #[serde(rename = "NewCasesCount")]
    pub new_cases_count: i64,
    #[serde(rename = "NCLTCount")]
    pub ncltcount: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CorporateDirectory {
    #[serde(rename = "CompanyKYC")]
    pub company_kyc: CompanyKyc,
    #[serde(rename = "CompanyMaster")]
    pub company_master: CompanyMaster,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CompanyKyc {
    #[serde(rename = "CompanyName")]
    pub company_name: String,
    #[serde(rename = "CompanyCIN")]
    pub company_cin: String,
    #[serde(rename = "CompanyStatus")]
    pub company_status: String,
    #[serde(rename = "CompanyPAN")]
    pub company_pan: String,
    #[serde(rename = "CompanyTAN")]
    pub company_tan: String,
    #[serde(rename = "CompanyEPF")]
    pub company_epf: Vec<String>,
    #[serde(rename = "CompanyGST")]
    pub company_gst: Vec<String>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CompanyMaster {
    #[serde(rename = "DateOfIncorporation")]
    pub date_of_incorporation: String,
    #[serde(rename = "Category")]
    pub category: String,
    #[serde(rename = "SubCategory")]
    pub sub_category: String,
    #[serde(rename = "Class")]
    pub class: String,
    #[serde(rename = "ListingStatus")]
    pub listing_status: String,
    #[serde(rename = "AuthorizedCapital")]
    pub authorized_capital: f64,
    #[serde(rename = "PaidupCapital")]
    pub paidup_capital: f64,
    #[serde(rename = "Address")]
    pub address: String,
    #[serde(rename = "LastAGMDate")]
    pub last_agmdate: String,
    #[serde(rename = "BalancesheetDate")]
    pub balancesheet_date: String,
    #[serde(rename = "Email")]
    pub email: String,
    #[serde(rename = "Website")]
    pub website: String,
    #[serde(rename = "CurrentDirectorsCount")]
    pub current_directors_count: i64,
    #[serde(rename = "PastDirectorsCount")]
    pub past_directors_count: i64,
    #[serde(rename = "SignatoriesCount")]
    pub signatories_count: i64,
    #[serde(rename = "ActiveCompliance")]
    pub active_compliance: String,
    #[serde(rename = "StatusUnderCIRP")]
    pub status_under_cirp: String,
    #[serde(rename = "SuspendedAtStockExchange")]
    pub suspended_at_stock_exchange: String,
    #[serde(rename = "FilingStatusForLastTwoYears")]
    pub filing_status_for_last_two_years: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProductAndServices {
    #[serde(rename = "NICProductsDetails")]
    pub nicproducts_details: Vec<NicproductsDetail>,
    #[serde(rename = "PrincipalProductsAndServices")]
    pub principal_products_and_services: Vec<PrincipalProductsAndService>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NicproductsDetail {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "MainActivityGroupDescription")]
    pub main_activity_group_description: String,
    #[serde(rename = "BusinessActivityDescription")]
    pub business_activity_description: String,
    #[serde(rename = "TurnoverPercentage")]
    pub turnover_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PrincipalProductsAndService {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "ITC8Digit")]
    pub itc8digit: i64,
    #[serde(rename = "ITC4Digit")]
    pub itc4digit: i64,
    #[serde(rename = "Category")]
    pub category: String,
    #[serde(rename = "Description")]
    pub description: String,
    #[serde(rename = "ITC8DigitTurnover")]
    pub itc8digit_turnover: f64,
    #[serde(rename = "ITC4DigitTurnover")]
    pub itc4digit_turnover: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OwnershipDetail {
    #[serde(rename = "ShareholderName")]
    pub shareholder_name: String,
    #[serde(rename = "OwnershipPercentages")]
    pub ownership_percentages: Vec<OwnershipPercentage>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OwnershipPercentage {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "OwnershipPercentage")]
    pub ownership_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ComparativeFinancialsStandalone {
    #[serde(rename = "ProfitAndLossStatement")]
    pub profit_and_loss_statement: ProfitAndLossStatement,
    #[serde(rename = "BalanceSheetStandalone")]
    pub balance_sheet_standalone: BalanceSheetStandalone,
    #[serde(rename = "CashFlowStatementStandalone")]
    pub cash_flow_statement_standalone: CashFlowStatementStandalone,
    #[serde(rename = "RatioAnalysisStandalone")]
    pub ratio_analysis_standalone: RatioAnalysisStandalone,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProfitAndLossStatement {
    #[serde(rename = "OperatingRevenues")]
    pub operating_revenues: Vec<OperatingRevenue>,
    #[serde(rename = "OtherIncomes")]
    pub other_incomes: Vec<OtherIncome>,
    #[serde(rename = "TotalRevenues")]
    pub total_revenues: Vec<TotalRevenue>,
    #[serde(rename = "TotalExpenses")]
    pub total_expenses: Vec<TotalExpense>,
    #[serde(rename = "EBDITA")]
    pub ebdita: Vec<Ebdita>,
    #[serde(rename = "Depreciations")]
    pub depreciations: Vec<Depreciation>,
    #[serde(rename = "Interests")]
    pub interests: Vec<Interest>,
    #[serde(rename = "PBT")]
    pub pbt: Vec<Pbt>,
    #[serde(rename = "Taxes")]
    pub taxes: Vec<Tax>,
    #[serde(rename = "OtherAdjustments")]
    pub other_adjustments: Vec<OtherAdjustment>,
    #[serde(rename = "PAT")]
    pub pat: Vec<Pat>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OperatingRevenue {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherIncome {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalRevenue {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalExpense {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Ebdita {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Depreciation {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Interest {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Pbt {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Tax {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherAdjustment {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Pat {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BalanceSheetStandalone {
    #[serde(rename = "NetWorth")]
    pub net_worth: Vec<NetWorth>,
    #[serde(rename = "Borrowings")]
    pub borrowings: Vec<Borrowing>,
    #[serde(rename = "OtherNonCurrentLiabilities")]
    pub other_non_current_liabilities: Vec<OtherNonCurrentLiability>,
    #[serde(rename = "CurrentLiabilitiesAndProvisions")]
    pub current_liabilities_and_provisions: Vec<CurrentLiabilitiesAndProvision>,
    #[serde(rename = "DeferredTaxLiabilityOfAssets")]
    pub deferred_tax_liability_of_assets: Vec<DeferredTaxLiabilityOfAsset>,
    #[serde(rename = "TotalEquityAndLiabilities")]
    pub total_equity_and_liabilities: Vec<TotalEquityAndLiability>,
    #[serde(rename = "TangibleAssets")]
    pub tangible_assets: Vec<TangibleAsset>,
    #[serde(rename = "CapitalWIPAndOthers")]
    pub capital_wipand_others: Vec<CapitalWipandOther>,
    #[serde(rename = "IntangibleAssets")]
    pub intangible_assets: Vec<IntangibleAsset>,
    #[serde(rename = "Investments")]
    pub investments: Vec<Investment>,
    #[serde(rename = "LoansAndAdvances")]
    pub loans_and_advances: Vec<LoansAndAdvance>,
    #[serde(rename = "Inventories")]
    pub inventories: Vec<Inventory>,
    #[serde(rename = "TradeReceivables")]
    pub trade_receivables: Vec<TradeReceivable>,
    #[serde(rename = "CashAndBankBalances")]
    pub cash_and_bank_balances: Vec<CashAndBankBalance>,
    #[serde(rename = "OtherAssets")]
    pub other_assets: Vec<OtherAsset>,
    #[serde(rename = "TotalAssets")]
    pub total_assets: Value,
    #[serde(rename = "CurrentLiabilities")]
    pub current_liabilities: Vec<CurrentLiability>,
    #[serde(rename = "CurrentAssets")]
    pub current_assets: Vec<CurrentAsset>,
    #[serde(rename = "WorkingCapitals")]
    pub working_capitals: Vec<WorkingCapital>,
    #[serde(rename = "RedFlags")]
    pub red_flags: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NetWorth {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Borrowing {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherNonCurrentLiability {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentLiabilitiesAndProvision {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DeferredTaxLiabilityOfAsset {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalEquityAndLiability {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TangibleAsset {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CapitalWipandOther {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct IntangibleAsset {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Investment {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansAndAdvance {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Inventory {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TradeReceivable {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CashAndBankBalance {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherAsset {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentLiability {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentAsset {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WorkingCapital {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CashFlowStatementStandalone {
    #[serde(rename = "OperatingActivities")]
    pub operating_activities: Vec<OperatingActivity>,
    #[serde(rename = "InvestingActivities")]
    pub investing_activities: Vec<InvestingActivity>,
    #[serde(rename = "FinancingActivities")]
    pub financing_activities: Vec<FinancingActivity>,
    #[serde(rename = "CashAndCashEquivalentAtEnds")]
    pub cash_and_cash_equivalent_at_ends: Vec<CashAndCashEquivalentAtEnd>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OperatingActivity {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InvestingActivity {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FinancingActivity {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CashAndCashEquivalentAtEnd {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RatioAnalysisStandalone {
    #[serde(rename = "OperativeRevenueGrowthPercentages")]
    pub operative_revenue_growth_percentages: Vec<OperativeRevenueGrowthPercentage>,
    #[serde(rename = "EBITDAGrowths")]
    pub ebitdagrowths: Vec<Ebitdagrowth>,
    #[serde(rename = "EPSGrowths")]
    pub epsgrowths: Vec<Epsgrowth>,
    #[serde(rename = "EBITDAMarginPercentages")]
    pub ebitdamargin_percentages: Vec<EbitdamarginPercentage>,
    #[serde(rename = "PATMarginPercentage")]
    pub patmargin_percentage: Vec<PatmarginPercentage>,
    #[serde(rename = "ReturnOnCapitalEmployedPercentage_RoCEs")]
    pub return_on_capital_employed_percentage_ro_ces: Vec<ReturnOnCapitalEmployedPercentageRoCe>,
    #[serde(rename = "ReturnOnEquityPercentage_RoEs")]
    pub return_on_equity_percentage_ro_es: Vec<ReturnOnEquityPercentageRoE>,
    #[serde(rename = "ReturnOnAssetsPercentage_RoAs")]
    pub return_on_assets_percentage_ro_as: Vec<ReturnOnAssetsPercentageRoA>,
    #[serde(rename = "AvgInventoryHoldingDays")]
    pub avg_inventory_holding_days: Vec<AvgInventoryHoldingDay>,
    #[serde(rename = "AvgDebtorsOutstandingDays")]
    pub avg_debtors_outstanding_days: Vec<AvgDebtorsOutstandingDay>,
    #[serde(rename = "AvgTradePayableDays")]
    pub avg_trade_payable_days: Vec<AvgTradePayableDay>,
    #[serde(rename = "AvgCashConversionCycle")]
    pub avg_cash_conversion_cycle: Vec<AvgCashConversionCycle>,
    #[serde(rename = "QuickRatios")]
    pub quick_ratios: Vec<QuickRatio>,
    #[serde(rename = "CurrentRatio")]
    pub current_ratio: Vec<CurrentRatio>,
    #[serde(rename = "LeverageTOL_TNWs")]
    pub leverage_tol_tnws: Vec<LeverageTolTnw>,
    #[serde(rename = "NetDebtEquities")]
    pub net_debt_equities: Vec<NetDebtEquity>,
    #[serde(rename = "InterestCoverages")]
    pub interest_coverages: Vec<InterestCoverage>,
    #[serde(rename = "CapitalEmployedTurnovers")]
    pub capital_employed_turnovers: Vec<CapitalEmployedTurnover>,
    #[serde(rename = "AssetTurnovers")]
    pub asset_turnovers: Vec<AssetTurnover>,
    #[serde(rename = "InventoryTurnovers")]
    pub inventory_turnovers: Vec<InventoryTurnover>,
    #[serde(rename = "ReceivablesTurnovers")]
    pub receivables_turnovers: Vec<ReceivablesTurnover>,
    #[serde(rename = "WorkingCapitalTurnovers")]
    pub working_capital_turnovers: Vec<WorkingCapitalTurnover>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OperativeRevenueGrowthPercentage {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Ebitdagrowth {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Epsgrowth {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EbitdamarginPercentage {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PatmarginPercentage {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ReturnOnCapitalEmployedPercentageRoCe {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ReturnOnEquityPercentageRoE {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ReturnOnAssetsPercentageRoA {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AvgInventoryHoldingDay {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AvgDebtorsOutstandingDay {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AvgTradePayableDay {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AvgCashConversionCycle {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct QuickRatio {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentRatio {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LeverageTolTnw {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NetDebtEquity {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InterestCoverage {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CapitalEmployedTurnover {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AssetTurnover {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InventoryTurnover {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ReceivablesTurnover {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WorkingCapitalTurnover {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SchedulesAndDisclosuresFinancialsInfo {
    #[serde(rename = "RevenueFromOperations")]
    pub revenue_from_operations: RevenueFromOperations,
    #[serde(rename = "FinanceCost")]
    pub finance_cost: FinanceCost,
    #[serde(rename = "ExpenseBreakup")]
    pub expense_breakup: ExpenseBreakup,
    #[serde(rename = "OtherExpense")]
    pub other_expense: OtherExpense2,
    #[serde(rename = "Borrowings")]
    pub borrowings: Borrowings,
    #[serde(rename = "LoansAndAdvancesSchedulesAndDisclosures")]
    pub loans_and_advances_schedules_and_disclosures: LoansAndAdvancesSchedulesAndDisclosures,
    #[serde(rename = "TradeReceivablesAgeing")]
    pub trade_receivables_ageing: TradeReceivablesAgeing,
    #[serde(rename = "EquityShareCapitalReconciliation")]
    pub equity_share_capital_reconciliation: Vec<Value>,
    #[serde(rename = "ContingentLiabilitiesAndCommitments")]
    pub contingent_liabilities_and_commitments: Vec<Value>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RevenueFromOperations {
    #[serde(rename = "DomesticTurnover")]
    pub domestic_turnover: DomesticTurnover,
    #[serde(rename = "ExportTurnover")]
    pub export_turnover: ExportTurnover,
    #[serde(rename = "TotalRevenueFromOperations")]
    pub total_revenue_from_operations: Vec<TotalRevenueFromOperation>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DomesticTurnover {
    #[serde(rename = "DomesticSalesOfManufacturedGoods")]
    pub domestic_sales_of_manufactured_goods: Vec<DomesticSalesOfManufacturedGood>,
    #[serde(rename = "DomesticSalesOfTradedGoods")]
    pub domestic_sales_of_traded_goods: Vec<DomesticSalesOfTradedGood>,
    #[serde(rename = "DomesticSalesOfServices")]
    pub domestic_sales_of_services: Vec<DomesticSalesOfService>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DomesticSalesOfManufacturedGood {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DomesticSalesOfTradedGood {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DomesticSalesOfService {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ExportTurnover {
    #[serde(rename = "ExportSalesOfManufacturedGoods")]
    pub export_sales_of_manufactured_goods: Vec<Value>,
    #[serde(rename = "ExportSalesOfTradedGoods")]
    pub export_sales_of_traded_goods: Vec<Value>,
    #[serde(rename = "ExportSalesOfServices")]
    pub export_sales_of_services: Vec<Value>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalRevenueFromOperation {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FinanceCost {
    #[serde(rename = "InterestOnBorrowings")]
    pub interest_on_borrowings: Vec<InterestOnBorrowing>,
    #[serde(rename = "OtherFinanceRelatedCharges")]
    pub other_finance_related_charges: Vec<OtherFinanceRelatedCharge>,
    #[serde(rename = "TotalFinanceCosts")]
    pub total_finance_costs: Vec<TotalFinanceCost>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InterestOnBorrowing {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherFinanceRelatedCharge {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalFinanceCost {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ExpenseBreakup {
    #[serde(rename = "DepreciationDepletionAndAmortizationsExpenses")]
    pub depreciation_depletion_and_amortizations_expenses: Vec<DepreciationDepletionAndAmortizationsExpense>,
    #[serde(rename = "OtherExpenses")]
    pub other_expenses: Vec<OtherExpense>,
    #[serde(rename = "CostOfMaterialsConsumed")]
    pub cost_of_materials_consumed: Vec<CostOfMaterialsConsumed>,
    #[serde(rename = "PurchasesOfStockInTrades")]
    pub purchases_of_stock_in_trades: Vec<PurchasesOfStockInTrade>,
    #[serde(rename = "ChangesInInventoriesOfFinishedGoodsWorkInProgressAndStockInTrades")]
    pub changes_in_inventories_of_finished_goods_work_in_progress_and_stock_in_trades: Vec<ChangesInInventoriesOfFinishedGoodsWorkInProgressAndStockInTrade>,
    #[serde(rename = "EmployeeBenefitExpenses")]
    pub employee_benefit_expenses: Vec<EmployeeBenefitExpense>,
    #[serde(rename = "FinanceCosts")]
    pub finance_costs: Vec<FinanceCost2>,
    #[serde(rename = "TotalExpenses")]
    pub total_expenses: Vec<TotalExpense2>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DepreciationDepletionAndAmortizationsExpense {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherExpense {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CostOfMaterialsConsumed {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PurchasesOfStockInTrade {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChangesInInventoriesOfFinishedGoodsWorkInProgressAndStockInTrade {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EmployeeBenefitExpense {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FinanceCost2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalExpense2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherExpense2 {
    #[serde(rename = "ConsumptionOfStoresAndSpareParts")]
    pub consumption_of_stores_and_spare_parts: Vec<ConsumptionOfStoresAndSparePart>,
    #[serde(rename = "PowerAndFuels")]
    pub power_and_fuels: Vec<PowerAndFuel>,
    #[serde(rename = "Rents")]
    pub rents: Vec<Rent>,
    #[serde(rename = "RepairsToBuildingAndMachineries")]
    pub repairs_to_building_and_machineries: Vec<RepairsToBuildingAndMachinery>,
    #[serde(rename = "TravellingConveyances")]
    pub travelling_conveyances: Vec<TravellingConveyance>,
    #[serde(rename = "RatesAndTaxes")]
    pub rates_and_taxes: Vec<RatesAndTax>,
    #[serde(rename = "LegalProfessionalCharges")]
    pub legal_professional_charges: Vec<LegalProfessionalCharge>,
    #[serde(rename = "AdvertisingPromotionals")]
    pub advertising_promotionals: Vec<AdvertisingPromotional>,
    #[serde(rename = "PaymentsToAuditors")]
    pub payments_to_auditors: Vec<PaymentsToAuditor>,
    #[serde(rename = "MiscellaneousExpenses")]
    pub miscellaneous_expenses: Vec<MiscellaneousExpense>,
    #[serde(rename = "TotalOtherExpenses")]
    pub total_other_expenses: Vec<TotalOtherExpense>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ConsumptionOfStoresAndSparePart {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PowerAndFuel {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Rent {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RepairsToBuildingAndMachinery {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TravellingConveyance {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RatesAndTax {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LegalProfessionalCharge {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AdvertisingPromotional {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PaymentsToAuditor {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MiscellaneousExpense {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalOtherExpense {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Borrowings {
    #[serde(rename = "SecuredBorrowings")]
    pub secured_borrowings: SecuredBorrowings,
    #[serde(rename = "UnsecuredBorrowings")]
    pub unsecured_borrowings: UnsecuredBorrowings,
    #[serde(rename = "TotalBorrowings")]
    pub total_borrowings: Vec<TotalBorrowing>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SecuredBorrowings {
    #[serde(rename = "SecuredBorrowingsLongTerm")]
    pub secured_borrowings_long_term: SecuredBorrowingsLongTerm,
    #[serde(rename = "SecuredBorrowingsShortTerm")]
    pub secured_borrowings_short_term: SecuredBorrowingsShortTerm,
    #[serde(rename = "TotalSecuredBorrowings")]
    pub total_secured_borrowings: Vec<TotalSecuredBorrowing>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SecuredBorrowingsLongTerm {
    #[serde(rename = "LoansFromOthers")]
    pub loans_from_others: Vec<LoansFromOther>,
    #[serde(rename = "LoansFromBanks")]
    pub loans_from_banks: Vec<LoansFromBank>,
    #[serde(rename = "OtherBorrowings")]
    pub other_borrowings: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansFromOther {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansFromBank {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SecuredBorrowingsShortTerm {
    #[serde(rename = "LoansRepayableOnDemandFromBanks")]
    pub loans_repayable_on_demand_from_banks: Vec<LoansRepayableOnDemandFromBank>,
    #[serde(rename = "LoansrepayableOnDemandFromOthers")]
    pub loansrepayable_on_demand_from_others: Vec<LoansrepayableOnDemandFromOther>,
    #[serde(rename = "OtherBorrowings")]
    pub other_borrowings: Vec<OtherBorrowing>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansRepayableOnDemandFromBank {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansrepayableOnDemandFromOther {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherBorrowing {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalSecuredBorrowing {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UnsecuredBorrowings {
    #[serde(rename = "UnsecuredBorrowingsLongTerm")]
    pub unsecured_borrowings_long_term: UnsecuredBorrowingsLongTerm,
    #[serde(rename = "UnsecuredBorrowingsShortTerm")]
    pub unsecured_borrowings_short_term: UnsecuredBorrowingsShortTerm,
    #[serde(rename = "TotalUnsecuredBorrowings")]
    pub total_unsecured_borrowings: Vec<TotalUnsecuredBorrowing>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UnsecuredBorrowingsLongTerm {
    #[serde(rename = "LoansFromBanks")]
    pub loans_from_banks: Vec<LoansFromBank2>,
    #[serde(rename = "LoansFromOthers")]
    pub loans_from_others: Vec<LoansFromOther2>,
    #[serde(rename = "OtherBorrowings")]
    pub other_borrowings: Vec<OtherBorrowing2>,
    #[serde(rename = "DeferredPaymentLiabilities")]
    pub deferred_payment_liabilities: Vec<Value>,
    #[serde(rename = "Deposits")]
    pub deposits: Vec<Value>,
    #[serde(rename = "LoansAndAdvancesFromRelatedParties")]
    pub loans_and_advances_from_related_parties: Vec<Value>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansFromBank2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansFromOther2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherBorrowing2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UnsecuredBorrowingsShortTerm {
    #[serde(rename = "LoansRepayableOnDemandFromBanks")]
    pub loans_repayable_on_demand_from_banks: Vec<LoansRepayableOnDemandFromBank2>,
    #[serde(rename = "LoansRepayableOnDemandFromOthers")]
    pub loans_repayable_on_demand_from_others: Vec<LoansRepayableOnDemandFromOther>,
    #[serde(rename = "UnsecuredOtherBorrowings")]
    pub unsecured_other_borrowings: Vec<UnsecuredOtherBorrowing>,
    #[serde(rename = "UnsecuredShortDeposits")]
    pub unsecured_short_deposits: Vec<Value>,
    #[serde(rename = "LoansAndAdvancesFromRelatedParties")]
    pub loans_and_advances_from_related_parties: Vec<Value>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansRepayableOnDemandFromBank2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansRepayableOnDemandFromOther {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UnsecuredOtherBorrowing {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalUnsecuredBorrowing {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalBorrowing {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansAndAdvancesSchedulesAndDisclosures {
    #[serde(rename = "SecuredLongGood")]
    pub secured_long_good: Vec<SecuredLongGood>,
    #[serde(rename = "UnsecuredLongGood")]
    pub unsecured_long_good: UnsecuredLongGood,
    #[serde(rename = "UnsecuredLongDoubtful")]
    pub unsecured_long_doubtful: UnsecuredLongDoubtful,
    #[serde(rename = "LongTermLoansAndAdvances")]
    pub long_term_loans_and_advances: Vec<LongTermLoansAndAdvance>,
    #[serde(rename = "ShortTermLoansAndAdvances")]
    pub short_term_loans_and_advances: Vec<ShortTermLoansAndAdvance>,
    #[serde(rename = "TotalLoansAndAdvances")]
    pub total_loans_and_advances: Vec<TotalLoansAndAdvance>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SecuredLongGood {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UnsecuredLongGood {
    #[serde(rename = "CapitalAdvances")]
    pub capital_advances: Vec<CapitalAdvance>,
    #[serde(rename = "SecurityDeposits")]
    pub security_deposits: Vec<SecurityDeposit>,
    #[serde(rename = "LoansAndAdvancesToRelatedParties")]
    pub loans_and_advances_to_related_parties: Vec<LoansAndAdvancesToRelatedParty>,
    #[serde(rename = "OtherLoansAndAdvances")]
    pub other_loans_and_advances: Vec<OtherLoansAndAdvance>,
    #[serde(rename = "LessProvisionOnRelatedParties")]
    pub less_provision_on_related_parties: Vec<LessProvisionOnRelatedParty>,
    #[serde(rename = "LessProvisionOnOthers")]
    pub less_provision_on_others: Vec<LessProvisionOnOther>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CapitalAdvance {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SecurityDeposit {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansAndAdvancesToRelatedParty {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherLoansAndAdvance {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LessProvisionOnRelatedParty {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LessProvisionOnOther {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UnsecuredLongDoubtful {
    #[serde(rename = "CapitalAdvances")]
    pub capital_advances: Vec<CapitalAdvance2>,
    #[serde(rename = "SecurityDeposits")]
    pub security_deposits: Vec<SecurityDeposit2>,
    #[serde(rename = "LoansAndAdvancesToRelatedParties")]
    pub loans_and_advances_to_related_parties: Vec<LoansAndAdvancesToRelatedParty2>,
    #[serde(rename = "OtherLoansAndAdvances")]
    pub other_loans_and_advances: Vec<OtherLoansAndAdvance2>,
    #[serde(rename = "LessProvisionOnRelatedParties")]
    pub less_provision_on_related_parties: Vec<LessProvisionOnRelatedParty2>,
    #[serde(rename = "LessProvisionOnOthers")]
    pub less_provision_on_others: Vec<LessProvisionOnOther2>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CapitalAdvance2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SecurityDeposit2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansAndAdvancesToRelatedParty2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherLoansAndAdvance2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LessProvisionOnRelatedParty2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LessProvisionOnOther2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LongTermLoansAndAdvance {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ShortTermLoansAndAdvance {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalLoansAndAdvance {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TradeReceivablesAgeing {
    #[serde(rename = "DueExceedingSixMonths")]
    pub due_exceeding_six_months: DueExceedingSixMonths,
    #[serde(rename = "DueUptoSixMonths")]
    pub due_upto_six_months: DueUptoSixMonths,
    #[serde(rename = "Unclassified")]
    pub unclassified: Unclassified,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DueExceedingSixMonths {
    #[serde(rename = "SecuredConsideredGood")]
    pub secured_considered_good: Vec<Value>,
    #[serde(rename = "UnsecuredConsideredGood")]
    pub unsecured_considered_good: Vec<Value>,
    #[serde(rename = "Doubtfuls")]
    pub doubtfuls: Vec<Value>,
    #[serde(rename = "LessProvisions")]
    pub less_provisions: Vec<Value>,
    #[serde(rename = "NetTradeReceivables")]
    pub net_trade_receivables: Vec<Value>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DueUptoSixMonths {
    #[serde(rename = "SecuredConsideredGood")]
    pub secured_considered_good: Vec<Value>,
    #[serde(rename = "UnsecuredConsideredGood")]
    pub unsecured_considered_good: Vec<Value>,
    #[serde(rename = "Doubtfuls")]
    pub doubtfuls: Vec<Value>,
    #[serde(rename = "LessProvisions")]
    pub less_provisions: Vec<Value>,
    #[serde(rename = "NetTradeReceivables")]
    pub net_trade_receivables: Vec<Value>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Unclassified {
    #[serde(rename = "TotalTradeReceivables")]
    pub total_trade_receivables: Vec<TotalTradeReceivable>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalTradeReceivable {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RiskReport {
    #[serde(rename = "PiotroskisFScore")]
    pub piotroskis_fscore: PiotroskisFscore,
    #[serde(rename = "OtherWidelyAcceptedTraditionalModels")]
    pub other_widely_accepted_traditional_models: OtherWidelyAcceptedTraditionalModels,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PiotroskisFscore {
    #[serde(rename = "ProfitabilityStrengths")]
    pub profitability_strengths: Vec<ProfitabilityStrength>,
    #[serde(rename = "LeverageAndLiquidityStrength")]
    pub leverage_and_liquidity_strength: Vec<LeverageAndLiquidityStrength>,
    #[serde(rename = "OperatingEfficiency")]
    pub operating_efficiency: Vec<OperatingEfficiency>,
    #[serde(rename = "OverallFinancialsStrengthTest")]
    pub overall_financials_strength_test: Vec<OverallFinancialsStrengthTest>,
    #[serde(rename = "RedFlags")]
    pub red_flags: Vec<String>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProfitabilityStrength {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LeverageAndLiquidityStrength {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OperatingEfficiency {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OverallFinancialsStrengthTest {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherWidelyAcceptedTraditionalModels {
    #[serde(rename = "BeneishsMScore_ProfitManipulationTests")]
    pub beneishs_mscore_profit_manipulation_tests: Vec<BeneishsMscoreProfitManipulationTest>,
    #[serde(rename = "AltmanZScore_FinancialDistressTest")]
    pub altman_zscore_financial_distress_test: Vec<AltmanZscoreFinancialDistressTest>,
    #[serde(rename = "MontiersCScore_WindowDressingTest")]
    pub montiers_cscore_window_dressing_test: Vec<MontiersCscoreWindowDressingTest>,
    #[serde(rename = "RedFlags")]
    pub red_flags: Value,
    #[serde(rename = "GreenFlags")]
    pub green_flags: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BeneishsMscoreProfitManipulationTest {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AltmanZscoreFinancialDistressTest {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct MontiersCscoreWindowDressingTest {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ComparativeFinancialsConsolidated {
    #[serde(rename = "ProfitAndLossStatement")]
    pub profit_and_loss_statement: ProfitAndLossStatement2,
    #[serde(rename = "BalanceSheetConsolidated")]
    pub balance_sheet_consolidated: BalanceSheetConsolidated,
    #[serde(rename = "CashFlowStatementConsolidated")]
    pub cash_flow_statement_consolidated: CashFlowStatementConsolidated,
    #[serde(rename = "RatioAnalysisConsolidated")]
    pub ratio_analysis_consolidated: RatioAnalysisConsolidated,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProfitAndLossStatement2 {
    #[serde(rename = "OperatingRevenues")]
    pub operating_revenues: Vec<OperatingRevenue2>,
    #[serde(rename = "OtherIncomes")]
    pub other_incomes: Vec<OtherIncome2>,
    #[serde(rename = "TotalRevenues")]
    pub total_revenues: Vec<TotalRevenue2>,
    #[serde(rename = "TotalExpenses")]
    pub total_expenses: Vec<TotalExpense3>,
    #[serde(rename = "EBDITA")]
    pub ebdita: Vec<Ebdita2>,
    #[serde(rename = "Depreciations")]
    pub depreciations: Vec<Depreciation2>,
    #[serde(rename = "Interests")]
    pub interests: Vec<Interest2>,
    #[serde(rename = "PBT")]
    pub pbt: Vec<Pbt2>,
    #[serde(rename = "Taxes")]
    pub taxes: Vec<Tax2>,
    #[serde(rename = "OtherAdjustments")]
    pub other_adjustments: Vec<OtherAdjustment2>,
    #[serde(rename = "PAT")]
    pub pat: Vec<Pat2>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OperatingRevenue2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherIncome2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalRevenue2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalExpense3 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Ebdita2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Depreciation2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Interest2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Pbt2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Tax2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherAdjustment2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Pat2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BalanceSheetConsolidated {
    #[serde(rename = "NetWorth")]
    pub net_worth: Vec<NetWorth2>,
    #[serde(rename = "Borrowings")]
    pub borrowings: Vec<Borrowing2>,
    #[serde(rename = "OtherNonCurrentLiabilities")]
    pub other_non_current_liabilities: Vec<OtherNonCurrentLiability2>,
    #[serde(rename = "CurrentLiabilitiesAndProvisions")]
    pub current_liabilities_and_provisions: Vec<CurrentLiabilitiesAndProvision2>,
    #[serde(rename = "DeferredTaxLiabilityOfAssets")]
    pub deferred_tax_liability_of_assets: Vec<DeferredTaxLiabilityOfAsset2>,
    #[serde(rename = "TotalEquityAndLiabilities")]
    pub total_equity_and_liabilities: Vec<TotalEquityAndLiability2>,
    #[serde(rename = "TangibleAssets")]
    pub tangible_assets: Vec<TangibleAsset2>,
    #[serde(rename = "CapitalWIPAndOthers")]
    pub capital_wipand_others: Vec<CapitalWipandOther2>,
    #[serde(rename = "IntangibleAssets")]
    pub intangible_assets: Vec<IntangibleAsset2>,
    #[serde(rename = "Investments")]
    pub investments: Vec<Investment2>,
    #[serde(rename = "LoansAndAdvances")]
    pub loans_and_advances: Vec<LoansAndAdvance2>,
    #[serde(rename = "Inventories")]
    pub inventories: Vec<Inventory2>,
    #[serde(rename = "TradeReceivables")]
    pub trade_receivables: Vec<TradeReceivable2>,
    #[serde(rename = "CashAndBankBalances")]
    pub cash_and_bank_balances: Vec<CashAndBankBalance2>,
    #[serde(rename = "OtherAssets")]
    pub other_assets: Vec<OtherAsset2>,
    #[serde(rename = "TotalAssets")]
    pub total_assets: Vec<TotalAsset>,
    #[serde(rename = "CurrentLiabilities")]
    pub current_liabilities: Vec<CurrentLiability2>,
    #[serde(rename = "CurrentAssets")]
    pub current_assets: Vec<CurrentAsset2>,
    #[serde(rename = "WorkingCapitals")]
    pub working_capitals: Vec<WorkingCapital2>,
    #[serde(rename = "RedFlags")]
    pub red_flags: Vec<Value>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NetWorth2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Borrowing2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherNonCurrentLiability2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentLiabilitiesAndProvision2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DeferredTaxLiabilityOfAsset2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalEquityAndLiability2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TangibleAsset2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CapitalWipandOther2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct IntangibleAsset2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Investment2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansAndAdvance2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Inventory2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TradeReceivable2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CashAndBankBalance2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherAsset2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalAsset {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentLiability2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentAsset2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WorkingCapital2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CashFlowStatementConsolidated {
    #[serde(rename = "OperatingActivities")]
    pub operating_activities: Vec<OperatingActivity2>,
    #[serde(rename = "InvestingActivities")]
    pub investing_activities: Vec<InvestingActivity2>,
    #[serde(rename = "FinancingActivities")]
    pub financing_activities: Vec<FinancingActivity2>,
    #[serde(rename = "CashAndCashEquivalentAtEnds")]
    pub cash_and_cash_equivalent_at_ends: Vec<CashAndCashEquivalentAtEnd2>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OperatingActivity2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InvestingActivity2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FinancingActivity2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CashAndCashEquivalentAtEnd2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RatioAnalysisConsolidated {
    #[serde(rename = "OperativeRevenueGrowthPercentages")]
    pub operative_revenue_growth_percentages: Vec<OperativeRevenueGrowthPercentage2>,
    #[serde(rename = "EBITDAGrowths")]
    pub ebitdagrowths: Vec<Ebitdagrowth2>,
    #[serde(rename = "EPSGrowths")]
    pub epsgrowths: Vec<Epsgrowth2>,
    #[serde(rename = "EBITDAMarginPercentages")]
    pub ebitdamargin_percentages: Vec<EbitdamarginPercentage2>,
    #[serde(rename = "PATMarginPercentage")]
    pub patmargin_percentage: Vec<PatmarginPercentage2>,
    #[serde(rename = "ReturnOnCapitalEmployedPercentage_RoCEs")]
    pub return_on_capital_employed_percentage_ro_ces: Vec<ReturnOnCapitalEmployedPercentageRoCe2>,
    #[serde(rename = "ReturnOnEquityPercentage_RoEs")]
    pub return_on_equity_percentage_ro_es: Vec<ReturnOnEquityPercentageRoE2>,
    #[serde(rename = "ReturnOnAssetsPercentage_RoAs")]
    pub return_on_assets_percentage_ro_as: Vec<ReturnOnAssetsPercentageRoA2>,
    #[serde(rename = "AvgInventoryHoldingDays")]
    pub avg_inventory_holding_days: Vec<AvgInventoryHoldingDay2>,
    #[serde(rename = "AvgDebtorsOutstandingDays")]
    pub avg_debtors_outstanding_days: Vec<AvgDebtorsOutstandingDay2>,
    #[serde(rename = "AvgTradePayableDays")]
    pub avg_trade_payable_days: Vec<AvgTradePayableDay2>,
    #[serde(rename = "AvgCashConversionCycle")]
    pub avg_cash_conversion_cycle: Vec<AvgCashConversionCycle2>,
    #[serde(rename = "QuickRatios")]
    pub quick_ratios: Vec<QuickRatio2>,
    #[serde(rename = "CurrentRatio")]
    pub current_ratio: Vec<CurrentRatio2>,
    #[serde(rename = "LeverageTOL_TNWs")]
    pub leverage_tol_tnws: Vec<LeverageTolTnw2>,
    #[serde(rename = "NetDebtEquities")]
    pub net_debt_equities: Vec<NetDebtEquity2>,
    #[serde(rename = "InterestCoverages")]
    pub interest_coverages: Vec<InterestCoverage2>,
    #[serde(rename = "CapitalEmployedTurnovers")]
    pub capital_employed_turnovers: Vec<CapitalEmployedTurnover2>,
    #[serde(rename = "AssetTurnovers")]
    pub asset_turnovers: Vec<AssetTurnover2>,
    #[serde(rename = "InventoryTurnovers")]
    pub inventory_turnovers: Vec<InventoryTurnover2>,
    #[serde(rename = "ReceivablesTurnovers")]
    pub receivables_turnovers: Vec<ReceivablesTurnover2>,
    #[serde(rename = "WorkingCapitalTurnovers")]
    pub working_capital_turnovers: Vec<WorkingCapitalTurnover2>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OperativeRevenueGrowthPercentage2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Ebitdagrowth2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Epsgrowth2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EbitdamarginPercentage2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PatmarginPercentage2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ReturnOnCapitalEmployedPercentageRoCe2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ReturnOnEquityPercentageRoE2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ReturnOnAssetsPercentageRoA2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AvgInventoryHoldingDay2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AvgDebtorsOutstandingDay2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AvgTradePayableDay2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AvgCashConversionCycle2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct QuickRatio2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentRatio2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LeverageTolTnw2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NetDebtEquity2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InterestCoverage2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CapitalEmployedTurnover2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AssetTurnover2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InventoryTurnover2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ReceivablesTurnover2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WorkingCapitalTurnover2 {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct StandaloneVsConsolidatedFinancials {
    #[serde(rename = "ProfitAndLossStatementAnalysis")]
    pub profit_and_loss_statement_analysis: ProfitAndLossStatementAnalysis,
    #[serde(rename = "BalanceSheetAnalysis")]
    pub balance_sheet_analysis: BalanceSheetAnalysis,
    #[serde(rename = "CommonSizeStatementAnalysis")]
    pub common_size_statement_analysis: CommonSizeStatementAnalysis,
    #[serde(rename = "RedFlags")]
    pub red_flags: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProfitAndLossStatementAnalysis {
    #[serde(rename = "TotalRevenueAnalysis")]
    pub total_revenue_analysis: Vec<TotalRevenueAnalysi>,
    #[serde(rename = "TotalExpensesAnalysis")]
    pub total_expenses_analysis: Value,
    #[serde(rename = "ProfitAfterTaxAnalysis")]
    pub profit_after_tax_analysis: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalRevenueAnalysi {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Standalone")]
    pub standalone: f64,
    #[serde(rename = "Consolidated")]
    pub consolidated: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BalanceSheetAnalysis {
    #[serde(rename = "NetWorthAnalysis")]
    pub net_worth_analysis: Vec<NetWorthAnalysi>,
    #[serde(rename = "ReturnOnNetworthAnalysis")]
    pub return_on_networth_analysis: Value,
    #[serde(rename = "LongTermAdvancesToLongTermBorrowingAnalysis")]
    pub long_term_advances_to_long_term_borrowing_analysis: Value,
    #[serde(rename = "CurrentRatioAnalysis")]
    pub current_ratio_analysis: Value,
    #[serde(rename = "DebtEquityRatioAnalysis")]
    pub debt_equity_ratio_analysis: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NetWorthAnalysi {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Standalone")]
    pub standalone: f64,
    #[serde(rename = "Consolidated")]
    pub consolidated: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CommonSizeStatementAnalysis {
    #[serde(rename = "ProfitAndLossAccountAnalysis")]
    pub profit_and_loss_account_analysis: ProfitAndLossAccountAnalysis,
    #[serde(rename = "BalanceSheetAnalysis")]
    pub balance_sheet_analysis: BalanceSheetAnalysis2,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ProfitAndLossAccountAnalysis {
    #[serde(rename = "TotalRevenue")]
    pub total_revenue: TotalRevenue3,
    #[serde(rename = "OperatingRevenue")]
    pub operating_revenue: OperatingRevenue3,
    #[serde(rename = "OtherIncome")]
    pub other_income: OtherIncome3,
    #[serde(rename = "TotalExpenses")]
    pub total_expenses: TotalExpenses,
    #[serde(rename = "EBDITACSSAnalysis")]
    pub ebditacssanalysis: Ebditacssanalysis,
    #[serde(rename = "DepreciationCSSAnalysis")]
    pub depreciation_cssanalysis: DepreciationCssanalysis,
    #[serde(rename = "InterestCSSAnalysis")]
    pub interest_cssanalysis: InterestCssanalysis,
    #[serde(rename = "PBTCSSAnalysis")]
    pub pbtcssanalysis: Pbtcssanalysis,
    #[serde(rename = "TaxCSSAnalysis")]
    pub tax_cssanalysis: TaxCssanalysis,
    #[serde(rename = "OtherAdjustmentsCSSAnalysis")]
    pub other_adjustments_cssanalysis: OtherAdjustmentsCssanalysis,
    #[serde(rename = "PATCSSAnalysis")]
    pub patcssanalysis: Patcssanalysis,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalRevenue3 {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OperatingRevenue3 {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherIncome3 {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalExpenses {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Ebditacssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DepreciationCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InterestCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Pbtcssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TaxCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherAdjustmentsCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Patcssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BalanceSheetAnalysis2 {
    #[serde(rename = "TotalEquityAndLiabilitiesCSSAnalysis")]
    pub total_equity_and_liabilities_cssanalysis: TotalEquityAndLiabilitiesCssanalysis,
    #[serde(rename = "NetWorthCSSAnalysis")]
    pub net_worth_cssanalysis: NetWorthCssanalysis,
    #[serde(rename = "BorrowingsCSSAnalysis")]
    pub borrowings_cssanalysis: BorrowingsCssanalysis,
    #[serde(rename = "OtherNonCurrentLiabilitiesCSSAnalysis")]
    pub other_non_current_liabilities_cssanalysis: OtherNonCurrentLiabilitiesCssanalysis,
    #[serde(rename = "CurrentLiabilitiesAndProvisionsCSSAnalysis")]
    pub current_liabilities_and_provisions_cssanalysis: CurrentLiabilitiesAndProvisionsCssanalysis,
    #[serde(rename = "DeferredTaxLiabilityOfAssetCSSAnalysis")]
    pub deferred_tax_liability_of_asset_cssanalysis: DeferredTaxLiabilityOfAssetCssanalysis,
    #[serde(rename = "TotalAssetsCSSAnalysis")]
    pub total_assets_cssanalysis: TotalAssetsCssanalysis,
    #[serde(rename = "TangibleAssetsCSSAnalysis")]
    pub tangible_assets_cssanalysis: TangibleAssetsCssanalysis,
    #[serde(rename = "CapitalWIPAndOthersCSSAnalysis")]
    pub capital_wipand_others_cssanalysis: CapitalWipandOthersCssanalysis,
    #[serde(rename = "IntangibleAssetsCSSAnalysis")]
    pub intangible_assets_cssanalysis: IntangibleAssetsCssanalysis,
    #[serde(rename = "InvestmentsCSSAnalysis")]
    pub investments_cssanalysis: InvestmentsCssanalysis,
    #[serde(rename = "LoansAndAdvancesCSSAnalysis")]
    pub loans_and_advances_cssanalysis: LoansAndAdvancesCssanalysis,
    #[serde(rename = "InventoriesCSSAnalysis")]
    pub inventories_cssanalysis: InventoriesCssanalysis,
    #[serde(rename = "TradeReceivablesCSSAnalysis")]
    pub trade_receivables_cssanalysis: TradeReceivablesCssanalysis,
    #[serde(rename = "CashAndBankBalancesCSSAnalysis")]
    pub cash_and_bank_balances_cssanalysis: CashAndBankBalancesCssanalysis,
    #[serde(rename = "OtherAssetsCSSAnalysis")]
    pub other_assets_cssanalysis: OtherAssetsCssanalysis,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalEquityAndLiabilitiesCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NetWorthCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BorrowingsCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherNonCurrentLiabilitiesCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentLiabilitiesAndProvisionsCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DeferredTaxLiabilityOfAssetCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TotalAssetsCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TangibleAssetsCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CapitalWipandOthersCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct IntangibleAssetsCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InvestmentsCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LoansAndAdvancesCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct InventoriesCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct TradeReceivablesCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CashAndBankBalancesCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherAssetsCssanalysis {
    #[serde(rename = "StandaloneValue")]
    pub standalone_value: f64,
    #[serde(rename = "ConsolidatedValue")]
    pub consolidated_value: f64,
    #[serde(rename = "StandalonePercentage")]
    pub standalone_percentage: f64,
    #[serde(rename = "ConsolidatedPercentage")]
    pub consolidated_percentage: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AuditorDetailsAndCaroreport {
    #[serde(rename = "AuditorsKYCAndDetails")]
    pub auditors_kycand_details: Vec<AuditorsKycandDetail>,
    #[serde(rename = "AuditorsReportQualificationDetails")]
    pub auditors_report_qualification_details: Value,
    #[serde(rename = "CAROReport")]
    pub caroreport: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AuditorsKycandDetail {
    #[serde(rename = "FirmName")]
    pub firm_name: String,
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "RegNo")]
    pub reg_no: String,
    #[serde(rename = "AuditorName")]
    pub auditor_name: String,
    #[serde(rename = "Membership")]
    pub membership: String,
    #[serde(rename = "Address")]
    pub address: String,
    #[serde(rename = "AuditorPAN")]
    pub auditor_pan: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GroupCompaniesAndRelatedPartyInformation {
    #[serde(rename = "GroupStructureHighlights")]
    pub group_structure_highlights: GroupStructureHighlights,
    #[serde(rename = "GroupCompanies")]
    pub group_companies: Value,
    #[serde(rename = "SubsidiaryFinancialsSnapshot")]
    pub subsidiary_financials_snapshot: Vec<SubsidiaryFinancialsSnapshot>,
    #[serde(rename = "RelatedPartyTransactions")]
    pub related_party_transactions: Vec<RelatedPartyTransaction>,
    #[serde(rename = "RelatedPartyTransactionsNotAtArmLengthPriceSchedule")]
    pub related_party_transactions_not_at_arm_length_price_schedule: Vec<Value>,
    #[serde(rename = "RelatedPartyMaterialTransactionsAtArmLengthPriceSchedule")]
    pub related_party_material_transactions_at_arm_length_price_schedule: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GroupStructureHighlights {
    #[serde(rename = "Holdings")]
    pub holdings: i64,
    #[serde(rename = "Subsidiaries")]
    pub subsidiaries: i64,
    #[serde(rename = "JointVenture")]
    pub joint_venture: i64,
    #[serde(rename = "Associate")]
    pub associate: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct SubsidiaryFinancialsSnapshot {
    #[serde(rename = "SubsidiaryName")]
    pub subsidiary_name: String,
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Country")]
    pub country: String,
    #[serde(rename = "ShareholdingPercentage")]
    pub shareholding_percentage: f64,
    #[serde(rename = "ShareCapital")]
    pub share_capital: f64,
    #[serde(rename = "Reserves")]
    pub reserves: f64,
    #[serde(rename = "Assets")]
    pub assets: f64,
    #[serde(rename = "Income")]
    pub income: Option<f64>,
    #[serde(rename = "PAT")]
    pub pat: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RelatedPartyTransaction {
    #[serde(rename = "RelatedParty")]
    pub related_party: String,
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Country")]
    pub country: String,
    #[serde(rename = "NatureOfRelationship")]
    pub nature_of_relationship: String,
    #[serde(rename = "DescriptionOfTransaction")]
    pub description_of_transaction: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OtherRelatedCompanies {
    #[serde(rename = "RelatedCompaniesByDirectors")]
    pub related_companies_by_directors: Vec<RelatedCompaniesByDirector>,
    #[serde(rename = "RelatedCompaniesByEmails")]
    pub related_companies_by_emails: Value,
    #[serde(rename = "RelatedCompaniesByAddresses")]
    pub related_companies_by_addresses: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct RelatedCompaniesByDirector {
    #[serde(rename = "Directors")]
    pub directors: Vec<String>,
    #[serde(rename = "CompanyCIN")]
    pub company_cin: String,
    #[serde(rename = "CompanyName")]
    pub company_name: String,
    #[serde(rename = "State")]
    pub state: String,
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "DateOfIncorporation")]
    pub date_of_incorporation: String,
    #[serde(rename = "CompanyStatus")]
    pub company_status: String,
    #[serde(rename = "Industry")]
    pub industry: Option<String>,
    #[serde(rename = "PaidupCapital")]
    pub paidup_capital: f64,
    #[serde(rename = "TotalIncome")]
    pub total_income: f64,
    #[serde(rename = "TotalExpenditure")]
    pub total_expenditure: f64,
    #[serde(rename = "ReservesAndSurplus")]
    pub reserves_and_surplus: f64,
    #[serde(rename = "Networth")]
    pub networth: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CreditRatings {
    #[serde(rename = "CreditRatingsAssignedInLastOneYear")]
    pub credit_ratings_assigned_in_last_one_year: Value,
    #[serde(rename = "CreditRatingsOlderThanLastOneYear")]
    pub credit_ratings_older_than_last_one_year: Vec<CreditRatingsOlderThanLastOneYear>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CreditRatingsOlderThanLastOneYear {
    #[serde(rename = "RatingAgency")]
    pub rating_agency: String,
    #[serde(rename = "DateOfRating")]
    pub date_of_rating: String,
    #[serde(rename = "InstrumentDetails")]
    pub instrument_details: String,
    #[serde(rename = "Amount")]
    pub amount: Value,
    #[serde(rename = "RatingAssigned")]
    pub rating_assigned: String,
    #[serde(rename = "Outlook")]
    pub outlook: String,
    #[serde(rename = "RationalLink")]
    pub rational_link: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Itatcase {
    #[serde(rename = "Appeal")]
    pub appeal: String,
    #[serde(rename = "Appellant")]
    pub appellant: String,
    #[serde(rename = "Respondent")]
    pub respondent: String,
    #[serde(rename = "TribunalBench")]
    pub tribunal_bench: String,
    #[serde(rename = "AssessmentYear")]
    pub assessment_year: String,
    #[serde(rename = "BenchAllotted")]
    pub bench_allotted: String,
    #[serde(rename = "CaseStatus")]
    pub case_status: String,
    #[serde(rename = "TribunalOrderLink")]
    pub tribunal_order_link: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct McaseriousComplaint {
    #[serde(rename = "ComplaintType")]
    pub complaint_type: String,
    #[serde(rename = "SRN")]
    pub srn: String,
    #[serde(rename = "FilingDate")]
    pub filing_date: String,
    #[serde(rename = "ComplaintStatus")]
    pub complaint_status: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ComplianceAndDelays {
    #[serde(rename = "GSTComplianceLatestSixMonths")]
    pub gstcompliance_latest_six_months: Vec<GstcomplianceLatestSixMonth>,
    #[serde(rename = "MCAAnnualCompliance")]
    pub mcaannual_compliance: McaannualCompliance,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GstcomplianceLatestSixMonth {
    #[serde(rename = "GSTIN")]
    pub gstin: String,
    #[serde(rename = "State")]
    pub state: String,
    #[serde(rename = "FilingDetail")]
    pub filing_detail: Vec<FilingDetail>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FilingDetail {
    #[serde(rename = "FilingMonth")]
    pub filing_month: String,
    #[serde(rename = "FilingStatus")]
    pub filing_status: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct McaannualCompliance {
    #[serde(rename = "Compliances")]
    pub compliances: Vec<Compliance>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Compliance {
    #[serde(rename = "Compliance")]
    pub compliance: String,
    #[serde(rename = "FilingStatus")]
    pub filing_status: Vec<FilingStatu>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FilingStatu {
    #[serde(rename = "FinancialYear")]
    pub financial_year: String,
    #[serde(rename = "Status")]
    pub status: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EstablishmentAndEpfdetails {
    #[serde(rename = "EstablishmentDetails")]
    pub establishment_details: Vec<EstablishmentDetail>,
    #[serde(rename = "EmploymentTrends")]
    pub employment_trends: Vec<EmploymentTrend>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EstablishmentDetail {
    #[serde(rename = "EstablishmentName")]
    pub establishment_name: String,
    #[serde(rename = "EstablishmentCode")]
    pub establishment_code: String,
    #[serde(rename = "City")]
    pub city: String,
    #[serde(rename = "State")]
    pub state: String,
    #[serde(rename = "Pincode")]
    pub pincode: Option<i64>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct EmploymentTrend {
    #[serde(rename = "MonthYear")]
    pub month_year: String,
    #[serde(rename = "TotalEmployees")]
    pub total_employees: i64,
    #[serde(rename = "EPFAmountPaid")]
    pub epfamount_paid: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChargeSearchReport {
    #[serde(rename = "OpenCharges")]
    pub open_charges: Vec<OpenCharge>,
    #[serde(rename = "SatisfiedCharges")]
    pub satisfied_charges: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OpenCharge {
    #[serde(rename = "ChargeHolder")]
    pub charge_holder: String,
    #[serde(rename = "ChargeCode")]
    pub charge_code: Option<i64>,
    #[serde(rename = "DateOfCreation")]
    pub date_of_creation: String,
    #[serde(rename = "OutstandingYears")]
    pub outstanding_years: Option<f64>,
    #[serde(rename = "DateOfLastModification")]
    pub date_of_last_modification: String,
    #[serde(rename = "AssetsSecured")]
    pub assets_secured: String,
    #[serde(rename = "Amount")]
    pub amount: f64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChargesProfileReport {
    #[serde(rename = "ChargesProfiles")]
    pub charges_profiles: Vec<ChargesProfile>,
    #[serde(rename = "FutureCharges")]
    pub future_charges: Value,
    #[serde(rename = "PersonalGuarantees")]
    pub personal_guarantees: Value,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChargesProfile {
    #[serde(rename = "ChargeID")]
    pub charge_id: String,
    #[serde(rename = "ChargeHolderName")]
    pub charge_holder_name: String,
    #[serde(rename = "ChargeAmount")]
    pub charge_amount: f64,
    #[serde(rename = "ChargeHolderCity")]
    pub charge_holder_city: Value,
    #[serde(rename = "ChargeHolderState")]
    pub charge_holder_state: Value,
    #[serde(rename = "AttachmentDetails")]
    pub attachment_details: String,
    #[serde(rename = "ListOfAttachments")]
    pub list_of_attachments: String,
    #[serde(rename = "OriginalCreationDate")]
    pub original_creation_date: String,
    #[serde(rename = "Modification")]
    pub modification: String,
    #[serde(rename = "ConsortiumFinance")]
    pub consortium_finance: String,
    #[serde(rename = "JointCharge")]
    pub joint_charge: String,
    #[serde(rename = "ChargeOn")]
    pub charge_on: String,
    #[serde(rename = "InterestRateDetails")]
    pub interest_rate_details: String,
    #[serde(rename = "TermsOfRepayment")]
    pub terms_of_repayment: String,
    #[serde(rename = "Margin")]
    pub margin: String,
    #[serde(rename = "ExtentAndOperationOfTheCharge")]
    pub extent_and_operation_of_the_charge: String,
    #[serde(rename = "ShortParticularsOfThePropertyOrAssetsCharged")]
    pub short_particulars_of_the_property_or_assets_charged: String,
    #[serde(rename = "ModificationHistory")]
    pub modification_history: String,
    #[serde(rename = "DownloadChargeForm")]
    pub download_charge_form: String,
    #[serde(rename = "OthersTerms")]
    pub others_terms: String,
    #[serde(rename = "NameOfPersonInCaseTheSaidPropertyIsNotRegisteredInCompanyName")]
    pub name_of_person_in_case_the_said_property_is_not_registered_in_company_name: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DirectorKycandNetworks {
    #[serde(rename = "BoardMembersKYCs")]
    pub board_members_kycs: Vec<BoardMembersKyc>,
    #[serde(rename = "CurrentDirectors")]
    pub current_directors: Vec<CurrentDirector>,
    #[serde(rename = "PastDirectors")]
    pub past_directors: Vec<PastDirector>,
    #[serde(rename = "NewDirectorshipDetails")]
    pub new_directorship_details: Vec<NewDirectorshipDetail>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct BoardMembersKyc {
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "DirectorDIN")]
    pub director_din: String,
    #[serde(rename = "Designation")]
    pub designation: String,
    #[serde(rename = "Age")]
    pub age: f64,
    #[serde(rename = "Tenure")]
    pub tenure: f64,
    #[serde(rename = "PAN")]
    pub pan: String,
    #[serde(rename = "City")]
    pub city: String,
    #[serde(rename = "State")]
    pub state: String,
    #[serde(rename = "Email")]
    pub email: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct CurrentDirector {
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "DirectorDIN")]
    pub director_din: String,
    #[serde(rename = "Designation")]
    pub designation: String,
    #[serde(rename = "AppointmentDate")]
    pub appointment_date: String,
    #[serde(rename = "DirectorshipCount")]
    pub directorship_count: i64,
    #[serde(rename = "DisqualifiedUS164_2")]
    pub disqualified_us164_2: String,
    #[serde(rename = "DINStatus")]
    pub dinstatus: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PastDirector {
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "DirectorDIN")]
    pub director_din: String,
    #[serde(rename = "Designation")]
    pub designation: String,
    #[serde(rename = "AppointmentDate")]
    pub appointment_date: String,
    #[serde(rename = "DirectorshipCount")]
    pub directorship_count: i64,
    #[serde(rename = "DisqualifiedUS164_2")]
    pub disqualified_us164_2: String,
    #[serde(rename = "DINStatus")]
    pub dinstatus: String,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NewDirectorshipDetail {
    #[serde(rename = "DirectorName")]
    pub director_name: String,
    #[serde(rename = "CompanyName")]
    pub company_name: String,
    #[serde(rename = "IncorporationDate")]
    pub incorporation_date: String,
    #[serde(rename = "Industry")]
    pub industry: String,
    #[serde(rename = "State")]
    pub state: String,
    #[serde(rename = "PaidupCapital")]
    pub paidup_capital: f64,
    #[serde(rename = "CommonDirectors")]
    pub common_directors: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct LegalInformation {
    #[serde(rename = "LegalCasesSummary")]
    pub legal_cases_summary: Value,
    #[serde(rename = "OpenCases")]
    pub open_cases: Vec<OpenCase>,
    #[serde(rename = "DisposedCases")]
    pub disposed_cases: Vec<DisposedCase>,
    #[serde(rename = "UnknownStatusCases")]
    pub unknown_status_cases: Vec<UnknownStatusCase>,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct OpenCase {
    #[serde(rename = "CaseNumber")]
    pub case_number: String,
    #[serde(rename = "Court")]
    pub court: String,
    #[serde(rename = "Petitioner")]
    pub petitioner: String,
    #[serde(rename = "Respondent")]
    pub respondent: String,
    #[serde(rename = "CaseType")]
    pub case_type: String,
    #[serde(rename = "OrderLink")]
    pub order_link: String,
    #[serde(rename = "CaseYear")]
    pub case_year: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct DisposedCase {
    #[serde(rename = "CaseNumber")]
    pub case_number: String,
    #[serde(rename = "Court")]
    pub court: String,
    #[serde(rename = "Petitioner")]
    pub petitioner: String,
    #[serde(rename = "Respondent")]
    pub respondent: String,
    #[serde(rename = "CaseType")]
    pub case_type: String,
    #[serde(rename = "OrderLink")]
    pub order_link: String,
    #[serde(rename = "CaseYear")]
    pub case_year: i64,
}

#[derive(Default, Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct UnknownStatusCase {
    #[serde(rename = "CaseNumber")]
    pub case_number: String,
    #[serde(rename = "Court")]
    pub court: String,
    #[serde(rename = "Petitioner")]
    pub petitioner: String,
    #[serde(rename = "Respondent")]
    pub respondent: String,
    #[serde(rename = "CaseType")]
    pub case_type: String,
    #[serde(rename = "OrderLink")]
    pub order_link: String,
    #[serde(rename = "CaseYear")]
    pub case_year: i64,
}
