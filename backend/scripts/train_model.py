#!/usr/bin/env python3
"""
Offline ML Model Training Script

Trains Random Forest classifier on synthetic MSME dataset with:
- 70/30 train/validation split
- Hyperparameter tuning with grid search
- SHAP explainer training
- Model artifact persistence to models/ directory

Outputs:
- classifier_v1.pkl: Trained Random Forest classifier
- explainer_v1.pkl: SHAP TreeExplainer
- training_metrics_v1.json: Performance metrics
"""
import argparse
import sys
import os
from pathlib import Path
import json
import pickle
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import shap

from scoring.synthetic_dataset_generator import SyntheticDatasetGenerator


def generate_training_data(size: int = 1000, seed: int = None) -> pd.DataFrame:
    """
    Generates synthetic training dataset.
    
    Args:
        size: Number of profiles to generate
        seed: Random seed for reproducibility
    
    Returns:
        DataFrame with features and labels
    """
    print(f"Generating {size} synthetic MSME profiles...")
    
    generator = SyntheticDatasetGenerator(seed=seed)
    profiles = generator.generate_dataset(
        size=size,
        low_pct=0.5,
        medium_pct=0.3,
        high_pct=0.2
    )
    
    # Convert to DataFrame
    data = []
    for profile in profiles:
        row = {
            'msme_id': profile.msme_id,
            'sector': profile.sector,
            'revenue_stability': profile.features['revenue_stability'],
            'transaction_velocity': profile.features['transaction_velocity'],
            'liquidity_ratio': profile.features['liquidity_ratio'],
            'employment_consistency': profile.features['employment_consistency'],
            'compliance_score': profile.features['compliance_score'],
            'growth_indicator': profile.features['growth_indicator'],
            'risk_band': profile.risk_band
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    
    print(f"Generated {len(df)} profiles")
    print(f"Distribution:")
    print(df['risk_band'].value_counts())
    
    return df


def prepare_data(df: pd.DataFrame) -> tuple:
    """
    Prepares data for training by extracting features and labels.
    
    Args:
        df: DataFrame with synthetic profiles
    
    Returns:
        Tuple of (X, y) where X is feature matrix and y is label vector
    """
    feature_columns = [
        'revenue_stability',
        'transaction_velocity',
        'liquidity_ratio',
        'employment_consistency',
        'compliance_score',
        'growth_indicator'
    ]
    
    X = df[feature_columns].values
    
    # Map risk bands to numeric labels
    risk_band_mapping = {'Low': 0, 'Medium': 1, 'High': 2}
    y = df['risk_band'].map(risk_band_mapping).values
    
    return X, y


def train_random_forest(X_train, y_train, X_val, y_val, tune_hyperparams: bool = True):
    """
    Trains Random Forest classifier with optional hyperparameter tuning.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        tune_hyperparams: Whether to perform grid search (default: True)
    
    Returns:
        Trained RandomForestClassifier
    """
    print("\nTraining Random Forest Classifier...")
    
    if tune_hyperparams:
        print("Performing hyperparameter tuning with grid search...")
        
        # Define parameter grid
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2']
        }
        
        # Create base classifier
        rf = RandomForestClassifier(random_state=42)
        
        # Grid search with 3-fold cross-validation
        grid_search = GridSearchCV(
            rf,
            param_grid,
            cv=3,
            scoring='f1_weighted',
            n_jobs=-1,
            verbose=1
        )
        
        start_time = time.time()
        grid_search.fit(X_train, y_train)
        elapsed = time.time() - start_time
        
        print(f"Grid search completed in {elapsed:.2f} seconds")
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best cross-validation F1 score: {grid_search.best_score_:.4f}")
        
        classifier = grid_search.best_estimator_
    else:
        # Train with default parameters
        classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42
        )
        
        start_time = time.time()
        classifier.fit(X_train, y_train)
        elapsed = time.time() - start_time
        
        print(f"Training completed in {elapsed:.2f} seconds")
    
    # Evaluate on validation set
    y_pred = classifier.predict(X_val)
    
    accuracy = accuracy_score(y_val, y_pred)
    print(f"\nValidation Accuracy: {accuracy:.4f}")
    
    return classifier


