#!/usr/bin/env python3
"""
Outlier Detector - Anomaly Detection System for Forensic Analysis

This module implements the OutlierDetector class that provides
advanced outlier detection capabilities for forensic investigations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class OutlierMethod(Enum):
    """Outlier detection methods."""

    STATISTICAL = "statistical"  # Z-score, IQR methods
    ISOLATION_FOREST = "isolation_forest"  # Machine learning approach
    LOCAL_OUTLIER_FACTOR = "lof"  # Density-based approach
    ELLIPTIC_ENVELOPE = "elliptic"  # Robust covariance approach
    CLUSTERING = "clustering"  # DBSCAN clustering
    HYBRID = "hybrid"  # Combination of methods


class OutlierType(Enum):
    """Types of outliers."""

    GLOBAL = "global"  # Outlier across entire dataset
    LOCAL = "local"  # Outlier within local context
    CONTEXTUAL = "contextual"  # Outlier based on context
    COLLECTIVE = "collective"  # Group of outliers


class OutlierSeverity(Enum):
    """Outlier severity levels."""

    CRITICAL = "critical"  # High-risk outlier
    HIGH = "high"  # Significant outlier
    MEDIUM = "medium"  # Moderate outlier
    LOW = "low"  # Minor outlier
    INFO = "info"  # Informational outlier


@dataclass
class OutlierResult:
    """Outlier detection result."""

    record_id: str
    outlier_score: float
    outlier_type: OutlierType
    severity: OutlierSeverity
    method: OutlierMethod
    features: List[str]
    feature_scores: Dict[str, float]
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """__post_init__ function."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class DetectionConfig:
    """Configuration for outlier detection."""

    method: OutlierMethod
    threshold: float
    contamination: float = 0.1
    n_neighbors: int = 20
    random_state: int = 42
    enable_feature_scaling: bool = True
    enable_context_awareness: bool = True

    def __post_init__(self):
        """__post_init__ function."""
        if not self.threshold:
            if self.method == OutlierMethod.STATISTICAL:
                self.threshold = 3.0  # Z-score threshold
            elif self.method == OutlierMethod.ISOLATION_FOREST:
                self.threshold = -0.5  # Isolation Forest threshold
            else:
                self.threshold = 0.5


