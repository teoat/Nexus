#!/usr/bin/env python3
"""
Explainable AI (XAI) Scorer

This module provides a simple, rule-based XAI scorer to generate
risk scores with clear, explainable factors.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class XAIScorer:
    """
    A simple rule-based scorer for Explainable AI.
    """

    def __init__(self):
        """Initializes the XAIScorer."""
        self.rules = self._get_default_rules()
        logger.info("XAIScorer initialized with default rules.")

    def _get_default_rules(self) -> Dict[str, Tuple[int, str]]:
        """Defines a set of simple, explainable rules."""
        return {
            "contains_anomaly": (30, "Data contains known anomaly patterns."),
            "is_high_value": (20, "Transaction value is unusually high."),
            "is_outside_business_hours": (15, "Transaction occurred outside of normal business hours."),
            "has_foreign_entity": (25, "Transaction involves a foreign entity."),
            "is_circular_transaction": (40, "Transaction is part of a circular payment chain."),
        }

    def score(self, data: Dict[str, Any]) -> Tuple[int, List[str]]:
        """
        Scores the given data based on the defined rules.

        Args:
            data: A dictionary representing the data to score (e.g., a transaction).

        Returns:
            A tuple containing the total risk score and a list of
            explainable factors that contributed to the score.
        """
        total_score = 0
        factors = []

        # This is a mock implementation. A real implementation would have
        # complex logic to check these conditions.
        if data.get("anomaly_detected", False):
            score, reason = self.rules["contains_anomaly"]
            total_score += score
            factors.append(reason)

        if data.get("value", 0) > 100000:
            score, reason = self.rules["is_high_value"]
            total_score += score
            factors.append(reason)

        if data.get("is_circular", False):
            score, reason = self.rules["is_circular_transaction"]
            total_score += score
            factors.append(reason)

        logger.info(f"Scoring complete. Total score: {total_score}, Factors: {len(factors)}")
        return total_score, factors

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scorer = XAIScorer()

    test_data_1 = {"value": 500}
    score_1, factors_1 = scorer.score(test_data_1)
    print(f"Test Data 1 Score: {score_1}, Factors: {factors_1}") # Expected: 0, []

    test_data_2 = {"value": 150000, "anomaly_detected": True}
    score_2, factors_2 = scorer.score(test_data_2)
    print(f"Test Data 2 Score: {score_2}, Factors: {factors_2}") # Expected: 50, [factor1, factor2]

    test_data_3 = {"is_circular": True}
    score_3, factors_3 = scorer.score(test_data_3)
    print(f"Test Data 3 Score: {score_3}, Factors: {factors_3}") # Expected: 40, [factor]