def train_gradient_boosting(X_train, y_train, X_val, y_val, tune_hyperparams: bool = True):
    """
    Trains Gradient Boosting classifier with optional hyperparameter tuning.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        tune_hyperparams: Whether to perform grid search (default: True)
    
    Returns:
        Trained GradientBoostingClassifier
    """
    print("\nTraining Gradient Boosting Classifier...")
    
    if tune_hyperparams:
        print("Performing hyperparameter tuning with grid search...")
        
        # Define parameter grid
        param_grid = {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        # Create base classifier
        gb = GradientBoostingClassifier(random_state=42)
        
        # Grid search with 3-fold cross-validation
        grid_search = GridSearchCV(
            gb,
            param_grid,
            cv=3,
            scoring='f1_weighted',
            n_jobs=-1,
            verbose=1
        )
        
        start_time = time.time()
        grid_search.fit(X_train, y_train)
        elapsed = time.time() - start_time
        
        print(f"Grid search completed in {elapsed:.2f} seconds")
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best cross-validation F1 score: {grid_search.best_score_:.4f}")
        
        classifier = grid_search.best_estimator_
    else:
        # Train with default parameters
        classifier = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        start_time = time.time()
        classifier.fit(X_train, y_train)
        elapsed = time.time() - start_time
        
        print(f"Training completed in {elapsed:.2f} seconds")
    
    # Evaluate on validation set
    y_pred = classifier.predict(X_val)
    
    accuracy = accuracy_score(y_val, y_pred)
    print(f"\nValidation Accuracy: {accuracy:.4f}")
    
    return classifier


def evaluate_model(classifier, X_val, y_val) -> dict:
    """
    Evaluates classifier on validation set and returns metrics.
    
    Args:
        classifier: Trained classifier
        X_val: Validation features
        y_val: Validation labels
    
    Returns:
        Dictionary with performance metrics
    """
    print("\nEvaluating model on validation set...")
    
    y_pred = classifier.predict(X_val)
    
    # Overall metrics
    accuracy = accuracy_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred, average='weighted')
    recall = recall_score(y_val, y_pred, average='weighted')
    f1 = f1_score(y_val, y_pred, average='weighted')
    
    # Per-class metrics
    class_report = classification_report(
        y_val,
        y_pred,
        target_names=['Low', 'Medium', 'High'],
        output_dict=True
    )
    
    print(f"Overall Metrics:")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    
    print(f"\nPer-Class Metrics:")
    for risk_band in ['Low', 'Medium', 'High']:
        metrics = class_report[risk_band]
        print(f"  {risk_band}:")
        print(f"    Precision: {metrics['precision']:.4f}")
        print(f"    Recall:    {metrics['recall']:.4f}")
        print(f"    F1 Score:  {metrics['f1-score']:.4f}")
    
    return {
        'accuracy': float(accuracy),
        'precision_weighted': float(precision),
        'recall_weighted': float(recall),
        'f1_weighted': float(f1),
        'per_class': {
            'Low': {
                'precision': float(class_report['Low']['precision']),
                'recall': float(class_report['Low']['recall']),
                'f1': float(class_report['Low']['f1-score']),
                'support': int(class_report['Low']['support'])
            },
            'Medium': {
                'precision': float(class_report['Medium']['precision']),
                'recall': float(class_report['Medium']['recall']),
                'f1': float(class_report['Medium']['f1-score']),
                'support': int(class_report['Medium']['support'])
            },
            'High': {
                'precision': float(class_report['High']['precision']),
                'recall': float(class_report['High']['recall']),
                'f1': float(class_report['High']['f1-score']),
                'support': int(class_report['High']['support'])
            }
        }
    }