class OutlierDetector:
    """
    Advanced outlier detection system for forensic analysis.

    The OutlierDetector is responsible for:
    - Detecting anomalies in forensic data
    - Using multiple detection methods
    - Providing contextual outlier analysis
    - Generating risk assessments
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the OutlierDetector.Initialize the OutlierDetector."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.default_method = OutlierMethod(config.get("default_method", "hybrid"))
        self.enable_auto_threshold = config.get("enable_auto_threshold", True)
        self.context_window_size = config.get("context_window_size", 100)
        self.min_outlier_score = config.get("min_outlier_score", 0.5)

        # Detection models
        self.isolation_forest = None
        self.local_outlier_factor = None
        self.elliptic_envelope = None

        # Internal state
        self.detection_history: List[OutlierResult] = []
        self.feature_statistics: Dict[str, Dict[str, float]] = {}
        self.context_patterns: Dict[str, Any] = {}

        # Performance tracking
        self.total_records_processed = 0
        self.total_outliers_detected = 0
        self.average_processing_time = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("OutlierDetector initialized successfully")

    async def start(self):
        """Start the OutlierDetector.Start the OutlierDetector."""
        self.logger.info("Starting OutlierDetector...")

        # Initialize detection models
        await self._initialize_models()

        # Start background tasks
        asyncio.create_task(self._update_feature_statistics())
        asyncio.create_task(self._cleanup_old_results())

        self.logger.info("OutlierDetector started successfully")

    async def stop(self):
        """Stop the OutlierDetector.Stop the OutlierDetector."""
        self.logger.info("Stopping OutlierDetector...")
        self.logger.info("OutlierDetector stopped")

    async def detect_outliers(
        self,
        data: List[Dict[str, Any]],
        method: OutlierMethod = None,
        config: DetectionConfig = None,
    ) -> List[OutlierResult]:
        """Detect outliers in the provided data.Detect outliers in the provided data."""
        try:
            start_time = datetime.utcnow()

            if not data:
                return []

            # Use default method if none specified
            if not method:
                method = self.default_method

            # Use default config if none specified
            if not config:
                config = DetectionConfig(method=method)

            self.logger.info(
                f"Detecting outliers using {method.value} method for {len(data)} records"
            )

            # Detect outliers based on method
            if method == OutlierMethod.STATISTICAL:
                results = await self._statistical_detection(data, config)
            elif method == OutlierMethod.ISOLATION_FOREST:
                results = await self._isolation_forest_detection(data, config)
            elif method == OutlierMethod.LOCAL_OUTLIER_FACTOR:
                results = await self._lof_detection(data, config)
            elif method == OutlierMethod.ELLIPTIC_ENVELOPE:
                results = await self._elliptic_envelope_detection(data, config)
            elif method == OutlierMethod.CLUSTERING:
                results = await self._clustering_detection(data, config)
            elif method == OutlierMethod.HYBRID:
                results = await self._hybrid_detection(data, config)
            else:
                results = await self._statistical_detection(data, config)

            # Filter results by threshold
            filtered_results = [
                result
                for result in results
                if result.outlier_score >= self.min_outlier_score
            ]

            # Update statistics
            self.total_records_processed += len(data)
            self.total_outliers_detected += len(filtered_results)

            # Store results
            self.detection_history.extend(filtered_results)

            # Update processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_processing_time(processing_time)

            self.logger.info(
                f"Outlier detection completed: {len(filtered_results)} outliers found in {processing_time:.2f}s"
            )

            return filtered_results

        except Exception as e:
            self.logger.error(f"Error in outlier detection: {e}")
            return []

    async def _statistical_detection(
        self, data: List[Dict[str, Any]], config: DetectionConfig
    ) -> List[OutlierResult]:
        """Detect outliers using statistical methods (Z-score, IQR).Detect outliers using statistical methods (Z-score, IQR)."""
        try:
            results = []

            # Extract numerical features
            numerical_features = self._extract_numerical_features(data)

            if not numerical_features:
                return []

            # Calculate statistics for each feature
            feature_stats = {}
            for feature in numerical_features:
                values = [
                    record[feature]
                    for record in data
                    if feature in record and record[feature] is not None
                ]
                if values:
                    feature_stats[feature] = {
                        "mean": np.mean(values),
                        "std": np.std(values),
                        "q1": np.percentile(values, 25),
                        "q3": np.percentile(values, 75),
                        "iqr": np.percentile(values, 75) - np.percentile(values, 25),
                    }

            # Detect outliers for each record
            for i, record in enumerate(data):
                outlier_scores = {}
                outlier_features = []

                for feature in numerical_features:
                    if feature in record and feature in feature_stats:
                        value = record[feature]
                        stats = feature_stats[feature]

                        # Z-score method
                        if stats["std"] > 0:
                            z_score = abs((value - stats["mean"]) / stats["std"])
                            if z_score > config.threshold:
                                outlier_scores[feature] = z_score
                                outlier_features.append(feature)

                        # IQR method
                        lower_bound = stats["q1"] - 1.5 * stats["iqr"]
                        upper_bound = stats["q3"] + 1.5 * stats["iqr"]
                        if value < lower_bound or value > upper_bound:
                            iqr_score = (
                                abs(value - stats["mean"]) / stats["std"]
                                if stats["std"] > 0
                                else 0
                            )
                            outlier_scores[feature] = max(
                                outlier_scores.get(feature, 0), iqr_score
                            )
                            if feature not in outlier_features:
                                outlier_features.append(feature)

                if outlier_features:
                    # Calculate overall outlier score
                    overall_score = np.mean(list(outlier_scores.values()))
                    severity = self._determine_severity(overall_score)

                    result = OutlierResult(
                        record_id=record.get("id", f"record_{i}"),
                        outlier_score=overall_score,
                        outlier_type=OutlierType.GLOBAL,
                        severity=severity,
                        method=OutlierMethod.STATISTICAL,
                        features=outlier_features,
                        feature_scores=outlier_scores,
                        context={"detection_method": "statistical"},
                    )

                    results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"Error in statistical detection: {e}")
            return []

    async def _isolation_forest_detection(
        self, data: List[Dict[str, Any]], config: DetectionConfig
    ) -> List[OutlierResult]:
        """Detect outliers using Isolation Forest algorithm.Detect outliers using Isolation Forest algorithm."""
        try:
            results = []

            # Extract numerical features
            numerical_features = self._extract_numerical_features(data)

            if not numerical_features:
                return []

            # Prepare feature matrix
            feature_matrix = []
            valid_indices = []

            for i, record in enumerate(data):
                feature_vector = []
                is_valid = True

                for feature in numerical_features:
                    if feature in record and record[feature] is not None:
                        feature_vector.append(float(record[feature]))
                    else:
                        feature_vector.append(0.0)
                        is_valid = False

                if is_valid:
                    feature_matrix.append(feature_vector)
                    valid_indices.append(i)

            if not feature_matrix:
                return []

            # Convert to numpy array
            X = np.array(feature_matrix)

            # Initialize and fit Isolation Forest
            if not self.isolation_forest:
                self.isolation_forest = IsolationForest(
                    contamination=config.contamination, random_state=config.random_state
                )

            # Fit the model
            self.isolation_forest.fit(X)

            # Predict outlier scores
            outlier_scores = self.isolation_forest.decision_function(X)

            # Create results
            for i, score in enumerate(outlier_scores):
                if score < config.threshold:
                    record = data[valid_indices[i]]

                    # Calculate feature-specific scores
                    feature_scores = {}
                    for j, feature in enumerate(numerical_features):
                        feature_scores[feature] = abs(score)

                    severity = self._determine_severity(abs(score))

                    result = OutlierResult(
                        record_id=record.get("id", f"record_{valid_indices[i]}"),
                        outlier_score=abs(score),
                        outlier_type=OutlierType.GLOBAL,
                        severity=severity,
                        method=OutlierMethod.ISOLATION_FOREST,
                        features=numerical_features,
                        feature_scores=feature_scores,
                        context={"detection_method": "isolation_forest"},
                    )

                    results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"Error in Isolation Forest detection: {e}")
            return []

    async def _lof_detection(
        self, data: List[Dict[str, Any]], config: DetectionConfig
    ) -> List[OutlierResult]:
        """Detect outliers using Local Outlier Factor algorithm.Detect outliers using Local Outlier Factor algorithm."""
        try:
            results = []

            # Extract numerical features
            numerical_features = self._extract_numerical_features(data)

            if not numerical_features:
                return []

            # Prepare feature matrix
            feature_matrix = []
            valid_indices = []

            for i, record in enumerate(data):
                feature_vector = []
                is_valid = True

                for feature in numerical_features:
                    if feature in record and record[feature] is not None:
                        feature_vector.append(float(record[feature]))
                    else:
                        feature_vector.append(0.0)
                        is_valid = False

                if is_valid:
                    feature_matrix.append(feature_vector)
                    valid_indices.append(i)

            if not feature_matrix:
                return []

            # Convert to numpy array
            X = np.array(feature_matrix)

            # Initialize and fit Local Outlier Factor
            if not self.local_outlier_factor:
                self.local_outlier_factor = LocalOutlierFactor(
                    n_neighbors=config.n_neighbors, contamination=config.contamination
                )

            # Fit the model and predict
            outlier_scores = self.local_outlier_factor.fit_predict(X)

            # Create results
            for i, score in enumerate(outlier_scores):
                if score == -1:  # -1 indicates outlier
                    record = data[valid_indices[i]]

                    # Calculate feature-specific scores
                    feature_scores = {}
                    for j, feature in enumerate(numerical_features):
                        feature_scores[feature] = 1.0  # High score for outliers

                    severity = self._determine_severity(1.0)

                    result = OutlierResult(
                        record_id=record.get("id", f"record_{valid_indices[i]}"),
                        outlier_score=1.0,
                        outlier_type=OutlierType.LOCAL,
                        severity=severity,
                        method=OutlierMethod.LOCAL_OUTLIER_FACTOR,
                        features=numerical_features,
                        feature_scores=feature_scores,
                        context={"detection_method": "local_outlier_factor"},
                    )

                    results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"Error in LOF detection: {e}")
            return []

    async def _elliptic_envelope_detection(
        self, data: List[Dict[str, Any]], config: DetectionConfig
    ) -> List[OutlierResult]:
        """Detect outliers using Elliptic Envelope algorithm.Detect outliers using Elliptic Envelope algorithm."""
        try:
            results = []

            # Extract numerical features
            numerical_features = self._extract_numerical_features(data)

            if not numerical_features:
                return []

            # Prepare feature matrix
            feature_matrix = []
            valid_indices = []

            for i, record in enumerate(data):
                feature_vector = []
                is_valid = True

                for feature in numerical_features:
                    if feature in record and record[feature] is not None:
                        feature_vector.append(float(record[feature]))
                    else:
                        feature_vector.append(0.0)
                        is_valid = False

                if is_valid:
                    feature_matrix.append(feature_vector)
                    valid_indices.append(i)

            if not feature_matrix:
                return []

            # Convert to numpy array
            X = np.array(feature_matrix)

            # Initialize and fit Elliptic Envelope
            if not self.elliptic_envelope:
                self.elliptic_envelope = EllipticEnvelope(
                    contamination=config.contamination, random_state=config.random_state
                )

            # Fit the model
            self.elliptic_envelope.fit(X)

            # Predict outlier scores
            outlier_scores = self.elliptic_envelope.decision_function(X)

            # Create results
            for i, score in enumerate(outlier_scores):
                if score < config.threshold:
                    record = data[valid_indices[i]]

                    # Calculate feature-specific scores
                    feature_scores = {}
                    for j, feature in enumerate(numerical_features):
                        feature_scores[feature] = abs(score)

                    severity = self._determine_severity(abs(score))

                    result = OutlierResult(
                        record_id=record.get("id", f"record_{valid_indices[i]}"),
                        outlier_score=abs(score),
                        outlier_type=OutlierType.GLOBAL,
                        severity=severity,
                        method=OutlierMethod.ELLIPTIC_ENVELOPE,
                        features=numerical_features,
                        feature_scores=feature_scores,
                        context={"detection_method": "elliptic_envelope"},
                    )

                    results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"Error in Elliptic Envelope detection: {e}")
            return []

    async def _clustering_detection(
        self, data: List[Dict[str, Any]], config: DetectionConfig
    ) -> List[OutlierResult]:
        """Detect outliers using clustering-based approach.Detect outliers using clustering-based approach."""
        try:
            results = []

            # Extract numerical features
            numerical_features = self._extract_numerical_features(data)

            if not numerical_features:
                return []

            # Prepare feature matrix
            feature_matrix = []
            valid_indices = []

            for i, record in enumerate(data):
                feature_vector = []
                is_valid = True

                for feature in numerical_features:
                    if feature in record and record[feature] is not None:
                        feature_vector.append(float(record[feature]))
                    else:
                        feature_vector.append(0.0)
                        is_valid = False

                if is_valid:
                    feature_matrix.append(feature_vector)
                    valid_indices.append(i)

            if not feature_matrix:
                return []

            # Convert to numpy array
            X = np.array(feature_matrix)

            # Use DBSCAN for clustering

            dbscan = DBSCAN(eps=0.5, min_samples=5)
            cluster_labels = dbscan.fit_predict(X)

            # Find outliers (label -1)
            outlier_indices = [
                i for i, label in enumerate(cluster_labels) if label == -1
            ]

            # Create results
            for i in outlier_indices:
                record = data[valid_indices[i]]

                # Calculate feature-specific scores
                feature_scores = {}
                for j, feature in enumerate(numerical_features):
                    feature_scores[feature] = 1.0  # High score for outliers

                severity = self._determine_severity(1.0)

                result = OutlierResult(
                    record_id=record.get("id", f"record_{valid_indices[i]}"),
                    outlier_score=1.0,
                    outlier_type=OutlierType.COLLECTIVE,
                    severity=severity,
                    method=OutlierMethod.CLUSTERING,
                    features=numerical_features,
                    feature_scores=feature_scores,
                    context={"detection_method": "clustering", "cluster_label": -1},
                )

                results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"Error in clustering detection: {e}")
            return []

    async def _hybrid_detection(
        self, data: List[Dict[str, Any]], config: DetectionConfig
    ) -> List[OutlierResult]:
        """Detect outliers using hybrid approach combining multiple methods.Detect outliers using hybrid approach combining multiple methods."""
        try:
            results = []

            # Run multiple detection methods
            methods = [
                (
                    OutlierMethod.STATISTICAL,
                    await self._statistical_detection(data, config),
                ),
                (
                    OutlierMethod.ISOLATION_FOREST,
                    await self._isolation_forest_detection(data, config),
                ),
                (
                    OutlierMethod.LOCAL_OUTLIER_FACTOR,
                    await self._lof_detection(data, config),
                ),
            ]

            # Combine results
            record_scores = defaultdict(list)

            for method, method_results in methods:
                for result in method_results:
                    record_scores[result.record_id].append(
                        {
                            "method": method,
                            "score": result.outlier_score,
                            "features": result.features,
                        }
                    )

            # Create combined results
            for record_id, scores in record_scores.items():
                if len(scores) >= 2:  # At least 2 methods detected as outlier
                    # Calculate combined score
                    combined_score = np.mean([score["score"] for score in scores])

                    # Combine features
                    all_features = set()
                    for score in scores:
                        all_features.update(score["features"])

                    # Calculate feature scores
                    feature_scores = {}
                    for feature in all_features:
                        feature_scores[feature] = combined_score

                    severity = self._determine_severity(combined_score)

                    result = OutlierResult(
                        record_id=record_id,
                        outlier_score=combined_score,
                        outlier_type=OutlierType.GLOBAL,
                        severity=severity,
                        method=OutlierMethod.HYBRID,
                        features=list(all_features),
                        feature_scores=feature_scores,
                        context={
                            "detection_method": "hybrid",
                            "methods_used": [score["method"].value for score in scores],
                            "method_count": len(scores),
                        },
                    )

                    results.append(result)

            return results

        except Exception as e:
            self.logger.error(f"Error in hybrid detection: {e}")
            return []

    def _extract_numerical_features(self, data: List[Dict[str, Any]]) -> List[str]:
        """Extract numerical features from data.Extract numerical features from data."""
        numerical_features = set()

        for record in data:
            for key, value in record.items():
                if isinstance(value, (int, float)) and value is not None:
                    numerical_features.add(key)

        return list(numerical_features)

    def _determine_severity(self, score: float) -> OutlierSeverity:
        """Determine outlier severity based on score.Determine outlier severity based on score."""
        if score >= 3.0:
            return OutlierSeverity.CRITICAL
        elif score >= 2.5:
            return OutlierSeverity.HIGH
        elif score >= 2.0:
            return OutlierSeverity.MEDIUM
        elif score >= 1.5:
            return OutlierSeverity.LOW
        else:
            return OutlierSeverity.INFO

    async def _initialize_models(self):
        """Initialize machine learning models.Initialize machine learning models."""
        try:
            # Initialize Isolation Forest
            self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)

            # Initialize Local Outlier Factor
            self.local_outlier_factor = LocalOutlierFactor(
                n_neighbors=20, contamination=0.1
            )

            # Initialize Elliptic Envelope
            self.elliptic_envelope = EllipticEnvelope(
                contamination=0.1, random_state=42
            )

            self.logger.info("Machine learning models initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing models: {e}")

    async def _update_feature_statistics(self):
        """Update feature statistics periodically.Update feature statistics periodically."""
        while True:
            try:
                # This would update feature statistics based on new data
                await asyncio.sleep(3600)  # Update every hour

            except Exception as e:
                self.logger.error(f"Error updating feature statistics: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_old_results(self):
        """Clean up old detection results.Clean up old detection results."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=30)

                # Remove old results
                self.detection_history = [
                    result
                    for result in self.detection_history
                    if result.timestamp > cutoff_time
                ]

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up old results: {e}")
                await asyncio.sleep(3600)

    def _update_average_processing_time(self, new_time: float):
        """Update average processing time.Update average processing time."""
        self.average_processing_time = (
            self.average_processing_time * self.total_records_processed + new_time
        ) / (self.total_records_processed + 1)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics.Get performance metrics."""
        return {
            "total_records_processed": self.total_records_processed,
            "total_outliers_detected": self.total_outliers_detected,
            "average_processing_time": self.average_processing_time,
            "outlier_detection_rate": (
                self.total_outliers_detected / self.total_records_processed
                if self.total_records_processed > 0
                else 0
            ),
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "default_method": "hybrid",
        "enable_auto_threshold": True,
        "context_window_size": 100,
        "min_outlier_score": 0.5,
    }

    # Initialize outlier detector
    detector = OutlierDetector(config)

    print("OutlierDetector system initialized successfully!")
