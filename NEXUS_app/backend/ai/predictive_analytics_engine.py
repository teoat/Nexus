#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
AI-Powered Predictive Analytics Engine
Implements machine learning models to predict system failures, user behavior patterns, and resource utilization trends
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import tensorflow as tf
    from tensorflow import keras
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionType(Enum):
    SYSTEM_FAILURE = "system_failure"
    USER_BEHAVIOR = "user_behavior"
    RESOURCE_UTILIZATION = "resource_utilization"
    PERFORMANCE_DEGRADATION = "performance_degradation"

@dataclass
class PredictionResult:
    """Result of a prediction"""
    prediction_type: PredictionType
    confidence: float
    predicted_value: Any
    timestamp: datetime
    features_used: List[str]
    model_version: str
    accuracy_score: Optional[float] = None

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    response_time: float
    error_rate: float
    active_connections: int
    timestamp: datetime

@dataclass
class UserBehaviorData:
    """User behavior data for prediction"""
    user_id: str
    session_duration: float
    page_views: int
    actions_performed: int
    time_of_day: int
    day_of_week: int
    device_type: str
    location: str
    timestamp: datetime

class PredictiveAnalyticsEngine:
    """AI-Powered Predictive Analytics Engine"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the predictive analytics engine"""
        self.config = config or {}
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.model_versions = {}
        self.prediction_history = []
        
        # Initialize models
        self._initialize_models()
        
        logger.info("Predictive Analytics Engine initialized")
    
    def _initialize_models(self):
        """Initialize ML models for different prediction types"""
        if not ML_AVAILABLE:
            return
        
        try:
            # System Failure Prediction Model
            self.models[PredictionType.SYSTEM_FAILURE] = self._create_system_failure_model()
            self.scalers[PredictionType.SYSTEM_FAILURE] = StandardScaler()
            
            # User Behavior Prediction Model
            self.models[PredictionType.USER_BEHAVIOR] = self._create_user_behavior_model()
            self.scalers[PredictionType.USER_BEHAVIOR] = StandardScaler()
            
            # Resource Utilization Prediction Model
            self.models[PredictionType.RESOURCE_UTILIZATION] = self._create_resource_utilization_model()
            self.scalers[PredictionType.RESOURCE_UTILIZATION] = StandardScaler()
            
            # Performance Degradation Model
            self.models[PredictionType.PERFORMANCE_DEGRADATION] = self._create_performance_model()
            self.scalers[PredictionType.PERFORMANCE_DEGRADATION] = StandardScaler()
            
            logger.info("All ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
    
    def _create_system_failure_model(self):
        """Create neural network model for system failure prediction"""
        if not ML_AVAILABLE:
            return None
        
        model = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_shape=(7,)),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model
    
    def _create_user_behavior_model(self):
        """Create model for user behavior prediction"""
        if not ML_AVAILABLE:
            return None
        
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(8,)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(3, activation='softmax')  # 3 behavior categories
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _create_resource_utilization_model(self):
        """Create model for resource utilization prediction"""
        if not ML_AVAILABLE:
            return None
        
        model = keras.Sequential([
            keras.layers.LSTM(50, return_sequences=True, input_shape=(10, 7)),
            keras.layers.LSTM(50, return_sequences=False),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(25),
            keras.layers.Dense(1)
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _create_performance_model(self):
        """Create model for performance degradation prediction"""
        if not ML_AVAILABLE:
            return None
        
        model = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_shape=(6,)),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
        self.models = {
        }
        self.scalers = {
        }
    
    def train_models(self, training_data: Dict[PredictionType, List[Any]]):
        """Train all models with provided data"""
        logger.info("Starting model training...")
        
        for prediction_type, data in training_data.items():
            try:
                    self._train_model(prediction_type, data)
                    logger.info(f"Model trained for {prediction_type.value}")
                else:
            except Exception as e:
                logger.error(f"Error training {prediction_type.value}: {e}")
        
        logger.info("Model training completed")
    
    def _train_model(self, prediction_type: PredictionType, data: List[Any]):
            return
        
        # Convert data to appropriate format
        X, y = self._prepare_training_data(prediction_type, data)
        
        if X is None or y is None:
            logger.warning(f"No valid training data for {prediction_type.value}")
            return
        
        # Split data
        
        # Scale features
        X_train_scaled = self.scalers[prediction_type].fit_transform(X_train)
        
        # Train model
        if prediction_type == PredictionType.RESOURCE_UTILIZATION:
            # Reshape for LSTM
            X_train_scaled = X_train_scaled.reshape((X_train_scaled.shape[0], 10, 7))
        
        history = self.models[prediction_type].fit(
            X_train_scaled, y_train,
            epochs=50,
            batch_size=32,
            verbose=0
        )
        
        # Evaluate model
        
        if prediction_type in [PredictionType.SYSTEM_FAILURE, PredictionType.PERFORMANCE_DEGRADATION]:
            predictions = (predictions > 0.5).astype(int)
        else:
        
        self.model_versions[prediction_type] = f"v1.0_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Model {prediction_type.value} trained with accuracy: {accuracy:.4f}")
    
    def _prepare_training_data(self, prediction_type: PredictionType, data: List[Any]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        if not data:
            return None, None
        
        if prediction_type == PredictionType.SYSTEM_FAILURE:
            return self._prepare_system_failure_data(data)
        elif prediction_type == PredictionType.USER_BEHAVIOR:
            return self._prepare_user_behavior_data(data)
        elif prediction_type == PredictionType.RESOURCE_UTILIZATION:
            return self._prepare_resource_utilization_data(data)
        elif prediction_type == PredictionType.PERFORMANCE_DEGRADATION:
            return self._prepare_performance_data(data)
        
        return None, None
    
    def _prepare_system_failure_data(self, data: List[SystemMetrics]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare system failure training data"""
        features = []
        labels = []
        
        for i, metric in enumerate(data):
            if i < len(data) - 1:  # Not the last item
                features.append([
                    metric.cpu_usage,
                    metric.memory_usage,
                    metric.disk_usage,
                    metric.network_io,
                    metric.response_time,
                    metric.error_rate,
                    metric.active_connections
                ])
                
                # Simple failure prediction: high error rate or resource usage
                failure = 1 if (metric.error_rate > 0.1 or 
                              metric.cpu_usage > 0.9 or 
                              metric.memory_usage > 0.9) else 0
                labels.append(failure)
        
        return np.array(features), np.array(labels)
    
    def _prepare_user_behavior_data(self, data: List[UserBehaviorData]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare user behavior training data"""
        features = []
        labels = []
        
        for behavior in data:
            features.append([
                behavior.session_duration,
                behavior.page_views,
                behavior.actions_performed,
                behavior.time_of_day,
                behavior.day_of_week,
                1 if behavior.device_type == 'mobile' else 0,
                1 if behavior.location == 'US' else 0,
                behavior.timestamp.hour
            ])
            
            # Categorize behavior: 0=low engagement, 1=medium, 2=high
            if behavior.session_duration > 1800 and behavior.page_views > 10:
                labels.append(2)  # High engagement
            elif behavior.session_duration > 600 and behavior.page_views > 5:
                labels.append(1)  # Medium engagement
            else:
                labels.append(0)  # Low engagement
        
        # Convert to categorical
        labels_categorical = keras.utils.to_categorical(labels, num_classes=3)
        
        return np.array(features), labels_categorical
    
    def _prepare_resource_utilization_data(self, data: List[SystemMetrics]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare resource utilization training data"""
        features = []
        labels = []
        
        # Create sequences of 10 time steps
        for i in range(len(data) - 10):
            sequence = []
            for j in range(10):
                metric = data[i + j]
                sequence.append([
                    metric.cpu_usage,
                    metric.memory_usage,
                    metric.disk_usage,
                    metric.network_io,
                    metric.response_time,
                    metric.error_rate,
                    metric.active_connections
                ])
            
            features.append(sequence)
            # Predict next CPU usage
            labels.append(data[i + 10].cpu_usage)
        
        return np.array(features), np.array(labels)
    
    def _prepare_performance_data(self, data: List[SystemMetrics]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare performance degradation training data"""
        features = []
        labels = []
        
        for metric in data:
            features.append([
                metric.response_time,
                metric.error_rate,
                metric.cpu_usage,
                metric.memory_usage,
                metric.active_connections,
                metric.network_io
            ])
            
            # Performance degradation: high response time or error rate
            degradation = 1 if (metric.response_time > 2.0 or metric.error_rate > 0.05) else 0
            labels.append(degradation)
        
        return np.array(features), np.array(labels)
    
    def predict_system_failure(self, metrics: SystemMetrics) -> PredictionResult:
        """Predict system failure probability"""
        features = np.array([[
            metrics.cpu_usage,
            metrics.memory_usage,
            metrics.disk_usage,
            metrics.network_io,
            metrics.response_time,
            metrics.error_rate,
            metrics.active_connections
        ]])
        
            features_scaled = self.scalers[PredictionType.SYSTEM_FAILURE].transform(features)
            prediction = self.models[PredictionType.SYSTEM_FAILURE].predict(features_scaled)[0][0]
        else:
        
        result = PredictionResult(
            prediction_type=PredictionType.SYSTEM_FAILURE,
            confidence=float(prediction),
            predicted_value=prediction > 0.5,
            timestamp=datetime.now(),
            features_used=['cpu_usage', 'memory_usage', 'disk_usage', 'network_io', 'response_time', 'error_rate', 'active_connections'],
        )
        
        self.prediction_history.append(result)
        return result
    
    def predict_user_behavior(self, behavior_data: UserBehaviorData) -> PredictionResult:
        """Predict user behavior category"""
        features = np.array([[
            behavior_data.session_duration,
            behavior_data.page_views,
            behavior_data.actions_performed,
            behavior_data.time_of_day,
            behavior_data.day_of_week,
            1 if behavior_data.device_type == 'mobile' else 0,
            1 if behavior_data.location == 'US' else 0,
            behavior_data.timestamp.hour
        ]])
        
            features_scaled = self.scalers[PredictionType.USER_BEHAVIOR].transform(features)
            prediction = self.models[PredictionType.USER_BEHAVIOR].predict(features_scaled)[0]
            predicted_class = np.argmax(prediction)
            confidence = float(np.max(prediction))
        else:
        
        result = PredictionResult(
            prediction_type=PredictionType.USER_BEHAVIOR,
            confidence=confidence,
            predicted_value=predicted_class,
            timestamp=datetime.now(),
            features_used=['session_duration', 'page_views', 'actions_performed', 'time_of_day', 'day_of_week', 'device_type', 'location', 'hour'],
        )
        
        self.prediction_history.append(result)
        return result
    
    def predict_resource_utilization(self, metrics_history: List[SystemMetrics]) -> PredictionResult:
        """Predict future resource utilization"""
        if len(metrics_history) < 10:
            # Not enough data for prediction
            return PredictionResult(
                prediction_type=PredictionType.RESOURCE_UTILIZATION,
                confidence=0.0,
                predicted_value=0.5,
                timestamp=datetime.now(),
                features_used=[],
                model_version="insufficient_data"
            )
        
        # Prepare sequence data
        sequence = []
        for metric in metrics_history[-10:]:
            sequence.append([
                metric.cpu_usage,
                metric.memory_usage,
                metric.disk_usage,
                metric.network_io,
                metric.response_time,
                metric.error_rate,
                metric.active_connections
            ])
        
        features = np.array([sequence])
        
            prediction = self.models[PredictionType.RESOURCE_UTILIZATION].predict(features)[0][0]
            confidence = 0.8
        else:
        
        result = PredictionResult(
            prediction_type=PredictionType.RESOURCE_UTILIZATION,
            confidence=confidence,
            predicted_value=float(prediction),
            timestamp=datetime.now(),
            features_used=['cpu_usage', 'memory_usage', 'disk_usage', 'network_io', 'response_time', 'error_rate', 'active_connections'],
        )
        
        self.prediction_history.append(result)
        return result
    
    def get_prediction_accuracy(self, prediction_type: PredictionType) -> float:
        if prediction_type not in self.model_versions:
            return 0.0
        
        # Calculate accuracy based on recent predictions
        recent_predictions = [p for p in self.prediction_history 
                            if p.prediction_type == prediction_type 
                            and p.timestamp > datetime.now() - timedelta(hours=24)]
        
        if not recent_predictions:
            return 0.0
        
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        status = {
            "total_models": len(self.models),
            "ml_available": ML_AVAILABLE,
            "models": {}
        }
        
        for prediction_type, model in self.models.items():
            status["models"][prediction_type.value] = {
                "version": self.model_versions.get(prediction_type, "unknown"),
                "accuracy": self.get_prediction_accuracy(prediction_type),
                "last_prediction": len([p for p in self.prediction_history if p.prediction_type == prediction_type])
            }
        
        return status
    
    def export_predictions(self, filepath: str):
        """Export prediction history to file"""
        data = []
        for prediction in self.prediction_history:
            data.append({
                "prediction_type": prediction.prediction_type.value,
                "confidence": prediction.confidence,
                "predicted_value": prediction.predicted_value,
                "timestamp": prediction.timestamp.isoformat(),
                "features_used": prediction.features_used,
                "model_version": prediction.model_version
            })
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Predictions exported to {filepath}")

    
    # Initialize engine
    engine = PredictiveAnalyticsEngine()
    
    
    # System metrics data
    system_data = []
    for i in range(100):
        system_data.append(SystemMetrics(
            cpu_usage=np.random.uniform(0.1, 0.9),
            memory_usage=np.random.uniform(0.2, 0.8),
            disk_usage=np.random.uniform(0.1, 0.7),
            network_io=np.random.uniform(0.0, 1.0),
            response_time=np.random.uniform(0.1, 3.0),
            error_rate=np.random.uniform(0.0, 0.2),
            active_connections=np.random.randint(10, 1000),
            timestamp=datetime.now() - timedelta(hours=100-i)
        ))
    
    # User behavior data
    user_data = []
    for i in range(100):
        user_data.append(UserBehaviorData(
            user_id=f"user_{i}",
            session_duration=np.random.uniform(60, 3600),
            page_views=np.random.randint(1, 50),
            actions_performed=np.random.randint(1, 100),
            time_of_day=np.random.randint(0, 24),
            day_of_week=np.random.randint(0, 7),
            device_type=np.random.choice(['mobile', 'desktop', 'tablet']),
            location=np.random.choice(['US', 'EU', 'AS']),
            timestamp=datetime.now() - timedelta(hours=100-i)
        ))
    
    # Train models
    training_data = {
        PredictionType.SYSTEM_FAILURE: system_data,
        PredictionType.USER_BEHAVIOR: user_data,
        PredictionType.RESOURCE_UTILIZATION: system_data,
        PredictionType.PERFORMANCE_DEGRADATION: system_data
    }
    
    print("🤖 Training ML models...")
    engine.train_models(training_data)
    
    
    
    print(f"   System Failure Prediction: {failure_prediction.predicted_value} (Confidence: {failure_prediction.confidence:.2f})")
    
    
    print(f"   User Behavior Prediction: {behavior_prediction.predicted_value} (Confidence: {behavior_prediction.confidence:.2f})")
    
    
    # Get model status
    print("\n📈 Model Status:")
    status = engine.get_model_status()
    for model_name, model_info in status["models"].items():
        print(f"   {model_name}: {model_info['type']} v{model_info['version']} (Accuracy: {model_info['accuracy']:.2f})")
    
    print(f"\n✅ Predictive Analytics Engine ready!")
    print(f"   Total Predictions Made: {len(engine.prediction_history)}")
    print(f"   ML Libraries Available: {ML_AVAILABLE}")

if __name__ == "__main__":
    main()
