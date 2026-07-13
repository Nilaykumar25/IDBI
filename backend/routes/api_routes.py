"""
API Routes for MSME Financial Health Score System
All routes are protected with JWT authentication
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from typing import Dict, Any
import os

import os

# Import appropriate middleware based on environment
if os.getenv('TEST_MODE') == 'true':
    from auth.test_middleware import require_auth_test as require_auth
    print("WARNING: Using test authentication middleware (TEST_MODE=true)")
else:
    from auth.middleware import require_auth
from scoring.scoring_engine import ScoringEngine, MSMEIdentifiers
from scoring.feature_engineering import NormalizedFeatures
from storage.score_history_store import ScoreHistoryStore


# Create Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize scoring engine (will be configured in app.py)
scoring_engine: ScoringEngine = None
score_history_store: ScoreHistoryStore = None


def init_scoring_engine(engine: ScoringEngine):
    """
    Initialize the scoring engine for this module.
    Called from app.py during application setup.
    
    Args:
        engine: Configured ScoringEngine instance
    """
    global scoring_engine, score_history_store
    scoring_engine = engine
    
    # Initialize score history store with Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if supabase_url and supabase_key:
        try:
            score_history_store = ScoreHistoryStore(supabase_url, supabase_key)
        except Exception as e:
            print(f"Warning: Failed to initialize ScoreHistoryStore: {e}")
            score_history_store = None
    else:
        print("Warning: SUPABASE_URL and SUPABASE_KEY not configured. Score history persistence disabled.")
        score_history_store = None


@api_bp.route('/scores', methods=['POST'])
@require_auth
def compute_score():
    """
    Computes financial health score for an MSME.
    
    Protected endpoint requiring valid JWT token.
    
    Request Body:
        {
            "msmeId": "string",
            "gstNumber": "string",
            "upiId": "string",
            "aaConsentToken": "string",
            "epfoEstablishmentId": "string",
            "sector": "Trader" | "Manufacturer" | "Services"
        }
    
    Returns:
        200: Score computation result
        400: Invalid request data
        401: Unauthorized (handled by @require_auth)
        500: Internal error during computation
    """
    try:
        # Parse request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Validate required fields
        required_fields = ['msmeId', 'gstNumber', 'upiId', 'aaConsentToken', 'epfoEstablishmentId', 'sector']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate sector
        valid_sectors = ['Trader', 'Manufacturer', 'Services']
        if data['sector'] not in valid_sectors:
            return jsonify({
                'success': False,
                'error': f'Invalid sector. Must be one of: {", ".join(valid_sectors)}'
            }), 400
        
        # Create identifiers object
        identifiers = MSMEIdentifiers(
            msme_id=data['msmeId'],
            gst_number=data['gstNumber'],
            upi_id=data['upiId'],
            aa_consent_token=data['aaConsentToken'],
            epfo_establishment_id=data['epfoEstablishmentId'],
            sector=data['sector']
        )
        
        # Compute score
        result = scoring_engine.compute_score(identifiers)
        
        # Persist result to score history store
        if score_history_store:
            try:
                score_record = {
                    'msme_id': result.msme_id,
                    'composite_score': result.composite_score,
                    'risk_band': result.ml_risk_band,
                    'ml_confidence': {
                        'low': result.ml_confidence.low,
                        'medium': result.ml_confidence.medium,
                        'high': result.ml_confidence.high
                    },
                    'features': {
                        'revenue_stability': result.features.revenue_stability,
                        'transaction_velocity': result.features.transaction_velocity,
                        'liquidity_ratio': result.features.liquidity_ratio,
                        'employment_consistency': result.features.employment_consistency,
                        'compliance_score': result.features.compliance_score,
                        'growth_indicator': result.features.growth_indicator
                    },
                    'shap_values': result.shap_values.to_dict(),
                    'missing_sources': result.missing_data_sources,
                    'sector': result.sector,
                    'computed_at': result.computed_at
                }
                score_history_store.save(score_record)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Warning: Failed to persist score to history: {e}")
        
        # Format response
        return jsonify({
            'success': True,
            'data': {
                'msmeId': result.msme_id,
                'compositeScore': result.composite_score,
                'riskBand': result.ml_risk_band,
                'confidence': {
                    'low': result.ml_confidence.low,
                    'medium': result.ml_confidence.medium,
                    'high': result.ml_confidence.high
                },
                'shapValues': result.shap_values.to_dict(),
                'features': {
                    'revenueStability': result.features.revenue_stability,
                    'transactionVelocity': result.features.transaction_velocity,
                    'liquidityRatio': result.features.liquidity_ratio,
                    'employmentConsistency': result.features.employment_consistency,
                    'complianceScore': result.features.compliance_score,
                    'growthIndicator': result.features.growth_indicator
                },
                'missingDataSources': result.missing_data_sources,
                'computedAt': result.computed_at.isoformat(),
                'sector': result.sector
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"Error computing score: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal error during score computation'
        }), 500


@api_bp.route('/scores/<msme_id>', methods=['GET'])
@require_auth
def retrieve_score(msme_id: str):
    """
    Retrieves most recent score for an MSME.
    
    Protected endpoint requiring valid JWT token.
    
    Path Parameters:
        msme_id: MSME identifier
    
    Returns:
        200: Score data
        404: MSME not found
        401: Unauthorized (handled by @require_auth)
        500: Internal error
    """
    try:
        # Check if score history store is available
        if not score_history_store:
            return jsonify({
                'success': False,
                'error': 'Score history storage not configured'
            }), 500
        
        # Retrieve most recent score
        score_record = score_history_store.retrieve(msme_id)
        
        if not score_record:
            return jsonify({
                'success': False,
                'error': f'No score found for MSME ID: {msme_id}'
            }), 404
        
        # Format response
        return jsonify({
            'success': True,
            'data': {
                'msmeId': score_record['msme_id'],
                'compositeScore': score_record['composite_score'],
                'riskBand': score_record['risk_band'],
                'confidence': {
                    'low': score_record['ml_confidence_low'],
                    'medium': score_record['ml_confidence_medium'],
                    'high': score_record['ml_confidence_high']
                },
                'shapValues': score_record['shap_values'],
                'features': score_record['features'],
                'missingDataSources': score_record.get('missing_sources', []),
                'computedAt': score_record['computed_at'],
                'sector': score_record['sector']
            }
        }), 200
        
    except Exception as e:
        print(f"Error retrieving score: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal error during score retrieval'
        }), 500


@api_bp.route('/scores/<msme_id>/history', methods=['GET'])
@require_auth
def retrieve_score_history(msme_id: str):
    """
    Retrieves historical scores for an MSME.
    
    Protected endpoint requiring valid JWT token.
    
    Path Parameters:
        msme_id: MSME identifier
    
    Query Parameters:
        startDate: ISO date string (optional, defaults to 6 months ago)
        endDate: ISO date string (optional, defaults to today)
    
    Returns:
        200: Array of historical score records
        400: Invalid date parameters
        401: Unauthorized (handled by @require_auth)
        500: Internal error
    """
    try:
        # Check if score history store is available
        if not score_history_store:
            return jsonify({
                'success': False,
                'error': 'Score history storage not configured'
            }), 500
        
        # Parse date range parameters
        start_date_str = request.args.get('startDate')
        end_date_str = request.args.get('endDate')
        
        # Default to 6 months history
        if not end_date_str:
            end_date = datetime.now()
        else:
            try:
                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid endDate format. Use ISO date string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).'
                }), 400
        
        if not start_date_str:
            start_date = end_date - timedelta(days=180)  # 6 months
        else:
            try:
                start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid startDate format. Use ISO date string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).'
                }), 400
        
        # Validate date range
        if start_date > end_date:
            return jsonify({
                'success': False,
                'error': 'startDate must be before endDate'
            }), 400
        
        # Retrieve historical scores
        history_records = score_history_store.retrieve_history(msme_id, start_date, end_date)
        
        # Format response
        formatted_records = []
        for record in history_records:
            formatted_records.append({
                'msmeId': record['msme_id'],
                'compositeScore': record['composite_score'],
                'riskBand': record['risk_band'],
                'computedAt': record['computed_at'],
                'sector': record['sector']
            })
        
        return jsonify({
            'success': True,
            'data': formatted_records
        }), 200
        
    except Exception as e:
        print(f"Error retrieving score history: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal error during score history retrieval'
        }), 500


@api_bp.route('/simulate', methods=['POST'])
@require_auth
def simulate_score():
    """
    Simulates score with adjusted features (What-If analysis).
    
    Protected endpoint requiring valid JWT token.
    
    Request Body:
        {
            "features": {
                "revenueStability": 0.0-1.0,
                "transactionVelocity": 0.0-1.0,
                "liquidityRatio": 0.0-1.0,
                "employmentConsistency": 0.0-1.0,
                "complianceScore": 0.0-1.0,
                "growthIndicator": 0.0-1.0
            },
            "sector": "Trader" | "Manufacturer" | "Services"
        }
    
    Returns:
        200: Simulated score result
        400: Invalid request data
        401: Unauthorized (handled by @require_auth)
        500: Internal error
    """
    try:
        # Parse request body
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        # Validate required fields
        if 'features' not in data or 'sector' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: features, sector'
            }), 400
        
        features_data = data['features']
        sector = data['sector']
        
        # Validate sector
        valid_sectors = ['Trader', 'Manufacturer', 'Services']
        if sector not in valid_sectors:
            return jsonify({
                'success': False,
                'error': f'Invalid sector. Must be one of: {", ".join(valid_sectors)}'
            }), 400
        
        # Validate feature values
        required_features = [
            'revenueStability', 'transactionVelocity', 'liquidityRatio',
            'employmentConsistency', 'complianceScore', 'growthIndicator'
        ]
        
        for feature in required_features:
            if feature not in features_data:
                return jsonify({
                    'success': False,
                    'error': f'Missing feature: {feature}'
                }), 400
            
            value = features_data[feature]
            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                return jsonify({
                    'success': False,
                    'error': f'Invalid value for {feature}. Must be between 0.0 and 1.0.'
                }), 400
        
        # Create NormalizedFeatures object
        features = NormalizedFeatures(
            revenue_stability=features_data['revenueStability'],
            transaction_velocity=features_data['transactionVelocity'],
            liquidity_ratio=features_data['liquidityRatio'],
            employment_consistency=features_data['employmentConsistency'],
            compliance_score=features_data['complianceScore'],
            growth_indicator=features_data['growthIndicator'],
            missing_sources=[]
        )
        
        # Compute simulated score
        result = scoring_engine.compute_with_partial_data(features, sector)
        
        # Format response
        return jsonify({
            'success': True,
            'data': {
                'compositeScore': result.composite_score,
                'riskBand': result.ml_risk_band,
                'confidence': {
                    'low': result.ml_confidence.low,
                    'medium': result.ml_confidence.medium,
                    'high': result.ml_confidence.high
                },
                'shapValues': result.shap_values.to_dict()
            }
        }), 200
        
    except Exception as e:
        print(f"Error simulating score: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal error during score simulation'
        }), 500


@api_bp.route('/ecosystem/consent', methods=['POST'])
@require_auth
def simulate_aa_consent():
    """
    Simulates Account Aggregator consent flow.
    
    Protected endpoint requiring valid JWT token.
    
    Returns mock consent token and approval timestamp.
    Responds within 500ms as per requirements.
    
    Returns:
        200: Mock consent approval
        401: Unauthorized (handled by @require_auth)
    """
    import uuid
    
    return jsonify({
        'success': True,
        'data': {
            'consentToken': f'mock-consent-{uuid.uuid4()}',
            'status': 'approved',
            'timestamp': datetime.now().isoformat()
        }
    }), 200


@api_bp.route('/ecosystem/publish', methods=['POST'])
@require_auth
def simulate_uli_publish():
    """
    Simulates ULI score publishing.
    
    Protected endpoint requiring valid JWT token.
    
    Returns mock transaction ID and confirmation.
    
    Returns:
        200: Mock publish confirmation
        401: Unauthorized (handled by @require_auth)
    """
    import uuid
    
    return jsonify({
        'success': True,
        'data': {
            'transactionId': f'uli-txn-{uuid.uuid4()}',
            'status': 'published',
            'message': 'Score successfully published to ULI',
            'timestamp': datetime.now().isoformat()
        }
    }), 200


@api_bp.route('/ecosystem/lenders', methods=['GET'])
@require_auth
def get_lender_matches():
    """
    Returns mock lender matches based on risk band.
    
    Protected endpoint requiring valid JWT token.
    
    Query Parameters:
        riskBand: "Low" | "Medium" | "High"
    
    Returns:
        200: Array of 2-3 matched lenders
        400: Invalid or missing riskBand parameter
        401: Unauthorized (handled by @require_auth)
    """
    risk_band = request.args.get('riskBand')
    
    if not risk_band:
        return jsonify({
            'success': False,
            'error': 'Missing required query parameter: riskBand'
        }), 400
    
    if risk_band not in ['Low', 'Medium', 'High']:
        return jsonify({
            'success': False,
            'error': 'Invalid riskBand. Must be one of: Low, Medium, High'
        }), 400
    
    # Mock lender data based on risk band
    lender_data = {
        'Low': [
            {
                'name': 'Prime Bank Ltd',
                'productType': 'Business Term Loan',
                'interestRate': '8-10% p.a.',
                'maxAmount': '₹50,00,000'
            },
            {
                'name': 'National Finance Corp',
                'productType': 'Working Capital Loan',
                'interestRate': '9-11% p.a.',
                'maxAmount': '₹75,00,000'
            },
            {
                'name': 'Growth Capital Partners',
                'productType': 'Equipment Financing',
                'interestRate': '10-12% p.a.',
                'maxAmount': '₹1,00,00,000'
            }
        ],
        'Medium': [
            {
                'name': 'Regional Microfinance',
                'productType': 'MSME Business Loan',
                'interestRate': '12-16% p.a.',
                'maxAmount': '₹25,00,000'
            },
            {
                'name': 'SME Finance Solutions',
                'productType': 'Invoice Financing',
                'interestRate': '14-18% p.a.',
                'maxAmount': '₹30,00,000'
            }
        ],
        'High': [
            {
                'name': 'Alternative Lending Co',
                'productType': 'Short-term Business Loan',
                'interestRate': '18-24% p.a.',
                'maxAmount': '₹10,00,000'
            },
            {
                'name': 'Quick Capital NBFC',
                'productType': 'Emergency Working Capital',
                'interestRate': '20-26% p.a.',
                'maxAmount': '₹15,00,000'
            }
        ]
    }
    
    return jsonify({
        'success': True,
        'data': {
            'riskBand': risk_band,
            'lenders': lender_data[risk_band]
        }
    }), 200
