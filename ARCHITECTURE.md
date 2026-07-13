# System Architecture Diagrams

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MSME BUSINESS ENTITY                            │
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ GST Filings │  │     UPI     │  │    Bank     │  │    EPFO     │       │
│  │  & Returns  │  │ Transactions│  │  Accounts   │  │ Enrollment  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└───────────┬──────────────┬────────────────┬────────────────┬───────────────┘
            │              │                │                │
            │ Government   │ Payment Rails  │ AA Framework   │ Social Security
            │ APIs         │                │                │ Portal
            ↓              ↓                ↓                ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA ADAPTER LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │     GST      │  │     UPI      │  │     AA       │  │    EPFO      │   │
│  │   Adapter    │  │   Adapter    │  │   Adapter    │  │   Adapter    │   │
│  │              │  │              │  │              │  │              │   │
│  │ • Revenue    │  │ • Txn Vol    │  │ • Cash Flow  │  │ • Headcount  │   │
│  │ • Filing     │  │ • Velocity   │  │ • Balances   │  │ • Payroll    │   │
│  │ • Compliance │  │ • Patterns   │  │ • Liquidity  │  │ • Turnover   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
└───────────┬──────────────┬────────────────┬────────────────┬───────────────┘
            │              │                │                │
            └──────────────┴────────────────┴────────────────┘
                                    │ Raw data streams
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      FEATURE ENGINEERING PIPELINE                            │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Raw Data Transformation                                           │     │
│  │  • Aggregate time-series data                                      │     │
│  │  • Calculate statistical metrics (mean, std, trends)               │     │
│  │  • Normalize to 0-1 scale                                          │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                     │
│  │   Revenue    │  │ Transaction  │  │  Liquidity   │                     │
│  │  Stability   │  │  Velocity    │  │    Ratio     │                     │
│  │   (0-1)      │  │   (0-1)      │  │   (0-1)      │                     │
│  └──────────────┘  └──────────────┘  └──────────────┘                     │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                     │
│  │ Employment   │  │ Compliance   │  │   Growth     │                     │
│  │ Consistency  │  │    Score     │  │  Indicator   │                     │
│  │   (0-1)      │  │   (0-1)      │  │   (0-1)      │                     │
│  └──────────────┘  └──────────────┘  └──────────────┘                     │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │ Normalized feature vector
                            ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SCORING ENGINE                                     │
│                                                                              │
│  ┌─────────────────────────────────┐  ┌──────────────────────────────────┐ │
│  │  Composite Weighted Model       │  │  ML Risk Classifier              │ │
│  │                                  │  │                                  │ │
│  │  Score = Σ(feature × weight)    │  │  Random Forest                   │ │
│  │                                  │  │  • 100 estimators                │ │
│  │  Sector Weights:                 │  │  • Max depth: 10                 │ │
│  │  ┌────────────────────────────┐ │  │  • Min samples: 5                │ │
│  │  │ Trader    │ Revenue: 0.25  │ │  │                                  │ │
│  │  │           │ Txn Vel: 0.20  │ │  │  Input: 6 features               │ │
│  │  │           │ Liquidity: 0.20│ │  │  Output: Risk Band + Confidence  │ │
│  │  ├───────────┼────────────────┤ │  │                                  │ │
│  │  │ Mfg       │ Revenue: 0.30  │ │  │  ┌──────────────────────────┐   │ │
│  │  │           │ Growth: 0.20   │ │  │  │ SHAP Explainer           │   │ │
│  │  │           │ Employ: 0.15   │ │  │  │                          │   │ │
│  │  ├───────────┼────────────────┤ │  │  │ • TreeExplainer          │   │ │
│  │  │ Service   │ Employ: 0.25   │ │  │  │ • Feature attributions   │   │ │
│  │  │           │ Txn Vel: 0.20  │ │  │  │ • Base value + deltas    │   │ │
│  │  │           │ Comply: 0.15   │ │  │  └──────────────────────────┘   │ │
│  │  └────────────────────────────┘ │  │                                  │ │
│  │                                  │  │                                  │ │
│  │  Output: Score (0-100)           │  │  Output: Risk + Confidence       │ │
│  └─────────────────────────────────┘  └──────────────────────────────────┘ │
│                            │                         │                       │
│                            └─────────┬───────────────┘                       │
│                                      │                                       │
└──────────────────────────────────────┼───────────────────────────────────────┘
                                       │ Unified assessment
                                       ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ASSESSMENT RESULT AGGREGATION                         │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  ScoreResult Object                                                │     │
