#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🧠 Frenly AI Natural Language Processing System
Advanced NLP capabilities for Frenly AI
"""

import asyncio
import logging
import time
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class NLPTask(Enum):
    """NLP task enumeration"""
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NAMED_ENTITY_RECOGNITION = "named_entity_recognition"
    TEXT_CLASSIFICATION = "text_classification"
    LANGUAGE_DETECTION = "language_detection"
    TEXT_SUMMARIZATION = "text_summarization"
    QUESTION_ANSWERING = "question_answering"
    TEXT_GENERATION = "text_generation"
    TRANSLATION = "translation"
    KEYWORD_EXTRACTION = "keyword_extraction"
    TOPIC_MODELING = "topic_modeling"

class SentimentLabel(Enum):
    """Sentiment label enumeration"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class EntityType(Enum):
    """Entity type enumeration"""
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    MONEY = "money"
    PERCENT = "percent"
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    CUSTOM = "custom"

@dataclass
class NLPAnalysis:
    """NLP analysis result"""
    id: str
    text: str
    task: NLPTask
    confidence: float
    result: Dict[str, Any]
    language: Optional[str] = None
    processing_time: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SentimentResult:
    """Sentiment analysis result"""
    label: SentimentLabel
    score: float
    confidence: float
    emotions: Dict[str, float] = field(default_factory=dict)

@dataclass
class EntityResult:
    """Named entity recognition result"""
    text: str
    label: EntityType
    start: int
    end: int
    confidence: float

@dataclass
class ClassificationResult:
    """Text classification result"""
    category: str
    confidence: float
    probabilities: Dict[str, float] = field(default_factory=dict)

@dataclass
class SummaryResult:
    """Text summarization result"""
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    key_sentences: List[str] = field(default_factory=list)

@dataclass
class NLPModel:
    """NLP model definition"""
    id: str
    name: str
    task: NLPTask
    language: str
    version: str
    accuracy: float
    model_path: str
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

