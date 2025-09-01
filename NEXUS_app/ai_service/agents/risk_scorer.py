#!/usr/bin/env python3
"""
Risk Scorer - Advanced Risk Assessment and Scoring System

This module implements the RiskScorer class that provides
comprehensive risk assessment and scoring capabilities for
fraud detection and risk management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class RiskCategory(Enum):
    """Risk categories for classification."""

    LOW = "low"  # Low risk
    MEDIUM = "medium"  # Medium risk
    HIGH = "high"  # High risk
    CRITICAL = "critical"  # Critical risk


class RiskFactor(Enum):
    """Types of risk factors."""

    FINANCIAL = "financial"  # Financial risk factors
    BEHAVIORAL = "behavioral"  # Behavioral risk factors
    NETWORK = "network"  # Network risk factors
    TEMPORAL = "temporal"  # Temporal risk factors
    GEOGRAPHIC = "geographic"  # Geographic risk factors
    DOCUMENTARY = "documentary"  # Documentary risk factors
    COMPLIANCE = "compliance"  # Compliance risk factors
    TECHNICAL = "technical"  # Technical risk factors


class ScoringMethod(Enum):
    """Risk scoring methods."""

    RULE_BASED = "rule_based"  # Rule-based scoring
    MACHINE_LEARNING = "machine_learning"  # ML-based scoring
    HYBRID = "hybrid"  # Hybrid approach
    STATISTICAL = "statistical"  # Statistical scoring
    EXPERT_SYSTEM = "expert_system"  # Expert system scoring


@dataclass
class RiskFactor:
    """A risk factor with its score and metadata."""

    id: str
    factor_type: RiskFactor
    name: str
    score: float
    weight: float
    description: str
    evidence: Dict[str, Any]
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """__post_init__ function."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class RiskAssessment:
    """Complete risk assessment for an entity."""

    entity_id: str
    overall_risk_score: float
    risk_category: RiskCategory
    risk_factors: List[RiskFactor]
    scoring_method: ScoringMethod
    confidence: float
    assessment_time: datetime
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """__post_init__ function."""
        if not self.assessment_time:
            self.assessment_time = datetime.utcnow()


