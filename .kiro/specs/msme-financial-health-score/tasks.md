# Implementation Plan: MSME Financial Health Score System

## Overview

This implementation plan breaks down the MSME Financial Health Score system into discrete, actionable coding tasks. The system will be implemented in **Python** with a Flask REST API backend, React frontend, PostgreSQL database, and scikit-learn for ML classification.

The implementation follows an incremental approach: infrastructure → data adapters → feature engineering → scoring engines → API → frontend → ecosystem integration.

## Tasks

- [x] 1. Set up project structure and core infrastructure
  - Create Python project structure with virtual environment
  - Initialize Flask application with basic configuration
  - Set up Supabase project and obtain URL and API key
  - Enable Supabase Auth (email/password provider) in Supabase dashboard
  - Install Supabase Python client (supabase-py) in backend
  - Install Supabase JS client (@supabase/supabase-js) in frontend
  - Configure environment variables (SUPABASE_URL, SUPABASE_KEY, SUPABASE_JWT_SECRET for backend, mock/production modes)
  - Create React frontend project with routing
  - _Requirements: All, 25.1, 25.2_

- [x] 2. Implement data adapter layer
  - [x] 2.1 Create base DataAdapter interface and abstract class
    - Define abstract methods: fetch_data(), normalize_data(), set_mode(), get_status()
    - Implement common adapter status tracking
    - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.3_
  
  - [x] 2.2 Implement GST adapter with mock data generation
    - Create GSTAdapter class extending base adapter
    - Implement mock data generation with realistic revenue patterns
    - Implement normalization to GSTNormalizedData format
    - Add 50-200ms latency simulation and 95% success rate
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.1, 5.2, 5.4_
  
  - [x] 2.3 Implement UPI adapter with mock data generation
    - Create UPIAdapter class extending base adapter
    - Implement mock transaction data with volume and frequency patterns
    - Implement normalization to UPINormalizedData format
    - Add latency simulation and realistic variability
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 5.1, 5.2, 5.4_
  
  - [x] 2.4 Implement Account Aggregator adapter with mock data
    - Create AAAdapter class extending base adapter
    - Implement mock bank account data with balance and transaction patterns
    - Implement normalization to AANormalizedData format
    - Add latency simulation
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 5.1, 5.2, 5.4_
  
  - [x] 2.5 Implement EPFO adapter with mock data generation
    - Create EPFOAdapter class extending base adapter
    - Implement mock employee and contribution data
    - Implement normalization to EPFONormalizedData format
    - Add latency simulation
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.4_

- [x] 3. Implement feature engineering pipeline
  - [x] 3.1 Create FeatureEngineeringPipeline class
    - Define interface: compute_features(), impute_missing_features(), normalize_features()
    - Implement data aggregation from all adapters
    - _Requirements: 6.1_
  
  - [x] 3.2 Implement feature computation algorithms
    - Implement revenue_stability calculation (1 - coefficient of variation)
    - Implement transaction_velocity composite metric
    - Implement liquidity_ratio calculation
    - Implement employment_consistency composite metric
    - Implement compliance_score calculation
    - Implement growth_indicator composite metric
    - _Requirements: 6.2_
  
  - [x] 3.3 Implement missing data handling and normalization
    - Implement default imputation strategies for each feature
    - Implement min-max normalization to 0-1 scale
    - Handle partial data scenarios
    - _Requirements: 6.3, 6.4_

- [x] 4. Implement composite weighted scoring model
  - [x] 4.1 Create CompositeWeightedModel class
    - Define sector weight configurations (Trader, Manufacturer, Services)
    - Implement compute_score() method with weighted aggregation
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [x] 4.2 Implement weight adjustment for missing features
    - Implement proportional weight redistribution
    - Handle cases where features are unavailable
    - _Requirements: 7.7_
  
  - [x] 4.3 Implement score calculation returning 0-100 range
    - Aggregate weighted features into final composite score
    - Ensure score bounds (0-100)
    - _Requirements: 7.6_

- [x] 5. Checkpoint - Verify data pipeline
  - Test all adapters in mock mode
  - Verify feature engineering with sample data
  - Verify composite scoring with all three sectors
  - Ensure all tests pass, ask the user if questions arise

