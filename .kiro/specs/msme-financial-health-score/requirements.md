# Requirements Document

## Introduction

This document defines requirements for the MSME Financial Health Score system, a web application that evaluates the financial health of Micro, Small, and Medium Enterprises (MSMEs) using alternate data sources. The system aggregates data from GST, UPI transactions, Account Aggregator bank data, and EPFO records to compute a comprehensive financial health score (0-100) with risk classification and explainability features.

## Glossary

- **MSME**: Micro, Small, and Medium Enterprise
- **Financial_Health_Score**: A numerical score between 0-100 representing the financial health of an MSME
- **Risk_Band**: Classification category (Low/Medium/High) derived from the Financial_Health_Score
- **Data_Adapter**: Component that retrieves and normalizes data from external data sources
- **GST_Adapter**: Data_Adapter for Goods and Services Tax records
- **UPI_Adapter**: Data_Adapter for Unified Payments Interface transaction data
- **Account_Aggregator_Adapter**: Data_Adapter for bank account data via Account Aggregator framework
- **EPFO_Adapter**: Data_Adapter for Employees' Provident Fund Organisation records
- **Feature_Engineering_Pipeline**: Component that transforms raw data into features for scoring
- **Scoring_Engine**: Component that computes Financial_Health_Score using weighted composite and ML models
- **Composite_Weighted_Model**: Scoring model that combines multiple weighted features using predefined weights
- **ML_Classifier**: Machine learning model that classifies MSMEs into risk categories
- **SHAP_Values**: SHapley Additive exPlanations values that explain ML_Classifier predictions
- **API_Layer**: REST API that exposes scoring and data retrieval endpoints
- **Dashboard**: React-based web interface for visualizing MSME financial health data
- **Score_Card**: Dashboard screen displaying the overall Financial_Health_Score and Risk_Band
- **Data_Sources_View**: Dashboard screen showing aggregated data from all Data_Adapters
- **Trend_Analysis_View**: Dashboard screen displaying historical score trends
- **Risk_Factors_View**: Dashboard screen showing explainability metrics using SHAP_Values
- **Recommendations_View**: Dashboard screen providing actionable recommendations
- **What-If_Simulator**: Dashboard component that allows analysts to adjust input features and observe real-time score recalculation
- **Ecosystem_Integration_Panel**: Dashboard component simulating interactions with Account Aggregator, ULI, and OCEN platforms
- **ULI**: Unified Lending Interface, a protocol for standardized lending interactions
- **OCEN**: Open Credit Enablement Network, a framework for connecting borrowers with lenders
- **Score_History_Store**: Persistent storage mechanism for Financial_Health_Score computations over time
- **Synthetic_Dataset_Generator**: Component that generates realistic MSME profiles with labeled financial health data for training
- **MSME_Sector**: Category of MSME business type (Trader, Manufacturer, Services)
- **Sector_Weight_Profile**: Configuration of feature weights specific to an MSME_Sector
- **Authenticated_User**: A bank analyst who has successfully logged in via Supabase Auth
- **Session**: A valid authentication session managed by Supabase Auth with JWT token and auto-refresh
- **Protected_Endpoint**: An API endpoint that requires a valid authenticated session to access

## Requirements

### Requirement 1: GST Data Retrieval

**User Story:** As a bank analyst, I want to retrieve GST data for an MSME, so that I can assess their tax compliance and revenue patterns.

#### Acceptance Criteria

1. WHEN a valid GST identification number is provided, THE GST_Adapter SHALL retrieve GST return data
2. WHEN GST data is successfully retrieved, THE GST_Adapter SHALL normalize the data into a standard format
3. IF GST data retrieval fails, THEN THE GST_Adapter SHALL return an error with a descriptive message
4. THE GST_Adapter SHALL extract revenue figures, filing frequency, and compliance status

### Requirement 2: UPI Transaction Data Retrieval

**User Story:** As a bank analyst, I want to retrieve UPI transaction data for an MSME, so that I can analyze their payment activity and cash flow patterns.

#### Acceptance Criteria

1. WHEN a valid UPI identifier is provided, THE UPI_Adapter SHALL retrieve transaction history
2. WHEN UPI data is successfully retrieved, THE UPI_Adapter SHALL normalize the data into a standard format
3. IF UPI data retrieval fails, THEN THE UPI_Adapter SHALL return an error with a descriptive message
4. THE UPI_Adapter SHALL extract transaction volume, frequency, and average transaction values