def train_shap_explainer(classifier, X_train) -> shap.TreeExplainer:
    """
    Trains SHAP TreeExplainer on the trained model.
    
    Args:
        classifier: Trained tree-based classifier
        X_train: Training features for background dataset
    
    Returns:
        Trained SHAP TreeExplainer
    """
    print("\nTraining SHAP TreeExplainer...")
    
    start_time = time.time()
    explainer = shap.TreeExplainer(classifier)
    elapsed = time.time() - start_time
    
    print(f"SHAP explainer trained in {elapsed:.2f} seconds")
    
    return explainer


def save_model_artifacts(classifier, explainer, metrics, model_dir: str = 'models', version: str = 'v1'):
    """
    Saves model artifacts to disk.
    
    Args:
        classifier: Trained classifier
        explainer: Trained SHAP explainer
        metrics: Performance metrics dictionary
        model_dir: Directory to save models (default: 'models')
        version: Model version (default: 'v1')
    """
    print(f"\nSaving model artifacts to {model_dir}/...")
    
    # Create models directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Save classifier
    classifier_path = os.path.join(model_dir, f'classifier_{version}.pkl')
    with open(classifier_path, 'wb') as f:
        pickle.dump(classifier, f)
    print(f"  Saved classifier: {classifier_path}")
    
    # Save explainer
    explainer_path = os.path.join(model_dir, f'explainer_{version}.pkl')
    with open(explainer_path, 'wb') as f:
        pickle.dump(explainer, f)
    print(f"  Saved explainer: {explainer_path}")
    
    # Save metrics
    metrics_path = os.path.join(model_dir, f'training_metrics_{version}.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"  Saved metrics: {metrics_path}")
    
    print("\nModel artifacts saved successfully!")


def main():
    """Main entry point for model training"""
    parser = argparse.ArgumentParser(
        description='Train ML classifier for MSME risk classification'
    )
    parser.add_argument(
        '--dataset-size',
        type=int,
        default=1000,
        help='Number of synthetic profiles to generate (default: 1000)'
    )
    parser.add_argument(
        '--model-type',
        type=str,
        choices=['random_forest', 'gradient_boosting'],
        default='random_forest',
        help='Type of classifier to train (default: random_forest)'
    )
    parser.add_argument(
        '--no-tune',
        action='store_true',
        help='Skip hyperparameter tuning (faster training)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--model-dir',
        type=str,
        default='models',
        help='Directory to save model artifacts (default: models)'
    )
    parser.add_argument(
        '--version',
        type=str,
        default='v1',
        help='Model version suffix (default: v1)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ML Classifier Training Pipeline")
    print("=" * 60)
    
    # Generate training data
    df = generate_training_data(size=args.dataset_size, seed=args.seed)
    
    # Prepare features and labels
    X, y = prepare_data(df)
    
    # Split into train and validation sets (70/30 split)
    print(f"\nSplitting data: 70% train, 30% validation")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.3, random_state=args.seed, stratify=y
    )
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Validation set: {len(X_val)} samples")
    
    # Train classifier
    if args.model_type == 'random_forest':
        classifier = train_random_forest(
            X_train, y_train, X_val, y_val,
            tune_hyperparams=not args.no_tune
        )
    else:
        classifier = train_gradient_boosting(
            X_train, y_train, X_val, y_val,
            tune_hyperparams=not args.no_tune
        )
    
    # Evaluate model
    metrics = evaluate_model(classifier, X_val, y_val)
    
    # Train SHAP explainer
    explainer = train_shap_explainer(classifier, X_train)
    
    # Save artifacts
    save_model_artifacts(
        classifier, explainer, metrics,
        model_dir=args.model_dir,
        version=args.version
    )
    
    print("\n" + "=" * 60)
    print("Training completed successfully!")
    print("=" * 60)
    print(f"\nModel artifacts saved to {args.model_dir}/:")
    print(f"  - classifier_{args.version}.pkl")
    print(f"  - explainer_{args.version}.pkl")
    print(f"  - training_metrics_{args.version}.json")
    print("\nTo use the trained model:")
    print(f"  from scoring.ml_classifier import MLClassifier")
    print(f"  classifier = MLClassifier(model_dir='{args.model_dir}')")
    print(f"  classifier.load_model(version='{args.version}')")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
