#!/usr/bin/env python3
"""
AI-Powered Fuzzy Matcher - Advanced Fuzzy Matching with Machine Learning

This module implements the AIFuzzyMatcher class that provides
AI-powered fuzzy matching capabilities for Nexus.
"""

import asyncio
import logging
import re
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import jaro
import numpy as np

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class FuzzyAlgorithm(Enum):
    """Fuzzy matching algorithm types."""

    TFIDF_COSINE = "tfidf_cosine"
    JARO_WINKLER = "jaro_winkler"
    LEVENSHTEIN = "levenshtein"
    NGRAM = "ngram"
    PHONETIC = "phonetic"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class MatchQuality(Enum):
    """Match quality levels."""

    EXCELLENT = "excellent"  # 95-100% confidence
    VERY_GOOD = "very_good"  # 90-94% confidence
    GOOD = "good"  # 80-89% confidence
    FAIR = "fair"  # 70-79% confidence
    POOR = "poor"  # Below 70% confidence


@dataclass
class FuzzyMatchResult:
    """Fuzzy match result data."""

    source_id: str
    target_id: str
    algorithm: FuzzyAlgorithm
    confidence: float
    quality: MatchQuality
    similarity_score: float
    matched_features: List[str]
    feature_scores: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """__post_init__ function."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow()


@dataclass
class MatchingFeature:
    """Feature for matching analysis."""

    name: str
    value: Any
    weight: float
    algorithm: FuzzyAlgorithm
    normalized_value: str = ""
    feature_vector: Optional[np.ndarray] = None

    def __post_init__(self):
        """__post_init__ function."""
        if not self.normalized_value:
            self.normalized_value = self._normalize_value()

    def _normalize_value(self) -> str:
        """Normalize feature value for matching."""
        if isinstance(self.value, str):
            return self.value.lower().strip()
        elif isinstance(self.value, (int, float)):
            return str(self.value)
        else:
            return str(self.value).lower().strip()


class AIFuzzyMatcher:
    """
    AI-powered fuzzy matching engine for Nexus.

    The AIFuzzyMatcher is responsible for:
    - Implementing advanced fuzzy matching algorithms
    - Using machine learning for similarity scoring
    - Providing configurable matching strategies
    - Optimizing matching performance
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the AIFuzzyMatcher."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.enable_tfidf = config.get("enable_tfidf", True)
        self.enable_jaro = config.get("enable_jaro", True)
        self.enable_levenshtein = config.get("enable_levenshtein", True)
        self.enable_ngram = config.get("enable_ngram", True)
        self.enable_phonetic = config.get("enable_phonetic", True)
        self.enable_semantic = config.get("enable_semantic", True)

        # Thresholds
        self.min_confidence = config.get("min_confidence", 0.6)
        self.excellent_threshold = config.get("excellent_threshold", 0.95)
        self.very_good_threshold = config.get("very_good_threshold", 0.90)
        self.good_threshold = config.get("good_threshold", 0.80)
        self.fair_threshold = config.get("fair_threshold", 0.70)

        # Internal state
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", ngram_range=(1, 3), min_df=1
        )
        self.feature_vectors: Dict[str, np.ndarray] = {}
        self.matching_history: List[FuzzyMatchResult] = []

        # Performance tracking
        self.total_matches_processed = 0
        self.average_processing_time = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("AIFuzzyMatcher initialized successfully")

    async def start(self):
        """Start the AIFuzzyMatcher.Start the AIFuzzyMatcher."""
        self.logger.info("Starting AIFuzzyMatcher...")

        # Initialize vectorizer with sample data
        await self._initialize_vectorizer()

        self.logger.info("AIFuzzyMatcher started successfully")

    async def stop(self):
        """Stop the AIFuzzyMatcher.Stop the AIFuzzyMatcher."""
        self.logger.info("Stopping AIFuzzyMatcher...")
        self.logger.info("AIFuzzyMatcher stopped")

    async def find_fuzzy_matches(
        self,
        source_record: Dict[str, Any],
        target_records: List[Dict[str, Any]],
        algorithm: FuzzyAlgorithm = FuzzyAlgorithm.HYBRID,
    ) -> List[FuzzyMatchResult]:
        """Find fuzzy matches using the specified algorithm.Find fuzzy matches using the specified algorithm."""
        try:
            start_time = datetime.utcnow()

            if algorithm == FuzzyAlgorithm.HYBRID:
                return await self._hybrid_fuzzy_match(source_record, target_records)
            elif algorithm == FuzzyAlgorithm.TFIDF_COSINE:
                return await self._tfidf_cosine_match(source_record, target_records)
            elif algorithm == FuzzyAlgorithm.JARO_WINKLER:
                return await self._jaro_winkler_match(source_record, target_records)
            elif algorithm == FuzzyAlgorithm.LEVENSHTEIN:
                return await self._levenshtein_match(source_record, target_records)
            elif algorithm == FuzzyAlgorithm.NGRAM:
                return await self._ngram_match(source_record, target_records)
            elif algorithm == FuzzyAlgorithm.PHONETIC:
                return await self._phonetic_match(source_record, target_records)
            elif algorithm == FuzzyAlgorithm.SEMANTIC:
                return await self._semantic_match(source_record, target_records)
            else:
                return await self._hybrid_fuzzy_match(source_record, target_records)

        except Exception as e:
            self.logger.error(f"Error in fuzzy matching: {e}")
            return []

    async def _hybrid_fuzzy_match(
        self, source_record: Dict[str, Any], target_records: List[Dict[str, Any]]
    ) -> List[FuzzyMatchResult]:
        """Perform hybrid fuzzy matching combining multiple algorithms.Perform hybrid fuzzy matching combining multiple algorithms."""
        try:
            all_matches = []

            # Get matches from different algorithms
            if self.enable_tfidf:
                tfidf_matches = await self._tfidf_cosine_match(
                    source_record, target_records
                )
                all_matches.extend(tfidf_matches)

            if self.enable_jaro:
                jaro_matches = await self._jaro_winkler_match(
                    source_record, target_records
                )
                all_matches.extend(jaro_matches)

            if self.enable_levenshtein:
                levenshtein_matches = await self._levenshtein_match(
                    source_record, target_records
                )
                all_matches.extend(levenshtein_matches)

            if self.enable_ngram:
                ngram_matches = await self._ngram_match(source_record, target_records)
                all_matches.extend(ngram_matches)

            # Combine and rank matches
            combined_matches = self._combine_match_results(all_matches)

            # Filter by confidence threshold
            filtered_matches = [
                match
                for match in combined_matches
                if match.confidence >= self.min_confidence
            ]

            # Sort by confidence (descending)
            filtered_matches.sort(key=lambda m: m.confidence, reverse=True)

            return filtered_matches

        except Exception as e:
            self.logger.error(f"Error in hybrid fuzzy matching: {e}")
            return []

    async def _tfidf_cosine_match(
        self, source_record: Dict[str, Any], target_records: List[Dict[str, Any]]
    ) -> List[FuzzyMatchResult]:
        """Perform TF-IDF cosine similarity matching.Perform TF-IDF cosine similarity matching."""
        try:
            matches = []

            # Prepare source text
            source_text = self._prepare_text_for_tfidf(source_record)

            # Prepare target texts
            target_texts = []
            target_ids = []

            for target_record in target_records:
                target_text = self._prepare_text_for_tfidf(target_record)
                target_texts.append(target_text)
                target_ids.append(target_record.get("id", str(uuid.uuid4())))

            if not target_texts:
                return []

            # Vectorize texts
            try:
                all_texts = [source_text] + target_texts
                tfidf_matrix = self.vectorizer.fit_transform(all_texts)

                # Calculate cosine similarities
                source_vector = tfidf_matrix[0:1]
                target_vectors = tfidf_matrix[1:]

                similarities = cosine_similarity(
                    source_vector, target_vectors
                ).flatten()

                # Create match results
                for i, similarity in enumerate(similarities):
                    if similarity > 0:
                        confidence = float(similarity)
                        quality = self._determine_quality(confidence)

                        match = FuzzyMatchResult(
                            source_id=source_record.get("id", "unknown"),
                            target_id=target_ids[i],
                            algorithm=FuzzyAlgorithm.TFIDF_COSINE,
                            confidence=confidence,
                            quality=quality,
                            similarity_score=similarity,
                            matched_features=["text_content"],
                            feature_scores={"text_similarity": similarity},
                            metadata={"algorithm": "tfidf_cosine"},
                        )

                        matches.append(match)

            except Exception as e:
                self.logger.warning(f"TF-IDF processing failed: {e}")

            return matches

        except Exception as e:
            self.logger.error(f"Error in TF-IDF matching: {e}")
            return []

    async def _jaro_winkler_match(
        self, source_record: Dict[str, Any], target_records: List[Dict[str, Any]]
    ) -> List[FuzzyMatchResult]:
        """Perform Jaro-Winkler similarity matching.Perform Jaro-Winkler similarity matching."""
        try:
            matches = []

            # Extract text fields for comparison
            source_fields = self._extract_text_fields(source_record)

            for target_record in target_records:
                target_fields = self._extract_text_fields(target_record)

                # Calculate Jaro-Winkler similarity for each field
                field_scores = {}
                total_similarity = 0.0
                field_count = 0

                for field_name in source_fields.keys():
                    if field_name in target_fields:
                        source_value = source_fields[field_name]
                        target_value = target_fields[field_name]

                        # Calculate Jaro-Winkler similarity
                        similarity = jaro.jaro_winkler_metric(
                            source_value, target_value
                        )
                        field_scores[field_name] = similarity
                        total_similarity += similarity
                        field_count += 1

                if field_count > 0:
                    average_similarity = total_similarity / field_count
                    confidence = average_similarity
                    quality = self._determine_quality(confidence)

                    match = FuzzyMatchResult(
                        source_id=source_record.get("id", "unknown"),
                        target_id=target_record.get("id", "unknown"),
                        algorithm=FuzzyAlgorithm.JARO_WINKLER,
                        confidence=confidence,
                        quality=quality,
                        similarity_score=average_similarity,
                        matched_features=list(field_scores.keys()),
                        feature_scores=field_scores,
                        metadata={"algorithm": "jaro_winkler"},
                    )

                    matches.append(match)

            return matches

        except Exception as e:
            self.logger.error(f"Error in Jaro-Winkler matching: {e}")
            return []

    async def _levenshtein_match(
        self, source_record: Dict[str, Any], target_records: List[Dict[str, Any]]
    ) -> List[FuzzyMatchResult]:
        """Perform Levenshtein distance matching.Perform Levenshtein distance matching."""
        try:
            matches = []

            # Extract text fields for comparison
            source_fields = self._extract_text_fields(source_record)

            for target_record in target_records:
                target_fields = self._extract_text_fields(target_record)

                # Calculate Levenshtein similarity for each field
                field_scores = {}
                total_similarity = 0.0
                field_count = 0

                for field_name in source_fields.keys():
                    if field_name in target_fields:
                        source_value = source_fields[field_name]
                        target_value = target_fields[field_name]

                        # Calculate Levenshtein distance and convert to similarity
                        distance = self._levenshtein_distance(
                            source_value, target_value
                        )
                        max_length = max(len(source_value), len(target_value))

                        if max_length > 0:
                            similarity = 1 - (distance / max_length)
                            field_scores[field_name] = similarity
                            total_similarity += similarity
                            field_count += 1

                if field_count > 0:
                    average_similarity = total_similarity / field_count
                    confidence = average_similarity
                    quality = self._determine_quality(confidence)

                    match = FuzzyMatchResult(
                        source_id=source_record.get("id", "unknown"),
                        target_id=target_record.get("id", "unknown"),
                        algorithm=FuzzyAlgorithm.LEVENSHTEIN,
                        confidence=confidence,
                        quality=quality,
                        similarity_score=average_similarity,
                        matched_features=list(field_scores.keys()),
                        feature_scores=field_scores,
                        metadata={"algorithm": "levenshtein"},
                    )

                    matches.append(match)

            return matches

        except Exception as e:
            self.logger.error(f"Error in Levenshtein matching: {e}")
            return []

    async def _ngram_match(
        self, source_record: Dict[str, Any], target_records: List[Dict[str, Any]]
    ) -> List[FuzzyMatchResult]:
        """Perform N-gram similarity matching.Perform N-gram similarity matching."""
        try:
            matches = []

            # Extract text fields for comparison
            source_fields = self._extract_text_fields(source_record)

            for target_record in target_records:
                target_fields = self._extract_text_fields(target_record)

                # Calculate N-gram similarity for each field
                field_scores = {}
                total_similarity = 0.0
                field_count = 0

                for field_name in source_fields.keys():
                    if field_name in target_fields:
                        source_value = source_fields[field_name]
                        target_value = target_fields[field_name]

                        # Calculate N-gram similarity
                        similarity = self._ngram_similarity(source_value, target_value)
                        field_scores[field_name] = similarity
                        total_similarity += similarity
                        field_count += 1

                if field_count > 0:
                    average_similarity = total_similarity / field_count
                    confidence = average_similarity
                    quality = self._determine_quality(confidence)

                    match = FuzzyMatchResult(
                        source_id=source_record.get("id", "unknown"),
                        target_id=target_record.get("id", "unknown"),
                        algorithm=FuzzyAlgorithm.NGRAM,
                        confidence=confidence,
                        quality=quality,
                        similarity_score=average_similarity,
                        matched_features=list(field_scores.keys()),
                        feature_scores=field_scores,
                        metadata={"algorithm": "ngram"},
                    )

                    matches.append(match)

            return matches

        except Exception as e:
            self.logger.error(f"Error in N-gram matching: {e}")
            return []

    async def _phonetic_match(
        self, source_record: Dict[str, Any], target_records: List[Dict[str, Any]]
    ) -> List[FuzzyMatchResult]:
        """Perform phonetic similarity matching.Perform phonetic similarity matching."""
        try:
            matches = []

            # Extract text fields for comparison
            source_fields = self._extract_text_fields(source_record)

            for target_record in target_records:
                target_fields = self._extract_text_fields(target_record)

                # Calculate phonetic similarity for each field
                field_scores = {}
                total_similarity = 0.0
                field_count = 0

                for field_name in source_fields.keys():
                    if field_name in target_fields:
                        source_value = source_fields[field_name]
                        target_value = target_fields[field_name]

                        # Calculate phonetic similarity
                        similarity = self._phonetic_similarity(
                            source_value, target_value
                        )
                        field_scores[field_name] = similarity
                        total_similarity += similarity
                        field_count += 1

                if field_count > 0:
                    average_similarity = total_similarity / field_count
                    confidence = average_similarity
                    quality = self._determine_quality(confidence)

                    match = FuzzyMatchResult(
                        source_id=source_record.get("id", "unknown"),
                        target_id=target_record.get("id", "unknown"),
                        algorithm=FuzzyAlgorithm.PHONETIC,
                        confidence=confidence,
                        quality=quality,
                        similarity_score=average_similarity,
                        matched_features=list(field_scores.keys()),
                        feature_scores=field_scores,
                        metadata={"algorithm": "phonetic"},
                    )

                    matches.append(match)

            return matches

        except Exception as e:
            self.logger.error(f"Error in phonetic matching: {e}")
            return []

    async def _semantic_match(
        self, source_record: Dict[str, Any], target_records: List[Dict[str, Any]]
    ) -> List[FuzzyMatchResult]:
        """Perform semantic similarity matching.Perform semantic similarity matching."""
        try:
            matches = []

            # This would integrate with semantic models like BERT or Word2Vec
            # For now, use a simplified approach based on keyword overlap

            source_keywords = self._extract_keywords(source_record)

            for target_record in target_records:
                target_keywords = self._extract_keywords(target_record)

                # Calculate keyword overlap similarity
                if source_keywords and target_keywords:
                    intersection = source_keywords.intersection(target_keywords)
                    union = source_keywords.union(target_keywords)

                    if union:
                        similarity = len(intersection) / len(union)
                        confidence = similarity
                        quality = self._determine_quality(confidence)

                        match = FuzzyMatchResult(
                            source_id=source_record.get("id", "unknown"),
                            target_id=target_record.get("id", "unknown"),
                            algorithm=FuzzyAlgorithm.SEMANTIC,
                            confidence=confidence,
                            quality=quality,
                            similarity_score=similarity,
                            matched_features=["keywords"],
                            feature_scores={"keyword_overlap": similarity},
                            metadata={
                                "algorithm": "semantic",
                                "keywords_matched": list(intersection),
                            },
                        )

                        matches.append(match)

            return matches

        except Exception as e:
            self.logger.error(f"Error in semantic matching: {e}")
            return []

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings.Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def _ngram_similarity(self, s1: str, s2: str, n: int = 3) -> float:
        """Calculate N-gram similarity between two strings.Calculate N-gram similarity between two strings."""
        if not s1 or not s2:
            return 0.0

        # Generate N-grams
        s1_grams = set(s1[i : i + n] for i in range(len(s1) - n + 1))
        s2_grams = set(s2[i : i + n] for i in range(len(s2) - n + 1))

        if not s1_grams or not s2_grams:
            return 0.0

        # Calculate Jaccard similarity
        intersection = s1_grams.intersection(s2_grams)
        union = s1_grams.union(s2_grams)

        return len(intersection) / len(union) if union else 0.0

    def _phonetic_similarity(self, s1: str, s2: str) -> float:
        """Calculate phonetic similarity between two strings.Calculate phonetic similarity between two strings."""
        # Simple phonetic similarity using soundex-like approach
        # In a real implementation, you'd use libraries like fuzzy or jellyfish

        # Convert to lowercase and remove non-alphabetic characters
        s1_clean = re.sub(r"[^a-z]", "", s1.lower())
        s2_clean = re.sub(r"[^a-z]", "", s2.lower())

        if not s1_clean or not s2_clean:
            return 0.0

        # Simple phonetic comparison
        if s1_clean == s2_clean:
            return 1.0

        # Check if strings start with same letter
        if s1_clean[0] == s2_clean[0]:
            return 0.8

        return 0.0

    def _extract_keywords(self, record: Dict[str, Any]) -> set:
        """Extract keywords from a record.Extract keywords from a record."""
        keywords = set()

        for value in record.values():
            if isinstance(value, str):
                # Simple keyword extraction
                words = re.findall(r"\b\w+\b", value.lower())
                # Filter out common stop words
                stop_words = {
                    "the",
                    "a",
                    "an",
                    "and",
                    "or",
                    "but",
                    "in",
                    "on",
                    "at",
                    "to",
                    "for",
                    "of",
                    "with",
                    "by",
                }
                keywords.update(
                    word for word in words if word not in stop_words and len(word) > 2
                )

        return keywords

    def _prepare_text_for_tfidf(self, record: Dict[str, Any]) -> str:
        """Prepare text from record for TF-IDF processing.Prepare text from record for TF-IDF processing."""
        text_parts = []

        for key, value in record.items():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, (int, float)):
                text_parts.append(str(value))
            elif isinstance(value, dict):
                text_parts.append(self._prepare_text_for_tfidf(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict):
                        text_parts.append(self._prepare_text_for_tfidf(item))

        return " ".join(text_parts)

    def _extract_text_fields(self, record: Dict[str, Any]) -> Dict[str, str]:
        """Extract text fields from a record.Extract text fields from a record."""
        text_fields = {}

        for key, value in record.items():
            if isinstance(value, str):
                text_fields[key] = value
            elif isinstance(value, (int, float)):
                text_fields[key] = str(value)

        return text_fields

    def _combine_match_results(
        self, matches: List[FuzzyMatchResult]
    ) -> List[FuzzyMatchResult]:
        """Combine and deduplicate match results.Combine and deduplicate match results."""
        try:
            # Group matches by target_id
            grouped_matches = defaultdict(list)

            for match in matches:
                grouped_matches[match.target_id].append(match)

            # Combine matches for each target
            combined_matches = []

            for target_id, target_matches in grouped_matches.items():
                if len(target_matches) == 1:
                    combined_matches.append(target_matches[0])
                else:
                    # Combine multiple matches for the same target
                    combined_match = self._combine_target_matches(target_matches)
                    combined_matches.append(combined_match)

            return combined_matches

        except Exception as e:
            self.logger.error(f"Error combining match results: {e}")
            return matches

    def _combine_target_matches(
        self, matches: List[FuzzyMatchResult]
    ) -> FuzzyMatchResult:
        """Combine multiple matches for the same target.Combine multiple matches for the same target."""
        try:
            # Use the best match as base
            best_match = max(matches, key=lambda m: m.confidence)

            # Calculate weighted average confidence
            total_weight = 0.0
            weighted_confidence = 0.0

            for match in matches:
                weight = 1.0
                if match.algorithm == FuzzyAlgorithm.TFIDF_COSINE:
                    weight = 1.2  # Give higher weight to TF-IDF
                elif match.algorithm == FuzzyAlgorithm.SEMANTIC:
                    weight = 1.1  # Give higher weight to semantic

                weighted_confidence += match.confidence * weight
                total_weight += weight

            combined_confidence = (
                weighted_confidence / total_weight
                if total_weight > 0
                else best_match.confidence
            )

            # Combine feature scores
            combined_feature_scores = {}
            for match in matches:
                for feature, score in match.feature_scores.items():
                    if feature not in combined_feature_scores:
                        combined_feature_scores[feature] = []
                    combined_feature_scores[feature].append(score)

            # Average feature scores
            for feature, scores in combined_feature_scores.items():
                combined_feature_scores[feature] = sum(scores) / len(scores)

            # Create combined match
            combined_match = FuzzyMatchResult(
                source_id=best_match.source_id,
                target_id=best_match.target_id,
                algorithm=FuzzyAlgorithm.HYBRID,
                confidence=combined_confidence,
                quality=self._determine_quality(combined_confidence),
                similarity_score=combined_confidence,
                matched_features=best_match.matched_features,
                feature_scores=combined_feature_scores,
                metadata={
                    "combined_algorithms": [m.algorithm.value for m in matches],
                    "original_matches": len(matches),
                },
            )

            return combined_match

        except Exception as e:
            self.logger.error(f"Error combining target matches: {e}")
            return matches[0] if matches else None

    def _determine_quality(self, confidence: float) -> MatchQuality:
        """Determine match quality based on confidence score.Determine match quality based on confidence score."""
        if confidence >= self.excellent_threshold:
            return MatchQuality.EXCELLENT
        elif confidence >= self.very_good_threshold:
            return MatchQuality.VERY_GOOD
        elif confidence >= self.good_threshold:
            return MatchQuality.GOOD
        elif confidence >= self.fair_threshold:
            return MatchQuality.FAIR
        else:
            return MatchQuality.POOR

    async def _initialize_vectorizer(self):
        """Initialize TF-IDF vectorizer with sample data.Initialize TF-IDF vectorizer with sample data."""
        try:
            # Sample data for vectorizer initialization
            sample_texts = [
                "sample text for initialization",
                "another sample text",
                "third sample text",
            ]

            # Fit vectorizer with sample data
            self.vectorizer.fit(sample_texts)

            self.logger.info("TF-IDF vectorizer initialized with sample data")

        except Exception as e:
            self.logger.error(f"Error initializing vectorizer: {e}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics.Get performance metrics."""
        return {
            "total_matches_processed": self.total_matches_processed,
            "average_processing_time": self.average_processing_time,
            "matching_algorithms_enabled": {
                "tfidf": self.enable_tfidf,
                "jaro": self.enable_jaro,
                "levenshtein": self.enable_levenshtein,
                "ngram": self.enable_ngram,
                "phonetic": self.enable_phonetic,
                "semantic": self.enable_semantic,
            },
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "enable_tfidf": True,
        "enable_jaro": True,
        "enable_levenshtein": True,
        "enable_ngram": True,
        "enable_phonetic": True,
        "enable_semantic": True,
        "min_confidence": 0.6,
        "excellent_threshold": 0.95,
        "very_good_threshold": 0.90,
        "good_threshold": 0.80,
        "fair_threshold": 0.70,
    }

    # Initialize AI fuzzy matcher
    matcher = AIFuzzyMatcher(config)

    print("AIFuzzyMatcher system initialized successfully!")
