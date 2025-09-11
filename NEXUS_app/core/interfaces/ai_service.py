"""
🤖 AI Service Interface
Defines the standard contract for all AI services in the Nexus Platform.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import asyncio

class AIProviderType(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    LOCAL = "local"
    CUSTOM = "custom"

class AIModelType(Enum):
    """Supported AI model types"""
    TEXT_GENERATION = "text_generation"
    TEXT_EMBEDDING = "text_embedding"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_GENERATION = "audio_generation"
    MULTIMODAL = "multimodal"
    AGENT = "agent"

@dataclass
class AIRequest:
    """Standard AI request structure"""
    prompt: str
    model: str
    provider: AIProviderType
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class AIResponse:
    """Standard AI response structure"""
    content: str
    model: str
    provider: AIProviderType
    usage: Dict[str, Any]
    metadata: Dict[str, Any]
    error: Optional[str] = None

@dataclass
class AIModelInfo:
    """AI model information"""
    name: str
    provider: AIProviderType
    type: AIModelType
    capabilities: List[str]
    max_tokens: Optional[int] = None
    cost_per_token: Optional[float] = None
    available: bool = True

class AIServiceInterface(ABC):
    """Base interface for all AI services"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the AI service"""
        pass
    
    @abstractmethod
    async def generate_text(self, request: AIRequest) -> AIResponse:
        """Generate text using the AI service"""
        pass
    
    @abstractmethod
    async def generate_embeddings(self, text: str, model: str) -> List[float]:
        """Generate embeddings for text"""
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[AIModelInfo]:
        """Get list of available models"""
        pass
    
    @abstractmethod
    async def get_model_info(self, model_name: str) -> Optional[AIModelInfo]:
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the service gracefully"""
        pass

class AIServiceManager(ABC):
    """Manages multiple AI services"""
    
    @abstractmethod
    async def register_service(self, service: AIServiceInterface, name: str) -> bool:
        """Register an AI service"""
        pass
    
    @abstractmethod
    async def get_service(self, name: str) -> Optional[AIServiceInterface]:
        """Get a registered service by name"""
        pass
    
    @abstractmethod
    async def list_services(self) -> List[str]:
        """List all registered services"""
        pass
    
    @abstractmethod
    async def route_request(self, request: AIRequest) -> AIResponse:
        """Route request to appropriate service"""
        pass
    
    @abstractmethod
    async def get_service_health(self) -> Dict[str, Any]:
        """Get health status of all services"""
        pass
