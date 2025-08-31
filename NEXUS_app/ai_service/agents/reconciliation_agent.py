#!/usr/bin/env python3
"""
Reconciliation Agent - Deterministic Matching and Reconciliation Engine

This module implements the ReconciliationAgent class that handles
deterministic matching algorithms for Nexus.
"""

import asyncio
import difflib
import hashlib
import json
import logging
import re
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class MatchingAlgorithm(Enum):
    """Matching algorithm types."""

    EXACT_MATCH = "exact_match"
    FUZZY_MATCH = "fuzzy_match"
    HASH_MATCH = "hash_match"
    PATTERN_MATCH = "pattern_match"
    SEMANTIC_MATCH = "semantic_match"
    COMPOSITE_MATCH = "composite_match"


class MatchConfidence(Enum):
    """Match confidence levels."""

    EXACT = "exact"  # 100% confidence
    HIGH = "high"  # 90-99% confidence
    MEDIUM = "medium"  # 70-89% confidence
    LOW = "low"  # 50-69% confidence
    POOR = "poor"  # Below 50% confidence


@dataclass
class MatchResult:
    """Match result data."""

    source_id: str
    target_id: str
    algorithm: MatchingAlgorithm
    confidence: float
    confidence_level: MatchConfidence
    match_score: float
    matched_fields: List[str]
    unmatched_fields: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """__post_init__ function."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class ReconciliationRecord:
    """Reconciliation record data."""

    id: str
    source_system: str
    target_system: str
    record_type: str
    record_data: Dict[str, Any]
    hash_value: str
    normalized_data: Dict[str, Any] = field(default_factory=dict)
    match_candidates: List[MatchResult] = field(default_factory=list)
    best_match: Optional[MatchResult] = None
    reconciliation_status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """__post_init__ function."""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()


class ReconciliationAgent:
    """
    Reconciliation agent for forensic investigations.

    The ReconciliationAgent is responsible for:
    - Implementing deterministic matching algorithms
    - Processing reconciliation records
    - Generating match results with confidence scores
    - Managing reconciliation workflows
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the ReconciliationAgent.Initialize the ReconciliationAgent."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.enable_exact_matching = config.get("enable_exact_matching", True)
        self.enable_fuzzy_matching = config.get("enable_fuzzy_matching", True)
        self.enable_hash_matching = config.get("enable_hash_matching", True)
        self.fuzzy_threshold = config.get("fuzzy_threshold", 0.8)
        self.hash_algorithms = config.get("hash_algorithms", ["md5", "sha1", "sha256"])

        # Internal state
        self.reconciliation_records: Dict[str, ReconciliationRecord] = {}
        self.match_results: List[MatchResult] = []
        self.matching_rules: Dict[str, Dict[str, Any]] = {}

        # Performance tracking
        self.total_records_processed = 0
        self.total_matches_found = 0
        self.average_processing_time = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("ReconciliationAgent initialized successfully")

    async def start(self):
        """Start the ReconciliationAgent.Start the ReconciliationAgent."""
        self.logger.info("Starting ReconciliationAgent...")

        # Initialize matching rules
        await self._initialize_matching_rules()

        # Start background tasks
        asyncio.create_task(self._process_reconciliation_queue())
        asyncio.create_task(self._cleanup_old_records())

        self.logger.info("ReconciliationAgent started successfully")

    async def stop(self):
        """Stop the ReconciliationAgent.Stop the ReconciliationAgent."""
        self.logger.info("Stopping ReconciliationAgent...")
        self.logger.info("ReconciliationAgent stopped")

    async def add_reconciliation_record(self, record: ReconciliationRecord) -> bool:
        """Add a reconciliation record for processing.Add a reconciliation record for processing."""
        try:
            # Generate hash value
            record.hash_value = self._generate_hash(record.record_data)

            # Normalize data
            record.normalized_data = await self._normalize_record_data(
                record.record_data
            )

            # Store record
            self.reconciliation_records[record.id] = record

            self.logger.info(f"Added reconciliation record {record.id}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding reconciliation record: {e}")
            return False

    async def process_reconciliation(
        self, source_system: str, target_system: str, record_type: str = None
    ) -> List[MatchResult]:
        """Process reconciliation between two systems.Process reconciliation between two systems."""
        try:
            start_time = datetime.utcnow()

            # Get records for reconciliation
            source_records = [
                r
                for r in self.reconciliation_records.values()
                if r.source_system == source_system
                and (not record_type or r.record_type == record_type)
            ]

            target_records = [
                r
                for r in self.reconciliation_records.values()
                if r.target_system == target_system
                and (not record_type or r.record_type == record_type)
            ]

            if not source_records or not target_records:
                self.logger.info(
                    f"No records found for reconciliation: {source_system} -> {target_system}"
                )
                return []

            self.logger.info(
                f"Processing reconciliation: {len(source_records)} source records vs {len(target_records)} target records"
            )

            # Process each source record
            all_matches = []
            for source_record in source_records:
                matches = await self._find_matches_for_record(
                    source_record, target_records
                )
                source_record.match_candidates = matches

                if matches:
                    # Find best match
                    best_match = max(matches, key=lambda m: m.confidence)
                    source_record.best_match = best_match
                    source_record.reconciliation_status = "matched"
                    all_matches.extend(matches)
                else:
                    source_record.reconciliation_status = "unmatched"

            # Update performance metrics
            self.total_records_processed += len(source_records)
            self.total_matches_found += len(all_matches)

            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_average_processing_time(processing_time)

            self.logger.info(
                f"Reconciliation completed: {len(all_matches)} matches found in {processing_time:.2f}s"
            )
            return all_matches

        except Exception as e:
            self.logger.error(f"Error processing reconciliation: {e}")
            return []

    async def get_match_results(self, record_id: str = None) -> List[MatchResult]:
        """Get match results for a specific record or all records.Get match results for a specific record or all records."""
        if record_id:
            if record_id in self.reconciliation_records:
                return self.reconciliation_records[record_id].match_candidates
            return []

        return self.match_results

    async def get_reconciliation_status(
        self, source_system: str, target_system: str
    ) -> Dict[str, Any]:
        """Get reconciliation status summary.Get reconciliation status summary."""
        try:
            source_records = [
                r
                for r in self.reconciliation_records.values()
                if r.source_system == source_system
            ]

            target_records = [
                r
                for r in self.reconciliation_records.values()
                if r.target_system == target_system
            ]

            matched_count = sum(
                1 for r in source_records if r.reconciliation_status == "matched"
            )
            unmatched_count = sum(
                1 for r in source_records if r.reconciliation_status == "unmatched"
            )

            return {
                "source_system": source_system,
                "target_system": target_system,
                "total_source_records": len(source_records),
                "total_target_records": len(target_records),
                "matched_records": matched_count,
                "unmatched_records": unmatched_count,
                "match_rate": (
                    matched_count / len(source_records) if source_records else 0
                ),
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error getting reconciliation status: {e}")
            return {}

    async def _find_matches_for_record(
        self,
        source_record: ReconciliationRecord,
        target_records: List[ReconciliationRecord],
    ) -> List[MatchResult]:
        """Find matches for a specific source record.Find matches for a specific source record."""
        try:
            matches = []

            for target_record in target_records:
                # Skip if same record
                if source_record.id == target_record.id:
                    continue

                # Try different matching algorithms
                if self.enable_exact_matching:
                    exact_match = await self._exact_match(source_record, target_record)
                    if exact_match:
                        matches.append(exact_match)
                        continue  # Exact match found, no need for other algorithms

                if self.enable_hash_matching:
                    hash_match = await self._hash_match(source_record, target_record)
                    if hash_match:
                        matches.append(hash_match)
                        continue  # Hash match found, no need for other algorithms

                if self.enable_fuzzy_matching:
                    fuzzy_match = await self._fuzzy_match(source_record, target_record)
                    if fuzzy_match and fuzzy_match.confidence >= self.fuzzy_threshold:
                        matches.append(fuzzy_match)

            # Sort matches by confidence (descending)
            matches.sort(key=lambda m: m.confidence, reverse=True)

            return matches

        except Exception as e:
            self.logger.error(
                f"Error finding matches for record {source_record.id}: {e}"
            )
            return []

    async def _exact_match(
        self, source_record: ReconciliationRecord, target_record: ReconciliationRecord
    ) -> Optional[MatchResult]:
        """Perform exact matching between records.Perform exact matching between records."""
        try:
            # Check if hash values match exactly
            if source_record.hash_value == target_record.hash_value:
                return MatchResult(
                    source_id=source_record.id,
                    target_id=target_record.id,
                    algorithm=MatchingAlgorithm.EXACT_MATCH,
                    confidence=1.0,
                    confidence_level=MatchConfidence.EXACT,
                    match_score=1.0,
                    matched_fields=list(source_record.normalized_data.keys()),
                    unmatched_fields=[],
                    metadata={"hash_match": True},
                )

            # Check for exact field matches
            matched_fields = []
            unmatched_fields = []

            for field, source_value in source_record.normalized_data.items():
                if field in target_record.normalized_data:
                    target_value = target_record.normalized_data[field]
                    if source_value == target_value:
                        matched_fields.append(field)
                    else:
                        unmatched_fields.append(field)
                else:
                    unmatched_fields.append(field)

            # Calculate exact match confidence
            if matched_fields:
                confidence = len(matched_fields) / len(source_record.normalized_data)
                if confidence == 1.0:
                    return MatchResult(
                        source_id=source_record.id,
                        target_id=target_record.id,
                        algorithm=MatchingAlgorithm.EXACT_MATCH,
                        confidence=confidence,
                        confidence_level=MatchConfidence.EXACT,
                        match_score=confidence,
                        matched_fields=matched_fields,
                        unmatched_fields=unmatched_fields,
                        metadata={"field_match": True},
                    )

            return None

        except Exception as e:
            self.logger.error(f"Error in exact matching: {e}")
            return None

    async def _hash_match(
        self, source_record: ReconciliationRecord, target_record: ReconciliationRecord
    ) -> Optional[MatchResult]:
        """Perform hash-based matching between records.Perform hash-based matching between records."""
        try:
            # Check multiple hash algorithms
            for hash_alg in self.hash_algorithms:
                source_hash = self._generate_hash_with_algorithm(
                    source_record.record_data, hash_alg
                )
                target_hash = self._generate_hash_with_algorithm(
                    target_record.record_data, hash_alg
                )

                if source_hash == target_hash:
                    return MatchResult(
                        source_id=source_record.id,
                        target_id=target_record.id,
                        algorithm=MatchingAlgorithm.HASH_MATCH,
                        confidence=0.95,  # High confidence for hash matches
                        confidence_level=MatchConfidence.HIGH,
                        match_score=0.95,
                        matched_fields=["hash_value"],
                        unmatched_fields=[],
                        metadata={"hash_algorithm": hash_alg, "hash_match": True},
                    )

            return None

        except Exception as e:
            self.logger.error(f"Error in hash matching: {e}")
            return None

    async def _fuzzy_match(
        self, source_record: ReconciliationRecord, target_record: ReconciliationRecord
    ) -> Optional[MatchResult]:
        """Perform fuzzy matching between records.Perform fuzzy matching between records."""
        try:
            matched_fields = []
            unmatched_fields = []
            total_similarity = 0.0
            field_count = 0

            # Compare each field using fuzzy matching
            for field, source_value in source_record.normalized_data.items():
                if field in target_record.normalized_data:
                    target_value = target_record.normalized_data[field]

                    # Convert to strings for comparison
                    source_str = str(source_value).lower()
                    target_str = str(target_value).lower()

                    # Calculate similarity using difflib
                    similarity = difflib.SequenceMatcher(
                        None, source_str, target_str
                    ).ratio()
                    total_similarity += similarity
                    field_count += 1

                    if similarity >= self.fuzzy_threshold:
                        matched_fields.append(field)
                    else:
                        unmatched_fields.append(field)
                else:
                    unmatched_fields.append(field)

            if field_count == 0:
                return None

            # Calculate overall confidence
            confidence = total_similarity / field_count

            # Determine confidence level
            if confidence >= 0.9:
                confidence_level = MatchConfidence.HIGH
            elif confidence >= 0.7:
                confidence_level = MatchConfidence.MEDIUM
            else:
                confidence_level = MatchConfidence.LOW

            return MatchResult(
                source_id=source_record.id,
                target_id=target_record.id,
                algorithm=MatchingAlgorithm.FUZZY_MATCH,
                confidence=confidence,
                confidence_level=confidence_level,
                match_score=confidence,
                matched_fields=matched_fields,
                unmatched_fields=unmatched_fields,
                metadata={"fuzzy_threshold": self.fuzzy_threshold},
            )

        except Exception as e:
            self.logger.error(f"Error in fuzzy matching: {e}")
            return None

    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """Generate hash value for record data.Generate hash value for record data."""
        try:
            # Sort keys for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(sorted_data.encode()).hexdigest()

        except Exception as e:
            self.logger.error(f"Error generating hash: {e}")
            return ""

    def _generate_hash_with_algorithm(
        self, data: Dict[str, Any], algorithm: str
    ) -> str:
        """Generate hash value using specific algorithm.Generate hash value using specific algorithm."""
        try:
            sorted_data = json.dumps(data, sort_keys=True, default=str)

            if algorithm == "md5":
                return hashlib.md5(sorted_data.encode()).hexdigest()
            elif algorithm == "sha1":
                return hashlib.sha1(sorted_data.encode()).hexdigest()
            elif algorithm == "sha256":
                return hashlib.sha256(sorted_data.encode()).hexdigest()
            else:
                return hashlib.sha256(sorted_data.encode()).hexdigest()

        except Exception as e:
            self.logger.error(f"Error generating hash with algorithm {algorithm}: {e}")
            return ""

    async def _normalize_record_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize record data for consistent matching.Normalize record data for consistent matching."""
        try:
            normalized = {}

            for key, value in data.items():
                # Normalize key names
                normalized_key = key.lower().strip().replace(" ", "_")

                # Normalize values
                if isinstance(value, str):
                    normalized_value = value.lower().strip()
                    # Remove common punctuation
                    normalized_value = re.sub(r"[^\w\s]", "", normalized_value)
                elif isinstance(value, (int, float)):
                    normalized_value = str(value)
                elif isinstance(value, datetime):
                    normalized_value = value.isoformat()
                else:
                    normalized_value = str(value).lower().strip()

                normalized[normalized_key] = normalized_value

            return normalized

        except Exception as e:
            self.logger.error(f"Error normalizing record data: {e}")
            return data

    async def _initialize_matching_rules(self):
        """Initialize matching rules and configurations.Initialize matching rules and configurations."""
        try:
            # Define matching rules for different record types
            self.matching_rules = {
                "transaction": {
                    "primary_fields": ["transaction_id", "amount", "date"],
                    "secondary_fields": ["description", "account_number"],
                    "fuzzy_threshold": 0.8,
                    "required_fields": ["transaction_id"],
                },
                "customer": {
                    "primary_fields": ["customer_id", "email", "phone"],
                    "secondary_fields": ["name", "address"],
                    "fuzzy_threshold": 0.7,
                    "required_fields": ["customer_id"],
                },
                "document": {
                    "primary_fields": ["document_id", "hash_value"],
                    "secondary_fields": ["title", "content"],
                    "fuzzy_threshold": 0.6,
                    "required_fields": ["document_id"],
                },
            }

            self.logger.info(f"Initialized {len(self.matching_rules)} matching rules")

        except Exception as e:
            self.logger.error(f"Error initializing matching rules: {e}")

    async def _process_reconciliation_queue(self):
        """Process reconciliation queue in background.Process reconciliation queue in background."""
        # This would process reconciliation jobs from the queue
        # For now, it's a placeholder
        pass

    async def _cleanup_old_records(self):
        """Clean up old reconciliation records.Clean up old reconciliation records."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(days=30)

                # Remove old records
                old_records = [
                    record_id
                    for record_id, record in self.reconciliation_records.items()
                    if record.created_at < cutoff_time
                ]

                for record_id in old_records:
                    del self.reconciliation_records[record_id]

                if old_records:
                    self.logger.info(
                        f"Cleaned up {len(old_records)} old reconciliation records"
                    )

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up old records: {e}")
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
            "total_matches_found": self.total_matches_found,
            "average_processing_time": self.average_processing_time,
            "match_rate": (
                self.total_matches_found / self.total_records_processed
                if self.total_records_processed > 0
                else 0
            ),
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "enable_exact_matching": True,
        "enable_fuzzy_matching": True,
        "enable_hash_matching": True,
        "fuzzy_threshold": 0.8,
        "hash_algorithms": ["md5", "sha1", "sha256"],
    }

    # Initialize reconciliation agent
    agent = ReconciliationAgent(config)

    print("ReconciliationAgent system initialized successfully!")
