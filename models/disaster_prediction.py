"""
ENHANCED Disaster prediction models with ensemble learning and advanced features
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class EnhancedDisasterPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.ensemble_models = {}
        
        # ENHANCED: More comprehensive features
        self.feature_names = {
            'flood': [
                'temperature', 'humidity', 'precipitation_24h', 'precipitation_7d',
                'pressure', 'wind_speed', 'elevation', 'river_distance',
                'temp_change_rate', 'pressure_change', 'soil_saturation'
            ],
            'drought': [
                'temperature', 'humidity', 'precipitation_30d', 'precipitation_90d',
                'pressure', 'wind_speed', 'vegetation_index', 'soil_moisture',
                'temp_avg_7d', 'evapotranspiration', 'humidity_avg'
            ],
            'heatwave': [
                'temperature', 'humidity', 'pressure', 'wind_speed',
                'temperature_trend', 'humidity_trend', 'urban_heat_index',
                'temp_max_7d', 'heat_index', 'consecutive_hot_days'
            ]
        }
        
        self.model_path = "data/models/"
        os.makedirs(self.model_path, exist_ok=True)
    
    def create_enhanced_training_data(self, disaster_type: str = 'flood', n_samples: int = 2000):
        """
        Create ENHANCED training data with more realistic patterns
        """
        np.random.seed(42)
        features = self.feature_names[disaster_type]
        
        if disaster_type == 'flood':
            # More realistic flood scenarios
            data = {
                'temperature': np.random.normal(25, 8, n_samples),
                'humidity': np.random.gamma(4, 20, n_samples),  # More realistic humidity
                'precipitation_24h': np.random.exponential(12, n_samples),
                'precipitation_7d': np.random.exponential(35, n_samples),
                'pressure': np.random.normal(1010, 15, n_samples),
                'wind_speed': np.random.exponential(15, n_samples),
                'elevation': np.random.uniform(0, 1000, n_samples),
                'river_distance': np.random.exponential(5000, n_samples),
                'temp_change_rate': np.random.normal(0, 2, n_samples),
                'pressure_change': np.random.normal(0, 5, n_samples),
                'soil_saturation': np.random.uniform(0, 100, n_samples)
            }
            
            df = pd.DataFrame(data)
            
            # ENHANCED: More complex decision rules
            labels = (
                (df['precipitation_24h'] > 30) |
                (df['precipitation_7d'] > 120) |
                ((df['precipitation_24h'] > 20) & (df['elevation'] < 150) & (df['soil_saturation'] > 70)) |
                ((df['precipitation_7d'] > 80) & (df['humidity'] > 85))
            ).astype(int)
            
        elif disaster_type == 'drought':
            data = {
                'temperature': np.random.normal(33, 12, n_samples),
                'humidity': np.random.normal(45, 22, n_samples),
                'precipitation_30d': np.random.exponential(15, n_samples),
                'precipitation_90d': np.random.exponential(45, n_samples),
                'pressure': np.random.normal(1018, 12, n_samples),
                'wind_speed': np.random.exponential(10, n_samples),
                'vegetation_index': np.random.beta(2, 5, n_samples),
                'soil_moisture': np.random.gamma(2, 20, n_samples),
                'temp_avg_7d': np.random.normal(33, 10, n_samples),
                'evapotranspiration': np.random.uniform(0, 10, n_samples),
                'humidity_avg': np.random.normal(45, 18, n_samples)
            }
            
            df = pd.DataFrame(data)
            labels = (
                ((df['precipitation_30d'] < 8) & (df['temperature'] > 32)) |
                ((df['precipitation_90d'] < 25) & (df['soil_moisture'] < 25) & (df['vegetation_index'] < 0.3)) |
                ((df['temp_avg_7d'] > 38) & (df['humidity_avg'] < 30))
            ).astype(int)
            
        else:  # heatwave
            data = {
                'temperature': np.random.normal(32, 14, n_samples),
                'humidity': np.random.normal(65, 28, n_samples),
                'pressure': np.random.normal(1008, 18, n_samples),
                'wind_speed': np.random.exponential(8, n_samples),
                'temperature_trend': np.random.normal(0, 3, n_samples),
                'humidity_trend': np.random.normal(0, 6, n_samples),
                'urban_heat_index': np.random.uniform(0, 12, n_samples),
                'temp_max_7d': np.random.normal(38, 12, n_samples),
                'heat_index': np.random.normal(35, 15, n_samples),
                'consecutive_hot_days': np.random.poisson(2, n_samples)
            }
            
            df = pd.DataFrame(data)
            labels = (
                (df['temperature'] > 42) |
                ((df['temp_max_7d'] > 40) & (df['consecutive_hot_days'] > 3)) |
                ((df['temperature'] > 37) & (df['humidity'] > 75) & (df['wind_speed'] < 5)) |
                ((df['heat_index'] > 45) & (df['urban_heat_index'] > 7))
            ).astype(int)
        
        return df[features], labels
    
    def train_ensemble_model(self, disaster_type: str = 'flood'):
        """
        Train ENSEMBLE model (multiple algorithms voting)
        """
        logger.info(f"Training ENHANCED {disaster_type} prediction model...")
        
        # Get enhanced training data
        X, y = self.create_enhanced_training_data(disaster_type, n_samples=3000)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Create ensemble of 3 different models
        rf_model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        
        gb_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        # Ensemble voting classifier
        ensemble = VotingClassifier(
            estimators=[
                ('rf', rf_model),
                ('gb', gb_model)
            ],
            voting='soft'  # Use probability voting
        )
        
        ensemble.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = ensemble.score(X_train_scaled, y_train)
        test_score = ensemble.score(X_test_scaled, y_test)
        
        logger.info(f"{disaster_type} ENSEMBLE - Train: {train_score:.3f}, Test: {test_score:.3f}")
        
        # Cross-validation
        cv_scores = cross_val_score(ensemble, X_train_scaled, y_train, cv=5)
        logger.info(f"{disaster_type} CV Score: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Save models
        self.ensemble_models[disaster_type] = ensemble
        self.scalers[disaster_type] = scaler
        
        # Save to disk
        model_file = os.path.join(self.model_path, f"{disaster_type}_ensemble.joblib")
        scaler_file = os.path.join(self.model_path, f"{disaster_type}_scaler.joblib")
        
        joblib.dump(ensemble, model_file)
        joblib.dump(scaler, scaler_file)
        
        logger.info(f"Enhanced model saved to {model_file}")
        return ensemble, scaler
    
    def load_model(self, disaster_type: str):
        """Load trained ensemble model"""
        try:
            model_file = os.path.join(self.model_path, f"{disaster_type}_ensemble.joblib")
            scaler_file = os.path.join(self.model_path, f"{disaster_type}_scaler.joblib")
            
            if os.path.exists(model_file) and os.path.exists(scaler_file):
                self.ensemble_models[disaster_type] = joblib.load(model_file)
                self.scalers[disaster_type] = joblib.load(scaler_file)
                logger.info(f"Loaded {disaster_type} ensemble model")
                return True
            else:
                logger.warning(f"Model not found for {disaster_type}, training...")
                self.train_ensemble_model(disaster_type)
                return True
        except Exception as e:
            logger.error(f"Error loading {disaster_type}: {e}")
            return False
    
    def predict_disaster_risk(self, weather_data: Dict, disaster_type: str = 'flood') -> Tuple[float, str, Dict]:
        """
        ENHANCED prediction with confidence and explanation
        
        Returns:
            Tuple of (risk_score, risk_level, details_dict)
        """
        try:
            # Load model if needed
            if disaster_type not in self.ensemble_models:
                self.load_model(disaster_type)
            
            model = self.ensemble_models[disaster_type]
            scaler = self.scalers[disaster_type]
            features = self.feature_names[disaster_type]
            
            # Prepare enhanced feature vector
            feature_vector = []
            for feature in features:
                if feature in weather_data:
                    feature_vector.append(weather_data[feature])
                else:
                    # Smart defaults based on feature type
                    default_values = self._get_default_feature_values(weather_data, feature)
                    feature_vector.append(default_values.get(feature, 0))
            
            # Scale and predict
            feature_vector = np.array(feature_vector).reshape(1, -1)
            feature_vector_scaled = scaler.transform(feature_vector)
            
            # Get prediction with probability
            risk_score = model.predict_proba(feature_vector_scaled)[0][1]
            
            # Determine risk level with finer granularity
            if risk_score < 0.25:
                risk_level = "Low"
                confidence = "High"
            elif risk_score < 0.5:
                risk_level = "Low-Medium"
                confidence = "Medium"
            elif risk_score < 0.65:
                risk_level = "Medium"
                confidence = "Medium"
            elif risk_score < 0.80:
                risk_level = "Medium-High"
                confidence = "Medium"
            else:
                risk_level = "High"
                confidence = "High"
            
            # Generate explanation
            explanation = self._generate_explanation(weather_data, disaster_type, risk_score)
            
            # Compile details
            details = {
                'risk_score': round(risk_score, 4),
                'risk_level': risk_level,
                'confidence': confidence,
                'explanation': explanation,
                'timestamp': datetime.now().isoformat()
            }
            
            return risk_score, risk_level, details
            
        except Exception as e:
            logger.error(f"Error predicting {disaster_type}: {e}")
            return 0.0, "Unknown", {'error': str(e)}
    
    def _get_default_feature_values(self, weather_data: Dict, feature: str) -> Dict:
        """Smart default values for missing features"""
        precip = weather_data.get('precipitation', 0)
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 60)
        
        return {
            'elevation': 100,
            'river_distance': 5000,
            'vegetation_index': 0.5,
            'soil_moisture': 50,
            'temperature_trend': 0,
            'humidity_trend': 0,
            'urban_heat_index': 2,
            'precipitation_24h': precip,
            'precipitation_7d': precip * 5,
            'precipitation_30d': precip * 15,
            'precipitation_90d': precip * 40,
            'temp_change_rate': 0,
            'pressure_change': 0,
            'soil_saturation': min(precip * 5, 100),
            'temp_avg_7d': temp,
            'evapotranspiration': max(temp - 20, 0) * 0.3,
            'humidity_avg': humidity,
            'temp_max_7d': temp + 3,
            'heat_index': temp + (humidity * 0.1),
            'consecutive_hot_days': 0
        }
    
    def _generate_explanation(self, weather_data: Dict, disaster_type: str, risk_score: float) -> str:
        """Generate human-readable explanation"""
        temp = weather_data.get('temperature', 0)
        humidity = weather_data.get('humidity', 0)
        precip = weather_data.get('precipitation', 0)
        wind = weather_data.get('wind_speed', 0)
        
        if disaster_type == 'flood':
            if risk_score > 0.7:
                return f"⚠️ HIGH RISK: Heavy precipitation ({precip:.1f}mm) with high humidity ({humidity:.0f}%). Flooding likely."
            elif risk_score > 0.4:
                return f"⚠️ MODERATE: Elevated precipitation ({precip:.1f}mm). Monitor water levels."
            else:
                return f"✅ LOW RISK: Normal precipitation levels ({precip:.1f}mm)."
        
        elif disaster_type == 'drought':
            if risk_score > 0.7:
                return f"⚠️ HIGH RISK: High temp ({temp:.1f}°C), low humidity ({humidity:.0f}%), minimal rain. Drought conditions."
            elif risk_score > 0.4:
                return f"⚠️ MODERATE: Below-average rainfall. Water conservation recommended."
            else:
                return f"✅ LOW RISK: Adequate moisture levels."
        
        else:  # heatwave
            if risk_score > 0.7:
                return f"⚠️ HIGH RISK: Extreme heat ({temp:.1f}°C) with high humidity ({humidity:.0f}%). Heat index dangerous."
            elif risk_score > 0.4:
                return f"⚠️ MODERATE: Elevated temperatures ({temp:.1f}°C). Stay hydrated."
            else:
                return f"✅ LOW RISK: Temperatures within normal range ({temp:.1f}°C)."
    
    def get_feature_importance(self, disaster_type: str) -> Optional[Dict]:
        """Get feature importance from ensemble"""
        try:
            if disaster_type not in self.ensemble_models:
                self.load_model(disaster_type)
            
            model = self.ensemble_models[disaster_type]
            features = self.feature_names[disaster_type]
            
            # Get importance from Random Forest (first estimator)
            rf_model = model.estimators_[0]
            importance = rf_model.feature_importances_
            
            # Sort by importance
            importance_dict = dict(zip(features, importance))
            sorted_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
            
            return sorted_importance
        except Exception as e:
            logger.error(f"Error getting importance: {e}")
            return None

# Global predictor instance
disaster_predictor = EnhancedDisasterPredictor()

def initialize_models():
    """Initialize all enhanced models"""
    print("🤖 Initializing ENHANCED disaster prediction models...")
    for disaster_type in ['flood', 'drought', 'heatwave']:
        try:
            disaster_predictor.load_model(disaster_type)
            print(f"✅ {disaster_type.capitalize()} ensemble model ready")
        except Exception as e:
            print(f"❌ Error with {disaster_type}: {e}")

if __name__ == "__main__":
    initialize_models()
    
    # Test
    test_weather = {
        'temperature': 28,
        'humidity': 85,
        'precipitation': 15,
        'pressure': 1010,
        'wind_speed': 12
    }
    
    for dtype in ['flood', 'drought', 'heatwave']:
        score, level, details = disaster_predictor.predict_disaster_risk(test_weather, dtype)
        print(f"\n{dtype.upper()}:")
        print(f"  Risk: {score:.3f} ({level})")
        print(f"  Confidence: {details['confidence']}")
        print(f"  {details['explanation']}")