### Requirement 3: Account Aggregator Bank Data Retrieval

**User Story:** As a bank analyst, I want to retrieve bank account data via Account Aggregator, so that I can analyze the MSME's banking behavior and liquidity.

#### Acceptance Criteria

1. WHEN a valid Account Aggregator consent token is provided, THE Account_Aggregator_Adapter SHALL retrieve bank account data
2. WHEN bank data is successfully retrieved, THE Account_Aggregator_Adapter SHALL normalize the data into a standard format
3. IF Account Aggregator data retrieval fails, THEN THE Account_Aggregator_Adapter SHALL return an error with a descriptive message
4. THE Account_Aggregator_Adapter SHALL extract account balances, transaction patterns, and credit-debit ratios

### Requirement 4: EPFO Data Retrieval

**User Story:** As a bank analyst, I want to retrieve EPFO data for an MSME, so that I can verify their employee count and payroll stability.

#### Acceptance Criteria

1. WHEN a valid EPFO establishment ID is provided, THE EPFO_Adapter SHALL retrieve employee and contribution data
2. WHEN EPFO data is successfully retrieved, THE EPFO_Adapter SHALL normalize the data into a standard format
3. IF EPFO data retrieval fails, THEN THE EPFO_Adapter SHALL return an error with a descriptive message
4. THE EPFO_Adapter SHALL extract employee count, contribution amounts, and contribution regularity

### Requirement 5: Data Adapter Mock Implementation

**User Story:** As a developer, I want mock implementations of all data adapters, so that I can develop and test the system without real API credentials.

#### Acceptance Criteria

1. WHERE mock mode is enabled, THE Data_Adapter SHALL return simulated data that matches the normalized format
2. WHEN a data request is made in mock mode, THE Data_Adapter SHALL respond within 200 milliseconds
3. THE Data_Adapter SHALL support both mock and production modes via configuration
4. WHERE mock mode is enabled, THE Data_Adapter SHALL generate realistic sample data with variability

### Requirement 6: Feature Engineering Pipeline

**User Story:** As a data scientist, I want to transform raw data into scoring features, so that the Scoring_Engine can compute accurate health scores.

#### Acceptance Criteria

1. WHEN raw data from all Data_Adapters is available, THE Feature_Engineering_Pipeline SHALL compute derived features
2. THE Feature_Engineering_Pipeline SHALL calculate revenue stability, transaction velocity, liquidity ratios, and employment consistency
3. WHEN feature computation fails due to missing data, THE Feature_Engineering_Pipeline SHALL apply default imputation strategies
4. THE Feature_Engineering_Pipeline SHALL normalize all features to comparable scales between 0 and 1

### Requirement 7: Composite Weighted Scoring with Sector Configuration

**User Story:** As a bank analyst, I want a composite weighted score with sector-specific weights, so that I can assess MSME financial health using dimensions appropriate to their business type.

#### Acceptance Criteria

1. WHEN engineered features are provided, THE Composite_Weighted_Model SHALL compute a score between 0 and 100
2. WHERE the MSME_Sector is Trader, THE Composite_Weighted_Model SHALL apply default weights of revenue stability (25%), transaction activity (35%), liquidity (30%), and employment stability (10%)
3. WHERE the MSME_Sector is Manufacturer, THE Composite_Weighted_Model SHALL apply default weights of revenue stability (35%), transaction activity (20%), liquidity (25%), and employment stability (20%)
4. WHERE the MSME_Sector is Services, THE Composite_Weighted_Model SHALL apply default weights of revenue stability (30%), transaction activity (25%), liquidity (20%), and employment stability (25%)
5. THE Composite_Weighted_Model SHALL support configuration of custom Sector_Weight_Profile values per MSME_Sector
6. THE Composite_Weighted_Model SHALL aggregate weighted feature scores into a single Financial_Health_Score
7. WHEN any feature is missing, THE Composite_Weighted_Model SHALL adjust weights proportionally across available features

### Requirement 8: ML-Based Risk Classification

**User Story:** As a bank analyst, I want ML-based risk classification, so that I can identify MSMEs requiring closer scrutiny.