│  │  ├── compositeScore: float (0-100)                                 │     │
│  │  ├── riskBand: string ('Low'|'Medium'|'High')                      │     │
│  │  ├── confidence: {low: float, medium: float, high: float}          │     │
│  │  ├── features: {feature_name: normalized_value}                    │     │
│  │  ├── shapValues: {feature_name: shap_impact}                       │     │
│  │  ├── computedAt: timestamp                                         │     │
│  │  └── missingDataSources: [string]                                  │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PERSISTENCE & DELIVERY LAYER                         │
│                                                                              │
│  ┌────────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │  Database (PostgreSQL)         │  │  REST API Endpoints              │  │
│  │                                 │  │                                  │  │
│  │  score_history table:           │  │  POST /api/scores                │  │
│  │  • msme_id                      │  │  → Compute new assessment        │  │
│  │  • composite_score              │  │                                  │  │
│  │  • risk_band                    │  │  GET /api/scores/:msmeId         │  │
│  │  • confidence (JSONB)           │  │  → Retrieve latest score         │  │
│  │  • features (JSONB)             │  │                                  │  │
│  │  • shap_values (JSONB)          │  │  GET /api/scores/:msmeId/history │  │
│  │  • computed_at                  │  │  → Retrieve trend data           │  │
│  │  • sector                       │  │                                  │  │
│  │                                 │  │  POST /api/simulate              │  │
│  │  Indexes: msme_id, computed_at  │  │  → What-if scenario analysis     │  │
│  └────────────────────────────────┘  └──────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACES                                   │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Credit Officer Dashboard                                          │     │
│  │  ┌──────────────────────────────────────────────────────────────┐ │     │
│  │  │  Score Card View                                             │ │     │
│  │  │  • Headline score with risk stamp                            │ │     │
│  │  │  • ML confidence distribution                                │ │     │
│  │  │  • Feature breakdown                                         │ │     │
│  │  │  • Download PDF report                                       │ │     │
│  │  └──────────────────────────────────────────────────────────────┘ │     │
│  │  ┌──────────────────────────────────────────────────────────────┐ │     │
│  │  │  Risk Factors View                                           │ │     │
│  │  │  • SHAP waterfall chart                                      │ │     │
│  │  │  • Feature importance ranking                                │ │     │
│  │  │  • Risk factor explanations                                  │ │     │
│  │  └──────────────────────────────────────────────────────────────┘ │     │
│  │  ┌──────────────────────────────────────────────────────────────┐ │     │
│  │  │  Trend Analysis View                                         │ │     │
│  │  │  • Historical score chart                                    │ │     │
│  │  │  • Feature evolution over time                               │ │     │
│  │  │  • Risk band transitions                                     │ │     │
│  │  └──────────────────────────────────────────────────────────────┘ │     │
│  │  ┌──────────────────────────────────────────────────────────────┐ │     │
│  │  │  What-If Simulator                                           │ │     │
│  │  │  • Adjustable feature sliders                                │ │     │
│  │  │  • Real-time score recalculation                             │ │     │
│  │  │  • Impact visualization                                      │ │     │
│  │  └──────────────────────────────────────────────────────────────┘ │     │
│  │  ┌──────────────────────────────────────────────────────────────┐ │     │
│  │  │  Recommendations View                                        │ │     │
│  │  │  • Prioritized action items                                  │ │     │
│  │  │  • Expected score improvement                                │ │     │
│  │  │  • Implementation guidance                                   │ │     │
│  │  └──────────────────────────────────────────────────────────────┘ │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Sequence Diagram

```
User            Frontend         API Gateway      Scoring Engine    Adapters      Database
 │                │                  │                  │              │              │
 │ Search MSME    │                  │                  │              │              │
 ├───────────────>│                  │                  │              │              │
 │                │                  │                  │              │              │
 │                │  POST /scores    │                  │              │              │
 │                ├─────────────────>│                  │              │              │
 │                │                  │                  │              │              │
 │                │                  │  Validate Auth   │              │              │
 │                │                  ├──────────────────┤              │              │
 │                │                  │                  │              │              │
 │                │                  │  Fetch Data      │              │              │
 │                │                  ├─────────────────────────────────>│              │
 │                │                  │                  │              │              │
 │                │                  │                  │  GST API     │              │
 │                │                  │                  │<─────────────┤              │
 │                │                  │                  │              │              │
 │                │                  │                  │  UPI API     │              │
 │                │                  │                  │<─────────────┤              │
 │                │                  │                  │              │              │
 │                │                  │                  │  AA API      │              │
 │                │                  │                  │<─────────────┤              │
 │                │                  │                  │              │              │
 │                │                  │                  │  EPFO API    │              │
 │                │                  │                  │<─────────────┤              │
 │                │                  │                  │              │              │
 │                │                  │   Raw Data       │              │              │
 │                │                  │<─────────────────────────────────┤              │
 │                │                  │                  │              │              │
 │                │                  │  Engineer Features               │              │
 │                │                  ├─────────────────>│              │              │
 │                │                  │                  │              │              │
 │                │                  │  Compute Score   │              │              │
 │                │                  ├─────────────────>│              │              │
 │                │                  │                  │              │              │
 │                │                  │  ML Classify     │              │              │
 │                │                  │<─────────────────┤              │              │
 │                │                  │                  │              │              │
 │                │                  │  SHAP Explain    │              │              │
 │                │                  │<─────────────────┤              │              │
 │                │                  │                  │              │              │
 │                │                  │  ScoreResult     │              │              │
 │                │                  │<─────────────────┤              │              │
 │                │                  │                  │              │              │
 │                │                  │  Persist Score                  │              │
 │                │                  ├────────────────────────────────────────────────>│
 │                │                  │                  │              │              │
 │                │  Assessment      │                  │              │              │
 │                │<─────────────────┤                  │              │              │
 │                │                  │                  │              │              │
 │  Score Card    │                  │                  │              │              │
 │<───────────────┤                  │                  │              │              │
 │                │                  │                  │              │              │
```

---

## 3. Component Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION LAYER                               │
│                                                                              │
│  ┌────────────────────┐                        ┌────────────────────────┐   │
│  │   Web Frontend     │                        │    Mobile App          │   │
│  │   (React SPA)      │                        │   (Future)             │   │
│  │                    │                        │                        │   │
│  │  • Authentication  │                        │  • Self-assessment     │   │
│  │  • Search          │                        │  • Notifications       │   │
│  │  • Visualizations  │                        │  • Progress tracking   │   │
│  │  • PDF Export      │                        │                        │   │
│  └────────┬───────────┘                        └───────────┬────────────┘   │
│           │                                                │                │
└───────────┼────────────────────────────────────────────────┼────────────────┘
            │                                                │
            └────────────────────┬───────────────────────────┘
                                 │ HTTPS/JSON
                                 ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY LAYER                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  REST API Server                                                    │    │