@dataclass
class RiskModel:
    """Risk scoring model configuration."""

    id: str
    name: str
    method: ScoringMethod
    parameters: Dict[str, Any]
    training_data_size: int
    accuracy: float
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class RiskScorer:
    """
    Comprehensive risk scoring system for fraud detection.

    The RiskScorer is responsible for:
    - Assessing risk across multiple dimensions
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the RiskScorer.Initialize the RiskScorer."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.default_scoring_method = ScoringMethod.HYBRID
        self.risk_thresholds = config.get(
            "risk_thresholds", {"low": 0.3, "medium": 0.6, "high": 0.8, "critical": 0.9}
        )
        self.min_confidence = config.get("min_confidence", 0.7)

        # Risk models
        self.risk_models: Dict[str, RiskModel] = {}
        self.ml_models: Dict[str, Any] = {}
        self.scalers: Dict[str, StandardScaler] = {}

        # Risk factors and assessments
        self.risk_factors: Dict[str, RiskFactor] = {}
        self.risk_assessments: Dict[str, RiskAssessment] = {}

        # Performance tracking
        self.total_assessments = 0
        self.average_assessment_time = 0.0
        self.model_accuracy = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("RiskScorer initialized successfully")

    async def start(self):
        """Start the RiskScorer.Start the RiskScorer."""
        self.logger.info("Starting RiskScorer...")

        # Initialize risk models
        await self._initialize_risk_models()

        # Start background tasks
        asyncio.create_task(self._update_model_accuracy())
        asyncio.create_task(self._cleanup_old_data())

        self.logger.info("RiskScorer started successfully")

    async def stop(self):
        """Stop the RiskScorer.Stop the RiskScorer."""
        self.logger.info("Stopping RiskScorer...")
        self.logger.info("RiskScorer stopped")

    async def assess_risk(
        self,
        entity_id: str,
        entity_data: Dict[str, Any],
        scoring_method: ScoringMethod = None,
    ) -> RiskAssessment:
        """Perform comprehensive risk assessment for an entity.Perform comprehensive risk assessment for an entity."""
        try:
            start_time = datetime.utcnow()

            if not scoring_method:
                scoring_method = self.default_scoring_method

            self.logger.info(f"Starting risk assessment for entity: {entity_id}")

            # Extract risk factors
            risk_factors = await self._extract_risk_factors(entity_data)

            # Calculate risk score based on method
            if scoring_method == ScoringMethod.RULE_BASED:
                risk_score = await self._calculate_rule_based_score(risk_factors)
            elif scoring_method == ScoringMethod.MACHINE_LEARNING:
                risk_score = await self._calculate_ml_score(entity_data, risk_factors)
            elif scoring_method == ScoringMethod.HYBRID:
                rule_score = await self._calculate_rule_based_score(risk_factors)
                ml_score = await self._calculate_ml_score(entity_data, risk_factors)
                risk_score = (rule_score + ml_score) / 2
            elif scoring_method == ScoringMethod.STATISTICAL:
                risk_score = await self._calculate_statistical_score(risk_factors)
            else:
                risk_score = await self._calculate_rule_based_score(risk_factors)

            # Determine risk category
            risk_category = self._categorize_risk(risk_score)

            # Calculate confidence
            confidence = self._calculate_confidence(risk_factors, scoring_method)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                risk_factors, risk_score
            )

            # Create risk assessment
            assessment = RiskAssessment(
                entity_id=entity_id,
                overall_risk_score=risk_score,
                risk_category=risk_category,
                risk_factors=risk_factors,
                scoring_method=scoring_method,
                confidence=confidence,
                assessment_time=datetime.utcnow(),
                recommendations=recommendations,
            )

            # Store assessment
            self.risk_assessments[entity_id] = assessment

            # Update statistics
            self.total_assessments += 1

            # Update processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_assessment_time(processing_time)

            self.logger.info(
                f"Risk assessment completed: {entity_id} - Score: {risk_score:.3f}, Category: {risk_category.value}"
            )

            return assessment

        except Exception as e:
            self.logger.error(f"Error in risk assessment for {entity_id}: {e}")
            raise

    async def _extract_risk_factors(
        self, entity_data: Dict[str, Any]
    ) -> List[RiskFactor]:
        """Extract risk factors from entity data.Extract risk factors from entity data."""
        try:
            risk_factors = []

            # Financial risk factors
            financial_factors = self._extract_financial_risk_factors(entity_data)
            risk_factors.extend(financial_factors)

            # Behavioral risk factors
            behavioral_factors = self._extract_behavioral_risk_factors(entity_data)
            risk_factors.extend(behavioral_factors)

            # Network risk factors
            network_factors = self._extract_network_risk_factors(entity_data)
            risk_factors.extend(network_factors)

            # Temporal risk factors
            temporal_factors = self._extract_temporal_risk_factors(entity_data)
            risk_factors.extend(temporal_factors)

            # Geographic risk factors
            geographic_factors = self._extract_geographic_risk_factors(entity_data)
            risk_factors.extend(geographic_factors)

            # Documentary risk factors
            documentary_factors = self._extract_documentary_risk_factors(entity_data)
            risk_factors.extend(documentary_factors)

            # Compliance risk factors
            compliance_factors = self._extract_compliance_risk_factors(entity_data)
            risk_factors.extend(compliance_factors)

            # Technical risk factors
            technical_factors = self._extract_technical_risk_factors(entity_data)
            risk_factors.extend(technical_factors)

            return risk_factors

        except Exception as e:
            self.logger.error(f"Error extracting risk factors: {e}")
            return []

    def _extract_financial_risk_factors(
        self, entity_data: Dict[str, Any]
    ) -> List[RiskFactor]:
        """Extract financial risk factors.Extract financial risk factors."""
        try:
            factors = []

            # Transaction amount risk
            if "transaction_amount" in entity_data:
                amount = entity_data["transaction_amount"]
                if amount > 100000:  # $100K threshold
                    factor = RiskFactor(
                        id=f"financial_amount_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.FINANCIAL,
                        name="High Transaction Amount",
                        score=min(1.0, amount / 1000000),  # Scale to 0-1
                        weight=0.3,
                        description=f"Transaction amount ${amount:,.2f} exceeds risk threshold",
                        evidence={"amount": amount, "threshold": 100000},
                        confidence=0.9,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            # Transaction frequency risk
            if "transaction_count" in entity_data:
                count = entity_data["transaction_count"]
                if count > 50:  # High frequency threshold
                    factor = RiskFactor(
                        id=f"financial_frequency_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.FINANCIAL,
                        name="High Transaction Frequency",
                        score=min(1.0, count / 100),  # Scale to 0-1
                        weight=0.2,
                        description=f"Transaction count {count} exceeds normal frequency",
                        evidence={"count": count, "threshold": 50},
                        confidence=0.8,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            # Balance risk
            if "account_balance" in entity_data:
                balance = entity_data["account_balance"]
                if balance < 0:  # Negative balance
                    factor = RiskFactor(
                        id=f"financial_balance_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.FINANCIAL,
                        name="Negative Account Balance",
                        score=0.8,
                        weight=0.4,
                        description=f"Account balance ${balance:,.2f} is negative",
                        evidence={"balance": balance},
                        confidence=0.95,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            return factors

        except Exception as e:
            self.logger.error(f"Error extracting financial risk factors: {e}")
            return []

    def _extract_behavioral_risk_factors(
        self, entity_data: Dict[str, Any]
    ) -> List[RiskFactor]:
        """Extract behavioral risk factors.Extract behavioral risk factors."""
        try:
            factors = []

            # Login pattern risk
            if "login_attempts" in entity_data:
                attempts = entity_data["login_attempts"]
                if attempts > 10:  # Multiple login attempts
                    factor = RiskFactor(
                        id=f"behavioral_login_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.BEHAVIORAL,
                        name="Multiple Login Attempts",
                        score=min(1.0, attempts / 20),  # Scale to 0-1
                        weight=0.3,
                        description=f"Multiple login attempts: {attempts}",
                        evidence={"attempts": attempts, "threshold": 10},
                        confidence=0.8,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            # Session duration risk
            if "session_duration" in entity_data:
                duration = entity_data["session_duration"]
                if duration > 3600:  # 1 hour threshold
                    factor = RiskFactor(
                        id=f"behavioral_session_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.BEHAVIORAL,
                        name="Long Session Duration",
                        score=min(1.0, duration / 7200),  # Scale to 0-1
                        weight=0.2,
                        description=f"Session duration {duration}s exceeds normal",
                        evidence={"duration": duration, "threshold": 3600},
                        confidence=0.7,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            # Unusual time activity
            if "last_activity_hour" in entity_data:
                hour = entity_data["last_activity_hour"]
                if hour < 6 or hour > 22:  # Outside normal hours
                    factor = RiskFactor(
                        id=f"behavioral_time_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.BEHAVIORAL,
                        name="Unusual Activity Time",
                        score=0.6,
                        weight=0.2,
                        description=f"Activity at unusual hour: {hour}:00",
                        evidence={"hour": hour, "normal_range": "6:00-22:00"},
                        confidence=0.8,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            return factors

        except Exception as e:
            self.logger.error(f"Error extracting behavioral risk factors: {e}")
            return []

    def _extract_network_risk_factors(
        self, entity_data: Dict[str, Any]
    ) -> List[RiskFactor]:
        """Extract network risk factors.Extract network risk factors."""
        try:
            factors = []

            # Connection count risk
            if "connection_count" in entity_data:
                connections = entity_data["connection_count"]
                if connections > 100:  # High connection count
                    factor = RiskFactor(
                        id=f"network_connections_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.NETWORK,
                        name="High Connection Count",
                        score=min(1.0, connections / 500),  # Scale to 0-1
                        weight=0.3,
                        description=f"High number of network connections: {connections}",
                        evidence={"connections": connections, "threshold": 100},
                        confidence=0.8,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            # Suspicious IP addresses
            if "suspicious_ips" in entity_data:
                suspicious_count = len(entity_data["suspicious_ips"])
                if suspicious_count > 0:
                    factor = RiskFactor(
                        id=f"network_suspicious_ips_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.NETWORK,
                        name="Suspicious IP Addresses",
                        score=min(1.0, suspicious_count / 5),  # Scale to 0-1
                        weight=0.4,
                        description=f"Connected to {suspicious_count} suspicious IP addresses",
                        evidence={"suspicious_ips": entity_data["suspicious_ips"]},
                        confidence=0.9,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            return factors

        except Exception as e:
            self.logger.error(f"Error extracting network risk factors: {e}")
            return []

    def _extract_temporal_risk_factors(
        self, entity_data: Dict[str, Any]
    ) -> List[RiskFactor]:
        """Extract temporal risk factors.Extract temporal risk factors."""
        try:
            factors = []

            # Recent activity risk
            if "last_activity" in entity_data:
                last_activity = entity_data["last_activity"]
                if isinstance(last_activity, str):
                    last_activity = datetime.fromisoformat(last_activity)

                time_diff = datetime.utcnow() - last_activity
                if time_diff.days > 30:  # Inactive for 30+ days
                    factor = RiskFactor(
                        id=f"temporal_inactivity_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.TEMPORAL,
                        name="Account Inactivity",
                        score=min(1.0, time_diff.days / 90),  # Scale to 0-1
                        weight=0.2,
                        description=f"Account inactive for {time_diff.days} days",
                        evidence={"inactive_days": time_diff.days, "threshold": 30},
                        confidence=0.9,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            # Time-based pattern risk
            if "activity_hours" in entity_data:
                activity_hours = entity_data["activity_hours"]
                if len(activity_hours) > 0:
                    # Check for 24/7 activity (suspicious)
                    if len(activity_hours) == 24:
                        factor = RiskFactor(
                            id=f"temporal_24_7_{datetime.utcnow().timestamp()}",
                            factor_type=RiskFactor.TEMPORAL,
                            name="24/7 Activity Pattern",
                            score=0.8,
                            weight=0.3,
                            description="Activity detected 24/7 (suspicious pattern)",
                            evidence={"activity_hours": activity_hours},
                            confidence=0.8,
                            timestamp=datetime.utcnow(),
                        )
                        factors.append(factor)

            return factors

        except Exception as e:
            self.logger.error(f"Error extracting temporal risk factors: {e}")
            return []

    def _extract_geographic_risk_factors(
        self, entity_data: Dict[str, Any]
    ) -> List[RiskFactor]:
        """Extract geographic risk factors.Extract geographic risk factors."""
        try:
            factors = []

            # Multiple locations risk
            if "locations" in entity_data:
                locations = entity_data["locations"]
                if len(locations) > 3:  # Multiple locations
                    factor = RiskFactor(
                        id=f"geographic_multiple_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.GEOGRAPHIC,
                        name="Multiple Geographic Locations",
                        score=min(1.0, len(locations) / 10),  # Scale to 0-1
                        weight=0.3,
                        description=f"Activity from {len(locations)} different locations",
                        evidence={
                            "location_count": len(locations),
                            "locations": locations,
                        },
                        confidence=0.8,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            # High-risk locations
            if "high_risk_locations" in entity_data:
                high_risk_count = len(entity_data["high_risk_locations"])
                if high_risk_count > 0:
                    factor = RiskFactor(
                        id=f"geographic_high_risk_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.GEOGRAPHIC,
                        name="High-Risk Geographic Locations",
                        score=min(1.0, high_risk_count / 3),  # Scale to 0-1
                        weight=0.4,
                        description=f"Activity from {high_risk_count} high-risk locations",
                        evidence={
                            "high_risk_locations": entity_data["high_risk_locations"]
                        },
                        confidence=0.9,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            return factors

        except Exception as e:
            self.logger.error(f"Error extracting geographic risk factors: {e}")
            return []

    def _extract_documentary_risk_factors(
        self, entity_data: Dict[str, Any]
    ) -> List[RiskFactor]:
        """Extract documentary risk factors.Extract documentary risk factors."""
        try:
            factors = []

            # Missing documents
            if "missing_documents" in entity_data:
                missing_count = len(entity_data["missing_documents"])
                if missing_count > 0:
                    factor = RiskFactor(
                        id=f"documentary_missing_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.DOCUMENTARY,
                        name="Missing Required Documents",
                        score=min(1.0, missing_count / 5),  # Scale to 0-1
                        weight=0.3,
                        description=f"Missing {missing_count} required documents",
                        evidence={
                            "missing_documents": entity_data["missing_documents"]
                        },
                        confidence=0.9,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            # Document verification issues
            if "verification_issues" in entity_data:
                issues = entity_data["verification_issues"]
                if len(issues) > 0:
                    factor = RiskFactor(
                        id=f"documentary_verification_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.DOCUMENTARY,
                        name="Document Verification Issues",
                        score=min(1.0, len(issues) / 3),  # Scale to 0-1
                        weight=0.4,
                        description=f"Document verification issues: {len(issues)} problems",
                        evidence={"verification_issues": issues},
                        confidence=0.8,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            return factors

        except Exception as e:
            self.logger.error(f"Error extracting documentary risk factors: {e}")
            return []

    def _extract_compliance_risk_factors(
        self, entity_data: Dict[str, Any]
    ) -> List[RiskFactor]:
        """Extract compliance risk factors.Extract compliance risk factors."""
        try:
            factors = []

            # Compliance violations
            if "compliance_violations" in entity_data:
                violations = entity_data["compliance_violations"]
                if len(violations) > 0:
                    factor = RiskFactor(
                        id=f"compliance_violations_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.COMPLIANCE,
                        name="Compliance Violations",
                        score=min(1.0, len(violations) / 5),  # Scale to 0-1
                        weight=0.5,
                        description=f"Compliance violations: {len(violations)} issues",
                        evidence={"violations": violations},
                        confidence=0.9,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            # Regulatory flags
            if "regulatory_flags" in entity_data:
                flags = entity_data["regulatory_flags"]
                if len(flags) > 0:
                    factor = RiskFactor(
                        id=f"compliance_regulatory_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.COMPLIANCE,
                        name="Regulatory Flags",
                        score=min(1.0, len(flags) / 3),  # Scale to 0-1
                        weight=0.4,
                        description=f"Regulatory flags: {len(flags)} issues",
                        evidence={"regulatory_flags": flags},
                        confidence=0.8,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            return factors

        except Exception as e:
            self.logger.error(f"Error extracting compliance risk factors: {e}")
            return []

    def _extract_technical_risk_factors(
        self, entity_data: Dict[str, Any]
    ) -> List[RiskFactor]:
        """Extract technical risk factors.Extract technical risk factors."""
        try:
            factors = []

            # Security vulnerabilities
            if "security_vulnerabilities" in entity_data:
                vulnerabilities = entity_data["security_vulnerabilities"]
                if len(vulnerabilities) > 0:
                    factor = RiskFactor(
                        id=f"technical_vulnerabilities_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.TECHNICAL,
                        name="Security Vulnerabilities",
                        score=min(1.0, len(vulnerabilities) / 5),  # Scale to 0-1
                        weight=0.4,
                        description=f"Security vulnerabilities: {len(vulnerabilities)} issues",
                        evidence={"vulnerabilities": vulnerabilities},
                        confidence=0.8,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            # Outdated software
            if "outdated_software" in entity_data:
                outdated_count = len(entity_data["outdated_software"])
                if outdated_count > 0:
                    factor = RiskFactor(
                        id=f"technical_outdated_{datetime.utcnow().timestamp()}",
                        factor_type=RiskFactor.TECHNICAL,
                        name="Outdated Software",
                        score=min(1.0, outdated_count / 10),  # Scale to 0-1
                        weight=0.3,
                        description=f"Outdated software: {outdated_count} components",
                        evidence={
                            "outdated_software": entity_data["outdated_software"]
                        },
                        confidence=0.7,
                        timestamp=datetime.utcnow(),
                    )
                    factors.append(factor)

            return factors

        except Exception as e:
            self.logger.error(f"Error extracting technical risk factors: {e}")
            return []

    async def _calculate_rule_based_score(
        self, risk_factors: List[RiskFactor]
    ) -> float:
        """Calculate risk score using rule-based approach.Calculate risk score using rule-based approach."""
        try:
            if not risk_factors:
                return 0.0

            # Calculate weighted score
            total_weighted_score = 0.0
            total_weight = 0.0

            for factor in risk_factors:
                weighted_score = factor.score * factor.weight
                total_weighted_score += weighted_score
                total_weight += factor.weight

            # Normalize score
            if total_weight > 0:
                risk_score = total_weighted_score / total_weight
            else:
                risk_score = 0.0

            return min(1.0, risk_score)

        except Exception as e:
            self.logger.error(f"Error calculating rule-based score: {e}")
            return 0.5

    async def _calculate_ml_score(
        self, entity_data: Dict[str, Any], risk_factors: List[RiskFactor]
    ) -> float:
        """Calculate risk score using machine learning.Calculate risk score using machine learning."""
        try:
            # Check if ML models are available
            if not self.ml_models:
                self.logger.warning("No ML models available, using fallback scoring")
                return await self._calculate_rule_based_score(risk_factors)

            # Prepare features for ML model
            features = self._prepare_ml_features(entity_data, risk_factors)

            # Use default model if available
            default_model = self.ml_models.get("default")
            if default_model:
                # Scale features
                scaler = self.scalers.get("default")
                if scaler:
                    features_scaled = scaler.transform([features])
                else:
                    features_scaled = [features]

                # Predict risk score
                prediction = default_model.predict_proba(features_scaled)[0]
                risk_score = prediction[1]  # Probability of high risk

                return risk_score

            # Fallback to rule-based scoring
            return await self._calculate_rule_based_score(risk_factors)

        except Exception as e:
            self.logger.error(f"Error calculating ML score: {e}")
            return await self._calculate_rule_based_score(risk_factors)

    def _prepare_ml_features(
        self, entity_data: Dict[str, Any], risk_factors: List[RiskFactor]
    ) -> List[float]:
        """Prepare features for machine learning model.Prepare features for machine learning model."""
        try:
            features = []

            # Extract numerical features from entity data
            numerical_features = [
                entity_data.get("transaction_amount", 0),
                entity_data.get("transaction_count", 0),
                entity_data.get("account_balance", 0),
                entity_data.get("login_attempts", 0),
                entity_data.get("session_duration", 0),
                entity_data.get("connection_count", 0),
                len(entity_data.get("suspicious_ips", [])),
                len(entity_data.get("locations", [])),
                len(entity_data.get("high_risk_locations", [])),
                len(entity_data.get("missing_documents", [])),
                len(entity_data.get("verification_issues", [])),
                len(entity_data.get("compliance_violations", [])),
                len(entity_data.get("regulatory_flags", [])),
                len(entity_data.get("security_vulnerabilities", [])),
                len(entity_data.get("outdated_software", [])),
            ]

            # Add risk factor scores
            factor_scores = [factor.score for factor in risk_factors]

            # Combine features
            features = numerical_features + factor_scores

            # Pad or truncate to fixed length
            target_length = 50
            if len(features) < target_length:
                features.extend([0.0] * (target_length - len(features)))
            elif len(features) > target_length:
                features = features[:target_length]

            return features

        except Exception as e:
            self.logger.error(f"Error preparing ML features: {e}")
            return [0.0] * 50

    async def _calculate_statistical_score(
        self, risk_factors: List[RiskFactor]
    ) -> float:
        """Calculate risk score using statistical methods.Calculate risk score using statistical methods."""
        try:
            if not risk_factors:
                return 0.0

            # Calculate statistical measures
            scores = [factor.score for factor in risk_factors]

            # Use multiple statistical measures
            mean_score = np.mean(scores)
            median_score = np.median(scores)
            std_score = np.std(scores)

            # Calculate outlier-adjusted score
            if std_score > 0:
                z_scores = [(score - mean_score) / std_score for score in scores]
                outlier_adjusted_scores = [
                    score
                    for score, z_score in zip(scores, z_scores)
                    if abs(z_score) <= 2  # Remove outliers beyond 2 standard deviations
                ]

                if outlier_adjusted_scores:
                    adjusted_mean = np.mean(outlier_adjusted_scores)
                else:
                    adjusted_mean = mean_score
            else:
                adjusted_mean = mean_score

            # Combine measures
            risk_score = (mean_score + median_score + adjusted_mean) / 3

            return min(1.0, risk_score)

        except Exception as e:
            self.logger.error(f"Error calculating statistical score: {e}")
            return 0.5

    def _categorize_risk(self, risk_score: float) -> RiskCategory:
        """Categorize risk based on score.Categorize risk based on score."""
        try:
            if risk_score >= self.risk_thresholds["critical"]:
                return RiskCategory.CRITICAL
            elif risk_score >= self.risk_thresholds["high"]:
                return RiskCategory.HIGH
            elif risk_score >= self.risk_thresholds["medium"]:
                return RiskCategory.MEDIUM
            else:
                return RiskCategory.LOW

        except Exception as e:
            self.logger.error(f"Error categorizing risk: {e}")
            return RiskCategory.MEDIUM

    def _calculate_confidence(
        self, risk_factors: List[RiskFactor], scoring_method: ScoringMethod
    ) -> float:
        """Calculate confidence in the risk assessment.Calculate confidence in the risk assessment."""
        try:
            if not risk_factors:
                return 0.5

            # Base confidence on scoring method
            method_confidence = {
                ScoringMethod.RULE_BASED: 0.7,
                ScoringMethod.MACHINE_LEARNING: 0.8,
                ScoringMethod.HYBRID: 0.85,
                ScoringMethod.STATISTICAL: 0.75,
                ScoringMethod.EXPERT_SYSTEM: 0.9,
            }.get(scoring_method, 0.7)

            # Adjust confidence based on risk factors
            factor_confidence = np.mean([factor.confidence for factor in risk_factors])

            # Combine confidences
            overall_confidence = (method_confidence + factor_confidence) / 2

            return min(1.0, overall_confidence)

        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.7

    async def _generate_recommendations(
        self, risk_factors: List[RiskFactor], risk_score: float
    ) -> List[str]:
        """Generate risk mitigation recommendations.Generate risk mitigation recommendations."""
        try:
            recommendations = []

            # High-level recommendations based on risk score
            if risk_score >= 0.8:
                recommendations.append(
                    "Immediate investigation required - High risk entity"
                )
                recommendations.append("Implement enhanced monitoring and controls")
                recommendations.append("Consider account suspension pending review")
            elif risk_score >= 0.6:
                recommendations.append("Enhanced due diligence recommended")
                recommendations.append("Implement additional monitoring")
                recommendations.append("Review entity documentation")
            elif risk_score >= 0.4:
                recommendations.append("Standard monitoring procedures")
                recommendations.append("Regular risk assessment updates")
            else:
                recommendations.append("Continue standard monitoring")
                recommendations.append("Regular risk assessment schedule")

            # Specific recommendations based on risk factors
            for factor in risk_factors:
                if factor.score > 0.7:
                    if factor.factor_type == RiskFactor.FINANCIAL:
                        recommendations.append(
                            "Review financial transactions and patterns"
                        )
                    elif factor.factor_type == RiskFactor.BEHAVIORAL:
                        recommendations.append(
                            "Investigate unusual behavioral patterns"
                        )
                    elif factor.factor_type == RiskFactor.NETWORK:
                        recommendations.append(
                            "Review network connections and IP addresses"
                        )
                    elif factor.factor_type == RiskFactor.COMPLIANCE:
                        recommendations.append(
                            "Address compliance violations immediately"
                        )

            return recommendations

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return ["Conduct comprehensive risk assessment"]

    async def _initialize_risk_models(self):
        """Initialize risk scoring models.Initialize risk scoring models."""
        try:
            # Create default rule-based model
            default_model = RiskModel(
                id="default_rule_based",
                name="Default Rule-Based Model",
                method=ScoringMethod.RULE_BASED,
                parameters={"version": "1.0"},
                training_data_size=0,
                accuracy=0.75,
                last_updated=datetime.utcnow(),
            )

            self.risk_models["default"] = default_model

            # Initialize ML models if training data is available
            await self._initialize_ml_models()

            self.logger.info("Risk models initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing risk models: {e}")

    async def _initialize_ml_models(self):
        """Initialize machine learning models.Initialize machine learning models."""
        try:
            # This would load pre-trained models or train new ones
            # For now, create placeholder models

            # Random Forest model
            rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.ml_models["random_forest"] = rf_model

            # Gradient Boosting model
            gb_model = GradientBoostingClassifier(random_state=42)
            self.ml_models["gradient_boosting"] = gb_model

            # Logistic Regression model
            lr_model = LogisticRegression(random_state=42)
            self.ml_models["logistic_regression"] = rf_model

            # Set default model
            self.ml_models["default"] = rf_model

            # Initialize scalers
            self.scalers["default"] = StandardScaler()

            self.logger.info("ML models initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")

    async def _update_model_accuracy(self):
        """Update model accuracy metrics.Update model accuracy metrics."""
        while True:
            try:
                # This would calculate accuracy based on validation data
                # For now, use a placeholder
                self.model_accuracy = 0.82

                await asyncio.sleep(3600)  # Update every hour

            except Exception as e:
                self.logger.error(f"Error updating model accuracy: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_old_data(self):
        """Clean up old risk assessments.Clean up old risk assessments."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=90)

                # Remove old assessments
                old_assessments = [
                    entity_id
                    for entity_id, assessment in self.risk_assessments.items()
                    if assessment.assessment_time < cutoff_time
                ]

                for entity_id in old_assessments:
                    del self.risk_assessments[entity_id]

                if old_assessments:
                    self.logger.info(
                        f"Cleaned up {len(old_assessments)} old risk assessments"
                    )

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up old data: {e}")
                await asyncio.sleep(3600)

    def _update_average_assessment_time(self, new_time: float):
        """Update average assessment time.Update average assessment time."""
        self.average_assessment_time = (
            self.average_assessment_time * self.total_assessments + new_time
        ) / (self.total_assessments + 1)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics.Get performance metrics."""
        return {
            "total_assessments": self.total_assessments,
            "average_assessment_time": self.average_assessment_time,
            "model_accuracy": self.model_accuracy,
            "active_models": len(self.risk_models),
            "ml_models": len(self.ml_models),
            "risk_factors_analyzed": len(self.risk_factors),
            "scoring_methods_supported": [
                "rule_based",
                "machine_learning",
                "hybrid",
                "statistical",
                "expert_system",
            ],
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "risk_thresholds": {"low": 0.3, "medium": 0.6, "high": 0.8, "critical": 0.9},
        "min_confidence": 0.7,
    }

    # Initialize risk scorer
    risk_scorer = RiskScorer(config)

    print("RiskScorer system initialized successfully!")
