"""
MSME Financial Health Score System - Flask Backend
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from routes.api_routes import api_bp, init_scoring_engine
from scoring.scoring_engine import ScoringEngine

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SUPABASE_URL'] = os.getenv('SUPABASE_URL')
app.config['SUPABASE_KEY'] = os.getenv('SUPABASE_KEY')
app.config['SUPABASE_JWT_SECRET'] = os.getenv('SUPABASE_JWT_SECRET')
app.config['MODE'] = os.getenv('MODE', 'mock')  # 'mock' or 'production'
app.config['ADAPTER_MODE'] = os.getenv('ADAPTER_MODE', 'mock')
app.config['MODEL_DIR'] = os.getenv('MODEL_DIR', 'models')

# Initialize scoring engine
scoring_engine = ScoringEngine(
    mode=app.config['ADAPTER_MODE'],
    model_dir=app.config['MODEL_DIR']
)

# Initialize scoring engine in routes module
init_scoring_engine(scoring_engine)

# Register blueprints
app.register_blueprint(api_bp)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint (no authentication required)"""
    return jsonify({
        'status': 'healthy',
        'mode': app.config['MODE'],
        'adapterMode': app.config['ADAPTER_MODE']
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
