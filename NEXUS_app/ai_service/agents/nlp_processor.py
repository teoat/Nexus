#!/usr/bin/env python3
"""
NLP Processing System - Evidence Agent Component

This module implements the NLPProcessor class that provides
comprehensive natural language processing capabilities for evidence analysis.
"""

import asyncio
import logging
import re
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict

from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class NLPModelType(Enum):
    """Types of NLP models."""

    SENTIMENT_ANALYSIS = "sentiment_analysis"  # Sentiment analysis
    NAMED_ENTITY_RECOGNITION = "ner"  # Named entity recognition
    TOPIC_MODELING = "topic_modeling"  # Topic extraction
    TEXT_CLASSIFICATION = "text_classification"  # Text categorization
    KEYWORD_EXTRACTION = "keyword_extraction"  # Keyword extraction
    SUMMARIZATION = "summarization"  # Text summarization
    TRANSLATION = "translation"  # Language translation
    CUSTOM = "custom"  # Custom NLP model


class ProcessingLevel(Enum):
    """Levels of NLP processing."""

    BASIC = "basic"  # Basic text processing
    INTERMEDIATE = "intermediate"  # Intermediate analysis
    ADVANCED = "advanced"  # Advanced NLP features
    EXPERT = "expert"  # Expert-level analysis


class TextType(Enum):
    """Types of text content."""

    CHAT_LOG = "chat_log"  # Chat/messaging logs
    EMAIL = "email"  # Email content
    DOCUMENT = "document"  # Document text
    SOCIAL_MEDIA = "social_media"  # Social media posts
    TRANSCRIPT = "transcript"  # Audio/video transcripts
    CODE = "code"  # Source code
    LOG_FILE = "log_file"  # System logs
    UNKNOWN = "unknown"  # Unknown text type


@dataclass
class TextDocument:
    """A text document for NLP processing."""

    document_id: str
    content: str
    text_type: TextType
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    language: str = "en"
    encoding: str = "utf-8"