│  │                                                                      │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │    │
│  │  │  Auth Middleware │  │  Rate Limiter    │  │  CORS Handler    │ │    │
│  │  │  • JWT Verify    │  │  • Per-user cap  │  │  • Origin check  │ │    │
│  │  │  • Token refresh │  │  • IP throttle   │  │  • Header mgmt   │ │    │
│  │  └──────────────────┘  └──────────────────┘  └──────────────────┘ │    │
│  │                                                                      │    │
│  │  ┌──────────────────────────────────────────────────────────────┐  │    │
│  │  │  Route Handlers                                              │  │    │
│  │  │  • /auth/login                                               │  │    │
│  │  │  • /auth/signup                                              │  │    │
│  │  │  • /scores (POST) - Compute assessment                       │  │    │
│  │  │  • /scores/:msmeId (GET) - Retrieve assessment               │  │    │
│  │  │  • /scores/:msmeId/history (GET) - Trend data                │  │    │
│  │  │  • /simulate (POST) - What-if analysis                       │  │    │
│  │  │  • /health (GET) - Health check                              │  │    │
│  │  └──────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BUSINESS LOGIC LAYER                               │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Scoring Engine (Orchestrator)                                     │     │
│  │                                                                     │     │
│  │  • Coordinates data fetching                                       │     │
│  │  • Invokes feature engineering                                     │     │
│  │  • Calls composite model                                           │     │
│  │  • Calls ML classifier                                             │     │
│  │  • Requests SHAP explanations                                      │     │
│  │  • Aggregates results                                              │     │
│  │  • Handles errors & fallbacks                                      │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  Feature Eng.    │  │  Composite Model │  │  ML Classifier   │          │
│  │  • Aggregation   │  │  • Sector weights│  │  • RandomForest  │          │
│  │  • Normalization │  │  • Score calc    │  │  • SHAP explainer│          │
│  │  • Validation    │  │  • Validation    │  │  • Prediction    │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└───────────────────────────┬─────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA ACCESS LAYER                                  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Adapter Layer (Abstraction Interface)                            │     │
│  │                                                                     │     │
│  │  BaseAdapter:                                                       │     │
│  │  • fetch_data(msme_id, date_range)                                 │     │
│  │  • validate_response()                                             │     │
│  │  • handle_errors()                                                 │     │
│  │  • cache_results()                                                 │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ GST Adapter │  │ UPI Adapter │  │  AA Adapter │  │ EPFO Adapter│       │
│  │             │  │             │  │             │  │             │       │
│  │ • Returns   │  │ • Txn list  │  │ • Accounts  │  │ • Employees │       │
│  │ • Filings   │  │ • Totals    │  │ • Balances  │  │ • Contrib.  │       │
│  │ • ITC data  │  │ • Patterns  │  │ • Txn flow  │  │ • Turnover  │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│        │                 │                 │                 │              │
│        │  Mock Mode      │  Mock Mode      │  Mock Mode      │  Mock Mode   │
│        │  OR             │  OR             │  OR             │  OR          │
│        │  Production     │  Production     │  Production     │  Production  │
│        ↓                 ↓                 ↓                 ↓              │
└─────────────────────────────────────────────────────────────────────────────┘
         │                 │                 │                 │
         └─────────────────┴─────────────────┴─────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL DATA SOURCES                              │
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │   GST API   │  │   NPCI UPI  │  │  AA Network │  │  EPFO API   │       │
│  │  (Govt)     │  │   Platform  │  │  (RBI)      │  │  (Govt)     │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘

---

## 4. Database Schema Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    score_history                           │
├────────────────────────────────────────────────────────────┤
│  PK  id                    BIGSERIAL                       │
│  FK  msme_id               VARCHAR(100)    [Indexed]       │
│      composite_score       NUMERIC(5,2)                    │
│      risk_band             VARCHAR(20)                     │
│      confidence            JSONB                           │
│      │  └─ { low: 0.2, medium: 0.6, high: 0.2 }          │
│      features              JSONB                           │
│      │  └─ { revenue_stability: 0.75, ... }               │
│      shap_values           JSONB                           │
│      │  └─ { revenue_stability: +0.12, ... }              │
│      sector                VARCHAR(50)                     │
│      computed_at           TIMESTAMP      [Indexed]        │
│      data_sources          JSONB                           │
│      missing_sources       TEXT[]                          │
│      model_version         VARCHAR(20)                     │
│      created_at            TIMESTAMP      DEFAULT NOW()    │
└────────────────────────────────────────────────────────────┘

Indexes:
  • idx_msme_id_computed_at  ON (msme_id, computed_at DESC)
  • idx_risk_band            ON (risk_band)
  • idx_sector               ON (sector)

Query Patterns:
  1. Latest score:     WHERE msme_id = ? ORDER BY computed_at DESC LIMIT 1
  2. Trend analysis:   WHERE msme_id = ? AND computed_at >= ? ORDER BY computed_at
  3. Risk portfolio:   WHERE risk_band = ? AND computed_at >= ?
  4. Sector analysis:  WHERE sector = ? GROUP BY risk_band
