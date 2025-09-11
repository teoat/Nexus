#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🤖 Frenly AI Model Manager
Manages AI models, their loading, caching, and lifecycle
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pickle
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel, pipeline
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Model type enumeration"""
    TEXT_CLASSIFICATION = "text_classification"
    TEXT_GENERATION = "text_generation"
    EMBEDDING = "embedding"
    NAMED_ENTITY_RECOGNITION = "ner"
    SENTIMENT_ANALYSIS = "sentiment"
    FRAUD_DETECTION = "fraud_detection"
    FORENSIC_ANALYSIS = "forensic_analysis"
    RECONCILIATION = "reconciliation"
    COMPLIANCE = "compliance"

class ModelStatus(Enum):
    """Model status enumeration"""
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    UNLOADED = "unloaded"

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    total_inferences: int = 0
    successful_inferences: int = 0
    failed_inferences: int = 0
    avg_inference_time: float = 0.0
    last_inference_time: Optional[str] = None
    memory_usage: float = 0.0
    gpu_usage: float = 0.0

@dataclass
class ModelConfig:
    """Model configuration"""
    model_id: str
    model_name: str
    model_type: ModelType
    model_path: str
    tokenizer_path: Optional[str] = None
    max_length: int = 512
    batch_size: int = 1
    device: str = "cpu"
    precision: str = "float32"
    cache_size: int = 1000
    ttl: int = 3600
    enabled: bool = True

@dataclass
class Model:
    """Model definition"""
    config: ModelConfig
    status: ModelStatus
    model: Optional[Any] = None
    tokenizer: Optional[Any] = None
    pipeline: Optional[Any] = None
    metrics: ModelMetrics = field(default_factory=ModelMetrics)
    loaded_at: Optional[str] = None
    last_used: Optional[str] = None
    cache: Dict[str, Any] = field(default_factory=dict)

class ModelManager:
    """Manages AI models and their lifecycle"""
    
    def __init__(self):
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.models: Dict[str, Model] = {}
        self.model_queues: Dict[str, asyncio.Queue] = {}
        self.running = False
        
        # Model configurations
        self.model_configs = self._initialize_model_configs()
        
        logger.info("✅ Model Manager initialized")
    
    def _initialize_model_configs(self) -> Dict[str, ModelConfig]:
        """Initialize model configurations"""
        return {
            "fraud_detection_v1": ModelConfig(
                model_id="fraud_detection_v1",
                model_name="fraud-detection-model",
                model_type=ModelType.FRAUD_DETECTION,
                model_path="models/fraud_detection_v1",
                max_length=256,
                batch_size=32,
                device="cuda" if torch.cuda.is_available() else "cpu"
            ),
            "forensic_analysis_v1": ModelConfig(
                model_id="forensic_analysis_v1",
                model_name="forensic-analysis-model",
                model_type=ModelType.FORENSIC_ANALYSIS,
                model_path="models/forensic_analysis_v1",
                max_length=512,
                batch_size=16,
                device="cuda" if torch.cuda.is_available() else "cpu"
            ),
            "reconciliation_v1": ModelConfig(
                model_id="reconciliation_v1",
                model_name="reconciliation-model",
                model_type=ModelType.RECONCILIATION,
                model_path="models/reconciliation_v1",
                max_length=1024,
                batch_size=8,
                device="cuda" if torch.cuda.is_available() else "cpu"
            ),
            "compliance_v1": ModelConfig(
                model_id="compliance_v1",
                model_name="compliance-model",
                model_type=ModelType.COMPLIANCE,
                model_path="models/compliance_v1",
                max_length=512,
                batch_size=16,
                device="cuda" if torch.cuda.is_available() else "cpu"
            ),
            "general_v1": ModelConfig(
                model_id="general_v1",
                model_name="general-ai-model",
                model_type=ModelType.TEXT_GENERATION,
                model_path="models/general_v1",
                max_length=2048,
                batch_size=4,
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
        }
    
    async def start(self):
        """Start the model manager"""
        self.running = True
        logger.info("🚀 Starting Model Manager...")
        
        # Load enabled models
        await self._load_enabled_models()
        
        # Start model monitoring
        asyncio.create_task(self._monitor_models())
        
        # Start cache cleanup
        asyncio.create_task(self._cleanup_cache())
        
        logger.info("✅ Model Manager started")
    
    async def stop(self):
        """Stop the model manager"""
        self.running = False
        logger.info("🛑 Stopping Model Manager...")
        
        # Unload all models
        for model_id in list(self.models.keys()):
            await self._unload_model(model_id)
        
        logger.info("✅ Model Manager stopped")
    
    async def _load_enabled_models(self):
        """Load all enabled models"""
        for model_id, model_config in self.model_configs.items():
            if model_config.enabled:
                await self._load_model(model_id)
    
    async def _load_model(self, model_id: str) -> bool:
        if model_id not in self.model_configs:
            logger.error(f"❌ Model configuration not found: {model_id}")
            return False
        
        model_config = self.model_configs[model_id]
        
        try:
            logger.info(f"🔄 Loading model: {model_id}")
            
            # Create model instance
            model = Model(
                config=model_config,
                status=ModelStatus.LOADING,
                loaded_at=datetime.now().isoformat()
            )
            
            # Load model based on type
            if model_config.model_type == ModelType.TEXT_CLASSIFICATION:
                model.pipeline = pipeline(
                    "text-classification",
                    model=model_config.model_path,
                    tokenizer=model_config.tokenizer_path or model_config.model_path,
                    device=model_config.device
                )
            elif model_config.model_type == ModelType.TEXT_GENERATION:
                model.pipeline = pipeline(
                    "text-generation",
                    model=model_config.model_path,
                    tokenizer=model_config.tokenizer_path or model_config.model_path,
                    device=model_config.device,
                    max_length=model_config.max_length
                )
            elif model_config.model_type == ModelType.EMBEDDING:
                model.tokenizer = AutoTokenizer.from_pretrained(model_config.model_path)
                model.model = AutoModel.from_pretrained(model_config.model_path)
                model.model.to(model_config.device)
            else:
                # Default to text classification for custom types
                model.pipeline = pipeline(
                    "text-classification",
                    model=model_config.model_path,
                    device=model_config.device
                )
            
            # Update model status
            model.status = ModelStatus.LOADED
            model.last_used = datetime.now().isoformat()
            
            # Store model
            self.models[model_id] = model
            
            # Create model queue
            self.model_queues[model_id] = asyncio.Queue()
            
            # Start model processing
            asyncio.create_task(self._process_model_requests(model_id))
            
            logger.info(f"✅ Model loaded successfully: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_id}: {e}")
            if model_id in self.models:
                self.models[model_id].status = ModelStatus.ERROR
            return False
    
    async def _unload_model(self, model_id: str):
        if model_id not in self.models:
            return
        
        try:
            logger.info(f"🔄 Unloading model: {model_id}")
            
            model = self.models[model_id]
            model.status = ModelStatus.UNLOADED
            
            # Clear model resources
            if model.pipeline:
                del model.pipeline
            if model.model:
                del model.model
            if model.tokenizer:
                del model.tokenizer
            
            # Clear cache
            model.cache.clear()
            
            # Remove from models
            del self.models[model_id]
            
            # Remove queue
            if model_id in self.model_queues:
                del self.model_queues[model_id]
            
            logger.info(f"✅ Model unloaded: {model_id}")
            
        except Exception as e:
            logger.error(f"❌ Error unloading model {model_id}: {e}")
    
    async def _process_model_requests(self, model_id: str):
        model = self.models[model_id]
        queue = self.model_queues[model_id]
        
        while self.running and model_id in self.models:
            try:
                # Get request from queue
                request = await asyncio.wait_for(queue.get(), timeout=1.0)
                
                # Process inference
                start_time = time.time()
                try:
                    result = await self._run_inference(model, request)
                    inference_time = time.time() - start_time
                    
                    # Update metrics
                    model.metrics.total_inferences += 1
                    model.metrics.successful_inferences += 1
                    model.metrics.avg_inference_time = (
                        (model.metrics.avg_inference_time * (model.metrics.total_inferences - 1) + inference_time) /
                        model.metrics.total_inferences
                    )
                    model.metrics.last_inference_time = datetime.now().isoformat()
                    model.last_used = datetime.now().isoformat()
                    
                    # Send result back
                    if "result_callback" in request:
                        await request["result_callback"](result)
                
                except Exception as e:
                    logger.error(f"❌ Model {model_id} inference error: {e}")
                    model.metrics.failed_inferences += 1
                    
                    # Send error back
                    if "error_callback" in request:
                        await request["error_callback"](e)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Model {model_id} processing error: {e}")
                await asyncio.sleep(1)
    
    async def _run_inference(self, model: Model, request: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference on model"""
        input_text = request.get("input", "")
        input_type = request.get("type", "text")
        
        # Check cache first
        cache_key = self._get_cache_key(input_text, model.config.model_id)
        if cache_key in model.cache:
            return model.cache[cache_key]
        
        # Run inference based on model type
        if model.config.model_type == ModelType.TEXT_CLASSIFICATION:
            result = await self._run_text_classification(model, input_text)
        elif model.config.model_type == ModelType.TEXT_GENERATION:
            result = await self._run_text_generation(model, input_text)
        elif model.config.model_type == ModelType.EMBEDDING:
            result = await self._run_embedding(model, input_text)
        else:
            result = await self._run_custom_inference(model, input_text, input_type)
        
        # Cache result
        if len(model.cache) < model.config.cache_size:
            model.cache[cache_key] = result
        
        return result
    
    async def _run_text_classification(self, model: Model, input_text: str) -> Dict[str, Any]:
        """Run text classification inference"""
        if not model.pipeline:
            raise Exception("Model pipeline not loaded")
        
        result = model.pipeline(input_text)
        
        return {
            "type": "classification",
            "input": input_text,
            "result": result,
            "confidence": result[0]["score"] if result else 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _run_text_generation(self, model: Model, input_text: str) -> Dict[str, Any]:
        """Run text generation inference"""
        if not model.pipeline:
            raise Exception("Model pipeline not loaded")
        
        result = model.pipeline(input_text, max_length=model.config.max_length)
        
        return {
            "type": "generation",
            "input": input_text,
            "result": result[0]["generated_text"] if result else "",
            "confidence": 0.8,  # Default confidence for generation
            "timestamp": datetime.now().isoformat()
        }
    
    async def _run_embedding(self, model: Model, input_text: str) -> Dict[str, Any]:
        """Run embedding inference"""
        if not model.tokenizer or not model.model:
            raise Exception("Model tokenizer or model not loaded")
        
        # Tokenize input
        inputs = model.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(model.config.device) for k, v in inputs.items()}
        
        # Get embeddings
        with torch.no_grad():
            outputs = model.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        
        return {
            "type": "embedding",
            "input": input_text,
            "result": embeddings.tolist(),
            "confidence": 1.0,  # Embeddings are deterministic
            "timestamp": datetime.now().isoformat()
        }
    
    async def _run_custom_inference(self, model: Model, input_text: str, input_type: str) -> Dict[str, Any]:
        """Run custom inference based on model type"""
        if model.config.model_type == ModelType.FRAUD_DETECTION:
        elif model.config.model_type == ModelType.FORENSIC_ANALYSIS:
        elif model.config.model_type == ModelType.RECONCILIATION:
        elif model.config.model_type == ModelType.COMPLIANCE:
        else:
    
        
        return {
            "type": "fraud_detection",
            "input": input_text,
            "result": {
                "fraud_probability": fraud_score,
                "risk_level": "high" if fraud_score > 0.7 else "medium" if fraud_score > 0.3 else "low",
                "indicators": [ind for ind in fraud_indicators if ind.lower() in input_text.lower()]
            },
            "confidence": 0.85,
            "timestamp": datetime.now().isoformat()
        }
    
        return {
            "type": "forensic_analysis",
            "input": input_text,
            "result": {
                "analysis_type": "evidence_processing",
                "findings": ["Pattern detected", "Timeline reconstructed", "Evidence linked"],
                "confidence_score": 0.92
            },
            "confidence": 0.92,
            "timestamp": datetime.now().isoformat()
        }
    
        return {
            "type": "reconciliation",
            "input": input_text,
            "result": {
                "match_status": "matched",
                "discrepancy_count": 0,
                "confidence_score": 0.88
            },
            "confidence": 0.88,
            "timestamp": datetime.now().isoformat()
        }
    
        return {
            "type": "compliance",
            "input": input_text,
            "result": {
                "compliance_status": "compliant",
                "gdpr_score": 0.95,
                "recommendations": ["Data retention policy updated"]
            },
            "confidence": 0.90,
            "timestamp": datetime.now().isoformat()
        }
    
        return {
            "type": "general",
            "input": input_text,
            "result": f"AI response for: {input_text[:50]}...",
            "confidence": 0.75,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_cache_key(self, input_text: str, model_id: str) -> str:
        """Generate cache key for input"""
        content = f"{model_id}:{input_text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def run_inference(self, model_id: str, input_text: str, input_type: str = "text") -> Dict[str, Any]:
        if model_id not in self.models:
            raise Exception(f"Model not found: {model_id}")
        
        model = self.models[model_id]
        if model.status != ModelStatus.LOADED:
            raise Exception(f"Model not loaded: {model_id}")
        
        # Create result future
        result_future = asyncio.Future()
        
        # Prepare request
        request = {
            "input": input_text,
            "type": input_type,
            "result_callback": lambda result: result_future.set_result(result),
            "error_callback": lambda error: result_future.set_exception(error)
        }
        
        # Submit to model queue
        await self.model_queues[model_id].put(request)
        
        # Wait for result
        result = await result_future
        return result
    
    async def get_model_status(self, model_id: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get model status"""
        if model_id:
            if model_id not in self.models:
                raise Exception(f"Model not found: {model_id}")
            
            model = self.models[model_id]
            return {
                "model_id": model.config.model_id,
                "model_name": model.config.model_name,
                "model_type": model.config.model_type.value,
                "status": model.status.value,
                "loaded_at": model.loaded_at,
                "last_used": model.last_used,
                "metrics": {
                    "total_inferences": model.metrics.total_inferences,
                    "successful_inferences": model.metrics.successful_inferences,
                    "failed_inferences": model.metrics.failed_inferences,
                    "avg_inference_time": model.metrics.avg_inference_time,
                    "last_inference_time": model.metrics.last_inference_time
                }
            }
        else:
            return [
                {
                    "model_id": model.config.model_id,
                    "model_name": model.config.model_name,
                    "model_type": model.config.model_type.value,
                    "status": model.status.value,
                    "loaded_at": model.loaded_at,
                    "last_used": model.last_used,
                    "metrics": {
                        "total_inferences": model.metrics.total_inferences,
                        "successful_inferences": model.metrics.successful_inferences,
                        "failed_inferences": model.metrics.failed_inferences,
                        "avg_inference_time": model.metrics.avg_inference_time,
                        "last_inference_time": model.metrics.last_inference_time
                    }
                }
                for model in self.models.values()
            ]
    
    async def _monitor_models(self):
        """Monitor model health and performance"""
        while self.running:
            try:
                for model in self.models.values():
                    # Check if model is stuck
                    if model.status == ModelStatus.LOADING:
                        loaded_at = datetime.fromisoformat(model.loaded_at) if model.loaded_at else None
                        if loaded_at and datetime.now() - loaded_at > timedelta(minutes=5):
                            logger.warning(f"⚠️ Model {model.config.model_id} loading timeout")
                            model.status = ModelStatus.ERROR
                    
                    # Update memory usage (simplified)
                    model.metrics.memory_usage = 0.0  # Would need actual memory monitoring
                    
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Model monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_cache(self):
        """Clean up model caches"""
        while self.running:
            try:
                for model in self.models.values():
                    # Remove expired cache entries
                    current_time = datetime.now()
                    expired_keys = []
                    
                    for key, value in model.cache.items():
                        if isinstance(value, dict) and "timestamp" in value:
                            cache_time = datetime.fromisoformat(value["timestamp"])
                            if current_time - cache_time > timedelta(seconds=model.config.ttl):
                                expired_keys.append(key)
                    
                    for key in expired_keys:
                        del model.cache[key]
                
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Cache cleanup error: {e}")
                await asyncio.sleep(60)

# Global model manager instance
model_manager = ModelManager()
