#!/usr/bin/env python3
"""
Fixed Compliance Rule Engine - Risk Agent Compliance Engine
Priority: HIGH | Duration: 18-24 hours
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ComplianceType(Enum):
    """Types of compliance"""

    SOX = "sox"
    PCI_DSS = "pci_dss"
    AML = "aml"
    GDPR = "gdpr"


@dataclass
class ComplianceRule:
    """Individual compliance rule"""

    id: str
    name: str
    compliance_type: ComplianceType
    description: str
    severity: str
    enabled: bool
    parameters: Dict[str, Any]


@dataclass
class ComplianceResult:
    """Result of compliance check"""

    rule_id: str
    status: str
    score: float
    details: Dict[str, Any]
    timestamp: datetime


class ComplianceRuleEngine:
    """Fixed compliance rule engine for risk assessment"""

    def __init__(self):
        """__init__ function."""
        self.rules: Dict[str, ComplianceRule] = {}
        self.results: List[ComplianceResult] = []
        self.compliance_scores: Dict[ComplianceType, float] = {}

        # Initialize default rules
        self._initialize_default_rules()

        logger.info("Compliance Rule Engine initialized successfully")

    def _initialize_default_rules(self):
        """Initialize default compliance rulesInitialize default compliance rules"""
        default_rules = [
            ComplianceRule(
                id="sox_001",
                name="Financial Statement Accuracy",
                compliance_type=ComplianceType.SOX,
                description="Ensure financial statements are accurate and complete",
                severity="high",
                enabled=True,
                parameters={"threshold": 0.95},
            ),
            ComplianceRule(
                id="pci_001",
                name="Card Data Protection",
                compliance_type=ComplianceType.PCI_DSS,
                description="Protect cardholder data from unauthorized access",
                severity="critical",
                enabled=True,
                parameters={"encryption_required": True},
            ),
            ComplianceRule(
                id="aml_001",
                name="Suspicious Transaction Detection",
                compliance_type=ComplianceType.AML,
                description="Detect and report suspicious transactions",
                severity="high",
                enabled=True,
                parameters={"threshold_amount": 10000},
            ),
            ComplianceRule(
                id="gdpr_001",
                name="Data Privacy Protection",
                compliance_type=ComplianceType.GDPR,
                description="Ensure personal data is protected and processed lawfully",
                severity="high",
                enabled=True,
                parameters={"consent_required": True},
            ),
        ]

        for rule in default_rules:
            self.rules[rule.id] = rule

    def add_rule(self, rule: ComplianceRule) -> bool:
        """Add a new compliance ruleAdd a new compliance rule"""
        try:
            self.rules[rule.id] = rule
            logger.info(f"Added compliance rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add rule {rule.name}: {e}")
            return False

    def check_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance against all enabled rulesCheck compliance against all enabled rules"""
        results = {}
        overall_score = 0.0
        total_rules = 0

        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue

            total_rules += 1
            result = self._evaluate_rule(rule, data)
            results[rule_id] = result
            overall_score += result.score

        if total_rules > 0:
            overall_score = overall_score / total_rules

        return {
            "overall_score": overall_score,
            "total_rules": total_rules,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    def _evaluate_rule(
        self, rule: ComplianceRule, data: Dict[str, Any]
    ) -> ComplianceResult:
        """Evaluate a single compliance ruleEvaluate a single compliance rule"""
        try:
            if rule.compliance_type == ComplianceType.SOX:
                score = self._evaluate_sox_rule(rule, data)
            elif rule.compliance_type == ComplianceType.PCI_DSS:
                score = self._evaluate_pci_rule(rule, data)
            elif rule.compliance_type == ComplianceType.AML:
                score = self._evaluate_aml_rule(rule, data)
            elif rule.compliance_type == ComplianceType.GDPR:
                score = self._evaluate_gdpr_rule(rule, data)
            else:
                score = 0.0

            result = ComplianceResult(
                rule_id=rule.id,
                status="pass" if score >= 0.8 else "fail",
                score=score,
                details={"evaluation_method": "rule_based"},
                timestamp=datetime.now(),
            )

            self.results.append(result)
            return result

        except Exception as e:
            logger.error(f"Error evaluating rule {rule.id}: {e}")
            return ComplianceResult(
                rule_id=rule.id,
                status="error",
                score=0.0,
                details={"error": str(e)},
                timestamp=datetime.now(),
            )

    def _evaluate_sox_rule(self, rule: ComplianceRule, data: Dict[str, Any]) -> float:
        """Evaluate SOX compliance ruleEvaluate SOX compliance rule"""
        # Simple SOX evaluation logic
        if "financial_data" in data:
            accuracy = data.get("financial_accuracy", 0.9)
            return min(accuracy, 1.0)
        return 0.5

    def _evaluate_pci_rule(self, rule: ComplianceRule, data: Dict[str, Any]) -> float:
        """Evaluate PCI DSS compliance ruleEvaluate PCI DSS compliance rule"""
        # Simple PCI evaluation logic
        if "card_data_encrypted" in data:
            return 1.0 if data["card_data_encrypted"] else 0.0
        return 0.5

    def _evaluate_aml_rule(self, rule: ComplianceRule, data: Dict[str, Any]) -> float:
        """Evaluate AML compliance ruleEvaluate AML compliance rule"""
        # Simple AML evaluation logic
        if "transaction_amount" in data:
            amount = data["transaction_amount"]
            threshold = rule.parameters.get("threshold_amount", 10000)
            return 1.0 if amount < threshold else 0.3
        return 0.5

    def _evaluate_gdpr_rule(self, rule: ComplianceRule, data: Dict[str, Any]) -> float:
        """Evaluate GDPR compliance ruleEvaluate GDPR compliance rule"""
        # Simple GDPR evaluation logic
        if "consent_given" in data:
            return 1.0 if data["consent_given"] else 0.0
        return 0.5

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance summaryGet compliance summary"""
        if not self.results:
            return {"message": "No compliance checks performed yet"}

        summary = {
            "total_checks": len(self.results),
            "passed": len([r for r in self.results if r.status == "pass"]),
            "failed": len([r for r in self.results if r.status == "fail"]),
            "errors": len([r for r in self.results if r.status == "error"]),
            "average_score": sum(r.score for r in self.results) / len(self.results),
            "last_check": max(r.timestamp for r in self.results).isoformat(),
        }

        return summary


def main():
    """Test the compliance rule engineTest the compliance rule engine"""
    print("🧪 Testing Fixed Compliance Rule Engine")
    print("=" * 50)

    # Create engine
    engine = ComplianceRuleEngine()

    # Test data
    test_data = {
        "financial_accuracy": 0.98,
        "card_data_encrypted": True,
        "transaction_amount": 5000,
        "consent_given": True,
    }

    # Check compliance
    print("📋 Checking compliance...")
    results = engine.check_compliance(test_data)

    print(f"Overall Score: {results['overall_score']:.2f}")
    print(f"Total Rules: {results['total_rules']}")

    print("\n📊 Individual Rule Results:")
    for rule_id, result in results["results"].items():
        print(f"  {rule_id}: {result.status} (Score: {result.score:.2f})")

    # Get summary
    print("\n📈 Compliance Summary:")
    summary = engine.get_compliance_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\n✅ Compliance Rule Engine test completed!")


if __name__ == "__main__":
    main()