```

---

## 5. ML Model Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MACHINE LEARNING PIPELINE                            │
│                                                                              │
│  TRAINING PHASE (Offline)                                                   │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  Synthetic Dataset Generator                                    │        │
│  │  • Generates 10,000 samples across 3 sectors                    │        │
│  │  • Simulates realistic feature correlations                     │        │
│  │  • Assigns risk labels based on composite thresholds            │        │
│  │  • Exports to CSV + JSON                                        │        │
│  └───────────────────────────┬─────────────────────────────────────┘        │
│                              │                                               │
│                              ↓                                               │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  Training Script                                                │        │
│  │                                                                  │        │
│  │  1. Load synthetic dataset                                      │        │
│  │  2. Split: 80% train, 20% test                                  │        │
│  │  3. Train RandomForestClassifier                                │        │
│  │     • n_estimators: 100                                         │        │
│  │     • max_depth: 10                                             │        │
│  │     • min_samples_split: 5                                      │        │
│  │     • class_weight: balanced                                    │        │
│  │  4. Evaluate on test set                                        │        │
│  │  5. Initialize TreeExplainer for SHAP                           │        │
│  │  6. Serialize model artifacts                                   │        │
│  └───────────────────────────┬─────────────────────────────────────┘        │
│                              │                                               │
│                              ↓                                               │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  Model Artifacts (Serialized)                                   │        │
│  │  • classifier_v1.pkl      - Trained Random Forest               │        │
│  │  • explainer_v1.pkl       - SHAP TreeExplainer                  │        │
│  │  • training_metrics_v1.json - Accuracy, precision, recall       │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                              │
│                                                                              │
│  INFERENCE PHASE (Online)                                                   │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  ML Classifier (Runtime)                                        │        │
│  │                                                                  │        │
│  │  Load at startup:                                               │        │
│  │  • RandomForest model                                           │        │
│  │  • SHAP explainer                                               │        │
│  │                                                                  │        │
│  │  predict(features):                                             │        │
│  │  ┌────────────────────────────────────────────────────────┐    │        │
│  │  │ Input: [0.65, 0.72, 0.58, 0.81, 0.90, 0.45]           │    │        │
│  │  │        ↓                                                │    │        │
│  │  │ RandomForest.predict_proba()                           │    │        │
│  │  │        ↓                                                │    │        │
│  │  │ Output: [0.15, 0.65, 0.20]                             │    │        │
│  │  │         (Low, Medium, High probabilities)              │    │        │
│  │  └────────────────────────────────────────────────────────┘    │        │
│  │                                                                  │        │
│  │  explain_prediction(features):                                  │        │
│  │  ┌────────────────────────────────────────────────────────┐    │        │
│  │  │ Input: [0.65, 0.72, 0.58, 0.81, 0.90, 0.45]           │    │        │
│  │  │        ↓                                                │    │        │
│  │  │ explainer.shap_values()                                │    │        │
│  │  │        ↓                                                │    │        │
│  │  │ Output: {                                              │    │        │
│  │  │   revenue_stability: +0.12,                            │    │        │
│  │  │   transaction_velocity: +0.08,                         │    │        │
│  │  │   liquidity_ratio: -0.15,        ← Increases risk      │    │        │
│  │  │   employment_consistency: +0.05,                       │    │        │
│  │  │   compliance_score: +0.03,                             │    │        │
│  │  │   growth_indicator: -0.20        ← Increases risk      │    │        │
│  │  │ }                                                      │    │        │
│  │  └────────────────────────────────────────────────────────┘    │        │
│  └─────────────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘

Model Performance Metrics (Typical):
  • Accuracy:  ~98%
  • Precision: ~97% (Low), ~98% (Medium), ~99% (High)
  • Recall:    ~99% (Low), ~98% (Medium), ~97% (High)
  • F1-Score:  ~98% (weighted average)
```

---

## 6. Security Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY & AUTH FLOW                                 │
│                                                                              │
│  USER AUTHENTICATION                                                         │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌──────────┐                    ┌────────────────┐                         │
│  │  Client  │                    │ Supabase Auth  │                         │
│  │ (Browser)│                    │   Service      │                         │
│  └─────┬────┘                    └────────┬───────┘                         │
│        │                                  │                                  │
│        │  1. POST /auth/signup            │                                  │
│        │  { email, password }             │                                  │
│        ├─────────────────────────────────>│                                  │
│        │                                  │                                  │
│        │  2. Create user account          │                                  │
│        │  3. Generate JWT session         │                                  │
│        │                                  │                                  │
│        │  4. Return access_token +        │                                  │
│        │     refresh_token                │                                  │
│        │<─────────────────────────────────┤                                  │
│        │                                  │                                  │
│        │  5. Store in memory +            │                                  │
│        │     localStorage                 │                                  │
│        │                                  │                                  │
│                                                                              │
│  API REQUEST AUTHENTICATION                                                  │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌──────────┐         ┌─────────────┐         ┌────────────────┐           │
│  │  Client  │         │  API Server │         │ Supabase Auth  │           │
│  └─────┬────┘         └──────┬──────┘         └────────┬───────┘           │
│        │                     │                         │                    │
│        │  1. API Request     │                         │                    │
│        │  Authorization:     │                         │                    │
│        │  Bearer <JWT>       │                         │                    │
│        ├────────────────────>│                         │                    │
│        │                     │                         │                    │
│        │                     │  2. Verify JWT          │                    │
│        │                     ├────────────────────────>│                    │
│        │                     │                         │                    │
│        │                     │  3. Validate signature, │                    │
│        │                     │     expiry, claims      │                    │
│        │                     │                         │                    │
│        │                     │  4. Return user_id      │                    │
│        │                     │<────────────────────────┤                    │
│        │                     │                         │                    │
│        │                     │  5. Process request     │                    │
│        │                     │     with user context   │                    │
│        │                     │                         │                    │
│        │  6. API Response    │                         │                    │
│        │<────────────────────┤                         │                    │
│        │                     │                         │                    │
│                                                                              │
│  TOKEN REFRESH FLOW                                                          │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌──────────┐                    ┌────────────────┐                         │
│  │  Client  │                    │ Supabase Auth  │                         │
│  └─────┬────┘                    └────────┬───────┘                         │
│        │                                  │                                  │
│        │  1. Access token expired         │                                  │
│        │  2. POST /auth/refresh           │                                  │
│        │  { refresh_token }               │                                  │
│        ├─────────────────────────────────>│                                  │
│        │                                  │                                  │
│        │  3. Validate refresh token       │                                  │
│        │  4. Generate new access token    │                                  │
│        │                                  │                                  │
│        │  5. Return new access_token      │                                  │
│        │<─────────────────────────────────┤                                  │
│        │                                  │                                  │
│        │  6. Update stored token          │                                  │
│        │  7. Retry original request       │                                  │
│        │                                  │                                  │
└─────────────────────────────────────────────────────────────────────────────┘

