#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
👁️ Frenly AI Computer Vision System
Advanced computer vision capabilities for Frenly AI
"""

import asyncio
import logging
import time
import json
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class VisionTask(Enum):
    """Computer vision task enumeration"""
    OBJECT_DETECTION = "object_detection"
    FACE_RECOGNITION = "face_recognition"
    TEXT_RECOGNITION = "text_recognition"
    IMAGE_CLASSIFICATION = "image_classification"
    IMAGE_SEGMENTATION = "image_segmentation"
    POSE_ESTIMATION = "pose_estimation"
    SCENE_UNDERSTANDING = "scene_understanding"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ENHANCEMENT = "image_enhancement"
    OPTICAL_CHARACTER_RECOGNITION = "optical_character_recognition"

class ObjectClass(Enum):
    """Object class enumeration"""
    PERSON = "person"
    VEHICLE = "vehicle"
    ANIMAL = "animal"
    FURNITURE = "furniture"
    ELECTRONICS = "electronics"
    FOOD = "food"
    SPORTS = "sports"
    BUILDING = "building"
    NATURE = "nature"
    TEXT = "text"

class ImageFormat(Enum):
    """Image format enumeration"""
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"

@dataclass
class BoundingBox:
    """Bounding box definition"""
    x: int
    y: int
    width: int
    height: int
    confidence: float

@dataclass
class DetectedObject:
    """Detected object definition"""
    class_name: str
    class_id: int
    confidence: float
    bounding_box: BoundingBox
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FaceInfo:
    """Face information definition"""
    face_id: str
    confidence: float
    bounding_box: BoundingBox
    landmarks: List[Tuple[int, int]] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TextRegion:
    """Text region definition"""
    text: str
    confidence: float
    bounding_box: BoundingBox
    language: Optional[str] = None

@dataclass
class VisionAnalysis:
    """Computer vision analysis result"""
    id: str
    image_path: str
    task: VisionTask
    confidence: float
    result: Dict[str, Any]
    processing_time: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class VisionModel:
    """Computer vision model definition"""
    id: str
    name: str
    task: VisionTask
    version: str
    accuracy: float
    model_path: str
    input_size: Tuple[int, int]
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

class ComputerVisionSystem:
    """Computer Vision System for Frenly AI"""
    
    def __init__(self):
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # Vision storage
        self.vision_analyses: Dict[str, VisionAnalysis] = {}
        self.vision_models: Dict[str, VisionModel] = {}
        self.image_cache: Dict[str, str] = {}
        
        # Configuration
        self.cache_ttl = 3600  # 1 hour
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        self.supported_formats = [ImageFormat.JPEG, ImageFormat.PNG, ImageFormat.GIF, ImageFormat.BMP]
        
        # Initialize models
        self._initialize_models()
        
        logger.info("✅ Computer Vision System initialized")
    
    def _initialize_models(self):
        """Initialize computer vision models"""
        try:
            # Object Detection Model
            object_detection_model = VisionModel(
                id="object_detection_v1",
                name="Object Detection Model",
                task=VisionTask.OBJECT_DETECTION,
                version="1.0",
                accuracy=0.89,
                model_path="/models/object_detection.pkl",
                input_size=(640, 640)
            )
            self.vision_models["object_detection_v1"] = object_detection_model
            
            # Face Recognition Model
            face_recognition_model = VisionModel(
                id="face_recognition_v1",
                name="Face Recognition Model",
                task=VisionTask.FACE_RECOGNITION,
                version="1.0",
                accuracy=0.94,
                model_path="/models/face_recognition.pkl",
                input_size=(224, 224)
            )
            self.vision_models["face_recognition_v1"] = face_recognition_model
            
            # Text Recognition Model
            text_recognition_model = VisionModel(
                id="text_recognition_v1",
                name="Text Recognition Model",
                task=VisionTask.TEXT_RECOGNITION,
                version="1.0",
                accuracy=0.91,
                model_path="/models/text_recognition.pkl",
                input_size=(512, 512)
            )
            self.vision_models["text_recognition_v1"] = text_recognition_model
            
            # Image Classification Model
            image_classification_model = VisionModel(
                id="image_classification_v1",
                name="Image Classification Model",
                task=VisionTask.IMAGE_CLASSIFICATION,
                version="1.0",
                accuracy=0.87,
                model_path="/models/image_classification.pkl",
                input_size=(224, 224)
            )
            self.vision_models["image_classification_v1"] = image_classification_model
            
            # Image Segmentation Model
            image_segmentation_model = VisionModel(
                id="image_segmentation_v1",
                name="Image Segmentation Model",
                task=VisionTask.IMAGE_SEGMENTATION,
                version="1.0",
                accuracy=0.85,
                model_path="/models/image_segmentation.pkl",
                input_size=(512, 512)
            )
            self.vision_models["image_segmentation_v1"] = image_segmentation_model
            
            logger.info(f"Initialized {len(self.vision_models)} computer vision models")
            
        except Exception as e:
            logger.error(f"❌ Error initializing computer vision models: {e}")
    
    async def start(self):
        """Start the computer vision system"""
        self.running = True
        logger.info("🚀 Starting Computer Vision System...")
        
        # Load existing data
        await self._load_vision_data()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_old_data())
        
        logger.info("✅ Computer Vision System started")
    
    async def stop(self):
        """Stop the computer vision system"""
        self.running = False
        logger.info("🛑 Stopping Computer Vision System...")
        
        # Save vision data
        await self._save_vision_data()
        
        logger.info("✅ Computer Vision System stopped")
    
    async def analyze_image(
        self,
        image_path: str,
        task: VisionTask,
        model_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        try:
            if not image_path or not image_path.strip():
                raise ValueError("Image path cannot be empty")
            
            # Validate image format
            if not await self._validate_image_format(image_path):
                raise ValueError("Unsupported image format")
            
            # Check image size
            if not await self._validate_image_size(image_path):
                raise ValueError(f"Image too large. Maximum size: {self.max_image_size} bytes")
            
            # Generate analysis ID
            analysis_id = f"vision_analysis_{int(time.time())}_{hashlib.md5(image_path.encode()).hexdigest()[:8]}"
            
            # Check cache first
            cache_key = f"{task.value}_{hashlib.md5(image_path.encode()).hexdigest()}"
            if cache_key in self.image_cache:
                cached_result = self.image_cache[cache_key]
                logger.info(f"Using cached result for {task.value}")
                return cached_result
            
            # Find appropriate model
            if not model_id:
                model_id = await self._find_best_model(task)
            
            if not model_id:
                raise ValueError(f"No model available for task: {task.value}")
            
            # Perform analysis
            start_time = time.time()
            result = await self._perform_vision_analysis(image_path, task, model_id, options or {})
            processing_time = time.time() - start_time
            
            # Create analysis record
            analysis = VisionAnalysis(
                id=analysis_id,
                image_path=image_path,
                task=task,
                confidence=result.get("confidence", 0.0),
                result=result,
                processing_time=processing_time
            )
            
            self.vision_analyses[analysis_id] = analysis
            
            # Cache result
            self.image_cache[cache_key] = analysis_id
            if self.redis_client:
                self.redis_client.setex(cache_key, self.cache_ttl, analysis_id)
            
            logger.info(f"Computer vision analysis completed: {analysis_id}")
            return analysis_id
            
        except Exception as e:
            logger.error(f"❌ Error analyzing image: {e}")
            raise
    
    async def get_analysis(self, analysis_id: str) -> Optional[VisionAnalysis]:
        """Get computer vision analysis result"""
        return self.vision_analyses.get(analysis_id)
    
    async def object_detection(self, image_path: str, model_id: Optional[str] = None) -> List[DetectedObject]:
        """Perform object detection on image"""
        try:
            analysis_id = await self.analyze_image(image_path, VisionTask.OBJECT_DETECTION, model_id)
            analysis = self.vision_analyses[analysis_id]
            
            objects_data = analysis.result["objects"]
            objects = []
            
            for obj_data in objects_data:
                obj = DetectedObject(
                    class_name=obj_data["class_name"],
                    class_id=obj_data["class_id"],
                    confidence=obj_data["confidence"],
                    bounding_box=BoundingBox(
                        x=obj_data["bounding_box"]["x"],
                        y=obj_data["bounding_box"]["y"],
                        width=obj_data["bounding_box"]["width"],
                        height=obj_data["bounding_box"]["height"],
                        confidence=obj_data["bounding_box"]["confidence"]
                    ),
                    attributes=obj_data.get("attributes", {})
                )
                objects.append(obj)
            
            return objects
            
        except Exception as e:
            logger.error(f"❌ Error in object detection: {e}")
            raise
    
    async def face_recognition(self, image_path: str, model_id: Optional[str] = None) -> List[FaceInfo]:
        """Perform face recognition on image"""
        try:
            analysis_id = await self.analyze_image(image_path, VisionTask.FACE_RECOGNITION, model_id)
            analysis = self.vision_analyses[analysis_id]
            
            faces_data = analysis.result["faces"]
            faces = []
            
            for face_data in faces_data:
                face = FaceInfo(
                    face_id=face_data["face_id"],
                    confidence=face_data["confidence"],
                    bounding_box=BoundingBox(
                        x=face_data["bounding_box"]["x"],
                        y=face_data["bounding_box"]["y"],
                        width=face_data["bounding_box"]["width"],
                        height=face_data["bounding_box"]["height"],
                        confidence=face_data["bounding_box"]["confidence"]
                    ),
                    landmarks=face_data.get("landmarks", []),
                    attributes=face_data.get("attributes", {})
                )
                faces.append(face)
            
            return faces
            
        except Exception as e:
            logger.error(f"❌ Error in face recognition: {e}")
            raise
    
    async def text_recognition(self, image_path: str, model_id: Optional[str] = None) -> List[TextRegion]:
        """Perform text recognition on image"""
        try:
            analysis_id = await self.analyze_image(image_path, VisionTask.TEXT_RECOGNITION, model_id)
            analysis = self.vision_analyses[analysis_id]
            
            text_regions_data = analysis.result["text_regions"]
            text_regions = []
            
            for region_data in text_regions_data:
                region = TextRegion(
                    text=region_data["text"],
                    confidence=region_data["confidence"],
                    bounding_box=BoundingBox(
                        x=region_data["bounding_box"]["x"],
                        y=region_data["bounding_box"]["y"],
                        width=region_data["bounding_box"]["width"],
                        height=region_data["bounding_box"]["height"],
                        confidence=region_data["bounding_box"]["confidence"]
                    ),
                    language=region_data.get("language")
                )
                text_regions.append(region)
            
            return text_regions
            
        except Exception as e:
            logger.error(f"❌ Error in text recognition: {e}")
            raise
    
    async def image_classification(self, image_path: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform image classification"""
        try:
            analysis_id = await self.analyze_image(image_path, VisionTask.IMAGE_CLASSIFICATION, model_id)
            analysis = self.vision_analyses[analysis_id]
            
            return analysis.result
            
        except Exception as e:
            logger.error(f"❌ Error in image classification: {e}")
            raise
    
    async def image_segmentation(self, image_path: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform image segmentation"""
        try:
            analysis_id = await self.analyze_image(image_path, VisionTask.IMAGE_SEGMENTATION, model_id)
            analysis = self.vision_analyses[analysis_id]
            
            return analysis.result
            
        except Exception as e:
            logger.error(f"❌ Error in image segmentation: {e}")
            raise
    
    async def pose_estimation(self, image_path: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform pose estimation"""
        try:
            analysis_id = await self.analyze_image(image_path, VisionTask.POSE_ESTIMATION, model_id)
            analysis = self.vision_analyses[analysis_id]
            
            return analysis.result
            
        except Exception as e:
            logger.error(f"❌ Error in pose estimation: {e}")
            raise
    
    async def scene_understanding(self, image_path: str, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Perform scene understanding"""
        try:
            analysis_id = await self.analyze_image(image_path, VisionTask.SCENE_UNDERSTANDING, model_id)
            analysis = self.vision_analyses[analysis_id]
            
            return analysis.result
            
        except Exception as e:
            logger.error(f"❌ Error in scene understanding: {e}")
            raise
    
    async def image_generation(self, prompt: str, model_id: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> str:
        """Generate image from text prompt"""
        try:
            # Create a temporary image path for generation
            image_path = f"/tmp/generated_{int(time.time())}.png"
            
            analysis_id = await self.analyze_image(image_path, VisionTask.IMAGE_GENERATION, model_id, options)
            analysis = self.vision_analyses[analysis_id]
            
            return analysis.result["generated_image_path"]
            
        except Exception as e:
            logger.error(f"❌ Error in image generation: {e}")
            raise
    
    async def image_enhancement(self, image_path: str, enhancement_type: str, model_id: Optional[str] = None) -> str:
        """Enhance image quality"""
        try:
            options = {"enhancement_type": enhancement_type}
            analysis_id = await self.analyze_image(image_path, VisionTask.IMAGE_ENHANCEMENT, model_id, options)
            analysis = self.vision_analyses[analysis_id]
            
            return analysis.result["enhanced_image_path"]
            
        except Exception as e:
            logger.error(f"❌ Error in image enhancement: {e}")
            raise
    
    async def optical_character_recognition(self, image_path: str, model_id: Optional[str] = None) -> str:
        """Perform OCR on image"""
        try:
            analysis_id = await self.analyze_image(image_path, VisionTask.OPTICAL_CHARACTER_RECOGNITION, model_id)
            analysis = self.vision_analyses[analysis_id]
            
            return analysis.result["text"]
            
        except Exception as e:
            logger.error(f"❌ Error in OCR: {e}")
            raise
    
    async def get_vision_analytics(self) -> Dict[str, Any]:
        """Get computer vision system analytics"""
        try:
            total_analyses = len(self.vision_analyses)
            total_models = len(self.vision_models)
            
            # Task distribution
            task_distribution = {}
            for analysis in self.vision_analyses.values():
                task = analysis.task.value
                task_distribution[task] = task_distribution.get(task, 0) + 1
            
            # Average processing time
            processing_times = [a.processing_time for a in self.vision_analyses.values()]
            avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
            
            # Model accuracy
            model_accuracies = {model_id: model.accuracy for model_id, model in self.vision_models.items()}
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_analyses = [
                a for a in self.vision_analyses.values()
                if datetime.fromisoformat(a.created_at) > recent_cutoff
            ]
            
            return {
                "analyses": {
                    "total": total_analyses,
                    "recent": len(recent_analyses)
                },
                "models": {
                    "total": total_models,
                    "enabled": len([m for m in self.vision_models.values() if m.enabled]),
                    "accuracies": model_accuracies
                },
                "tasks": {
                    "distribution": task_distribution
                },
                "performance": {
                    "avg_processing_time": avg_processing_time
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting vision analytics: {e}")
            return {"error": str(e)}
    
    async def _validate_image_format(self, image_path: str) -> bool:
        """Validate image format"""
        try:
            # Check file extension
            extension = image_path.split('.')[-1].lower()
            return extension in [fmt.value for fmt in self.supported_formats]
            
        except Exception as e:
            logger.error(f"❌ Error validating image format: {e}")
            return False
    
    async def _validate_image_size(self, image_path: str) -> bool:
        """Validate image size"""
        try:
            import os
            file_size = os.path.getsize(image_path)
            return file_size <= self.max_image_size
            
        except Exception as e:
            logger.error(f"❌ Error validating image size: {e}")
            return False
    
    async def _find_best_model(self, task: VisionTask) -> Optional[str]:
        """Find the best model for a task"""
        try:
            # Filter models by task
            task_models = [model for model in self.vision_models.values() if model.task == task and model.enabled]
            
            if not task_models:
                return None
            
            # Return model with highest accuracy
            best_model = max(task_models, key=lambda m: m.accuracy)
            return best_model.id
            
        except Exception as e:
            logger.error(f"❌ Error finding best model: {e}")
            return None
    
    async def _perform_vision_analysis(self, image_path: str, task: VisionTask, model_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the actual computer vision analysis"""
        try:
            # In practice, this would load and run actual ML models
            
            import random
            
            if task == VisionTask.OBJECT_DETECTION:
            elif task == VisionTask.FACE_RECOGNITION:
            elif task == VisionTask.TEXT_RECOGNITION:
            elif task == VisionTask.IMAGE_CLASSIFICATION:
            elif task == VisionTask.IMAGE_SEGMENTATION:
            elif task == VisionTask.POSE_ESTIMATION:
            elif task == VisionTask.SCENE_UNDERSTANDING:
            elif task == VisionTask.IMAGE_GENERATION:
            elif task == VisionTask.IMAGE_ENHANCEMENT:
            elif task == VisionTask.OPTICAL_CHARACTER_RECOGNITION:
            else:
                return {"error": f"Unsupported task: {task.value}"}
            
        except Exception as e:
            logger.error(f"❌ Error performing vision analysis: {e}")
            return {"error": str(e)}
    
        import random
        
        objects = []
        num_objects = random.randint(0, 10)
        
        for i in range(num_objects):
            obj = {
                "class_name": random.choice(["person", "car", "dog", "cat", "bicycle", "motorcycle", "bus", "truck", "bird", "horse"]),
                "class_id": random.randint(0, 79),
                "confidence": 0.7 + random.uniform(0, 0.3),
                "bounding_box": {
                    "x": random.randint(0, 500),
                    "y": random.randint(0, 500),
                    "width": random.randint(50, 200),
                    "height": random.randint(50, 200),
                    "confidence": 0.7 + random.uniform(0, 0.3)
                },
                "attributes": {
                    "color": random.choice(["red", "blue", "green", "yellow", "black", "white"]),
                    "size": random.choice(["small", "medium", "large"])
                }
            }
            objects.append(obj)
        
        return {
            "objects": objects,
            "confidence": 0.8 + random.uniform(0, 0.2)
        }
    
        import random
        
        faces = []
        num_faces = random.randint(0, 5)
        
        for i in range(num_faces):
            face = {
                "face_id": f"face_{i}_{int(time.time())}",
                "confidence": 0.8 + random.uniform(0, 0.2),
                "bounding_box": {
                    "x": random.randint(0, 400),
                    "y": random.randint(0, 400),
                    "width": random.randint(80, 150),
                    "height": random.randint(80, 150),
                    "confidence": 0.8 + random.uniform(0, 0.2)
                },
                "landmarks": [
                    (random.randint(0, 100), random.randint(0, 100)) for _ in range(5)
                ],
                "attributes": {
                    "age": random.randint(18, 80),
                    "gender": random.choice(["male", "female"]),
                    "emotion": random.choice(["happy", "sad", "neutral", "angry", "surprised"])
                }
            }
            faces.append(face)
        
        return {
            "faces": faces,
            "confidence": 0.9 + random.uniform(0, 0.1)
        }
    
        import random
        
        text_regions = []
        num_regions = random.randint(0, 8)
        
        for i in range(num_regions):
            region = {
                "confidence": 0.8 + random.uniform(0, 0.2),
                "bounding_box": {
                    "x": random.randint(0, 400),
                    "y": random.randint(0, 400),
                    "width": random.randint(100, 300),
                    "height": random.randint(20, 50),
                    "confidence": 0.8 + random.uniform(0, 0.2)
                },
                "language": random.choice(["en", "es", "fr", "de", "it"])
            }
            text_regions.append(region)
        
        return {
            "text_regions": text_regions,
            "confidence": 0.85 + random.uniform(0, 0.15)
        }
    
        import random
        
        categories = ["cat", "dog", "car", "person", "building", "tree", "flower", "food", "book", "phone"]
        category = random.choice(categories)
        confidence = 0.7 + random.uniform(0, 0.3)
        
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
        
        num_segments = random.randint(1, 5)
        segments = []
        
        for i in range(num_segments):
            segment = {
                "class": random.choice(["person", "car", "building", "sky", "ground"]),
                "mask_path": f"/tmp/segment_{i}.png",
                "confidence": 0.8 + random.uniform(0, 0.2)
            }
            segments.append(segment)
        
        return {
            "segments": segments,
            "confidence": 0.8 + random.uniform(0, 0.2)
        }
    
        import random
        
        keypoints = []
        num_people = random.randint(0, 3)
        
        for person in range(num_people):
            person_keypoints = []
            for joint in range(17):  # COCO format has 17 keypoints
                keypoint = {
                    "x": random.randint(0, 640),
                    "y": random.randint(0, 480),
                    "confidence": 0.7 + random.uniform(0, 0.3)
                }
                person_keypoints.append(keypoint)
            
            keypoints.append({
                "person_id": person,
                "keypoints": person_keypoints,
                "confidence": 0.8 + random.uniform(0, 0.2)
            })
        
        return {
            "keypoints": keypoints,
            "confidence": 0.8 + random.uniform(0, 0.2)
        }
    
        import random
        
        scenes = ["indoor", "outdoor", "urban", "rural", "beach", "forest", "mountain", "desert"]
        scene = random.choice(scenes)
        confidence = 0.8 + random.uniform(0, 0.2)
        
        return {
            "scene": scene,
            "confidence": confidence,
            "attributes": {
                "lighting": random.choice(["bright", "dim", "natural", "artificial"]),
                "weather": random.choice(["sunny", "cloudy", "rainy", "snowy"]),
                "time_of_day": random.choice(["morning", "afternoon", "evening", "night"])
            }
        }
    
        import random
        
        
        return {
            "generated_image_path": generated_path,
            "confidence": 0.8 + random.uniform(0, 0.2),
            "prompt": options.get("prompt", "Generated image"),
            "style": options.get("style", "realistic")
        }
    
        import random
        
        enhancement_type = options.get("enhancement_type", "general")
        enhanced_path = f"/tmp/enhanced_{int(time.time())}.png"
        
        return {
            "enhanced_image_path": enhanced_path,
            "enhancement_type": enhancement_type,
            "confidence": 0.8 + random.uniform(0, 0.2),
            "improvements": ["sharpness", "contrast", "brightness"]
        }
    
        import random
        
            "The quick brown fox jumps over the lazy dog.",
        ]
        
        confidence = 0.8 + random.uniform(0, 0.2)
        
        return {
            "text": extracted_text,
            "confidence": confidence,
            "language": "en"
        }
    
    async def _cleanup_old_data(self):
        """Clean up old vision data"""
        while self.running:
            try:
                # Clean up old analyses
                cutoff_date = datetime.now() - timedelta(days=7)
                
                old_analyses = [
                    analysis_id for analysis_id, analysis in self.vision_analyses.items()
                    if datetime.fromisoformat(analysis.created_at) < cutoff_date
                ]
                
                for analysis_id in old_analyses:
                    del self.vision_analyses[analysis_id]
                
                if old_analyses:
                    logger.info(f"Cleaned up {len(old_analyses)} old analyses")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_vision_data(self):
        """Load vision data from storage"""
        try:
            if self.redis_client:
                # Load vision analyses
                analyses_data = self.redis_client.get("frenly_vision_analyses")
                if analyses_data:
                    analyses_json = json.loads(analyses_data)
                    for analysis_id, analysis_data in analyses_json.items():
                        analysis = VisionAnalysis(
                            id=analysis_id,
                            image_path=analysis_data["image_path"],
                            task=VisionTask(analysis_data["task"]),
                            confidence=analysis_data["confidence"],
                            result=analysis_data["result"],
                            processing_time=analysis_data.get("processing_time", 0.0),
                            created_at=analysis_data["created_at"]
                        )
                        self.vision_analyses[analysis_id] = analysis
                
                # Load vision models
                models_data = self.redis_client.get("frenly_vision_models")
                if models_data:
                    models_json = json.loads(models_data)
                    for model_id, model_data in models_json.items():
                        model = VisionModel(
                            id=model_id,
                            name=model_data["name"],
                            task=VisionTask(model_data["task"]),
                            version=model_data["version"],
                            accuracy=model_data["accuracy"],
                            model_path=model_data["model_path"],
                            input_size=tuple(model_data["input_size"]),
                            enabled=model_data.get("enabled", True),
                            created_at=model_data["created_at"]
                        )
                        self.vision_models[model_id] = model
                
                logger.info(f"Loaded {len(self.vision_analyses)} analyses and {len(self.vision_models)} models")
            
        except Exception as e:
            logger.error(f"❌ Error loading vision data: {e}")
    
    async def _save_vision_data(self):
        """Save vision data to storage"""
        try:
            if self.redis_client:
                # Save vision analyses
                analyses_data = {
                    analysis_id: {
                        "image_path": analysis.image_path,
                        "task": analysis.task.value,
                        "confidence": analysis.confidence,
                        "result": analysis.result,
                        "processing_time": analysis.processing_time,
                        "created_at": analysis.created_at
                    }
                    for analysis_id, analysis in self.vision_analyses.items()
                }
                self.redis_client.setex("frenly_vision_analyses", 86400, json.dumps(analyses_data))
                
                # Save vision models
                models_data = {
                    model_id: {
                        "name": model.name,
                        "task": model.task.value,
                        "version": model.version,
                        "accuracy": model.accuracy,
                        "model_path": model.model_path,
                        "input_size": list(model.input_size),
                        "enabled": model.enabled,
                        "created_at": model.created_at
                    }
                    for model_id, model in self.vision_models.items()
                }
                self.redis_client.setex("frenly_vision_models", 86400, json.dumps(models_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving vision data: {e}")

# Global computer vision system instance
computer_vision = ComputerVisionSystem()