@dataclass
class NLPResult:
    """Result of NLP processing."""

    result_id: str
    document_id: str
    model_type: NLPModelType
    processing_level: ProcessingLevel
    results: Dict[str, Any]
    confidence: float
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NamedEntity:
    """A named entity found in text."""

    entity_id: str
    text: str
    entity_type: str
    confidence: float
    start_position: int
    end_position: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""

    sentiment_id: str
    overall_sentiment: str
    sentiment_score: float
    positive_score: float
    negative_score: float
    neutral_score: float
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TopicResult:
    """Result of topic modeling."""

    topic_id: str
    topic_name: str
    topic_score: float
    keywords: List[str]
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NLPProcessorMetrics:
    """Metrics for NLP processing performance."""

    total_documents_processed: int
    total_processing_time: float
    average_processing_time: float
    success_rate: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class NLPProcessor:
    """
    Comprehensive NLP processing system.

    The NLPProcessor is responsible for:
    - Processing various types of text content
    - Applying multiple NLP models and techniques
    - Extracting insights and patterns from text
    - Supporting multiple languages and text formats
    - Providing confidence scores and metadata
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the NLPProcessor."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.enable_sentiment_analysis = config.get("enable_sentiment_analysis", True)
        self.enable_ner = config.get("enable_ner", True)
        self.enable_topic_modeling = config.get("enable_topic_modeling", True)
        self.enable_keyword_extraction = config.get("enable_keyword_extraction", True)
        self.max_text_length = config.get("max_text_length", 10000)
        self.supported_languages = config.get(
            "supported_languages", ["en", "es", "fr", "de"]
        )

        # Document storage
        self.documents: Dict[str, TextDocument] = {}
        self.nlp_results: Dict[str, NLPResult] = {}
        self.entity_index: Dict[str, List[NamedEntity]] = defaultdict(list)

        # Performance tracking
        self.total_documents_processed = 0
        self.total_processing_time = 0.0
        self.successful_processing = 0
        self.failed_processing = 0

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Initialize NLP processing components
        self._initialize_nlp_processing_components()

        self.logger.info("NLPProcessor initialized successfully")

    async def start(self):
        """Start the NLPProcessor."""
        self.logger.info("Starting NLPProcessor...")

        # Initialize NLP processing components
        await self._initialize_nlp_processing_components()

        self.logger.info("NLPProcessor started successfully")

    async def stop(self):
        """Stop the NLPProcessor."""
        self.logger.info("Stopping NLPProcessor...")
        self.logger.info("NLPProcessor stopped")

    def _initialize_nlp_processing_components(self):
        """Initialize NLP processing components."""
        try:
            # Initialize text preprocessing
            self._initialize_text_preprocessing()

            # Initialize NLP models
            self._initialize_nlp_models()

            # Initialize language detection
            self._initialize_language_detection()

            self.logger.info("NLP processing components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing NLP processing components: {e}")

    def _initialize_text_preprocessing(self):
        """Initialize text preprocessing components."""
        try:
            # Common stop words
            self.stop_words = {
                "en": {
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
                },
                "es": {
                    "el",
                    "la",
                    "los",
                    "las",
                    "un",
                    "una",
                    "unos",
                    "unas",
                    "y",
                    "o",
                    "pero",
                    "en",
                    "con",
                    "por",
                },
                "fr": {
                    "le",
                    "la",
                    "les",
                    "un",
                    "une",
                    "des",
                    "et",
                    "ou",
                    "mais",
                    "dans",
                    "avec",
                    "par",
                },
                "de": {
                    "der",
                    "die",
                    "das",
                    "ein",
                    "eine",
                    "eines",
                    "und",
                    "oder",
                    "aber",
                    "in",
                    "mit",
                    "von",
                },
            }

            # Text cleaning patterns
            self.cleaning_patterns = {
                "urls": r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                "emails": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "phone_numbers": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                "special_chars": r"[^\w\s]",
                "extra_whitespace": r"\s+",
            }

            self.logger.info("Text preprocessing components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing text preprocessing: {e}")

    def _initialize_nlp_models(self):
        """Initialize NLP models."""
        try:
            # Sentiment analysis models
            self.sentiment_models = {
                "en": self._create_sentiment_model("en"),
                "es": self._create_sentiment_model("es"),
                "fr": self._create_sentiment_model("fr"),
                "de": self._create_sentiment_model("de"),
            }

            # Named entity recognition models
            self.ner_models = {
                "en": self._create_ner_model("en"),
                "es": self._create_ner_model("es"),
                "fr": self._create_ner_model("fr"),
                "de": self._create_ner_model("de"),
            }

            # Topic modeling models
            self.topic_models = {
                "en": self._create_topic_model("en"),
                "es": self._create_topic_model("es"),
                "fr": self._create_topic_model("fr"),
                "de": self._create_topic_model("de"),
            }

            self.logger.info("NLP models initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing NLP models: {e}")

    def _initialize_language_detection(self):
        """Initialize language detection."""
        try:
            # Language detection patterns
            self.language_patterns = {
                "en": r"\b(the|and|or|but|in|on|at|to|for|of|with|by)\b",
                "es": r"\b(el|la|los|las|un|una|unos|unas|y|o|pero|en|con|por)\b",
                "fr": r"\b(le|la|les|un|une|des|et|ou|mais|dans|avec|par)\b",
                "de": r"\b(der|die|das|ein|eine|eines|und|oder|aber|in|mit|von)\b",
            }

            self.logger.info("Language detection initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing language detection: {e}")

    def _create_sentiment_model(self, language: str) -> Dict[str, Any]:
        """Create a sentiment analysis model for a language."""
        try:
            # Simple rule-based sentiment model
            positive_words = {
                "en": {
                    "good",
                    "great",
                    "excellent",
                    "amazing",
                    "wonderful",
                    "fantastic",
                    "positive",
                    "happy",
                },
                "es": {
                    "bueno",
                    "excelente",
                    "maravilloso",
                    "fantástico",
                    "positivo",
                    "feliz",
                },
                "fr": {
                    "bon",
                    "excellent",
                    "merveilleux",
                    "fantastique",
                    "positif",
                    "heureux",
                },
                "de": {
                    "gut",
                    "ausgezeichnet",
                    "wunderbar",
                    "fantastisch",
                    "positiv",
                    "glücklich",
                },
            }

            negative_words = {
                "en": {
                    "bad",
                    "terrible",
                    "awful",
                    "horrible",
                    "negative",
                    "sad",
                    "angry",
                    "disappointed",
                },
                "es": {
                    "malo",
                    "terrible",
                    "horrible",
                    "negativo",
                    "triste",
                    "enojado",
                    "decepcionado",
                },
                "fr": {
                    "mauvais",
                    "terrible",
                    "horrible",
                    "négatif",
                    "triste",
                    "fâché",
                    "déçu",
                },
                "de": {
                    "schlecht",
                    "schrecklich",
                    "schrecklich",
                    "negativ",
                    "traurig",
                    "wütend",
                    "enttäuscht",
                },
            }

            return {
                "positive_words": positive_words.get(language, positive_words["en"]),
                "negative_words": negative_words.get(language, negative_words["en"]),
                "language": language,
            }

        except Exception as e:
            self.logger.error(f"Error creating sentiment model for {language}: {e}")
            return {}

    def _create_ner_model(self, language: str) -> Dict[str, Any]:
        """Create a named entity recognition model for a language."""
        try:
            # Simple pattern-based NER model
            entity_patterns = {
                "en": {
                    "PERSON": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
                    "ORGANIZATION": r"\b[A-Z][a-z]+ (Inc|Corp|LLC|Ltd|Company|Organization)\b",
                    "LOCATION": r"\b[A-Z][a-z]+ (Street|Avenue|Road|City|State|Country)\b",
                    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                    "PHONE": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                },
                "es": {
                    "PERSON": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
                    "ORGANIZATION": r"\b[A-Z][a-z]+ (Inc|Corp|Sociedad|Organización)\b",
                    "LOCATION": r"\b[A-Z][a-z]+ (Calle|Avenida|Ciudad|Estado|País)\b",
                },
                "fr": {
                    "PERSON": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
                    "ORGANIZATION": r"\b[A-Z][a-z]+ (Inc|Corp|Société|Organisation)\b",
                    "LOCATION": r"\b[A-Z][a-z]+ (Rue|Avenue|Ville|État|Pays)\b",
                },
                "de": {
                    "PERSON": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",
                    "ORGANIZATION": r"\b[A-Z][a-z]+ (Inc|Corp|Gesellschaft|Organisation)\b",
                    "LOCATION": r"\b[A-Z][a-z]+ (Straße|Allee|Stadt|Staat|Land)\b",
                },
            }

            return {
                "patterns": entity_patterns.get(language, entity_patterns["en"]),
                "language": language,
            }

        except Exception as e:
            self.logger.error(f"Error creating NER model for {language}: {e}")
            return {}

    def _create_topic_model(self, language: str) -> Dict[str, Any]:
        """Create a topic modeling model for a language."""
        try:
            # Simple keyword-based topic model
            topic_keywords = {
                "en": {
                    "technology": [
                        "computer",
                        "software",
                        "hardware",
                        "internet",
                        "digital",
                        "system",
                    ],
                    "finance": [
                        "money",
                        "bank",
                        "investment",
                        "financial",
                        "economy",
                        "market",
                    ],
                    "health": [
                        "medical",
                        "health",
                        "doctor",
                        "hospital",
                        "treatment",
                        "medicine",
                    ],
                    "education": [
                        "school",
                        "university",
                        "student",
                        "teacher",
                        "learning",
                        "education",
                    ],
                },
                "es": {
                    "tecnología": [
                        "computadora",
                        "software",
                        "hardware",
                        "internet",
                        "digital",
                        "sistema",
                    ],
                    "finanzas": [
                        "dinero",
                        "banco",
                        "inversión",
                        "financiero",
                        "economía",
                        "mercado",
                    ],
                    "salud": [
                        "médico",
                        "salud",
                        "doctor",
                        "hospital",
                        "tratamiento",
                        "medicina",
                    ],
                    "educación": [
                        "escuela",
                        "universidad",
                        "estudiante",
                        "maestro",
                        "aprendizaje",
                        "educación",
                    ],
                },
            }

            return {
                "keywords": topic_keywords.get(language, topic_keywords["en"]),
                "language": language,
            }

        except Exception as e:
            self.logger.error(f"Error creating topic model for {language}: {e}")
            return {}

    async def process_document(
        self,
        content: str,
        text_type: TextType = TextType.UNKNOWN,
        source: str = "unknown",
        language: str = "en",
    ) -> str:
        """Process a text document with NLP analysis."""
        try:
            start_time = time.time()

            # Create document
            document = TextDocument(
                document_id=str(uuid.uuid4()),
                content=content,
                text_type=text_type,
                source=source,
                timestamp=datetime.utcnow(),
                language=language,
            )

            # Store document
            self.documents[document.document_id] = document

            # Preprocess text
            processed_content = await self._preprocess_text(content, language)

            # Perform NLP analysis
            nlp_results = await self._perform_nlp_analysis(document, processed_content)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Update metrics
            self.total_documents_processed += 1
            self.total_processing_time += processing_time
            self.successful_processing += 1

            self.logger.info(
                f"Processed document {document.document_id} in {processing_time:.2f}s"
            )

            return document.document_id

        except Exception as e:
            self.logger.error(f"Error processing document: {e}")
            self.failed_processing += 1
            raise

    async def _preprocess_text(self, content: str, language: str) -> str:
        """Preprocess text content."""
        try:
            # Convert to lowercase
            processed_content = content.lower()

            # Remove URLs
            processed_content = re.sub(
                self.cleaning_patterns["urls"], "", processed_content
            )

            # Remove emails
            processed_content = re.sub(
                self.cleaning_patterns["emails"], "", processed_content
            )

            # Remove phone numbers
            processed_content = re.sub(
                self.cleaning_patterns["phone_numbers"], "", processed_content
            )

            # Remove special characters
            processed_content = re.sub(
                self.cleaning_patterns["special_chars"], " ", processed_content
            )

            # Remove extra whitespace
            processed_content = re.sub(
                self.cleaning_patterns["extra_whitespace"], " ", processed_content
            )

            # Remove stop words
            stop_words = self.stop_words.get(language, self.stop_words["en"])
            words = processed_content.split()
            filtered_words = [word for word in words if word not in stop_words]
            processed_content = " ".join(filtered_words)

            return processed_content.strip()

        except Exception as e:
            self.logger.error(f"Error preprocessing text: {e}")
            return content

    async def _perform_nlp_analysis(
        self, document: TextDocument, processed_content: str
    ) -> Dict[str, Any]:
        """Perform comprehensive NLP analysis."""
        try:
            results = {}

            # Sentiment analysis
            if self.enable_sentiment_analysis:
                sentiment_result = await self._analyze_sentiment(
                    processed_content, document.language
                )
                results["sentiment"] = sentiment_result

                # Store sentiment result
                sentiment_nlp_result = NLPResult(
                    result_id=str(uuid.uuid4()),
                    document_id=document.document_id,
                    model_type=NLPModelType.SENTIMENT_ANALYSIS,
                    processing_level=ProcessingLevel.INTERMEDIATE,
                    results=sentiment_result,
                    confidence=sentiment_result.confidence,
                    processing_time=0.1,
                    timestamp=datetime.utcnow(),
                )
                self.nlp_results[sentiment_nlp_result.result_id] = sentiment_nlp_result

            # Named entity recognition
            if self.enable_ner:
                ner_result = await self._extract_named_entities(
                    processed_content, document.language
                )
                results["named_entities"] = ner_result

                # Store NER result
                ner_nlp_result = NLPResult(
                    result_id=str(uuid.uuid4()),
                    document_id=document.document_id,
                    model_type=NLPModelType.NAMED_ENTITY_RECOGNITION,
                    processing_level=ProcessingLevel.INTERMEDIATE,
                    results=ner_result,
                    confidence=0.8,
                    processing_time=0.1,
                    timestamp=datetime.utcnow(),
                )
                self.nlp_results[ner_nlp_result.result_id] = ner_nlp_result

                # Index entities
                for entity in ner_result:
                    self.entity_index[entity.entity_type].append(entity)

            # Topic modeling
            if self.enable_topic_modeling:
                topic_result = await self._extract_topics(
                    processed_content, document.language
                )
                results["topics"] = topic_result

                # Store topic result
                topic_nlp_result = NLPResult(
                    result_id=str(uuid.uuid4()),
                    document_id=document.document_id,
                    model_type=NLPModelType.TOPIC_MODELING,
                    processing_level=ProcessingLevel.ADVANCED,
                    results=topic_result,
                    confidence=0.7,
                    processing_time=0.1,
                    timestamp=datetime.utcnow(),
                )
                self.nlp_results[topic_nlp_result.result_id] = topic_nlp_result

            # Keyword extraction
            if self.enable_keyword_extraction:
                keywords_result = await self._extract_keywords(
                    processed_content, document.language
                )
                results["keywords"] = keywords_result

                # Store keyword result
                keyword_nlp_result = NLPResult(
                    result_id=str(uuid.uuid4()),
                    document_id=document.document_id,
                    model_type=NLPModelType.KEYWORD_EXTRACTION,
                    processing_level=ProcessingLevel.BASIC,
                    results=keywords_result,
                    confidence=0.9,
                    processing_time=0.1,
                    timestamp=datetime.utcnow(),
                )
                self.nlp_results[keyword_nlp_result.result_id] = keyword_nlp_result

            return results

        except Exception as e:
            self.logger.error(f"Error performing NLP analysis: {e}")
            return {}

    async def _analyze_sentiment(self, text: str, language: str) -> SentimentResult:
        """Analyze sentiment of text."""
        try:
            model = self.sentiment_models.get(language, self.sentiment_models["en"])

            if not model:
                return SentimentResult(
                    sentiment_id=str(uuid.uuid4()),
                    overall_sentiment="neutral",
                    sentiment_score=0.0,
                    positive_score=0.0,
                    negative_score=0.0,
                    neutral_score=1.0,
                    confidence=0.5,
                )

            words = text.split()
            positive_count = sum(1 for word in words if word in model["positive_words"])
            negative_count = sum(1 for word in words if word in model["negative_words"])
            total_words = len(words)

            if total_words == 0:
                positive_score = 0.0
                negative_score = 0.0
                neutral_score = 1.0
            else:
                positive_score = positive_count / total_words
                negative_score = negative_count / total_words
                neutral_score = 1.0 - positive_score - negative_score

            # Calculate overall sentiment
            if positive_score > negative_score:
                overall_sentiment = "positive"
                sentiment_score = positive_score
            elif negative_score > positive_score:
                overall_sentiment = "negative"
                sentiment_score = -negative_score
            else:
                overall_sentiment = "neutral"
                sentiment_score = 0.0

            # Calculate confidence
            confidence = max(positive_score, negative_score, neutral_score)

            return SentimentResult(
                sentiment_id=str(uuid.uuid4()),
                overall_sentiment=overall_sentiment,
                sentiment_score=sentiment_score,
                positive_score=positive_score,
                negative_score=negative_score,
                neutral_score=neutral_score,
                confidence=confidence,
            )

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return SentimentResult(
                sentiment_id=str(uuid.uuid4()),
                overall_sentiment="neutral",
                sentiment_score=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=1.0,
                confidence=0.5,
            )

    async def _extract_named_entities(
        self, text: str, language: str
    ) -> List[NamedEntity]:
        """Extract named entities from text."""
        try:
            model = self.ner_models.get(language, self.ner_models["en"])

            if not model:
                return []

            entities = []

            for entity_type, pattern in model["patterns"].items():
                matches = re.finditer(pattern, text, re.IGNORECASE)

                for match in matches:
                    entity = NamedEntity(
                        entity_id=str(uuid.uuid4()),
                        text=match.group(),
                        entity_type=entity_type,
                        confidence=0.8,
                        start_position=match.start(),
                        end_position=match.end(),
                    )
                    entities.append(entity)

            return entities

        except Exception as e:
            self.logger.error(f"Error extracting named entities: {e}")
            return []

    async def _extract_topics(self, text: str, language: str) -> List[TopicResult]:
        """Extract topics from text."""
        try:
            model = self.topic_models.get(language, self.topic_models["en"])

            if not model:
                return []

            topics = []
            words = text.split()

            for topic_name, keywords in model["keywords"].items():
                # Count keyword matches
                matches = sum(1 for word in words if word in keywords)

                if matches > 0:
                    # Calculate topic score
                    topic_score = matches / len(keywords)

                    if topic_score > 0.1:  # Minimum threshold
                        topic = TopicResult(
                            topic_id=str(uuid.uuid4()),
                            topic_name=topic_name,
                            topic_score=topic_score,
                            keywords=keywords,
                            confidence=topic_score,
                        )
                        topics.append(topic)

            # Sort by score
            topics.sort(key=lambda x: x.topic_score, reverse=True)

            return topics

        except Exception as e:
            self.logger.error(f"Error extracting topics: {e}")
            return []

    async def _extract_keywords(self, text: str, language: str) -> List[str]:
        """Extract keywords from text."""
        try:
            words = text.split()

            # Simple frequency-based keyword extraction
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Minimum word length
                    word_freq[word] = word_freq.get(word, 0) + 1

            # Get top keywords
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, freq in sorted_words[:10]]  # Top 10 keywords

            return keywords

        except Exception as e:
            self.logger.error(f"Error extracting keywords: {e}")
            return []

    async def get_document(self, document_id: str) -> Optional[TextDocument]:
        """Get a document by ID."""
        return self.documents.get(document_id)

    async def get_nlp_result(self, result_id: str) -> Optional[NLPResult]:
        """Get an NLP result by ID."""
        return self.nlp_results.get(result_id)

    async def get_document_analysis(self, document_id: str) -> Dict[str, Any]:
        """Get comprehensive analysis for a document."""
        try:
            document = self.documents.get(document_id)
            if not document:
                return {}

            # Get all NLP results for this document
            analysis = {
                "document": document,
                "sentiment": None,
                "named_entities": [],
                "topics": [],
                "keywords": [],
            }

            for result in self.nlp_results.values():
                if result.document_id == document_id:
                    if result.model_type == NLPModelType.SENTIMENT_ANALYSIS:
                        analysis["sentiment"] = result.results
                    elif result.model_type == NLPModelType.NAMED_ENTITY_RECOGNITION:
                        analysis["named_entities"] = result.results
                    elif result.model_type == NLPModelType.TOPIC_MODELING:
                        analysis["topics"] = result.results
                    elif result.model_type == NLPModelType.KEYWORD_EXTRACTION:
                        analysis["keywords"] = result.results

            return analysis

        except Exception as e:
            self.logger.error(f"Error getting document analysis: {e}")
            return {}

    async def search_entities(
        self, entity_type: str, query: str = None
    ) -> List[NamedEntity]:
        """Search for entities by type and optional query."""
        try:
            entities = self.entity_index.get(entity_type, [])

            if query:
                # Filter by query
                filtered_entities = []
                query_lower = query.lower()

                for entity in entities:
                    if query_lower in entity.text.lower():
                        filtered_entities.append(entity)

                return filtered_entities

            return entities

        except Exception as e:
            self.logger.error(f"Error searching entities: {e}")
            return []

    def get_nlp_processor_metrics(self) -> NLPProcessorMetrics:
        """Get NLP processing performance metrics."""
        try:
            if self.total_documents_processed > 0:
                average_processing_time = (
                    self.total_processing_time / self.total_documents_processed
                )
                success_rate = (
                    self.successful_processing / self.total_documents_processed
                )
            else:
                average_processing_time = 0.0
                success_rate = 0.0

            return NLPProcessorMetrics(
                total_documents_processed=self.total_documents_processed,
                total_processing_time=self.total_processing_time,
                average_processing_time=average_processing_time,
                success_rate=success_rate,
                metadata={
                    "successful_processing": self.successful_processing,
                    "failed_processing": self.failed_processing,
                    "enable_sentiment_analysis": self.enable_sentiment_analysis,
                    "enable_ner": self.enable_ner,
                    "enable_topic_modeling": self.enable_topic_modeling,
                    "enable_keyword_extraction": self.enable_keyword_extraction,
                    "supported_languages": self.supported_languages,
                    "max_text_length": self.max_text_length,
                    "nlp_model_types_supported": [mt.value for mt in NLPModelType],
                    "processing_levels_supported": [pl.value for pl in ProcessingLevel],
                    "text_types_supported": [tt.value for tt in TextType],
                },
            )

        except Exception as e:
            self.logger.error(f"Error getting NLP processor metrics: {e}")
            return NLPProcessorMetrics(
                total_documents_processed=0,
                total_processing_time=0.0,
                average_processing_time=0.0,
                success_rate=0.0,
            )


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "enable_sentiment_analysis": True,
        "enable_ner": True,
        "enable_topic_modeling": True,
        "enable_keyword_extraction": True,
        "max_text_length": 10000,
        "supported_languages": ["en", "es", "fr", "de"],
    }

    # Initialize NLP processor
    nlp_processor = NLPProcessor(config)

    print("NLPProcessor system initialized successfully!")