SECURITY LAYERS:
  ┌──────────────────────────────────────────────────────────────┐
  │  1. Transport Security (HTTPS/TLS)                           │
  │     • Encrypted data in transit                              │
  │     • Certificate validation                                 │
  └──────────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────────┐
  │  2. Authentication (JWT)                                     │
  │     • Signed tokens prevent tampering                        │
  │     • Expiry ensures time-limited access                     │
  │     • Refresh tokens enable session extension                │
  └──────────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────────┐
  │  3. Authorization (Role-Based)                               │
  │     • User-specific data access                              │
  │     • Admin vs. user permissions                             │
  │     • MSME owner vs. credit officer roles                    │
  └──────────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────────┐
  │  4. Data Privacy                                             │
  │     • Consent-based data aggregation                         │
  │     • Minimal retention policy                               │
  │     • Anonymization in ML training                           │
  └──────────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────────┐
  │  5. Rate Limiting & DDoS Protection                          │
  │     • Per-user request limits                                │
  │     • IP-based throttling                                    │
  │     • Exponential backoff                                    │
  └──────────────────────────────────────────────────────────────┘
```

---

## 7. Deployment Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION DEPLOYMENT                                │
│                                                                              │
│  CLOUD INFRASTRUCTURE                                                        │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  CDN / Edge Network                                                 │   │
│  │  • Static asset caching                                             │   │
│  │  • SSL/TLS termination                                              │   │
│  │  • DDoS protection                                                  │   │
│  └───────────────────────────┬─────────────────────────────────────────┘   │
│                              │                                              │
│                              ↓                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Load Balancer                                                      │   │
│  │  • Health checks                                                    │   │
│  │  • Traffic distribution                                             │   │
│  │  • SSL offloading                                                   │   │
│  └───────────┬─────────────────────────────┬───────────────────────────┘   │
│              │                             │                                │
│              ↓                             ↓                                │
│  ┌──────────────────────┐      ┌──────────────────────┐                    │
│  │  Frontend Servers    │      │  Frontend Servers    │                    │
│  │  (React App)         │      │  (React App)         │                    │
│  │  • Nginx/Apache      │      │  • Nginx/Apache      │                    │
│  │  • Static files      │      │  • Static files      │                    │
│  └──────────────────────┘      └──────────────────────┘                    │
│              │                             │                                │
│              └─────────────┬───────────────┘                                │
│                            │ API Calls                                      │
│                            ↓                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  API Gateway / Load Balancer                                        │   │
│  │  • Rate limiting                                                    │   │
│  │  • Request validation                                               │   │
│  │  • Logging & monitoring                                             │   │
│  └───────────┬─────────────────────────────┬───────────────────────────┘   │
│              │                             │                                │
│              ↓                             ↓                                │
│  ┌──────────────────────┐      ┌──────────────────────┐                    │
│  │  Backend API         │      │  Backend API         │                    │
│  │  (Flask/Python)      │      │  (Flask/Python)      │                    │
│  │  • Scoring engine    │      │  • Scoring engine    │                    │
│  │  • ML models loaded  │      │  • ML models loaded  │                    │
│  │  • Adapter layer     │      │  • Adapter layer     │                    │
│  └──────────┬───────────┘      └──────────┬───────────┘                    │
│             │                              │                                │
│             └──────────────┬───────────────┘                                │
│                            │                                                │
│                            ↓                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Database Cluster (Supabase PostgreSQL)                            │   │
│  │  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐        │   │
│  │  │   Primary   │─────>│  Replica 1  │      │  Replica 2  │        │   │
│  │  │   (Write)   │      │   (Read)    │      │   (Read)    │        │   │
│  │  └─────────────┘      └─────────────┘      └─────────────┘        │   │
│  │  • Automated backups                                               │   │
│  │  • Point-in-time recovery                                          │   │
│  │  • Connection pooling                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Cache Layer (Redis)                                                │   │
│  │  • Adapter response caching                                         │   │
│  │  • Session storage                                                  │   │
│  │  • Rate limit counters                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Object Storage (S3-compatible)                                     │   │
│  │  • ML model artifacts                                               │   │
│  │  • Training datasets                                                │   │
│  │  • Audit logs                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Monitoring & Logging                                               │   │
│  │  • Application metrics (CPU, memory, latency)                       │   │
│  │  • Request tracing                                                  │   │
│  │  • Error alerting                                                   │   │
│  │  • Business metrics (scores computed, API calls)                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

SCALING STRATEGY:
  ┌──────────────────────────────────────────────────────────────┐
  │  Horizontal Scaling                                          │
  │  • Add backend instances based on CPU/memory                 │
  │  • Auto-scaling groups for peak hours                        │
  │  • Stateless design enables easy scale-out                   │
  └──────────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────────┐
  │  Database Optimization                                       │
  │  • Read replicas for query distribution                      │
  │  • Indexed queries for score history                         │
  │  • Connection pooling                                        │
  └──────────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────────┐
  │  Caching Strategy                                            │
  │  • Adapter responses (15-min TTL)                            │
  │  • Feature engineering results (5-min TTL)                   │
  │  • ML model in-memory (persistent)                           │
  └──────────────────────────────────────────────────────────────┘
```

---