#### Acceptance Criteria

1. WHEN engineered features are provided, THE ML_Classifier SHALL classify the MSME into Low, Medium, or High Risk_Band
2. THE ML_Classifier SHALL use a trained classification model based on historical MSME data
3. WHEN classification is complete, THE ML_Classifier SHALL generate SHAP_Values for each feature
4. THE ML_Classifier SHALL return classification confidence scores for each Risk_Band

### Requirement 9: Explainability with SHAP Values

**User Story:** As a bank analyst, I want to understand why an MSME received a specific risk classification, so that I can make informed lending decisions.

#### Acceptance Criteria

1. WHEN the ML_Classifier produces a Risk_Band, THE Scoring_Engine SHALL compute SHAP_Values for all input features
2. THE Scoring_Engine SHALL rank features by their contribution magnitude to the classification decision
3. THE Scoring_Engine SHALL identify the top 5 features that most influenced the Risk_Band classification
4. THE Scoring_Engine SHALL provide both positive and negative SHAP_Values to show directional impact

### Requirement 10: Score Computation API

**User Story:** As a frontend developer, I want an API to compute scores, so that I can request financial health assessments for MSMEs.

#### Acceptance Criteria

1. WHEN a POST request with MSME identifiers is received, THE API_Layer SHALL orchestrate data retrieval from all Data_Adapters
2. WHEN data retrieval is complete, THE API_Layer SHALL invoke the Feature_Engineering_Pipeline
3. WHEN features are computed, THE API_Layer SHALL invoke both Composite_Weighted_Model and ML_Classifier
4. WHEN scoring is complete, THE API_Layer SHALL return Financial_Health_Score, Risk_Band, SHAP_Values, and source data
5. IF any Data_Adapter fails, THE API_Layer SHALL continue with available data and flag missing sources

### Requirement 11: Score Retrieval API

**User Story:** As a frontend developer, I want an API to retrieve previously computed scores, so that I can display historical assessments without recomputation.

#### Acceptance Criteria

1. WHEN a GET request with an MSME identifier is received, THE API_Layer SHALL retrieve stored score data
2. IF no score exists for the MSME, THEN THE API_Layer SHALL return a 404 status with a descriptive message
3. WHEN a score exists, THE API_Layer SHALL return Financial_Health_Score, Risk_Band, computation timestamp, and SHAP_Values
4. THE API_Layer SHALL support filtering by date range for historical score retrieval

### Requirement 12: Score Card Dashboard Screen

**User Story:** As a bank analyst, I want a score card view, so that I can see the overall financial health score and risk classification at a glance.

#### Acceptance Criteria

1. WHEN the Score_Card is rendered, THE Dashboard SHALL display the Financial_Health_Score as a large numeric value
2. THE Dashboard SHALL display the Risk_Band with color coding (green for Low, yellow for Medium, red for High)
3. THE Dashboard SHALL display a gauge visualization showing the score position on a 0-100 scale
4. THE Dashboard SHALL display the computation timestamp

### Requirement 13: Data Sources Dashboard View

**User Story:** As a bank analyst, I want to view aggregated data from all sources, so that I can verify the underlying data quality.

#### Acceptance Criteria

1. WHEN the Data_Sources_View is rendered, THE Dashboard SHALL display data from GST_Adapter, UPI_Adapter, Account_Aggregator_Adapter, and EPFO_Adapter
2. THE Dashboard SHALL organize data by source in separate panels
3. THE Dashboard SHALL indicate data freshness with timestamps
4. IF a Data_Adapter failed, THEN THE Dashboard SHALL display an error indicator for that source

### Requirement 14: Trend Analysis Dashboard View

**User Story:** As a bank analyst, I want to see score trends over time, so that I can identify improving or declining financial health patterns.

#### Acceptance Criteria

1. WHEN the Trend_Analysis_View is rendered, THE Dashboard SHALL display a line chart of Financial_Health_Score over time
2. THE Dashboard SHALL display Risk_Band transitions as color-coded segments
3. THE Dashboard SHALL allow date range selection for trend visualization
4. THE Dashboard SHALL display at least 6 months of historical data when available

### Requirement 15: Risk Factors Dashboard View