- [x] 6. Implement synthetic dataset generation for ML training
  - [x] 6.1 Create SyntheticDatasetGenerator class
    - Implement generate_synthetic_profile() with risk-correlated features
    - Generate Low risk profiles (50%): high stability, high liquidity, high compliance
    - Generate Medium risk profiles (30%): moderate indicators with some weaknesses
    - Generate High risk profiles (20%): low stability, poor liquidity, weak compliance
    - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5_
  
  - [x] 6.2 Add realistic noise and correlations to synthetic data
    - Introduce Gaussian noise to avoid perfect correlations
    - Implement cross-feature correlations (e.g., high revenue → high compliance)
    - Distribute profiles across Trader/Manufacturer/Services sectors
    - _Requirements: 23.6_
  
  - [x] 6.3 Implement dataset export and generation script
    - Create generate_dataset.py script producing exactly 1000 profiles
    - Export to CSV/JSON format compatible with scikit-learn
    - _Requirements: 23.7_

- [x] 6.5 Curate 4 demo MSME profiles for live demonstrations
  - Create demo profile 1: "DEMO-LOW-001" - clearly Low risk (Trader, score ~85)
    - High revenue stability (0.88), strong liquidity (0.92), excellent compliance (0.95)
    - Use for showcasing healthy MSME scoring
  - Create demo profile 2: "DEMO-HIGH-001" - clearly High risk (Services, score ~28)
    - Poor revenue stability (0.22), weak liquidity (0.18), low compliance (0.35)
    - Use for showcasing distressed MSME identification
  - Create demo profile 3: "DEMO-MED-001" - Medium/borderline with interesting SHAP story (Manufacturer, score ~58)
    - Mixed indicators: decent revenue (0.68) but poor transaction velocity (0.35) and declining employment (0.42)
    - Strong negative SHAP values for transaction velocity and employment showing clear improvement paths
  - Create demo profile 4: "DEMO-PARTIAL-001" - partial data scenario (Trader, score computed with 3/4 adapters)
    - GST, UPI, AA data available; EPFO adapter simulates failure
    - Demonstrates graceful degradation with adjusted weights and missing source warnings
  - Store demo profiles as fixtures with memorable IDs for easy access during demos
  - _Requirements: 5.1, 10.5, 19.2_

- [x] 7. Implement ML classifier and training pipeline
  - [x] 7.1 Create MLClassifier class with scikit-learn
    - Implement predict() method returning risk band and confidence
    - Implement load_model() to load pre-trained classifier
    - Use Random Forest or Gradient Boosting classifier
    - _Requirements: 8.1, 8.2, 8.4_
  
  - [x] 7.2 Implement SHAP explainability integration
    - Integrate SHAP library with trained model
    - Implement explain_prediction() returning SHAP values for all features
    - Rank features by absolute SHAP contribution
    - _Requirements: 8.3, 9.1, 9.2, 9.3, 9.4_
  
  - [x] 7.3 Create offline model training script
    - Create train_model.py script with 70/30 train/validation split
    - Implement hyperparameter tuning with grid search
    - Train Random Forest classifier on synthetic dataset
    - Train SHAP TreeExplainer on trained model
    - Save model artifacts to models/ directory: classifier_v1.pkl, explainer_v1.pkl, training_metrics_v1.json
    - _Requirements: 8.1, 8.2_

- [x] 8. Implement scoring engine orchestration
  - [x] 8.1 Create ScoringEngine class
    - Implement gather_data() orchestrating all adapter calls
    - Implement compute_score() coordinating feature engineering, composite model, and ML classifier
    - Handle partial data scenarios with missing source tracking
    - _Requirements: 10.1, 10.2, 10.3, 10.5_
  
  - [x] 8.2 Integrate composite model and ML classifier
    - Call CompositeWeightedModel for weighted score
    - Call MLClassifier for risk band prediction and SHAP values
    - Aggregate results into ScoreResult object
    - _Requirements: 10.4_

- [x] 8.5 Implement authentication middleware for Flask API
  - [x] 8.5.1 Create @require_auth decorator for route protection
    - Extract JWT token from Authorization header (Bearer scheme)
    - Validate token with Supabase Auth using supabase.auth.get_user(token)
    - Return 401 Unauthorized if token is missing, malformed, or invalid
    - Attach authenticated user info to Flask request context
    - _Requirements: 25.7, 25.8_
  
  - [x] 8.5.2 Apply @require_auth to all API endpoints
    - Protect POST /api/scores
    - Protect GET /api/scores/:msmeId
    - Protect GET /api/scores/:msmeId/history
    - Protect POST /api/simulate
    - Protect POST /api/ecosystem/consent
    - Protect POST /api/ecosystem/publish
    - Protect GET /api/ecosystem/lenders
    - _Requirements: 25.7, 25.8_

