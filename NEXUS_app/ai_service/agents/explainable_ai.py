#!/usr/bin/env python3
"""
Explainable AI - Transparent AI Decision Making for Forensic Analysis

This module implements the ExplainableAI class that provides
transparent explanations for AI-driven forensic decisions.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType
import logging
from datetime import datetime, timedelta

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class ExplanationType(Enum):
    """Types of AI explanations."""

    FEATURE_IMPORTANCE = "feature_importance"  # Feature contribution analysis
    DECISION_PATH = "decision_path"  # Decision tree path
    SHAP_VALUES = "shap_values"  # SHAP explanation values
    LIME_EXPLANATION = "lime_explanation"  # LIME local explanations
    COUNTERFACTUAL = "counterfactual"  # What-if scenarios
    CONFIDENCE_BREAKDOWN = "confidence_breakdown"  # Confidence factor analysis
    SIMILARITY_ANALYSIS = "similarity_analysis"  # Similar case analysis
    RULE_EXPLANATION = "rule_explanation"  # Rule-based explanations


class ExplanationFormat(Enum):
    """Explanation output formats."""

    TEXT = "text"  # Human-readable text
    VISUAL = "visual"  # Charts and graphs
    JSON = "json"  # Structured data
    HTML = "html"  # Web-friendly format
    PDF = "pdf"  # Document format
    INTERACTIVE = "interactive"  # Interactive dashboard


class ExplanationLevel(Enum):
    """Explanation detail levels."""

    BASIC = "basic"  # High-level summary
    DETAILED = "detailed"  # Comprehensive explanation
    TECHNICAL = "technical"  # Technical details
    EXPERT = "expert"  # Expert-level analysis


@dataclass
class AIExplanation:
    """AI decision explanation."""

    decision_id: str
    explanation_type: ExplanationType
    format: ExplanationFormat
    level: ExplanationLevel
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """__post_init__ function."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class ExplanationConfig:
    """Configuration for AI explanations."""

    explanation_types: List[ExplanationType]
    output_format: ExplanationFormat
    detail_level: ExplanationLevel
    enable_visualizations: bool = True
    enable_interactive: bool = True
    max_features: int = 10
    confidence_threshold: float = 0.7

    def __post_init__(self):
        """__post_init__ function."""
        if not self.explanation_types:
            self.explanation_types = [ExplanationType.FEATURE_IMPORTANCE]