class NLPSystem:
    """Natural Language Processing System for Frenly AI"""
    
    def __init__(self):
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # NLP storage
        self.nlp_analyses: Dict[str, NLPAnalysis] = {}
        self.nlp_models: Dict[str, NLPModel] = {}
        self.text_cache: Dict[str, str] = {}
        
        # Configuration
        self.cache_ttl = 3600  # 1 hour
        self.max_text_length = 10000
        self.batch_size = 100
        
        # Initialize models
        self._initialize_models()
        
        logger.info("✅ NLP System initialized")
    
    def _initialize_models(self):
        """Initialize NLP models"""
        try:
            # Sentiment Analysis Model
            sentiment_model = NLPModel(
                id="sentiment_v1",
                name="Sentiment Analysis Model",
                task=NLPTask.SENTIMENT_ANALYSIS,
                language="en",
                version="1.0",
                accuracy=0.92,
                model_path="/models/sentiment_model.pkl"
            )
            self.nlp_models["sentiment_v1"] = sentiment_model
            
            # Named Entity Recognition Model
            ner_model = NLPModel(
                id="ner_v1",
                name="Named Entity Recognition Model",
                task=NLPTask.NAMED_ENTITY_RECOGNITION,
                language="en",
                version="1.0",
                accuracy=0.89,
                model_path="/models/ner_model.pkl"
            )
            self.nlp_models["ner_v1"] = ner_model
            
            # Text Classification Model
            classification_model = NLPModel(
                id="classification_v1",
                name="Text Classification Model",
                task=NLPTask.TEXT_CLASSIFICATION,
                language="en",
                version="1.0",
                accuracy=0.87,
                model_path="/models/classification_model.pkl"
            )
            self.nlp_models["classification_v1"] = classification_model
            
            # Language Detection Model
            lang_detection_model = NLPModel(
                id="lang_detection_v1",
                name="Language Detection Model",
                task=NLPTask.LANGUAGE_DETECTION,
                language="multilingual",
                version="1.0",
                accuracy=0.95,
                model_path="/models/lang_detection_model.pkl"
            )
            self.nlp_models["lang_detection_v1"] = lang_detection_model
            
            logger.info(f"Initialized {len(self.nlp_models)} NLP models")
            
        except Exception as e:
            logger.error(f"❌ Error initializing NLP models: {e}")
    
    async def start(self):
        """Start the NLP system"""
        self.running = True
        logger.info("🚀 Starting NLP System...")
        
        # Load existing data
        await self._load_nlp_data()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_old_data())
        
        logger.info("✅ NLP System started")
    
    async def stop(self):
        """Stop the NLP system"""
        self.running = False
        logger.info("🛑 Stopping NLP System...")
        
        # Save NLP data
        await self._save_nlp_data()
        
        logger.info("✅ NLP System stopped")
    
    async def analyze_text(
        self,
        text: str,
        task: NLPTask,
        model_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        try:
            if not text or len(text.strip()) == 0:
                raise ValueError("Text cannot be empty")
            
            if len(text) > self.max_text_length:
                raise ValueError(f"Text too long. Maximum length: {self.max_text_length}")
            
            # Generate analysis ID
            analysis_id = f"analysis_{int(time.time())}_{hashlib.md5(text.encode()).hexdigest()[:8]}"
            
            # Check cache first
            cache_key = f"{task.value}_{hashlib.md5(text.encode()).hexdigest()}"
            if cache_key in self.text_cache:
                cached_result = self.text_cache[cache_key]
                logger.info(f"Using cached result for {task.value}")
                return cached_result
            
            # Find appropriate model
            if not model_id:
                model_id = await self._find_best_model(task, language)
            
            if not model_id:
                raise ValueError(f"No model available for task: {task.value}")
            
            # Perform analysis
            start_time = time.time()
            result = await self._perform_analysis(text, task, model_id)
            processing_time = time.time() - start_time
            
            # Create analysis record
            analysis = NLPAnalysis(
                id=analysis_id,
                text=text,
                task=task,
                confidence=result.get("confidence", 0.0),
                result=result,
                language=language,
                processing_time=processing_time
            )
            
            self.nlp_analyses[analysis_id] = analysis
            
            # Cache result
            self.text_cache[cache_key] = analysis_id
            if self.redis_client:
                self.redis_client.setex(cache_key, self.cache_ttl, analysis_id)
            
            logger.info(f"NLP analysis completed: {analysis_id}")
            return analysis_id
            
        except Exception as e:
            logger.error(f"❌ Error analyzing text: {e}")
            raise
    
    async def get_analysis(self, analysis_id: str) -> Optional[NLPAnalysis]:
        """Get NLP analysis result"""
        return self.nlp_analyses.get(analysis_id)
    
    async def batch_analyze(
        self,
        texts: List[str],
        task: NLPTask,
        model_id: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[str]:
        """Batch analyze multiple texts"""
        try:
            if not texts:
                return []
            
            if len(texts) > self.batch_size:
                raise ValueError(f"Batch size too large. Maximum: {self.batch_size}")
            
            # Find appropriate model
            if not model_id:
                model_id = await self._find_best_model(task, language)
            
            if not model_id:
                raise ValueError(f"No model available for task: {task.value}")
            
            analysis_ids = []
            
            # Process texts in parallel
            tasks = []
            for text in texts:
                task_coro = self.analyze_text(text, task, model_id, language)
                tasks.append(task_coro)
            
            analysis_ids = await asyncio.gather(*tasks)
            
            logger.info(f"Batch analysis completed: {len(analysis_ids)} analyses")
            return analysis_ids
            
        except Exception as e:
            logger.error(f"❌ Error in batch analysis: {e}")
            raise
    
    async def sentiment_analysis(self, text: str, model_id: Optional[str] = None) -> SentimentResult:
        """Perform sentiment analysis"""
        try:
            analysis_id = await self.analyze_text(text, NLPTask.SENTIMENT_ANALYSIS, model_id)
            analysis = self.nlp_analyses[analysis_id]
            
            result_data = analysis.result
            return SentimentResult(
                label=SentimentLabel(result_data["label"]),
                score=result_data["score"],
                confidence=result_data["confidence"],
                emotions=result_data.get("emotions", {})
            )
            
        except Exception as e:
            logger.error(f"❌ Error in sentiment analysis: {e}")
            raise
    
    async def named_entity_recognition(self, text: str, model_id: Optional[str] = None) -> List[EntityResult]:
        """Perform named entity recognition"""
        try:
            analysis_id = await self.analyze_text(text, NLPTask.NAMED_ENTITY_RECOGNITION, model_id)
            analysis = self.nlp_analyses[analysis_id]
            
            entities_data = analysis.result["entities"]
            entities = []
            
            for entity_data in entities_data:
                entity = EntityResult(
                    text=entity_data["text"],
                    label=EntityType(entity_data["label"]),
                    start=entity_data["start"],
                    end=entity_data["end"],
                    confidence=entity_data["confidence"]
                )
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"❌ Error in named entity recognition: {e}")
            raise
    
    async def text_classification(self, text: str, model_id: Optional[str] = None) -> ClassificationResult:
        """Perform text classification"""
        try:
            analysis_id = await self.analyze_text(text, NLPTask.TEXT_CLASSIFICATION, model_id)
            analysis = self.nlp_analyses[analysis_id]
            
            result_data = analysis.result
            return ClassificationResult(
                category=result_data["category"],
                confidence=result_data["confidence"],
                probabilities=result_data.get("probabilities", {})
            )
            
        except Exception as e:
            logger.error(f"❌ Error in text classification: {e}")
            raise
    
    async def language_detection(self, text: str, model_id: Optional[str] = None) -> str:
        """Detect text language"""
        try:
            analysis_id = await self.analyze_text(text, NLPTask.LANGUAGE_DETECTION, model_id)
            analysis = self.nlp_analyses[analysis_id]
            
            return analysis.result["language"]
            
        except Exception as e:
            logger.error(f"❌ Error in language detection: {e}")
            raise
    
    async def text_summarization(self, text: str, max_length: int = 150, model_id: Optional[str] = None) -> SummaryResult:
        """Summarize text"""
        try:
            analysis_id = await self.analyze_text(text, NLPTask.TEXT_SUMMARIZATION, model_id)
            analysis = self.nlp_analyses[analysis_id]
            
            result_data = analysis.result
            return SummaryResult(
                summary=result_data["summary"],
                original_length=len(text),
                summary_length=len(result_data["summary"]),
                compression_ratio=len(result_data["summary"]) / len(text),
                key_sentences=result_data.get("key_sentences", [])
            )
            
        except Exception as e:
            logger.error(f"❌ Error in text summarization: {e}")
            raise
    
    async def question_answering(self, question: str, context: str, model_id: Optional[str] = None) -> str:
        """Answer question based on context"""
        try:
            # Combine question and context
            combined_text = f"Question: {question}\nContext: {context}"
            
            analysis_id = await self.analyze_text(combined_text, NLPTask.QUESTION_ANSWERING, model_id)
            analysis = self.nlp_analyses[analysis_id]
            
            return analysis.result["answer"]
            
        except Exception as e:
            logger.error(f"❌ Error in question answering: {e}")
            raise
    
    async def text_generation(self, prompt: str, max_length: int = 100, model_id: Optional[str] = None) -> str:
        """Generate text based on prompt"""
        try:
            analysis_id = await self.analyze_text(prompt, NLPTask.TEXT_GENERATION, model_id)
            analysis = self.nlp_analyses[analysis_id]
            
            return analysis.result["generated_text"]
            
        except Exception as e:
            logger.error(f"❌ Error in text generation: {e}")
            raise
    
    async def translation(self, text: str, target_language: str, source_language: Optional[str] = None, model_id: Optional[str] = None) -> str:
        """Translate text to target language"""
        try:
            # Detect source language if not provided
            if not source_language:
                source_language = await self.language_detection(text)
            
            # Combine text with language info
            combined_text = f"[{source_language}->{target_language}] {text}"
            
            analysis_id = await self.analyze_text(combined_text, NLPTask.TRANSLATION, model_id)
            analysis = self.nlp_analyses[analysis_id]
            
            return analysis.result["translation"]
            
        except Exception as e:
            logger.error(f"❌ Error in translation: {e}")
            raise
    
    async def keyword_extraction(self, text: str, num_keywords: int = 10, model_id: Optional[str] = None) -> List[str]:
        """Extract keywords from text"""
        try:
            analysis_id = await self.analyze_text(text, NLPTask.KEYWORD_EXTRACTION, model_id)
            analysis = self.nlp_analyses[analysis_id]
            
            return analysis.result["keywords"][:num_keywords]
            
        except Exception as e:
            logger.error(f"❌ Error in keyword extraction: {e}")
            raise
    
    async def topic_modeling(self, texts: List[str], num_topics: int = 5, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform topic modeling on texts"""
        try:
            # Combine texts for analysis
            combined_text = "\n".join(texts)
            
            analysis_id = await self.analyze_text(combined_text, NLPTask.TOPIC_MODELING, model_id)
            analysis = self.nlp_analyses[analysis_id]
            
            return analysis.result
            
        except Exception as e:
            logger.error(f"❌ Error in topic modeling: {e}")
            raise
    
    async def get_nlp_analytics(self) -> Dict[str, Any]:
        """Get NLP system analytics"""
        try:
            total_analyses = len(self.nlp_analyses)
            total_models = len(self.nlp_models)
            
            # Task distribution
            task_distribution = {}
            for analysis in self.nlp_analyses.values():
                task = analysis.task.value
                task_distribution[task] = task_distribution.get(task, 0) + 1
            
            # Language distribution
            language_distribution = {}
            for analysis in self.nlp_analyses.values():
                if analysis.language:
                    language_distribution[analysis.language] = language_distribution.get(analysis.language, 0) + 1
            
            # Average processing time
            processing_times = [a.processing_time for a in self.nlp_analyses.values()]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Model accuracy
            model_accuracies = {model_id: model.accuracy for model_id, model in self.nlp_models.items()}
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_analyses = [
                a for a in self.nlp_analyses.values()
                if datetime.fromisoformat(a.created_at) > recent_cutoff
            ]
            
            return {
                "analyses": {
                    "total": total_analyses,
                    "recent": len(recent_analyses)
                },
                "models": {
                    "total": total_models,
                    "enabled": len([m for m in self.nlp_models.values() if m.enabled]),
                    "accuracies": model_accuracies
                },
                "tasks": {
                    "distribution": task_distribution
                },
                "languages": {
                    "distribution": language_distribution
                },
                "performance": {
                    "avg_processing_time": avg_processing_time
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting NLP analytics: {e}")
            return {"error": str(e)}
    
    async def _find_best_model(self, task: NLPTask, language: Optional[str] = None) -> Optional[str]:
        """Find the best model for a task"""
        try:
            # Filter models by task
            task_models = [model for model in self.nlp_models.values() if model.task == task and model.enabled]
            
            if not task_models:
                return None
            
            if language:
                lang_models = [model for model in task_models if model.language == language or model.language == "multilingual"]
                if lang_models:
                    task_models = lang_models
            
            # Return model with highest accuracy
            best_model = max(task_models, key=lambda m: m.accuracy)
            return best_model.id
            
        except Exception as e:
            logger.error(f"❌ Error finding best model: {e}")
            return None
    
    async def _perform_analysis(self, text: str, task: NLPTask, model_id: str) -> Dict[str, Any]:
        """Perform the actual NLP analysis"""
        try:
            # In practice, this would load and run actual ML models
            
            import random
            
            if task == NLPTask.SENTIMENT_ANALYSIS:
            elif task == NLPTask.NAMED_ENTITY_RECOGNITION:
            elif task == NLPTask.TEXT_CLASSIFICATION:
            elif task == NLPTask.LANGUAGE_DETECTION:
            elif task == NLPTask.TEXT_SUMMARIZATION:
            elif task == NLPTask.QUESTION_ANSWERING:
            elif task == NLPTask.TEXT_GENERATION:
            elif task == NLPTask.TRANSLATION:
            elif task == NLPTask.KEYWORD_EXTRACTION:
            elif task == NLPTask.TOPIC_MODELING:
            else:
                return {"error": f"Unsupported task: {task.value}"}
            
        except Exception as e:
            logger.error(f"❌ Error performing analysis: {e}")
            return {"error": str(e)}
    
        import random
        
        # Simple keyword-based sentiment
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "horrible", "worst", "disgusting"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            label = "positive"
            score = 0.7 + random.uniform(0, 0.3)
        elif negative_count > positive_count:
            label = "negative"
            score = -0.7 - random.uniform(0, 0.3)
        else:
            label = "neutral"
            score = random.uniform(-0.2, 0.2)
        
        return {
            "label": label,
            "score": score,
            "confidence": 0.8 + random.uniform(0, 0.2),
            "emotions": {
                "joy": random.uniform(0, 1),
                "sadness": random.uniform(0, 1),
                "anger": random.uniform(0, 1),
                "fear": random.uniform(0, 1),
                "surprise": random.uniform(0, 1)
            }
        }
    
        import random
        
        # Simple pattern-based NER
        entities = []
        
        # Find potential entities
        words = text.split()
        for i, word in enumerate(words):
            if word.istitle() and len(word) > 2:
                if random.random() < 0.3:  # 30% chance of being an entity
                    entity_type = random.choice(["person", "organization", "location"])
                    start = text.find(word)
                    end = start + len(word)
                    
                    entities.append({
                        "text": word,
                        "label": entity_type,
                        "start": start,
                        "end": end,
                        "confidence": 0.7 + random.uniform(0, 0.3)
                    })
        
        return {
            "entities": entities,
            "confidence": 0.8 + random.uniform(0, 0.2)
        }
    
        import random
        
        # Simple keyword-based classification
        categories = ["technology", "business", "sports", "politics", "entertainment", "science", "health"]
        
        
        # Generate probabilities for all categories
        probabilities = {}
        remaining_prob = 1.0 - confidence
        for cat in categories:
            if cat == category:
                probabilities[cat] = confidence
            else:
                probabilities[cat] = remaining_prob / (len(categories) - 1)
        
        return {
            "category": category,
            "confidence": confidence,
            "probabilities": probabilities
        }
    
        import random
        
        # Simple character-based language detection
        languages = ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko"]
        
        
        return {
            "language": language,
            "confidence": confidence
        }
    
        import random
        
        # Simple extractive summarization
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 2:
            summary = text
        else:
            # Select random sentences for summary
            num_sentences = max(1, len(sentences) // 3)
            summary = '. '.join(selected_sentences) + '.'
        
        return {
            "summary": summary,
            "key_sentences": selected_sentences if len(sentences) > 2 else sentences,
            "confidence": 0.8 + random.uniform(0, 0.2)
        }
    
        import random
        
        # Extract question and context
        if "Question:" in text and "Context:" in text:
            parts = text.split("Context:")
            question = parts[0].replace("Question:", "").strip()
            context = parts[1].strip()
        else:
            question = text
            context = text
        
        # Simple answer generation
        answers = [
            "Based on the context provided, the answer is unclear.",
            "The information suggests that this is a complex topic.",
            "Further analysis would be needed to provide a definitive answer.",
            "The context indicates multiple possible interpretations.",
            "This requires additional information to answer accurately."
        ]
        
        answer = random.choice(answers)
        confidence = 0.6 + random.uniform(0, 0.3)
        
        return {
            "answer": answer,
            "confidence": confidence
        }
    
        import random
        
        # Simple text continuation
        generated_text = text + " " + " ".join([
            "This", "is", "a", "generated", "continuation", "of", "the", "text.",
            "The", "model", "has", "created", "additional", "content", "based", "on", "the", "input."
        ])
        
        return {
            "generated_text": generated_text,
            "confidence": 0.7 + random.uniform(0, 0.3)
        }
    
        import random
        
        # Extract language info
        if "[en->es]" in text:
            target_lang = "es"
            source_text = text.replace("[en->es]", "").strip()
        elif "[es->en]" in text:
            target_lang = "en"
            source_text = text.replace("[es->en]", "").strip()
        else:
            target_lang = "en"
            source_text = text
        
        
        return {
            "translation": translation,
            "confidence": 0.8 + random.uniform(0, 0.2)
        }
    
        import random
        
        # Simple keyword extraction
        words = text.lower().split()
        # Filter out common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Remove duplicates and limit
        keywords = list(set(keywords))[:10]
        
        return {
            "keywords": keywords,
            "confidence": 0.8 + random.uniform(0, 0.2)
        }
    
        import random
        
        
        # Random topic assignment
        
        return {
            "topics": selected_topics,
            "confidence": 0.7 + random.uniform(0, 0.3)
        }
    
    async def _cleanup_old_data(self):
        """Clean up old NLP data"""
        while self.running:
            try:
                # Clean up old analyses
                cutoff_date = datetime.now() - timedelta(days=7)
                
                old_analyses = [
                    analysis_id for analysis_id, analysis in self.nlp_analyses.items()
                    if datetime.fromisoformat(analysis.created_at) < cutoff_date
                ]
                
                for analysis_id in old_analyses:
                    del self.nlp_analyses[analysis_id]
                
                if old_analyses:
                    logger.info(f"Cleaned up {len(old_analyses)} old analyses")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_nlp_data(self):
        """Load NLP data from storage"""
        try:
            if self.redis_client:
                # Load NLP analyses
                analyses_data = self.redis_client.get("frenly_nlp_analyses")
                if analyses_data:
                    analyses_json = json.loads(analyses_data)
                    for analysis_id, analysis_data in analyses_json.items():
                        analysis = NLPAnalysis(
                            id=analysis_id,
                            text=analysis_data["text"],
                            task=NLPTask(analysis_data["task"]),
                            confidence=analysis_data["confidence"],
                            result=analysis_data["result"],
                            language=analysis_data.get("language"),
                            processing_time=analysis_data.get("processing_time", 0.0),
                            created_at=analysis_data["created_at"]
                        )
                        self.nlp_analyses[analysis_id] = analysis
                
                # Load NLP models
                models_data = self.redis_client.get("frenly_nlp_models")
                if models_data:
                    models_json = json.loads(models_data)
                    for model_id, model_data in models_json.items():
                        model = NLPModel(
                            id=model_id,
                            name=model_data["name"],
                            task=NLPTask(model_data["task"]),
                            language=model_data["language"],
                            version=model_data["version"],
                            accuracy=model_data["accuracy"],
                            model_path=model_data["model_path"],
                            enabled=model_data.get("enabled", True),
                            created_at=model_data["created_at"]
                        )
                        self.nlp_models[model_id] = model
                
                logger.info(f"Loaded {len(self.nlp_analyses)} analyses and {len(self.nlp_models)} models")
            
        except Exception as e:
            logger.error(f"❌ Error loading NLP data: {e}")
    
    async def _save_nlp_data(self):
        """Save NLP data to storage"""
        try:
            if self.redis_client:
                # Save NLP analyses
                analyses_data = {
                    analysis_id: {
                        "text": analysis.text,
                        "task": analysis.task.value,
                        "confidence": analysis.confidence,
                        "result": analysis.result,
                        "language": analysis.language,
                        "processing_time": analysis.processing_time,
                        "created_at": analysis.created_at
                    }
                    for analysis_id, analysis in self.nlp_analyses.items()
                }
                self.redis_client.setex("frenly_nlp_analyses", 86400, json.dumps(analyses_data))
                
                # Save NLP models
                models_data = {
                    model_id: {
                        "name": model.name,
                        "task": model.task.value,
                        "language": model.language,
                        "version": model.version,
                        "accuracy": model.accuracy,
                        "model_path": model.model_path,
                        "enabled": model.enabled,
                        "created_at": model.created_at
                    }
                    for model_id, model in self.nlp_models.items()
                }
                self.redis_client.setex("frenly_nlp_models", 86400, json.dumps(models_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving NLP data: {e}")

# Global NLP system instance
nlp_system = NLPSystem()