**User Story:** As a bank analyst, I want to see which factors contributed to the risk classification, so that I can understand the key drivers of the assessment.

#### Acceptance Criteria

1. WHEN the Risk_Factors_View is rendered, THE Dashboard SHALL display SHAP_Values as a horizontal bar chart
2. THE Dashboard SHALL rank features by absolute SHAP_Values in descending order
3. THE Dashboard SHALL use color coding to distinguish positive (green) and negative (red) contributions
4. THE Dashboard SHALL display feature values alongside their SHAP_Values

### Requirement 16: Recommendations Dashboard View

**User Story:** As a bank analyst, I want actionable recommendations for MSMEs, so that I can provide guidance for improving their financial health.

#### Acceptance Criteria

1. WHEN the Recommendations_View is rendered, THE Dashboard SHALL generate recommendations based on SHAP_Values and feature values
2. WHERE the Risk_Band is Medium or High, THE Dashboard SHALL prioritize recommendations addressing the top negative SHAP_Values
3. THE Dashboard SHALL display at least 3 and at most 5 recommendations
4. THE Dashboard SHALL categorize recommendations by improvement area (revenue, liquidity, compliance, employment)

### Requirement 17: Dashboard Navigation

**User Story:** As a bank analyst, I want to navigate between dashboard screens, so that I can access different views of the MSME financial health data.

#### Acceptance Criteria

1. THE Dashboard SHALL provide navigation controls for switching between Score_Card, Data_Sources_View, Trend_Analysis_View, Risk_Factors_View, and Recommendations_View
2. WHEN a navigation control is activated, THE Dashboard SHALL render the selected view
3. THE Dashboard SHALL maintain the current MSME context across view transitions
4. THE Dashboard SHALL indicate the currently active view with visual highlighting

### Requirement 18: MSME Search and Selection

**User Story:** As a bank analyst, I want to search for and select an MSME, so that I can view their financial health assessment.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a search input for MSME identification
2. WHEN an MSME identifier is submitted, THE Dashboard SHALL request score computation via the API_Layer
3. WHILE score computation is in progress, THE Dashboard SHALL display a loading indicator
4. WHEN score computation completes, THE Dashboard SHALL render the Score_Card view with results

### Requirement 19: Error Handling and User Feedback

**User Story:** As a bank analyst, I want clear error messages, so that I can understand when and why score computation fails.

#### Acceptance Criteria

1. IF the API_Layer returns an error, THEN THE Dashboard SHALL display a user-friendly error message
2. IF partial data is available due to Data_Adapter failures, THE Dashboard SHALL display the results with warnings about missing data sources
3. THE Dashboard SHALL provide retry functionality for failed operations
4. THE Dashboard SHALL log errors for debugging without exposing sensitive details to the user

### Requirement 20: Responsive Dashboard Design

**User Story:** As a bank analyst, I want the dashboard to work on different screen sizes, so that I can access it from various devices.

#### Acceptance Criteria

1. THE Dashboard SHALL render correctly on desktop screens with width greater than 1024 pixels
2. THE Dashboard SHALL render correctly on tablet screens with width between 768 and 1024 pixels
3. WHEN the screen width is below 768 pixels, THE Dashboard SHALL use a mobile-optimized layout
4. THE Dashboard SHALL maintain readability and functionality across all supported screen sizes

### Requirement 21: What-If Simulator

**User Story:** As a bank analyst, I want to adjust key input features and see the Financial_Health_Score recompute in real time, so that I can understand improvement paths for a given MSME.

#### Acceptance Criteria

1. WHEN the What-If_Simulator is rendered, THE Dashboard SHALL display adjustable controls for key features including GST filing regularity, UPI transaction volume, liquidity ratio, and employment stability
2. WHEN a feature value is modified, THE What-If_Simulator SHALL recompute the Financial_Health_Score and Risk_Band without retrieving new data from Data_Adapters
3. WHEN recomputation completes, THE What-If_Simulator SHALL display the delta between the simulated score and the original score
4. THE What-If_Simulator SHALL provide a reset control that restores all features to their original values
5. THE What-If_Simulator SHALL update the score visualization within 100 milliseconds of feature adjustment

### Requirement 22: Ecosystem Integration Panel

