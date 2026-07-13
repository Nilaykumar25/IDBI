# MSME Financial Health Score System

A web application that evaluates the financial health of Micro, Small, and Medium Enterprises (MSMEs) using alternate data sources. The system aggregates data from GST, UPI transactions, Account Aggregator bank data, and EPFO records to compute a comprehensive financial health score (0-100) with risk classification and explainability features.

## 🏗️ Architecture

- **Backend**: Python/Flask with Supabase Auth JWT verification
- **Frontend**: React 18+ with Supabase Auth JS client
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth (email/password, JWT tokens)
- **ML Framework**: scikit-learn for classification, SHAP for explainability

## 📁 Project Structure

```
msme-financial-health-score/
├── backend/
│   ├── adapters/          # Data adapter implementations (GST, UPI, AA, EPFO)
│   ├── middleware/        # Authentication middleware
│   ├── models/            # ML model artifacts (.pkl files)
│   ├── routes/            # API route blueprints
│   ├── scoring/           # Scoring engine and feature engineering
│   ├── scripts/           # Utility scripts (dataset generation, model training)
│   ├── app.py             # Flask application entry point
│   ├── config.py          # Configuration management
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment variable template
│
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── contexts/      # React context providers (Auth)
│   │   ├── lib/           # Utility libraries (Supabase, API client)
│   │   ├── pages/         # Page components (Login, Signup, Dashboard)
│   │   ├── App.jsx        # Main app component with routing
│   │   ├── main.jsx       # React entry point
│   │   └── index.css      # Global styles
│   ├── package.json       # Node dependencies
│   ├── vite.config.js     # Vite configuration
│   └── .env.example       # Environment variable template
│
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 18+** (for frontend)
- **Supabase Account** (for authentication and database)

### 1. Supabase Setup

#### Create a Supabase Project

1. Go to [Supabase](https://app.supabase.com/)
2. Create a new project
3. Wait for the project to be provisioned

#### Enable Email/Password Authentication

1. Navigate to **Authentication → Providers** in your Supabase dashboard
2. Enable **Email** provider
3. Configure email settings (or use default for development)

#### Obtain Credentials

1. Go to **Project Settings → API**
2. Copy the following values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)
3. Go to **Project Settings → API → JWT Settings**
4. Copy the **JWT Secret** (used for backend token verification)

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Supabase credentials
# SUPABASE_URL=your_supabase_project_url
# SUPABASE_KEY=your_supabase_anon_key
# SUPABASE_JWT_SECRET=your_supabase_jwt_secret
# ADAPTER_MODE=mock
```

#### Run the Backend

```bash
python app.py
```

The backend API will start on `http://localhost:5000`

**API Endpoints:**
- `GET /api/health` - Health check endpoint (no auth required)
- Additional endpoints will be added in subsequent tasks

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd frontend

# Install dependencies
npm install
```

#### Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Supabase credentials
# VITE_SUPABASE_URL=your_supabase_project_url
# VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
# VITE_API_URL=http://localhost:5000/api
```

#### Run the Frontend

```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

### 4. Test the Application

1. Open your browser to `http://localhost:3000`
2. You will be redirected to the login page
3. Click "Sign up" to create a new account
4. Enter your email and password (minimum 6 characters)
5. After signup, you'll be automatically logged in and redirected to the dashboard
6. Test logout functionality using the logout button in the header

## 🔐 Authentication Flow

### User Registration
1. User navigates to `/signup`
2. User submits email and password
3. Supabase Auth creates user account
4. User is automatically signed in with session token
5. Frontend stores session and redirects to dashboard

### User Login
1. User navigates to `/login`
2. User submits email and password
3. Supabase Auth validates credentials and returns JWT session
4. Frontend stores session in memory and localStorage
5. User is redirected to `/dashboard`

### Session Management
- Supabase Auth automatically refreshes JWT tokens before expiration
- Session persists across browser refreshes via localStorage
- Invalid/expired tokens trigger redirect to login screen

### API Request Flow
1. Frontend includes JWT token in `Authorization: Bearer <token>` header
2. Flask middleware validates token with Supabase
3. If valid: Request proceeds to route handler
4. If invalid: Returns 401 Unauthorized response
5. Frontend detects 401 and redirects to login

## 🧪 Development Mode