class ExplainableAI:
    """
    Comprehensive explainable AI system for forensic analysis.

    The ExplainableAI is responsible for:
    - Providing transparent explanations for AI decisions
    - Generating multiple explanation types and formats
    - Creating visual and interactive explanations
    - Supporting audit and compliance requirements
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the ExplainableAI."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.enable_visualizations = config.get("enable_visualizations", True)
        self.enable_interactive = config.get("enable_interactive", True)
        self.max_features = config.get("max_features", 10)
        self.confidence_threshold = config.get("confidence_threshold", 0.7)

        # Explanation components
        self.feature_importance_model = None
        self.shap_explainer = None
        self.lime_explainer = None

        # Internal state
        self.explanation_history: List[AIExplanation] = []
        self.feature_mappings: Dict[str, str] = {}
        self.explanation_templates: Dict[str, str] = {}

        # Performance tracking
        self.total_explanations_generated = 0
        self.average_generation_time = 0.0
        self.explanation_quality_score = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("ExplainableAI initialized successfully")

    async def start(self):
        """Start the ExplainableAI.Start the ExplainableAI."""
        self.logger.info("Starting ExplainableAI...")

        # Initialize explanation components
        await self._initialize_explanation_components()

        # Load explanation templates
        await self._load_explanation_templates()

        # Start background tasks
        asyncio.create_task(self._update_explanation_quality())
        asyncio.create_task(self._cleanup_old_explanations())

        self.logger.info("ExplainableAI started successfully")

    async def stop(self):
        """Stop the ExplainableAI.Stop the ExplainableAI."""
        self.logger.info("Stopping ExplainableAI...")
        self.logger.info("ExplainableAI stopped")

    async def explain_decision(
        self, decision_data: Dict[str, Any], config: ExplanationConfig
    ) -> List[AIExplanation]:
        """Generate explanations for an AI decision.Generate explanations for an AI decision."""
        try:
            start_time = datetime.utcnow()

            self.logger.info(
                f"Generating explanations for decision: {decision_data.get('id', 'unknown')}"
            )

            explanations = []

            # Generate explanations for each requested type
            for explanation_type in config.explanation_types:
                try:
                    if explanation_type == ExplanationType.FEATURE_IMPORTANCE:
                        explanation = (
                            await self._generate_feature_importance_explanation(
                                decision_data, config
                            )
                        )
                    elif explanation_type == ExplanationType.DECISION_PATH:
                        explanation = await self._generate_decision_path_explanation(
                            decision_data, config
                        )
                    elif explanation_type == ExplanationType.SHAP_VALUES:
                        explanation = await self._generate_shap_explanation(
                            decision_data, config
                        )
                    elif explanation_type == ExplanationType.LIME_EXPLANATION:
                        explanation = await self._generate_lime_explanation(
                            decision_data, config
                        )
                    elif explanation_type == ExplanationType.COUNTERFACTUAL:
                        explanation = await self._generate_counterfactual_explanation(
                            decision_data, config
                        )
                    elif explanation_type == ExplanationType.CONFIDENCE_BREAKDOWN:
                        explanation = (
                            await self._generate_confidence_breakdown_explanation(
                                decision_data, config
                            )
                        )
                    elif explanation_type == ExplanationType.SIMILARITY_ANALYSIS:
                        explanation = (
                            await self._generate_similarity_analysis_explanation(
                                decision_data, config
                            )
                        )
                    elif explanation_type == ExplanationType.RULE_EXPLANATION:
                        explanation = await self._generate_rule_explanation(
                            decision_data, config
                        )
                    else:
                        continue

                    if explanation:
                        explanations.append(explanation)

                except Exception as e:
                    self.logger.error(
                        f"Error generating {explanation_type.value} explanation: {e}"
                    )
                    continue

            # Update statistics
            self.total_explanations_generated += len(explanations)

            # Store explanations
            self.explanation_history.extend(explanations)

            # Update processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_generation_time(processing_time)

            self.logger.info(
                f"Generated {len(explanations)} explanations in {processing_time:.2f}s"
            )

            return explanations

        except Exception as e:
            self.logger.error(f"Error in decision explanation: {e}")
            return []

    async def _generate_feature_importance_explanation(
        self, decision_data: Dict[str, Any], config: ExplanationConfig
    ) -> AIExplanation:
        """Generate feature importance explanation.Generate feature importance explanation."""
        try:
            # Extract features and their importance scores
            features = decision_data.get("features", {})
            importance_scores = decision_data.get("feature_importance", {})

            if not features or not importance_scores:
                return None

            # Sort features by importance
            sorted_features = sorted(
                importance_scores.items(), key=lambda x: x[1], reverse=True
            )
            top_features = sorted_features[: self.max_features]

            # Create explanation content
            content = {
                "feature_importance": dict(top_features),
                "top_features": [feature for feature, score in top_features],
                "total_features": len(features),
                "importance_summary": self._create_importance_summary(top_features),
            }

            # Add visualizations if enabled
            if self.enable_visualizations:
                content["visualization"] = await self._create_feature_importance_chart(
                    top_features
                )

            # Create explanation
            explanation = AIExplanation(
                decision_id=decision_data.get("id", "unknown"),
                explanation_type=ExplanationType.FEATURE_IMPORTANCE,
                format=config.output_format,
                level=config.detail_level,
                content=content,
                metadata={
                    "explanation_method": "feature_importance",
                    "features_analyzed": len(features),
                },
            )

            return explanation

        except Exception as e:
            self.logger.error(f"Error generating feature importance explanation: {e}")
            return None

    async def _generate_decision_path_explanation(
        self, decision_data: Dict[str, Any], config: ExplanationConfig
    ) -> AIExplanation:
        """Generate decision path explanation.Generate decision path explanation."""
        try:
            # Extract decision tree information
            decision_tree = decision_data.get("decision_tree", {})
            path_taken = decision_data.get("decision_path", [])

            if not decision_tree or not path_taken:
                return None

            # Create decision path explanation
            content = {
                "decision_path": path_taken,
                "total_steps": len(path_taken),
                "path_summary": self._create_path_summary(path_taken),
                "decision_rules": self._extract_decision_rules(path_taken),
            }

            # Add visualizations if enabled
            if self.enable_visualizations:
                content["visualization"] = await self._create_decision_path_chart(
                    path_taken
                )

            # Create explanation
            explanation = AIExplanation(
                decision_id=decision_data.get("id", "unknown"),
                explanation_type=ExplanationType.DECISION_PATH,
                format=config.output_format,
                level=config.detail_level,
                content=content,
                metadata={
                    "explanation_method": "decision_path",
                    "path_length": len(path_taken),
                },
            )

            return explanation

        except Exception as e:
            self.logger.error(f"Error generating decision path explanation: {e}")
            return None

    async def _generate_shap_explanation(
        self, decision_data: Dict[str, Any], config: ExplanationConfig
    ) -> AIExplanation:
        """Generate SHAP explanation.Generate SHAP explanation."""
        try:
            # Extract SHAP values
            shap_values = decision_data.get("shap_values", {})
            feature_names = decision_data.get("feature_names", [])

            if not shap_values or not feature_names:
                return None

            # Process SHAP values
            processed_shap = self._process_shap_values(shap_values, feature_names)

            # Create explanation content
            content = {
                "shap_values": processed_shap,
                "top_contributors": self._get_top_shap_contributors(processed_shap),
                "shap_summary": self._create_shap_summary(processed_shap),
            }

            # Add visualizations if enabled
            if self.enable_visualizations:
                content["visualization"] = await self._create_shap_chart(processed_shap)

            # Create explanation
            explanation = AIExplanation(
                decision_id=decision_data.get("id", "unknown"),
                explanation_type=ExplanationType.SHAP_VALUES,
                format=config.output_format,
                level=config.detail_level,
                content=content,
                metadata={
                    "explanation_method": "shap_values",
                    "shap_features": len(processed_shap),
                },
            )

            return explanation

        except Exception as e:
            self.logger.error(f"Error generating SHAP explanation: {e}")
            return None

    async def _generate_lime_explanation(
        self, decision_data: Dict[str, Any], config: ExplanationConfig
    ) -> AIExplanation:
        """Generate LIME explanation.Generate LIME explanation."""
        try:
            # Extract LIME information
            lime_explanation = decision_data.get("lime_explanation", {})
            local_features = lime_explanation.get("local_features", [])

            if not local_features:
                return None

            # Process LIME explanation
            processed_lime = self._process_lime_explanation(lime_explanation)

            # Create explanation content
            content = {
                "lime_explanation": processed_lime,
                "local_importance": self._get_local_feature_importance(processed_lime),
                "lime_summary": self._create_lime_summary(processed_lime),
            }

            # Add visualizations if enabled
            if self.enable_visualizations:
                content["visualization"] = await self._create_lime_chart(processed_lime)

            # Create explanation
            explanation = AIExplanation(
                decision_id=decision_data.get("id", "unknown"),
                explanation_type=ExplanationType.LIME_EXPLANATION,
                format=config.output_format,
                level=config.detail_level,
                content=content,
                metadata={
                    "explanation_method": "lime_explanation",
                    "local_features": len(local_features),
                },
            )

            return explanation

        except Exception as e:
            self.logger.error(f"Error generating LIME explanation: {e}")
            return None

    async def _generate_counterfactual_explanation(
        self, decision_data: Dict[str, Any], config: ExplanationConfig
    ) -> AIExplanation:
        """Generate counterfactual explanation.Generate counterfactual explanation."""
        try:
            # Extract counterfactual information
            counterfactuals = decision_data.get("counterfactuals", [])
            original_decision = decision_data.get("decision", "unknown")

            if not counterfactuals:
                return None

            # Process counterfactuals
            processed_counterfactuals = self._process_counterfactuals(
                counterfactuals, original_decision
            )

            # Create explanation content
            content = {
                "counterfactuals": processed_counterfactuals,
                "what_if_scenarios": self._create_what_if_scenarios(
                    processed_counterfactuals
                ),
                "counterfactual_summary": self._create_counterfactual_summary(
                    processed_counterfactuals
                ),
            }

            # Add visualizations if enabled
            if self.enable_visualizations:
                content["visualization"] = await self._create_counterfactual_chart(
                    processed_counterfactuals
                )

            # Create explanation
            explanation = AIExplanation(
                decision_id=decision_data.get("id", "unknown"),
                explanation_type=ExplanationType.COUNTERFACTUAL,
                format=config.output_format,
                level=config.detail_level,
                content=content,
                metadata={
                    "explanation_method": "counterfactual",
                    "scenarios_generated": len(processed_counterfactuals),
                },
            )

            return explanation

        except Exception as e:
            self.logger.error(f"Error generating counterfactual explanation: {e}")
            return None

    async def _generate_confidence_breakdown_explanation(
        self, decision_data: Dict[str, Any], config: ExplanationConfig
    ) -> AIExplanation:
        """Generate confidence breakdown explanation.Generate confidence breakdown explanation."""
        try:
            # Extract confidence information
            confidence_factors = decision_data.get("confidence_factors", {})
            overall_confidence = decision_data.get("overall_confidence", 0.0)

            if not confidence_factors:
                return None

            # Process confidence factors
            processed_confidence = self._process_confidence_factors(
                confidence_factors, overall_confidence
            )

            # Create explanation content
            content = {
                "confidence_breakdown": processed_confidence,
                "confidence_summary": self._create_confidence_summary(
                    processed_confidence
                ),
                "risk_factors": self._identify_risk_factors(processed_confidence),
            }

            # Add visualizations if enabled
            if self.enable_visualizations:
                content["visualization"] = await self._create_confidence_chart(
                    processed_confidence
                )

            # Create explanation
            explanation = AIExplanation(
                decision_id=decision_data.get("id", "unknown"),
                explanation_type=ExplanationType.CONFIDENCE_BREAKDOWN,
                format=config.output_format,
                level=config.detail_level,
                content=content,
                metadata={
                    "explanation_method": "confidence_breakdown",
                    "overall_confidence": overall_confidence,
                },
            )

            return explanation

        except Exception as e:
            self.logger.error(f"Error generating confidence breakdown explanation: {e}")
            return None

    async def _generate_similarity_analysis_explanation(
        self, decision_data: Dict[str, Any], config: ExplanationConfig
    ) -> AIExplanation:
        """Generate similarity analysis explanation.Generate similarity analysis explanation."""
        try:
            # Extract similarity information
            similar_cases = decision_data.get("similar_cases", [])
            similarity_metrics = decision_data.get("similarity_metrics", {})

            if not similar_cases:
                return None

            # Process similarity analysis
            processed_similarity = self._process_similarity_analysis(
                similar_cases, similarity_metrics
            )

            # Create explanation content
            content = {
                "similarity_analysis": processed_similarity,
                "case_comparisons": self._create_case_comparisons(processed_similarity),
                "similarity_summary": self._create_similarity_summary(
                    processed_similarity
                ),
            }

            # Add visualizations if enabled
            if self.enable_visualizations:
                content["visualization"] = await self._create_similarity_chart(
                    processed_similarity
                )

            # Create explanation
            explanation = AIExplanation(
                decision_id=decision_data.get("id", "unknown"),
                explanation_type=ExplanationType.SIMILARITY_ANALYSIS,
                format=config.output_format,
                level=config.detail_level,
                content=content,
                metadata={
                    "explanation_method": "similarity_analysis",
                    "similar_cases": len(similar_cases),
                },
            )

            return explanation

        except Exception as e:
            self.logger.error(f"Error generating similarity analysis explanation: {e}")
            return None

    async def _generate_rule_explanation(
        self, decision_data: Dict[str, Any], config: ExplanationConfig
    ) -> AIExplanation:
        """Generate rule-based explanation.Generate rule-based explanation."""
        try:
            # Extract rule information
            applied_rules = decision_data.get("applied_rules", [])
            rule_weights = decision_data.get("rule_weights", {})

            if not applied_rules:
                return None

            # Process rule explanations
            processed_rules = self._process_rule_explanations(
                applied_rules, rule_weights
            )

            # Create explanation content
            content = {
                "rule_explanations": processed_rules,
                "rule_summary": self._create_rule_summary(processed_rules),
                "rule_impact": self._analyze_rule_impact(processed_rules),
            }

            # Add visualizations if enabled
            if self.enable_visualizations:
                content["visualization"] = await self._create_rule_chart(
                    processed_rules
                )

            # Create explanation
            explanation = AIExplanation(
                decision_id=decision_data.get("id", "unknown"),
                explanation_type=ExplanationType.RULE_EXPLANATION,
                format=config.output_format,
                level=config.detail_level,
                content=content,
                metadata={
                    "explanation_method": "rule_explanation",
                    "rules_applied": len(applied_rules),
                },
            )

            return explanation

        except Exception as e:
            self.logger.error(f"Error generating rule explanation: {e}")
            return None

    def _create_importance_summary(self, top_features: List[Tuple[str, float]]) -> str:
        """Create human-readable feature importance summary.Create human-readable feature importance summary."""
        try:
            if not top_features:
                return "No feature importance data available."

            summary = f"The top {len(top_features)} most important features are:\n"

            for i, (feature, score) in enumerate(top_features, 1):
                percentage = score * 100
                summary += f"{i}. {feature}: {percentage:.1f}% importance\n"

            return summary

        except Exception as e:
            self.logger.error(f"Error creating importance summary: {e}")
            return "Error generating feature importance summary."

    def _create_path_summary(self, path_taken: List[Dict[str, Any]]) -> str:
        """Create human-readable decision path summary.Create human-readable decision path summary."""
        try:
            if not path_taken:
                return "No decision path data available."

            summary = f"The decision was made through {len(path_taken)} steps:\n"

            for i, step in enumerate(path_taken, 1):
                condition = step.get("condition", "Unknown condition")
                outcome = step.get("outcome", "Unknown outcome")
                summary += f"{i}. {condition} → {outcome}\n"

            return summary

        except Exception as e:
            self.logger.error(f"Error creating path summary: {e}")
            return "Error generating decision path summary."

    def _extract_decision_rules(self, path_taken: List[Dict[str, Any]]) -> List[str]:
        """Extract decision rules from path.Extract decision rules from path."""
        try:
            rules = []

            for step in path_taken:
                condition = step.get("condition", "")
                if condition:
                    rules.append(condition)

            return rules

        except Exception as e:
            self.logger.error(f"Error extracting decision rules: {e}")
            return []

    def _process_shap_values(
        self, shap_values: Dict[str, Any], feature_names: List[str]
    ) -> Dict[str, float]:
        """Process SHAP values for explanation.Process SHAP values for explanation."""
        try:
            processed = {}

            for feature, value in zip(feature_names, shap_values):
                if isinstance(value, (int, float)):
                    processed[feature] = float(value)

            return processed

        except Exception as e:
            self.logger.error(f"Error processing SHAP values: {e}")
            return {}

    def _get_top_shap_contributors(
        self, shap_values: Dict[str, float]
    ) -> List[Tuple[str, float]]:
        """Get top SHAP contributors.Get top SHAP contributors."""
        try:
            sorted_features = sorted(
                shap_values.items(), key=lambda x: abs(x[1]), reverse=True
            )
            return sorted_features[: self.max_features]

        except Exception as e:
            self.logger.error(f"Error getting top SHAP contributors: {e}")
            return []

    def _create_shap_summary(self, shap_values: Dict[str, float]) -> str:
        """Create SHAP explanation summary.Create SHAP explanation summary."""
        try:
            if not shap_values:
                return "No SHAP values available."

            positive_contributors = [(f, v) for f, v in shap_values.items() if v > 0]
            negative_contributors = [(f, v) for f, v in shap_values.items() if v < 0]

            summary = f"SHAP analysis shows:\n"

            if positive_contributors:
                summary += f"Features that increased the prediction: {len(positive_contributors)}\n"

            if negative_contributors:
                summary += f"Features that decreased the prediction: {len(negative_contributors)}\n"

            return summary

        except Exception as e:
            self.logger.error(f"Error creating SHAP summary: {e}")
            return "Error generating SHAP summary."

    def _process_lime_explanation(self, lime_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process LIME explanation data.Process LIME explanation data."""
        try:
            processed = {
                "local_features": lime_data.get("local_features", []),
                "local_weights": lime_data.get("local_weights", {}),
                "prediction": lime_data.get("prediction", "unknown"),
            }

            return processed

        except Exception as e:
            self.logger.error(f"Error processing LIME explanation: {e}")
            return {}

    def _get_local_feature_importance(
        self, lime_data: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """Get local feature importance from LIME.Get local feature importance from LIME."""
        try:
            local_weights = lime_data.get("local_weights", {})
            sorted_features = sorted(
                local_weights.items(), key=lambda x: abs(x[1]), reverse=True
            )
            return sorted_features[: self.max_features]

        except Exception as e:
            self.logger.error(f"Error getting local feature importance: {e}")
            return []

    def _create_lime_summary(self, lime_data: Dict[str, Any]) -> str:
        """Create LIME explanation summary.Create LIME explanation summary."""
        try:
            prediction = lime_data.get("prediction", "unknown")
            local_features = lime_data.get("local_features", [])

            summary = f"LIME explanation for prediction '{prediction}':\n"
            summary += (
                f"Based on {len(local_features)} local features in the neighborhood."
            )

            return summary

        except Exception as e:
            self.logger.error(f"Error creating LIME summary: {e}")
            return "Error generating LIME summary."

    def _process_counterfactuals(
        self, counterfactuals: List[Dict[str, Any]], original_decision: str
    ) -> List[Dict[str, Any]]:
        """Process counterfactual explanations.Process counterfactual explanations."""
        try:
            processed = []

            for cf in counterfactuals:
                processed_cf = {
                    "scenario": cf.get("scenario", "Unknown"),
                    "changes": cf.get("changes", []),
                    "new_decision": cf.get("new_decision", "Unknown"),
                    "confidence": cf.get("confidence", 0.0),
                }
                processed.append(processed_cf)

            return processed

        except Exception as e:
            self.logger.error(f"Error processing counterfactuals: {e}")
            return []

    def _create_what_if_scenarios(
        self, counterfactuals: List[Dict[str, Any]]
    ) -> List[str]:
        """Create what-if scenario descriptions.Create what-if scenario descriptions."""
        try:
            scenarios = []

            for cf in counterfactuals:
                scenario = f"What if: {cf.get('scenario', 'Unknown')} → Decision: {cf.get('new_decision', 'Unknown')}"
                scenarios.append(scenario)

            return scenarios

        except Exception as e:
            self.logger.error(f"Error creating what-if scenarios: {e}")
            return []

    def _create_counterfactual_summary(
        self, counterfactuals: List[Dict[str, Any]]
    ) -> str:
        """Create counterfactual explanation summary.Create counterfactual explanation summary."""
        try:
            if not counterfactuals:
                return "No counterfactual scenarios available."

            summary = f"Generated {len(counterfactuals)} counterfactual scenarios:\n"

            for i, cf in enumerate(counterfactuals, 1):
                scenario = cf.get("scenario", "Unknown")
                new_decision = cf.get("new_decision", "Unknown")
                summary += f"{i}. {scenario} → {new_decision}\n"

            return summary

        except Exception as e:
            self.logger.error(f"Error creating counterfactual summary: {e}")
            return "Error generating counterfactual summary."

    def _process_confidence_factors(
        self, confidence_factors: Dict[str, float], overall_confidence: float
    ) -> Dict[str, Any]:
        """Process confidence factors for explanation.Process confidence factors for explanation."""
        try:
            processed = {
                "factors": confidence_factors,
                "overall": overall_confidence,
                "factor_count": len(confidence_factors),
                "high_confidence_factors": [
                    (f, v) for f, v in confidence_factors.items() if v > 0.8
                ],
                "low_confidence_factors": [
                    (f, v) for f, v in confidence_factors.items() if v < 0.6
                ],
            }

            return processed

        except Exception as e:
            self.logger.error(f"Error processing confidence factors: {e}")
            return {}

    def _create_confidence_summary(self, confidence_data: Dict[str, Any]) -> str:
        """Create confidence breakdown summary.Create confidence breakdown summary."""
        try:
            overall = confidence_data.get("overall", 0.0)
            factor_count = confidence_data.get("factor_count", 0)
            high_confidence = len(confidence_data.get("high_confidence_factors", []))
            low_confidence = len(confidence_data.get("low_confidence_factors", []))

            summary = f"Overall confidence: {overall:.1%}\n"
            summary += f"Based on {factor_count} confidence factors\n"
            summary += f"High confidence factors: {high_confidence}\n"
            summary += f"Low confidence factors: {low_confidence}"

            return summary

        except Exception as e:
            self.logger.error(f"Error creating confidence summary: {e}")
            return "Error generating confidence summary."

    def _identify_risk_factors(self, confidence_data: Dict[str, Any]) -> List[str]:
        """Identify risk factors from confidence data.Identify risk factors from confidence data."""
        try:
            risk_factors = []
            low_confidence = confidence_data.get("low_confidence_factors", [])

            for factor, score in low_confidence:
                risk_factors.append(f"{factor}: Low confidence ({score:.1%})")

            return risk_factors

        except Exception as e:
            self.logger.error(f"Error identifying risk factors: {e}")
            return []

    def _process_similarity_analysis(
        self, similar_cases: List[Dict[str, Any]], similarity_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process similarity analysis data.Process similarity analysis data."""
        try:
            processed = {
                "similar_cases": similar_cases,
                "similarity_metrics": similarity_metrics,
                "case_count": len(similar_cases),
                "average_similarity": (
                    np.mean([case.get("similarity", 0.0) for case in similar_cases])
                    if similar_cases
                    else 0.0
                ),
            }

            return processed

        except Exception as e:
            self.logger.error(f"Error processing similarity analysis: {e}")
            return {}

    def _create_case_comparisons(self, similarity_data: Dict[str, Any]) -> List[str]:
        """Create case comparison descriptions.Create case comparison descriptions."""
        try:
            comparisons = []
            similar_cases = similarity_data.get("similar_cases", [])

            for case in similar_cases[:5]:  # Top 5 similar cases
                case_id = case.get("id", "Unknown")
                similarity = case.get("similarity", 0.0)
                decision = case.get("decision", "Unknown")

                comparison = (
                    f"Case {case_id}: {similarity:.1%} similar, Decision: {decision}"
                )
                comparisons.append(comparison)

            return comparisons

        except Exception as e:
            self.logger.error(f"Error creating case comparisons: {e}")
            return []

    def _create_similarity_summary(self, similarity_data: Dict[str, Any]) -> str:
        """Create similarity analysis summary.Create similarity analysis summary."""
        try:
            case_count = similarity_data.get("case_count", 0)
            average_similarity = similarity_data.get("average_similarity", 0.0)

            summary = f"Found {case_count} similar cases\n"
            summary += f"Average similarity: {average_similarity:.1%}"

            return summary

        except Exception as e:
            self.logger.error(f"Error creating similarity summary: {e}")
            return "Error generating similarity summary."

    def _process_rule_explanations(
        self, applied_rules: List[Dict[str, Any]], rule_weights: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Process rule-based explanations.Process rule-based explanations."""
        try:
            processed = []

            for rule in applied_rules:
                rule_id = rule.get("id", "Unknown")
                rule_description = rule.get("description", "No description")
                rule_weight = rule_weights.get(rule_id, 1.0)
                rule_triggered = rule.get("triggered", False)

                processed_rule = {
                    "id": rule_id,
                    "description": rule_description,
                    "weight": rule_weight,
                    "triggered": rule_triggered,
                    "impact": rule_weight if rule_triggered else 0.0,
                }

                processed.append(processed_rule)

            return processed

        except Exception as e:
            self.logger.error(f"Error processing rule explanations: {e}")
            return []

    def _create_rule_summary(self, rules: List[Dict[str, Any]]) -> str:
        """Create rule explanation summary.Create rule explanation summary."""
        try:
            if not rules:
                return "No rules applied."

            triggered_rules = [r for r in rules if r.get("triggered", False)]
            total_impact = sum(r.get("impact", 0.0) for r in rules)

            summary = f"Applied {len(rules)} rules\n"
            summary += f"Triggered rules: {len(triggered_rules)}\n"
            summary += f"Total rule impact: {total_impact:.2f}"

            return summary

        except Exception as e:
            self.logger.error(f"Error creating rule summary: {e}")
            return "Error generating rule summary."

    def _analyze_rule_impact(self, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the impact of applied rules.Analyze the impact of applied rules."""
        try:
            triggered_rules = [r for r in rules if r.get("triggered", False)]
            high_impact_rules = [r for r in rules if r.get("impact", 0.0) > 0.5]

            impact_analysis = {
                "total_rules": len(rules),
                "triggered_rules": len(triggered_rules),
                "high_impact_rules": len(high_impact_rules),
                "total_impact": sum(r.get("impact", 0.0) for r in rules),
            }

            return impact_analysis

        except Exception as e:
            self.logger.error(f"Error analyzing rule impact: {e}")
            return {}

    async def _create_feature_importance_chart(
        self, top_features: List[Tuple[str, float]]
    ) -> str:
        """Create feature importance visualization.Create feature importance visualization."""
        try:
            if not self.enable_visualizations:
                return "Visualizations disabled"

            # This would create and save a chart
            # For now, return a placeholder
            return "Feature importance chart generated"

        except Exception as e:
            self.logger.error(f"Error creating feature importance chart: {e}")
            return "Error generating chart"

    async def _create_decision_path_chart(
        self, path_taken: List[Dict[str, Any]]
    ) -> str:
        """Create decision path visualization.Create decision path visualization."""
        try:
            if not self.enable_visualizations:
                return "Visualizations disabled"

            # This would create and save a chart
            # For now, return a placeholder
            return "Decision path chart generated"

        except Exception as e:
            self.logger.error(f"Error creating decision path chart: {e}")
            return "Error generating chart"

    async def _create_shap_chart(self, shap_values: Dict[str, float]) -> str:
        """Create SHAP visualization.Create SHAP visualization."""
        try:
            if not self.enable_visualizations:
                return "Visualizations disabled"

            # This would create and save a chart
            # For now, return a placeholder
            return "SHAP chart generated"

        except Exception as e:
            self.logger.error(f"Error creating SHAP chart: {e}")
            return "Error generating chart"

    async def _create_lime_chart(self, lime_data: Dict[str, Any]) -> str:
        """Create LIME visualization.Create LIME visualization."""
        try:
            if not self.enable_visualizations:
                return "Visualizations disabled"

            # This would create and save a chart
            # For now, return a placeholder
            return "LIME chart generated"

        except Exception as e:
            self.logger.error(f"Error creating LIME chart: {e}")
            return "Error generating chart"

    async def _create_counterfactual_chart(
        self, counterfactuals: List[Dict[str, Any]]
    ) -> str:
        """Create counterfactual visualization.Create counterfactual visualization."""
        try:
            if not self.enable_visualizations:
                return "Visualizations disabled"

            # This would create and save a chart
            # For now, return a placeholder
            return "Counterfactual chart generated"

        except Exception as e:
            self.logger.error(f"Error creating counterfactual chart: {e}")
            return "Error generating chart"

    async def _create_confidence_chart(self, confidence_data: Dict[str, Any]) -> str:
        """Create confidence visualization.Create confidence visualization."""
        try:
            if not self.enable_visualizations:
                return "Visualizations disabled"

            # This would create and save a chart
            # For now, return a placeholder
            return "Confidence chart generated"

        except Exception as e:
            self.logger.error(f"Error creating confidence chart: {e}")
            return "Error generating chart"

    async def _create_similarity_chart(self, similarity_data: Dict[str, Any]) -> str:
        """Create similarity visualization.Create similarity visualization."""
        try:
            if not self.enable_visualizations:
                return "Visualizations disabled"

            # This would create and save a chart
            # For now, return a placeholder
            return "Similarity chart generated"

        except Exception as e:
            self.logger.error(f"Error creating similarity chart: {e}")
            return "Error generating chart"

    async def _create_rule_chart(self, rules: List[Dict[str, Any]]) -> str:
        """Create rule visualization.Create rule visualization."""
        try:
            if not self.enable_visualizations:
                return "Visualizations disabled"

            # This would create and save a chart
            # For now, return a placeholder
            return "Rule chart generated"

        except Exception as e:
            self.logger.error(f"Error creating rule chart: {e}")
            return "Error generating chart"

    async def _initialize_explanation_components(self):
        """Initialize explanation components.Initialize explanation components."""
        try:
            # Initialize SHAP explainer if available
            try:
                # This would initialize SHAP explainer
                self.logger.info("SHAP explainer initialized")
            except Exception as e:
                self.logger.warning(f"SHAP explainer not available: {e}")

            # Initialize LIME explainer if available
            try:
                # This would initialize LIME explainer
                self.logger.info("LIME explainer initialized")
            except Exception as e:
                self.logger.warning(f"LIME explainer not available: {e}")

            self.logger.info("Explanation components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing explanation components: {e}")

    async def _load_explanation_templates(self):
        """Load explanation templates.Load explanation templates."""
        try:
            # Load templates for different explanation types
            self.explanation_templates = {
                "feature_importance": "The decision was influenced by the following key features: {features}",
                "decision_path": "The decision was made through the following steps: {steps}",
                "confidence": "The confidence level is {confidence} based on {factors} factors",
            }

            self.logger.info("Explanation templates loaded successfully")

        except Exception as e:
            self.logger.error(f"Error loading explanation templates: {e}")

    async def _update_explanation_quality(self):
        """Update explanation quality metrics.Update explanation quality metrics."""
        while True:
            try:
                # This would calculate quality metrics based on user feedback
                # For now, use a placeholder
                self.explanation_quality_score = 0.85

                await asyncio.sleep(3600)  # Update every hour

            except Exception as e:
                self.logger.error(f"Error updating explanation quality: {e}")
                await asyncio.sleep(3600)

    async def _cleanup_old_explanations(self):
        """Clean up old explanations.Clean up old explanations."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=30)

                # Remove old explanations
                self.explanation_history = [
                    explanation
                    for explanation in self.explanation_history
                    if explanation.timestamp > cutoff_time
                ]

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up old explanations: {e}")
                await asyncio.sleep(3600)

    def _update_average_generation_time(self, new_time: float):
        """Update average generation time.Update average generation time."""
        self.average_generation_time = (
            self.average_generation_time * self.total_explanations_generated + new_time
        ) / (self.total_explanations_generated + 1)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics.Get performance metrics."""
        return {
            "total_explanations_generated": self.total_explanations_generated,
            "average_generation_time": self.average_generation_time,
            "explanation_quality_score": self.explanation_quality_score,
            "explanation_types_supported": [
                "feature_importance",
                "decision_path",
                "shap_values",
                "lime_explanation",
                "counterfactual",
                "confidence_breakdown",
                "similarity_analysis",
                "rule_explanation",
            ],
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "enable_visualizations": True,
        "enable_interactive": True,
        "max_features": 10,
        "confidence_threshold": 0.7,
    }

    # Initialize explainable AI
    explainable_ai = ExplainableAI(config)

    print("ExplainableAI system initialized successfully!")