**User Story:** As a bank analyst, I want a stubbed integration panel simulating Account Aggregator consent flow, ULI score publishing, and OCEN lender matching, so that the system demonstrates ecosystem interoperability even without live sandbox access.

#### Acceptance Criteria

1. WHEN the Ecosystem_Integration_Panel is rendered, THE Dashboard SHALL display simulated Account Aggregator consent request controls
2. WHEN a consent request action is triggered, THE Ecosystem_Integration_Panel SHALL simulate a consent approval flow and return a mock consent token within 500 milliseconds
3. THE Ecosystem_Integration_Panel SHALL provide a publish score action that simulates publishing the Financial_Health_Score to ULI
4. WHEN the publish score action is triggered, THE Ecosystem_Integration_Panel SHALL return a mock confirmation message with a simulated transaction identifier
5. THE Ecosystem_Integration_Panel SHALL display a mock list of 2 to 3 matched lenders based on the current Risk_Band
6. WHERE the Risk_Band is Low, THE Ecosystem_Integration_Panel SHALL display lenders offering prime rates
7. WHERE the Risk_Band is Medium or High, THE Ecosystem_Integration_Panel SHALL display lenders offering higher-risk lending products

### Requirement 23: Synthetic Training Dataset Generation

**User Story:** As a data scientist, I want a synthetic MSME dataset generator producing labeled profiles with realistic feature-target relationships, so that the ML_Classifier has data to train on in the absence of real historical records.

#### Acceptance Criteria

1. THE Synthetic_Dataset_Generator SHALL produce between 500 and 1000 MSME profiles
2. THE Synthetic_Dataset_Generator SHALL assign Risk_Band labels with distribution of approximately 50% Low risk, 30% Medium risk, and 20% High risk
3. THE Synthetic_Dataset_Generator SHALL generate feature values with realistic correlations to Risk_Band labels
4. WHERE a profile is labeled Low risk, THE Synthetic_Dataset_Generator SHALL generate features indicating strong revenue stability, high transaction volumes, healthy liquidity ratios, and consistent employment
5. WHERE a profile is labeled High risk, THE Synthetic_Dataset_Generator SHALL generate features indicating poor revenue stability, low transaction volumes, weak liquidity ratios, or inconsistent employment
6. THE Synthetic_Dataset_Generator SHALL introduce realistic noise and variability to avoid perfect feature-label correlations
7. THE Synthetic_Dataset_Generator SHALL export profiles in a format compatible with the Feature_Engineering_Pipeline and ML_Classifier training process

### Requirement 24: Score History Persistence

**User Story:** As a data analyst, I want Financial_Health_Score computations to be persisted over time, so that the Trend_Analysis_View can display historical score progression.

#### Acceptance Criteria

1. WHEN the API_Layer completes score computation, THE Score_History_Store SHALL persist the Financial_Health_Score, Risk_Band, computation timestamp, and MSME identifier
2. THE Score_History_Store SHALL maintain at least 6 months of historical score records per MSME
3. WHEN the Trend_Analysis_View requests historical data, THE Score_History_Store SHALL retrieve all score records for the specified MSME and date range
4. THE Score_History_Store SHALL index records by MSME identifier and timestamp for efficient retrieval
5. WHEN storage capacity limits are reached, THE Score_History_Store SHALL archive records older than 12 months

### Requirement 25: User Authentication and Session Management

**User Story:** As a bank analyst, I want to securely log in to the system using my email and password, so that only authorized users can access MSME financial health data.

#### Acceptance Criteria

1. THE Dashboard SHALL provide a login screen requiring email and password before accessing any MSME data
2. THE Dashboard SHALL provide a signup screen allowing new bank analysts to create accounts with email and password
3. WHEN a user successfully logs in, THE system SHALL create an authenticated session using Supabase Auth with JWT token
4. THE system SHALL automatically refresh the session token before expiration to maintain continuous access
5. THE system SHALL persist the session across browser refreshes and return visits
6. WHEN a user clicks logout, THE system SHALL terminate the session and return to the login screen
7. ALL API endpoints SHALL require a valid authenticated session token in the Authorization header
8. WHEN an API request lacks a valid session token, THE API_Layer SHALL return a 401 Unauthorized response
9. THE system SHALL treat all authenticated users as bank analysts with equal access to all features