- [x] 9. Implement database layer for score history
  - [x] 9.1 Create Supabase table for score_history
    - Use Supabase table editor or migration SQL to create score_history table
    - Define fields: id (uuid, primary key), msme_id (text), composite_score (numeric), risk_band (text), ml_confidence_low/medium/high (numeric), features (jsonb), shap_values (jsonb), missing_sources (text[]), computed_at (timestamp), sector (text)
    - Create indexes via Supabase: idx_msme_computed on (msme_id, computed_at DESC), idx_computed_at on (computed_at)
    - Enable Row Level Security (RLS) policies if needed for production
    - _Requirements: 24.1, 24.4_
  
  - [x] 9.2 Implement ScoreHistoryStore class using Supabase client
    - Initialize Supabase client with environment variables (SUPABASE_URL, SUPABASE_KEY)
    - Implement save() method using supabase.table('score_history').insert()
    - Implement retrieve() method to fetch most recent score by MSME ID using .select().eq().order().limit()
    - Implement retrieve_history() method with date range filtering using .select().eq().gte().lte()
    - _Requirements: 24.1, 24.3_
  
  - [x] 9.3 Implement retention policy and archival logic
    - Ensure minimum 6 months retention
    - Implement archival strategy for records older than 12 months (manual or scheduled via Supabase functions)
    - _Requirements: 24.2, 24.5_

- [x] 10. Implement REST API endpoints
  - [x] 10.1 Implement POST /api/scores endpoint
    - Parse request with MSME identifiers and sector
    - Call ScoringEngine.compute_score()
    - Persist result to ScoreHistoryStore
    - Return ScoreResult with 200 status or error with appropriate status code
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 10.2 Implement GET /api/scores/:msmeId endpoint
    - Retrieve most recent score from ScoreHistoryStore
    - Return 404 if no score found with descriptive message
    - Return ScoreResult with 200 status if found
    - _Requirements: 11.1, 11.2, 11.3_
  
  - [x] 10.3 Implement GET /api/scores/:msmeId/history endpoint
    - Parse date range query parameters (startDate, endDate)
    - Default to 6 months history if no date range specified
    - Retrieve historical records from ScoreHistoryStore
    - Return array of ScoreHistoryRecord objects
    - _Requirements: 11.4, 14.4_
  
  - [x] 10.4 Implement POST /api/simulate endpoint for What-If simulator
    - Parse request with adjusted features and sector
    - Compute simulated score using CompositeWeightedModel (no adapter calls)
    - Return simulated score, risk band, and delta from original
    - Respond within 100ms for real-time simulation
    - _Requirements: 21.2, 21.3, 21.5_

- [x] 11. Checkpoint - Verify backend API
  - Test all API endpoints with curl or Postman
  - Verify database persistence and retrieval
  - Test partial failure scenarios
  - Ensure all tests pass, ask the user if questions arise

- [x] 12. Implement ecosystem integration API endpoints
  - [x] 12.1 Implement POST /api/ecosystem/consent endpoint
    - Simulate Account Aggregator consent flow with <500ms response
    - Return mock consent token and approval timestamp
    - _Requirements: 22.1, 22.2_
  
  - [x] 12.2 Implement POST /api/ecosystem/publish endpoint
    - Simulate ULI score publishing
    - Return mock transaction ID and confirmation message
    - _Requirements: 22.3, 22.4_
  
  - [x] 12.3 Implement GET /api/ecosystem/lenders endpoint
    - Accept riskBand query parameter (Low/Medium/High)
    - Return 2-3 mock lender matches based on risk band
    - Low risk: prime rates (8-10%), Medium: standard rates (12-16%), High: high-risk rates (18-24%)
    - _Requirements: 22.5, 22.6, 22.7_

