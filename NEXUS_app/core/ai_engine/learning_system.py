#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🧠 Frenly AI Learning System
Agent learning, adaptation, and self-improvement capabilities
"""

import asyncio
import logging
import time
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from backend.config import get_config

logger = logging.getLogger(__name__)

class LearningType(Enum):
    """Learning type enumeration"""
    PERFORMANCE = "performance"
    CAPABILITY = "capability"
    COLLABORATION = "collaboration"
    OPTIMIZATION = "optimization"

class AdaptationLevel(Enum):
    """Adaptation level enumeration"""
    NONE = "none"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class LearningData:
    """Learning data point"""
    agent_id: str
    task_type: str
    input_complexity: float
    processing_time: float
    success: bool
    confidence: float
    user_satisfaction: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CapabilityProfile:
    """Agent capability profile"""
    agent_id: str
    strengths: List[str]
    weaknesses: List[str]
    learning_rate: float
    adaptation_level: AdaptationLevel
    performance_trend: float
    last_updated: str
    recommendations: List[str] = field(default_factory=list)

class LearningSystem:
    """Agent learning and adaptation system"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # Learning data storage
        self.learning_data: List[LearningData] = []
        self.capability_profiles: Dict[str, CapabilityProfile] = {}
        
        # ML models
        self.performance_model = None
        self.capability_model = None
        self.optimization_model = None
        
        # Learning configuration
        self.learning_window = 1000  # Number of data points to keep
        self.retrain_interval = 3600  # 1 hour
        self.adaptation_threshold = 0.1  # Minimum improvement threshold
        
        logger.info("✅ Learning System initialized")
    
    async def start(self):
        """Start the learning system"""
        self.running = True
        logger.info("🚀 Starting Learning System...")
        
        # Load existing data
        await self._load_learning_data()
        await self._load_capability_profiles()
        
        # Initialize models
        await self._initialize_models()
        
        # Start background tasks
        asyncio.create_task(self._continuous_learning())
        asyncio.create_task(self._capability_analysis())
        asyncio.create_task(self._optimization_recommendations())
        
        logger.info("✅ Learning System started")
    
    async def stop(self):
        """Stop the learning system"""
        self.running = False
        logger.info("🛑 Stopping Learning System...")
        
        # Save data
        await self._save_learning_data()
        await self._save_capability_profiles()
        
        logger.info("✅ Learning System stopped")
    
    async def record_learning_data(self, agent_id: str, task_type: str, 
                                 input_complexity: float, processing_time: float,
                                 success: bool, confidence: float,
                                 user_satisfaction: float = 0.5,
                                 metadata: Optional[Dict[str, Any]] = None):
        """Record learning data point"""
        try:
            learning_point = LearningData(
                agent_id=agent_id,
                task_type=task_type,
                input_complexity=input_complexity,
                processing_time=processing_time,
                success=success,
                confidence=confidence,
                user_satisfaction=user_satisfaction,
                timestamp=datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            self.learning_data.append(learning_point)
            
            # Keep only recent data
            if len(self.learning_data) > self.learning_window:
                self.learning_data = self.learning_data[-self.learning_window:]
            
            # Update capability profile
            await self._update_capability_profile(agent_id, learning_point)
            
            logger.debug(f"Learning data recorded for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"❌ Error recording learning data: {e}")
    
    async def get_agent_recommendations(self, agent_id: str) -> List[str]:
        """Get learning recommendations for agent"""
        try:
            if agent_id not in self.capability_profiles:
                return ["No learning data available for this agent"]
            
            profile = self.capability_profiles[agent_id]
            return profile.recommendations
            
        except Exception as e:
            logger.error(f"❌ Error getting agent recommendations: {e}")
            return []
    
    async def get_capability_profile(self, agent_id: str) -> Optional[CapabilityProfile]:
        """Get agent capability profile"""
        try:
            return self.capability_profiles.get(agent_id)
            
        except Exception as e:
            logger.error(f"❌ Error getting capability profile: {e}")
            return None
    
    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get learning system insights"""
        try:
            if not self.learning_data:
                return {"message": "No learning data available"}
            
            # Calculate insights
            total_data_points = len(self.learning_data)
            success_rate = sum(1 for d in self.learning_data if d.success) / total_data_points
            avg_confidence = sum(d.confidence for d in self.learning_data) / total_data_points
            avg_satisfaction = sum(d.user_satisfaction for d in self.learning_data) / total_data_points
            
            # Agent performance
            agent_performance = {}
            for agent_id in set(d.agent_id for d in self.learning_data):
                agent_data = [d for d in self.learning_data if d.agent_id == agent_id]
                agent_success_rate = sum(1 for d in agent_data if d.success) / len(agent_data)
                agent_avg_time = sum(d.processing_time for d in agent_data) / len(agent_data)
                
                agent_performance[agent_id] = {
                    "success_rate": agent_success_rate,
                    "avg_processing_time": agent_avg_time,
                    "data_points": len(agent_data)
                }
            
            # Learning trends
            recent_data = [d for d in self.learning_data 
                          if datetime.fromisoformat(d.timestamp) > datetime.now() - timedelta(hours=24)]
            recent_success_rate = sum(1 for d in recent_data if d.success) / len(recent_data) if recent_data else 0
            
            return {
                "total_data_points": total_data_points,
                "overall_success_rate": success_rate,
                "avg_confidence": avg_confidence,
                "avg_user_satisfaction": avg_satisfaction,
                "agent_performance": agent_performance,
                "recent_success_rate": recent_success_rate,
                "learning_trends": {
                    "improving": recent_success_rate > success_rate,
                    "trend_direction": "up" if recent_success_rate > success_rate else "down"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting learning insights: {e}")
            return {"error": str(e)}
    
    async def _update_capability_profile(self, agent_id: str, learning_point: LearningData):
        """Update agent capability profile"""
        try:
            if agent_id not in self.capability_profiles:
                self.capability_profiles[agent_id] = CapabilityProfile(
                    agent_id=agent_id,
                    strengths=[],
                    weaknesses=[],
                    learning_rate=0.1,
                    adaptation_level=AdaptationLevel.BASIC,
                    performance_trend=0.0,
                    last_updated=datetime.now().isoformat()
                )
            
            profile = self.capability_profiles[agent_id]
            
            # Get agent's recent performance
            agent_data = [d for d in self.learning_data if d.agent_id == agent_id]
            if len(agent_data) < 10:
                return  # Need more data
            
            # Calculate performance metrics
            success_rate = sum(1 for d in agent_data if d.success) / len(agent_data)
            avg_confidence = sum(d.confidence for d in agent_data) / len(agent_data)
            avg_satisfaction = sum(d.user_satisfaction for d in agent_data) / len(agent_data)
            
            # Update strengths and weaknesses
            strengths = []
            weaknesses = []
            
            if success_rate > 0.8:
                strengths.append("high_success_rate")
            elif success_rate < 0.6:
                weaknesses.append("low_success_rate")
            
            if avg_confidence > 0.8:
                strengths.append("high_confidence")
            elif avg_confidence < 0.6:
                weaknesses.append("low_confidence")
            
            if avg_satisfaction > 0.7:
                strengths.append("high_user_satisfaction")
            elif avg_satisfaction < 0.5:
                weaknesses.append("low_user_satisfaction")
            
            # Update profile
            profile.strengths = list(set(strengths))
            profile.weaknesses = list(set(weaknesses))
            profile.performance_trend = success_rate
            profile.last_updated = datetime.now().isoformat()
            
            # Generate recommendations
            await self._generate_recommendations(profile)
            
        except Exception as e:
            logger.error(f"❌ Error updating capability profile: {e}")
    
    async def _generate_recommendations(self, profile: CapabilityProfile):
        """Generate learning recommendations for agent"""
        try:
            recommendations = []
            
            # Performance-based recommendations
            if "low_success_rate" in profile.weaknesses:
                recommendations.append("Focus on improving task success rate through better error handling")
            
            if "low_confidence" in profile.weaknesses:
                recommendations.append("Work on improving confidence through better input validation")
            
            if "low_user_satisfaction" in profile.weaknesses:
                recommendations.append("Improve user experience through better response quality")
            
            # Learning rate recommendations
            if profile.learning_rate < 0.05:
                recommendations.append("Increase learning rate for faster adaptation")
            elif profile.learning_rate > 0.3:
                recommendations.append("Decrease learning rate for more stable learning")
            
            # Adaptation level recommendations
            if profile.adaptation_level == AdaptationLevel.NONE:
                recommendations.append("Enable basic learning capabilities")
            elif profile.adaptation_level == AdaptationLevel.BASIC:
                recommendations.append("Upgrade to intermediate learning for better performance")
            
            profile.recommendations = recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
    
    async def _continuous_learning(self):
        """Continuous learning process"""
        while self.running:
            try:
                # Retrain models if enough new data
                if len(self.learning_data) > 100:
                    await self._retrain_models()
                
                await asyncio.sleep(self.retrain_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in continuous learning: {e}")
                await asyncio.sleep(60)
    
    async def _capability_analysis(self):
        """Analyze agent capabilities"""
        while self.running:
            try:
                # Analyze capabilities for all agents
                for agent_id in set(d.agent_id for d in self.learning_data):
                    await self._analyze_agent_capabilities(agent_id)
                
                await asyncio.sleep(1800)  # Every 30 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in capability analysis: {e}")
                await asyncio.sleep(60)
    
    async def _optimization_recommendations(self):
        """Generate optimization recommendations"""
        while self.running:
            try:
                # Generate system-wide optimization recommendations
                await self._generate_system_optimizations()
                
                await asyncio.sleep(3600)  # Every hour
                
            except Exception as e:
                logger.error(f"❌ Error in optimization recommendations: {e}")
                await asyncio.sleep(60)
    
    async def _initialize_models(self):
        """Initialize ML models"""
        try:
            # Performance prediction model
            self.performance_model = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Capability clustering model
            self.capability_model = KMeans(n_clusters=3, random_state=42)
            
            # Optimization model
            self.optimization_model = RandomForestRegressor(n_estimators=50, random_state=42)
            
            logger.info("✅ ML models initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing models: {e}")
    
    async def _retrain_models(self):
        """Retrain ML models with new data"""
        try:
            if len(self.learning_data) < 50:
                return  # Not enough data
            
            # Prepare training data
            X = []
            y_performance = []
            y_optimization = []
            
            for data in self.learning_data:
                features = [
                    data.input_complexity,
                    data.processing_time,
                    data.confidence,
                    data.user_satisfaction,
                    1 if data.success else 0
                ]
                X.append(features)
                y_performance.append(data.processing_time)
                y_optimization.append(data.user_satisfaction)
            
            X = np.array(X)
            y_performance = np.array(y_performance)
            y_optimization = np.array(y_optimization)
            
            # Train models
            if self.performance_model:
                self.performance_model.fit(X, y_performance)
            
            if self.optimization_model:
                self.optimization_model.fit(X, y_optimization)
            
            logger.info("✅ Models retrained with new data")
            
        except Exception as e:
            logger.error(f"❌ Error retraining models: {e}")
    
    async def _analyze_agent_capabilities(self, agent_id: str):
        try:
            agent_data = [d for d in self.learning_data if d.agent_id == agent_id]
            if len(agent_data) < 10:
                return
            
            # Analyze performance patterns
            success_rate = sum(1 for d in agent_data if d.success) / len(agent_data)
            avg_confidence = sum(d.confidence for d in agent_data) / len(agent_data)
            
            # Update adaptation level based on performance
            if agent_id in self.capability_profiles:
                profile = self.capability_profiles[agent_id]
                
                if success_rate > 0.9 and avg_confidence > 0.8:
                    profile.adaptation_level = AdaptationLevel.ADVANCED
                elif success_rate > 0.7 and avg_confidence > 0.6:
                    profile.adaptation_level = AdaptationLevel.INTERMEDIATE
                else:
                    profile.adaptation_level = AdaptationLevel.BASIC
                
                profile.last_updated = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"❌ Error analyzing agent capabilities: {e}")
    
    async def _generate_system_optimizations(self):
        """Generate system-wide optimization recommendations"""
        try:
            # Analyze system performance
            if not self.learning_data:
                return
            
            # Calculate system metrics
            total_tasks = len(self.learning_data)
            success_rate = sum(1 for d in self.learning_data if d.success) / total_tasks
            avg_processing_time = sum(d.processing_time for d in self.learning_data) / total_tasks
            
            # Generate recommendations
            recommendations = []
            
            if success_rate < 0.8:
                recommendations.append("System success rate is below optimal. Consider improving error handling.")
            
            if avg_processing_time > 5.0:
                recommendations.append("Average processing time is high. Consider performance optimization.")
            
            # Store recommendations
            if self.redis_client:
                self.redis_client.setex(
                    "frenly_optimization_recommendations",
                    3600,  # 1 hour TTL
                    json.dumps(recommendations, default=str)
                )
            
        except Exception as e:
            logger.error(f"❌ Error generating system optimizations: {e}")
    
    async def _load_learning_data(self):
        """Load learning data from Redis"""
        try:
            if self.redis_client:
                data = self.redis_client.get("frenly_learning_data")
                if data:
                    data_list = json.loads(data)
                    self.learning_data = [LearningData(**item) for item in data_list]
                    logger.info(f"Loaded {len(self.learning_data)} learning data points")
            
        except Exception as e:
            logger.error(f"❌ Error loading learning data: {e}")
    
    async def _save_learning_data(self):
        """Save learning data to Redis"""
        try:
            if self.redis_client:
                data_list = [
                    {
                        "agent_id": d.agent_id,
                        "task_type": d.task_type,
                        "input_complexity": d.input_complexity,
                        "processing_time": d.processing_time,
                        "success": d.success,
                        "confidence": d.confidence,
                        "user_satisfaction": d.user_satisfaction,
                        "timestamp": d.timestamp,
                        "metadata": d.metadata
                    }
                    for d in self.learning_data
                ]
                
                self.redis_client.setex(
                    "frenly_learning_data",
                    86400,  # 24 hours TTL
                    json.dumps(data_list, default=str)
                )
            
        except Exception as e:
            logger.error(f"❌ Error saving learning data: {e}")
    
    async def _load_capability_profiles(self):
        """Load capability profiles from Redis"""
        try:
            if self.redis_client:
                data = self.redis_client.get("frenly_capability_profiles")
                if data:
                    profiles_data = json.loads(data)
                    self.capability_profiles = {
                        agent_id: CapabilityProfile(**profile_data)
                        for agent_id, profile_data in profiles_data.items()
                    }
                    logger.info(f"Loaded {len(self.capability_profiles)} capability profiles")
            
        except Exception as e:
            logger.error(f"❌ Error loading capability profiles: {e}")
    
    async def _save_capability_profiles(self):
        """Save capability profiles to Redis"""
        try:
            if self.redis_client:
                profiles_data = {
                    agent_id: {
                        "agent_id": profile.agent_id,
                        "strengths": profile.strengths,
                        "weaknesses": profile.weaknesses,
                        "learning_rate": profile.learning_rate,
                        "adaptation_level": profile.adaptation_level.value,
                        "performance_trend": profile.performance_trend,
                        "last_updated": profile.last_updated,
                        "recommendations": profile.recommendations
                    }
                    for agent_id, profile in self.capability_profiles.items()
                }
                
                self.redis_client.setex(
                    "frenly_capability_profiles",
                    86400,  # 24 hours TTL
                    json.dumps(profiles_data, default=str)
                )
            
        except Exception as e:
            logger.error(f"❌ Error saving capability profiles: {e}")

# Global learning system instance
learning_system = LearningSystem()