The system operates in **mock mode** by default (`ADAPTER_MODE=mock`), which means:
- Data adapters return simulated data without requiring real API credentials
- GST, UPI, Account Aggregator, and EPFO adapters generate realistic mock data
- 50-200ms latency simulation for realistic testing
- 95% success rate with occasional simulated failures

This allows full development and testing without:
- Real GST API credentials
- Real UPI transaction access
- Real Account Aggregator consent tokens
- Real EPFO establishment IDs

## 📊 Features (To Be Implemented)

Task 1 (Current) establishes the foundation:
- ✅ Python/Flask backend with Supabase integration
- ✅ React frontend with routing and authentication
- ✅ Supabase Auth (email/password, JWT tokens, session management)
- ✅ Protected routes and API authentication middleware
- ✅ Environment configuration and project structure

Upcoming tasks will add:
- Data adapters for GST, UPI, AA, EPFO
- Feature engineering pipeline
- Composite weighted scoring model with sector-specific weights
- ML-based risk classification with SHAP explainability
- REST API endpoints for score computation and retrieval
- PostgreSQL database for score history
- Dashboard views:
  - Score Card
  - Data Sources View
  - Trend Analysis View
  - Risk Factors View
  - Recommendations View
  - What-If Simulator
  - Ecosystem Integration Panel

## 🛠️ Technology Stack

### Backend
- **Flask 3.0**: Web framework
- **Supabase Python Client**: Auth and database
- **scikit-learn**: ML classification
- **SHAP**: Model explainability
- **pandas/numpy**: Data processing

### Frontend
- **React 18.2**: UI framework
- **React Router 6**: Client-side routing
- **Supabase JS Client**: Authentication
- **Axios**: HTTP client with interceptors
- **Lucide React**: Icon library
- **Recharts**: Data visualization
- **Vite**: Build tool and dev server

### Infrastructure
- **Supabase**: Authentication, PostgreSQL database, Row Level Security
- **Python Virtual Environment**: Dependency isolation
- **npm**: Frontend package management

## 📝 Environment Variables

### Backend (.env)
```bash
# Required - Supabase credentials
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret

# Optional - Adapter configuration
ADAPTER_MODE=mock  # 'mock' or 'production'

# Optional - Flask configuration
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
PORT=5000
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env)
```bash
# Required - Supabase credentials
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Required - Backend API
VITE_API_URL=http://localhost:5000/api
```

## 🔒 Security Notes

- **Never commit `.env` files** - they are gitignored by default
- **Use strong SECRET_KEY** in production
- **Enable Row Level Security** in Supabase for production
- **Use HTTPS** in production for both frontend and backend
- **Rotate JWT secrets** periodically in production
- **Validate all user inputs** on both client and server

## 🐛 Troubleshooting

### Backend won't start
- Check that Python 3.9+ is installed: `python --version`
- Verify virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check `.env` file exists and has valid Supabase credentials

### Frontend won't start
- Check that Node.js 18+ is installed: `node --version`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check `.env` file exists and has valid Supabase credentials
- Ensure backend is running on port 5000

### Authentication not working
- Verify Supabase project is active
- Check that email provider is enabled in Supabase dashboard
- Verify environment variables match your Supabase project
- Check browser console for error messages
- Try signing out and clearing browser localStorage

### CORS errors
- Ensure backend `CORS_ORIGINS` includes your frontend URL
- Check that frontend is accessing the correct backend URL
- Verify backend is running and accessible

## 📚 Next Steps

After Task 1 is complete, the following tasks will be implemented:

1. **Task 2**: Implement data adapter layer (GST, UPI, AA, EPFO)
2. **Task 3**: Implement feature engineering pipeline
3. **Task 4**: Implement composite weighted scoring model
4. **Task 5**: Checkpoint - Verify data pipeline
5. **Task 6**: Implement synthetic dataset generation
6. **Task 7**: Implement ML classifier and SHAP explainability
7. **Task 8**: Implement scoring engine orchestration
8. **Task 9**: Implement database layer for score history
9. **Task 10**: Implement REST API endpoints
10. **Tasks 11+**: Implement frontend dashboard views

## 📄 License

This project is part of the MSME Financial Health Score system specification.

## 🤝 Contributing

This project follows an incremental implementation plan. Each task builds on the previous foundation. Refer to `.kiro/specs/msme-financial-health-score/tasks.md` for the complete implementation roadmap.