- [x] 13. Implement React frontend foundation
  - [x] 13.1 Set up React project with routing and authentication
    - Create React app with React Router
    - Set up public routes: /login, /signup
    - Set up protected routes requiring authentication: /dashboard (all 7 views)
    - Create route structure: /dashboard/score-card, /dashboard/data-sources, /dashboard/trends, /dashboard/risk-factors, /dashboard/recommendations, /dashboard/what-if, /dashboard/ecosystem
    - Implement responsive layout with breakpoints (desktop >1024px, tablet 768-1024px, mobile (<768px)
    - _Requirements: 17.1, 17.2, 17.3, 17.4, 20.1, 20.2, 20.3, 20.4, 25.1_
  
  - [x] 13.2 Implement authentication context and Supabase Auth integration
    - Create AuthContext and AuthProvider wrapping the app
    - Initialize Supabase client with SUPABASE_URL and SUPABASE_KEY
    - Implement signUp() function calling supabase.auth.signUp()
    - Implement signIn() function calling supabase.auth.signInWithPassword()
    - Implement signOut() function calling supabase.auth.signOut()
    - Implement session state management with useState/useEffect
    - Listen to auth state changes with supabase.auth.onAuthStateChange()
    - Persist session across page reloads by checking supabase.auth.getSession() on mount
    - Automatically refresh tokens using Supabase's built-in refresh mechanism
    - _Requirements: 25.2, 25.3, 25.4, 25.5, 25.9_
  
  - [x] 13.3 Build Login and Signup screens
    - Create Login component at /login with email/password form
    - Create Signup component at /signup with email/password form and confirmation
    - Display validation errors (invalid credentials, weak password, email already exists)
    - Show loading states during authentication
    - Redirect to /dashboard on successful login/signup
    - Include "Don't have an account? Sign up" link on Login, and vice versa
    - _Requirements: 25.1, 25.2_
  
  - [x] 13.4 Implement ProtectedRoute wrapper component
    - Create ProtectedRoute component checking for valid session
    - Redirect to /login if session is null or expired
    - Allow access to child routes if session is valid
    - Wrap all /dashboard/* routes with ProtectedRoute
    - _Requirements: 25.1, 25.7_
  
  - [x] 13.5 Implement API integration layer with auth token injection
    - Create API client with Axios for all backend endpoints
    - Add Axios interceptor to inject Authorization: Bearer <token> header on every request
    - Extract token from Supabase session: session.access_token
    - Implement 401 response handler: redirect to /login on authentication failure
    - Implement error handling and retry logic
    - Implement loading states
    - _Requirements: 19.1, 19.3, 25.7, 25.8_
  
  - [x] 13.6 Add logout functionality to dashboard header
    - Add logout button/icon in dashboard navigation header using Lucide React icon
    - Call AuthContext.signOut() on click
    - Clear local state and redirect to /login
    - _Requirements: 25.6_
  
  - [x] 13.7 Implement MSME search and selection
    - Create search input component in authenticated dashboard
    - Implement score computation request on MSME ID submission
    - Show loading indicator during computation
    - Navigate to ScoreCard view on completion
    - _Requirements: 18.1, 18.2, 18.3, 18.4_
  
  - [x] 13.8 Define design system and establish visual identity
    - Define color palette:
      - Primary: Navy (#1e3a5f) and Teal (#14b8a6) for branding
      - Low risk: Emerald Green (#10b981)
      - Medium risk: Amber (#f59e0b)
      - High risk: Rose Red (#f43f5e)
      - Neutrals: Gray scale for text and backgrounds
    - Install and configure Lucide React for all icon usage throughout the app
    - Define typography: Use distinctive header font (e.g., "Inter" or "Outfit" from Google Fonts) for headings, system font stack for body text
    - Create global CSS/styled-components theme with color palette, typography, spacing, and shadows
    - _Requirements: 12.2, 20.1, 20.2, 20.3, 20.4_
  
  - [x] 13.9 Build custom SVG arc gauge component for Score Card
    - Create reusable SVG-based semi-circular gauge component (not a library dependency)
    - Implement smooth arc rendering with color zones: Rose (0-39), Amber (40-69), Emerald (70-100)
    - Add animated needle/pointer indicating current score position
    - Ensure responsive sizing and smooth animations
    - Make component accessible with ARIA labels and roles
    - _Requirements: 12.3_

- [x] 14. Implement dashboard views
  - [x] 14.1 Implement Score Card component
    - Display large numeric score (0-100) with distinctive header font
    - Integrate custom SVG arc gauge component with color zones (Rose 0-39, Amber 40-69, Emerald 70-100)
    - Display risk band with color-coded badge using design system colors (Emerald/Amber/Rose)
    - Display computation timestamp
    - Use Lucide React icons for visual elements
    - _Requirements: 12.1, 12.2, 12.3, 12.4_
  
  - [x] 14.2 Implement Data Sources View component
    - Create 4 panels for GST, UPI, AA, EPFO data
    - Display key metrics from each source
    - Show data freshness timestamps
    - Display error indicators for failed sources
    - Use responsive grid layout (2x2 desktop, stacked mobile)
    - _Requirements: 13.1, 13.2, 13.3, 13.4_
  
  - [x] 14.3 Implement Trend Analysis View component
    - Create line chart for score history over time
    - Display color-coded risk band segments on chart
    - Implement date range selector (default: 6 months)
    - Show summary statistics below chart
    - _Requirements: 14.1, 14.2, 14.3, 14.4_
  
  - [x] 14.4 Implement Risk Factors View component
    - Create horizontal bar chart for SHAP values
    - Rank features by absolute SHAP contribution
    - Use color coding: green (positive), red (negative)
    - Display feature values alongside SHAP bars
    - _Requirements: 15.1, 15.2, 15.3, 15.4_
  
  - [x] 14.5 Implement Recommendations View component
    - Generate 3-5 recommendations based on SHAP values and feature values
    - Prioritize recommendations for Medium/High risk bands addressing negative SHAP values
    - Categorize by improvement area (revenue, liquidity, compliance, employment)
    - Display as priority-ordered cards with color coding
    - _Requirements: 16.1, 16.2, 16.3, 16.4_

- [x] 15. Implement What-If Simulator component
  - [x] 15.1 Create simulator UI with feature adjustment controls
    - Implement sliders for all 6 features (revenue_stability, transaction_velocity, liquidity_ratio, employment_consistency, compliance_score, growth_indicator)
    - Display original vs simulated score comparison
    - Show delta calculation between scores
    - _Requirements: 21.1, 21.3_
  
  - [x] 15.2 Implement real-time score recalculation
    - Call POST /api/simulate on feature adjustment
    - Update display within 100ms
    - Highlight risk band changes
    - Visual highlighting for adjusted features
    - _Requirements: 21.2, 21.5_
  
  - [x] 15.3 Implement reset functionality
    - Add reset button to restore original feature values
    - Clear all adjustments and recalculate
    - _Requirements: 21.4_

- [x] 16. Implement Ecosystem Integration Panel component
  - [x] 16.1 Create Account Aggregator consent simulation UI
    - Display consent request controls
    - Implement mock consent approval flow with <500ms response
    - Display mock consent token and timestamp on approval
    - _Requirements: 22.1, 22.2_
  
  - [x] 16.2 Create ULI publishing simulation UI
    - Implement publish score action button
    - Display mock transaction ID on success
    - Show confirmation message and timestamp
    - _Requirements: 22.3, 22.4_
  
  - [x] 16.3 Create OCEN lender matching UI
    - Display 2-3 matched lenders based on current risk band
    - Show lender details: name, product type, interest rate, max amount
    - Update lender matches when risk band changes
    - Low risk: prime rate lenders, Medium/High: higher-risk lenders
    - _Requirements: 22.5, 22.6, 22.7_

- [x] 17. Implement error handling and user feedback
  - [x] 17.1 Implement error message display in dashboard
    - Show user-friendly error messages on API failures
    - Display warnings for partial data availability
    - Indicate missing data sources in relevant views
    - _Requirements: 19.1, 19.2_
  
  - [x] 17.2 Implement loading states and retry functionality
    - Show loading indicators during API calls
    - Implement retry button for failed operations
    - _Requirements: 19.3_

- [ ] 18. Final checkpoint and integration testing
  - Test complete end-to-end flow: MSME search → score computation → all 7 views
  - Verify responsive design on desktop, tablet, mobile
  - Test partial failure scenarios with missing adapters
  - Test What-If simulator with various feature adjustments
  - Test ecosystem integration panel simulations
  - Verify 6-month historical data display in Trend Analysis
  - Ensure all tests pass, ask the user if questions arise

- [ ] 19. Documentation and deployment preparation
  - Create README.md with setup instructions
  - Document API endpoints with examples
  - Document environment variables and configuration
  - Create deployment guide for backend and frontend
  - _Requirements: All_

## Notes

- All tasks build incrementally on previous steps
- Implementation uses Python/Flask backend, React frontend, PostgreSQL database
- Mock adapters simulate 50-200ms latency with 95% success rate
- ML training is offline - produces model artifacts loaded at runtime
- Checkpoints ensure incremental validation and user feedback opportunities
- Frontend implements 7 views with responsive design
- Score history retention: 6 months minimum, 12 months before archival