## 8. Feature Engineering Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FEATURE ENGINEERING DETAILED FLOW                         │
│                                                                              │
│  INPUT: Raw adapter data (GST, UPI, AA, EPFO)                               │
│  OUTPUT: Normalized feature vector [0-1]^6                                  │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FEATURE 1: REVENUE STABILITY                                                │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Input: GST monthly returns (12 months)                           │     │
│  │  │                                                                 │     │
│  │  │  [42L, 38L, 45L, 43L, 41L, 46L, 44L, 47L, 43L, 45L, 46L, 48L] │     │
│  │  │                                                                 │     │
│  │  ├─> Calculate:                                                   │     │
│  │  │   • Mean revenue = 44.83L                                      │     │
│  │  │   • Std deviation = 2.89L                                      │     │
│  │  │   • Coefficient of variation = 0.064                           │     │
│  │  │                                                                 │     │
│  │  ├─> Normalize:                                                   │     │
│  │  │   stability = 1 - min(CV / 0.5, 1.0)                           │     │
│  │  │   stability = 1 - min(0.064 / 0.5, 1.0)                        │     │
│  │  │   stability = 0.872                                            │     │
│  │  │                                                                 │     │
│  │  └─> Output: 0.872                                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  FEATURE 2: TRANSACTION VELOCITY                                             │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Input: UPI transactions (30 days)                                │     │
│  │  │                                                                 │     │
│  │  │  Total count: 1,250 transactions                               │     │
│  │  │  Unique customers: 320                                         │     │
│  │  │  Average per day: 41.67 txns                                   │     │
│  │  │                                                                 │     │
│  │  ├─> Calculate:                                                   │     │
│  │  │   • Daily average = 41.67                                      │     │
│  │  │   • Sector benchmark (Trader) = 50 txns/day                    │     │
│  │  │   • Velocity ratio = 41.67 / 50 = 0.833                        │     │
│  │  │                                                                 │     │
│  │  ├─> Normalize:                                                   │     │
│  │  │   velocity = min(ratio, 1.0)                                   │     │
│  │  │   velocity = 0.833                                             │     │
│  │  │                                                                 │     │
│  │  └─> Output: 0.833                                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  FEATURE 3: LIQUIDITY RATIO                                                  │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Input: AA bank account data (3 months)                           │     │
│  │  │                                                                 │     │
│  │  │  Average deposits: ₹18L/month                                  │     │
│  │  │  Average withdrawals: ₹15L/month                               │     │
│  │  │  Current balance: ₹8.5L                                        │     │
│  │  │  Minimum balance: ₹2.5L                                        │     │
│  │  │                                                                 │     │
│  │  ├─> Calculate:                                                   │     │
│  │  │   • Monthly obligation ≈ withdrawals = ₹15L                    │     │
│  │  │   • Liquidity buffer = current / monthly_obligation            │     │
│  │  │   • Liquidity buffer = 8.5 / 15 = 0.567 months                 │     │
│  │  │                                                                 │     │
│  │  ├─> Normalize:                                                   │     │
│  │  │   liquidity = min(buffer / 3.0, 1.0)                           │     │
│  │  │   liquidity = min(0.567 / 3.0, 1.0)                            │     │
│  │  │   liquidity = 0.189                                            │     │
│  │  │                                                                 │     │
│  │  └─> Output: 0.189                                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  FEATURE 4: EMPLOYMENT CONSISTENCY                                           │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Input: EPFO contribution data (12 months)                        │     │
│  │  │                                                                 │     │
│  │  │  Employee count: [24, 24, 25, 25, 26, 26, 25, 26, 27, 27, 28, 28]    │
│  │  │  Contribution regularity: 12/12 months (100%)                  │     │
│  │  │                                                                 │     │
│  │  ├─> Calculate:                                                   │     │
│  │  │   • Headcount growth = (28-24) / 24 = 16.67%                   │     │
│  │  │   • Contribution score = 12/12 = 1.0                           │     │
│  │  │   • Turnover rate = low (stable headcount)                     │     │
│  │  │                                                                 │     │
│  │  ├─> Normalize:                                                   │     │
│  │  │   consistency = 0.7*contribution + 0.2*growth_factor + 0.1*stability  │
│  │  │   consistency = 0.7*1.0 + 0.2*0.8 + 0.1*0.9                    │     │
│  │  │   consistency = 0.91                                           │     │
│  │  │                                                                 │     │
│  │  └─> Output: 0.91                                                 │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  FEATURE 5: COMPLIANCE SCORE                                                 │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Input: GST filing history (12 months)                            │     │
│  │  │                                                                 │     │
│  │  │  Returns filed on time: 12/12                                  │     │
│  │  │  Late filings: 0                                               │     │
│  │  │  Penalties: None                                               │     │
│  │  │                                                                 │     │
│  │  ├─> Calculate:                                                   │     │
│  │  │   • On-time ratio = 12/12 = 1.0                                │     │
│  │  │   • Penalty factor = 0 (no penalties)                          │     │
│  │  │                                                                 │     │
│  │  ├─> Normalize:                                                   │     │
│  │  │   compliance = on_time_ratio * (1 - penalty_factor)            │     │
│  │  │   compliance = 1.0 * 1.0                                       │     │
│  │  │   compliance = 1.0                                             │     │
│  │  │                                                                 │     │
│  │  └─> Output: 1.0                                                  │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  FEATURE 6: GROWTH INDICATOR                                                 │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Input: Multi-source trend data (12 months)                       │     │
│  │  │                                                                 │     │
│  │  │  Revenue trend: +8% YoY                                        │     │
│  │  │  Transaction trend: +12% YoY                                   │     │
│  │  │  Headcount trend: +16.67% YoY                                  │     │
│  │  │                                                                 │     │
│  │  ├─> Calculate:                                                   │     │
│  │  │   • Composite growth = (0.4*rev + 0.3*txn + 0.3*emp)           │     │
│  │  │   • Composite growth = (0.4*8 + 0.3*12 + 0.3*16.67)            │     │
│  │  │   • Composite growth = 11.4%                                   │     │
│  │  │                                                                 │     │
│  │  ├─> Normalize:                                                   │     │
│  │  │   growth = min(composite_growth / 20, 1.0)                     │     │
│  │  │   growth = min(11.4 / 20, 1.0)                                 │     │
│  │  │   growth = 0.57                                                │     │
│  │  │                                                                 │     │
│  │  └─> Output: 0.57                                                 │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FINAL OUTPUT: Feature Vector                                                │
│  [0.872, 0.833, 0.189, 0.91, 1.0, 0.57]                                     │
│   │     │     │     │    │    │                                             │
│   │     │     │     │    │    └─> Growth Indicator                          │
│   │     │     │     │    └──────> Compliance Score                          │
│   │     │     │     └───────────> Employment Consistency                    │
│   │     │     └─────────────────> Liquidity Ratio                           │
│   │     └───────────────────────> Transaction Velocity                      │
│   └─────────────────────────────> Revenue Stability                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Error Handling & Fallback Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ERROR HANDLING STRATEGY                                │
│                                                                              │
│  ADAPTER LAYER ERRORS                                                        │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │  Data Source Failure Scenarios                                  │       │
│  │                                                                   │       │
│  │  1. API Timeout (>30s)                                           │       │
│  │     ├─> Retry with exponential backoff (1s, 2s, 4s)             │       │
│  │     ├─> After 3 retries: Mark source as unavailable             │       │
│  │     └─> Continue with remaining sources                         │       │
│  │                                                                   │       │
│  │  2. Authentication Failure                                       │       │
│  │     ├─> Log error with details                                  │       │
│  │     ├─> Return error to user: "GST API credentials invalid"     │       │
│  │     └─> Do not compute score (hard failure)                     │       │
│  │                                                                   │       │
│  │  3. Invalid/Malformed Response                                   │       │
│  │     ├─> Log raw response for debugging                          │       │
│  │     ├─> Mark source as unavailable                              │       │
│  │     └─> Continue with remaining sources                         │       │
│  │                                                                   │       │
│  │  4. Rate Limit Exceeded                                          │       │
│  │     ├─> Wait for rate limit window                              │       │
│  │     ├─> Retry after cooldown period                             │       │
│  │     └─> If critical: fail request, else: continue               │       │
│  │                                                                   │       │
│  │  5. Data Not Found (404)                                         │       │
│  │     ├─> Valid scenario: MSME not registered with source         │       │
│  │     ├─> Mark source as "not applicable"                         │       │
│  │     └─> Continue with remaining sources                         │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                              │
│  SCORING ENGINE ERRORS                                                       │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │  Computation Failure Scenarios                                   │       │
│  │                                                                   │       │
│  │  1. Insufficient Data (< 2 sources)                              │       │
│  │     ├─> Return error: "Minimum 2 data sources required"          │       │
│  │     ├─> Suggest which sources are missing                        │       │
│  │     └─> Do not compute score                                     │       │
│  │                                                                   │       │
│  │  2. Feature Engineering Error                                    │       │
│  │     ├─> Log input data that caused error                         │       │
│  │     ├─> Return generic error to user                             │       │
│  │     └─> Alert engineering team                                   │       │
│  │                                                                   │       │
│  │  3. ML Model Not Loaded                                          │       │
│  │     ├─> Fallback: Return composite score only                    │       │
│  │     ├─> Set risk band based on score thresholds                  │       │
│  │     ├─> Skip SHAP explanations                                   │       │
│  │     └─> Log warning for ops team                                 │       │
│  │                                                                   │       │
│  │  4. SHAP Computation Timeout                                     │       │
│  │     ├─> Return score + risk band without explanations            │       │
│  │     ├─> Mark SHAP as unavailable in response                     │       │
│  │     └─> Continue normal flow                                     │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                              │
│  API LAYER ERRORS                                                            │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │  HTTP Error Responses                                            │       │
│  │                                                                   │       │
│  │  400 Bad Request                                                 │       │
│  │  • Invalid MSME ID format                                        │       │
│  │  • Missing required parameters                                   │       │
│  │  • Malformed JSON body                                           │       │
│  │                                                                   │       │
│  │  401 Unauthorized                                                │       │
│  │  • Missing JWT token                                             │       │
│  │  • Expired token                                                 │       │
│  │  • Invalid signature                                             │       │
│  │                                                                   │       │
│  │  403 Forbidden                                                   │       │
│  │  • User not authorized for requested MSME                        │       │
│  │  • Insufficient permissions                                      │       │
│  │                                                                   │       │
│  │  404 Not Found                                                   │       │
│  │  • MSME ID not found in system                                   │       │
│  │  • Endpoint does not exist                                       │       │
│  │                                                                   │       │
│  │  429 Too Many Requests                                           │       │
│  │  • Rate limit exceeded                                           │       │
│  │  • Retry-After header included                                   │       │
│  │                                                                   │       │
│  │  500 Internal Server Error                                       │       │
│  │  • Unexpected exception                                          │       │
│  │  • Database connection failure                                   │       │
│  │  • Generic fallback for uncaught errors                          │       │
│  │                                                                   │       │
│  │  503 Service Unavailable                                         │       │
│  │  • Maintenance mode                                              │       │
│  │  • External dependency unavailable                               │       │
│  │  • Database overloaded                                           │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                              │
│  GRACEFUL DEGRADATION                                                        │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  Priority Levels:                                                            │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │  P1 (Critical): GST + UPI                                  │             │
│  │  • Can compute score with just these two                   │             │
│  │  • Mark AA & EPFO as unavailable                           │             │
│  │  • Proceed with warning message                            │             │
│  └────────────────────────────────────────────────────────────┘             │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │  P2 (Important): AA or EPFO                                │             │
│  │  • Enhances score accuracy                                 │             │
│  │  • Missing = partial picture                               │             │
│  │  • Can proceed but with disclaimer                         │             │
│  └────────────────────────────────────────────────────────────┘             │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────┐             │
│  │  P3 (Optional): SHAP explanations                          │             │
│  │  • Nice to have, not essential                             │             │
│  │  • Can return score without explanations                   │             │
│  │  • User still gets actionable result                       │             │
│  └────────────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Caching & Performance Optimization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CACHING ARCHITECTURE                                   │
│                                                                              │
│  MULTI-LAYER CACHING STRATEGY                                                │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  Layer 1: In-Memory Cache (Application Level)                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  ML Model Artifacts                                                │     │
│  │  • classifier_v1.pkl          → Loaded at startup                  │     │
│  │  • explainer_v1.pkl           → Persistent in RAM                  │     │
│  │  • Eviction: Never (until restart)                                │     │
│  │  • Size: ~50MB                                                     │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Sector Weights Configuration                                      │     │
│  │  • Trader weights                → Loaded at startup               │     │
│  │  • Manufacturer weights          → Persistent in RAM               │     │
│  │  • Service provider weights      → Persistent in RAM               │     │
│  │  • Size: <1KB                                                      │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  Layer 2: Distributed Cache (Redis)                                          │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Adapter Responses                                                 │     │
│  │  • Key: adapter:{source}:{msme_id}:{date}                          │     │
│  │  • TTL: 15 minutes                                                 │     │
│  │  • Rationale: External API data changes infrequently              │     │
│  │  • Eviction: LRU                                                   │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Feature Engineering Results                                       │     │
│  │  • Key: features:{msme_id}:{data_hash}                             │     │
│  │  • TTL: 5 minutes                                                  │     │
│  │  • Rationale: Recompute if underlying data changes                │     │
│  │  • Eviction: LRU                                                   │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Rate Limit Counters                                               │     │
│  │  • Key: ratelimit:{user_id}:{minute}                               │     │
│  │  • TTL: 1 minute                                                   │     │
│  │  • Rationale: Sliding window rate limiting                         │     │
│  │  • Eviction: Automatic (TTL)                                       │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  Layer 3: Database Query Cache                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Recent Score Lookups                                              │     │
│  │  • Query: SELECT * FROM score_history WHERE msme_id = ?           │     │
│  │           ORDER BY computed_at DESC LIMIT 1                        │     │
│  │  • Cached by PostgreSQL query planner                             │     │
│  │  • Benefit from btree index on (msme_id, computed_at)             │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  PERFORMANCE OPTIMIZATION TECHNIQUES                                         │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Parallel Adapter Calls                                            │     │
│  │                                                                     │     │
│  │  Sequential (Slow):                                                │     │
│  │  GST  (2s) → UPI  (1.5s) → AA   (2.5s) → EPFO (1s) = 7s total    │     │
│  │                                                                     │     │
│  │  Parallel (Fast):                                                  │     │
│  │  ┌─ GST  (2s)   ─┐                                                │     │
│  │  ├─ UPI  (1.5s) ─┤                                                │     │
│  │  ├─ AA   (2.5s) ─┤ → All complete in 2.5s (max latency)          │     │
│  │  └─ EPFO (1s)   ─┘                                                │     │
│  │                                                                     │     │
│  │  Implementation: asyncio.gather() or concurrent.futures           │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Database Indexing Strategy                                        │     │
│  │                                                                     │     │
│  │  CREATE INDEX idx_msme_computed ON score_history                  │     │
│  │    (msme_id, computed_at DESC);                                    │     │
│  │  • Supports latest score lookup: ~1ms                              │     │
│  │                                                                     │     │
│  │  CREATE INDEX idx_risk_sector ON score_history                    │     │
│  │    (sector, risk_band, computed_at);                               │     │
│  │  • Supports portfolio analysis: ~10ms                              │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Connection Pooling                                                │     │
│  │  • Pool size: 10 connections                                       │     │
│  │  • Max overflow: 20                                                │     │
│  │  • Connection timeout: 30s                                         │     │
│  │  • Recycle connections after: 1 hour                               │     │
│  │  • Benefit: Eliminates connection establishment overhead           │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Lazy SHAP Computation                                             │     │
│  │  • Only compute if:                                                │     │
│  │    - Risk band is Medium or High                                   │     │
│  │    - User explicitly requests explanations                         │     │
│  │  • Skip for Low risk + no explanation request                      │     │
│  │  • Saves: ~500ms per assessment                                    │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  PERFORMANCE METRICS (Target SLAs)                                           │
│  ──────────────────────────────────────────────────────────────────────────│
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  End-to-End Latency                                                │     │
│  │  • P50: < 3 seconds                                                │     │
│  │  • P95: < 5 seconds                                                │     │
│  │  • P99: < 8 seconds                                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Throughput                                                        │     │
│  │  • Sustained: 100 requests/second                                  │     │
│  │  • Burst: 500 requests/second                                      │     │
│  │  • Daily capacity: 8.6M assessments                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  Cache Hit Rates                                                   │     │
│  │  • Adapter responses: > 60%                                        │     │
│  │  • Feature computations: > 40%                                     │     │
│  │  • Database queries: > 80%                                         │     │
│  └────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary

This architecture document provides comprehensive visual representations of:

1. **High-Level System Architecture** - Complete data flow from MSME sources to user interfaces
2. **Data Flow Sequence** - Step-by-step interaction between components
3. **Component Architecture** - Detailed layer breakdown
4. **Database Schema** - Score history table design
5. **ML Model Architecture** - Training and inference pipelines
6. **Security Architecture** - Authentication and authorization flows
7. **Deployment Architecture** - Production infrastructure setup
8. **Feature Engineering Pipeline** - Detailed calculation examples
9. **Error Handling & Fallback** - Comprehensive error management strategy
10. **Caching & Performance** - Multi-layer optimization approach

These diagrams serve as the technical blueprint for the MSME Financial Health Assessment System, enabling developers, architects, and stakeholders to understand the system's design, data flows, and operational characteristics.
