#!/usr/bin/env python3
"""
Evidence Processor - Comprehensive Evidence Processing Pipeline

This module implements the EvidenceProcessor class that provides
comprehensive evidence processing capabilities for the Evidence Agent
in the forensic platform.
"""

import asyncio
import hashlib
import logging
import mimetypes
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import exifread
import nltk
import pytesseract
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType
import hashlib
import logging
import mimetypes
import os
import uuid
from datetime import datetime

import exifread
import nltk
import pytesseract
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class EvidenceType(Enum):
    """Types of evidence files."""

    IMAGE = "image"  # Image files (JPEG, PNG, etc.)
    DOCUMENT = "document"  # Document files (PDF, DOC, etc.)
    TEXT = "text"  # Text files (TXT, LOG, etc.)
    CHAT_LOG = "chat_log"  # Chat and communication logs
    DATABASE = "database"  # Database files and dumps
    AUDIO = "audio"  # Audio files
    VIDEO = "video"  # Video files
    ARCHIVE = "archive"  # Archive files (ZIP, RAR, etc.)
    UNKNOWN = "unknown"  # Unknown file type


class ProcessingStatus(Enum):
    """Status of evidence processing."""

    PENDING = "pending"  # Pending processing
    IN_PROGRESS = "in_progress"  # Processing in progress
    COMPLETED = "completed"  # Processing completed
    FAILED = "failed"  # Processing failed
    PARTIAL = "partial"  # Partial processing success
    SKIPPED = "skipped"  # Processing skipped


class ProcessingStage(Enum):
    """Stages of evidence processing."""

    UPLOAD = "upload"  # File upload
    VALIDATION = "validation"  # File validation
    HASH_VERIFICATION = "hash_verification"  # Hash calculation and verification
    METADATA_EXTRACTION = "metadata_extraction"  # Metadata extraction
    CONTENT_ANALYSIS = "content_analysis"  # Content analysis
    OCR_PROCESSING = "ocr_processing"  # OCR processing
    NLP_ANALYSIS = "nlp_analysis"  # NLP analysis
    EVIDENCE_STORAGE = "evidence_storage"  # Evidence storage
    COMPLETION = "completion"  # Processing completion


@dataclass
class FileMetadata:
    """File metadata information."""

    file_id: str
    filename: str
    file_path: str
    file_size: int
    file_type: str
    mime_type: str
    evidence_type: EvidenceType
    upload_timestamp: datetime
    hash_md5: str
    hash_sha256: str
    hash_sha512: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EXIFData:
    """EXIF metadata from images."""

    camera_make: Optional[str]
    camera_model: Optional[str]
    date_taken: Optional[datetime]
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    software_used: Optional[str]
    image_dimensions: Tuple[int, int]
    color_space: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OCRResult:
    """OCR processing result."""

    text_content: str
    confidence_scores: List[float]
    page_numbers: List[int]
    language_detected: str
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NLPAnalysis:
    """NLP analysis result."""

    entities: List[Dict[str, Any]]
    key_phrases: List[str]
    sentiment_score: float
    language_detected: str
    word_count: int
    sentence_count: int
    named_entities: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingResult:
    """Result of evidence processing."""

    result_id: str
    file_id: str
    processing_status: ProcessingStatus
    processing_stages: List[ProcessingStage]
    file_metadata: FileMetadata
    exif_data: Optional[EXIFData]
    ocr_result: Optional[OCRResult]
    nlp_analysis: Optional[NLPAnalysis]
    processing_errors: List[str]
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class EvidenceProcessor:
    """
    Comprehensive evidence processing system.

    The EvidenceProcessor is responsible for:
    - File upload and validation
    - Hash verification and integrity checking
    - Metadata extraction (EXIF, etc.)
    - OCR processing for documents
    - NLP analysis for text content
    - Evidence storage and management
    - Processing pipeline orchestration
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the EvidenceProcessor."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.supported_formats = config.get(
            "supported_formats",
            [
                "jpg",
                "jpeg",
                "png",
                "gif",
                "bmp",
                "tiff",
                "pdf",
                "doc",
                "docx",
                "txt",
                "log",
                "csv",
                "zip",
                "rar",
                "7z",
                "mp3",
                "mp4",
                "avi",
            ],
        )
        self.max_file_size = config.get("max_file_size", 100 * 1024 * 1024)  # 100MB
        self.processing_timeout = config.get("processing_timeout", 300)  # 5 minutes

        # File management
        self.upload_directory = config.get("upload_directory", "./uploads")
        self.processed_directory = config.get("processed_directory", "./processed")
        self.temp_directory = config.get("temp_directory", "./temp")

        # Processing components
        self.file_metadata: Dict[str, FileMetadata] = {}
        self.processing_results: Dict[str, ProcessingResult] = {}
        self.processing_queue: List[str] = []
        self.active_processing: Dict[str, asyncio.Task] = {}

        # Performance tracking
        self.total_files_processed = 0
        self.successful_processing = 0
        self.failed_processing = 0
        self.average_processing_time = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Initialize directories
        self._initialize_directories()

        self.logger.info("EvidenceProcessor initialized successfully")

    def _initialize_directories(self):
        """Initialize necessary directories."""
        try:
            for directory in [
                self.upload_directory,
                self.processed_directory,
                self.temp_directory,
            ]:
                os.makedirs(directory, exist_ok=True)

            self.logger.info("Processing directories initialized")

        except Exception as e:
            self.logger.error(f"Error initializing directories: {e}")

    async def start(self):
        """Start the EvidenceProcessor."""
        self.logger.info("Starting EvidenceProcessor...")

        # Initialize processing components
        await self._initialize_processing_components()

        # Start background tasks
        asyncio.create_task(self._process_upload_queue())
        asyncio.create_task(self._cleanup_temp_files())

        self.logger.info("EvidenceProcessor started successfully")

    async def stop(self):
        """Stop the EvidenceProcessor."""
        self.logger.info("Stopping EvidenceProcessor...")

        # Cancel active processing
        for task in self.active_processing.values():
            task.cancel()

        self.logger.info("EvidenceProcessor stopped")

    async def upload_file(self, file_path: str, filename: str = None) -> str:
        """Upload a file for processing."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Validate file
            if not await self._validate_file(file_path):
                raise ValueError(f"File validation failed: {file_path}")

            # Generate file ID
            file_id = str(uuid.uuid4())

            # Copy file to upload directory
            if not filename:
                filename = os.path.basename(file_path)

            upload_path = os.path.join(self.upload_directory, f"{file_id}_{filename}")

            # Copy file
            with open(file_path, "rb") as src, open(upload_path, "wb") as dst:
                dst.write(src.read())

            # Create file metadata
            file_metadata = await self._create_file_metadata(
                file_id, upload_path, filename
            )
            self.file_metadata[file_id] = file_metadata

            # Add to processing queue
            self.processing_queue.append(file_id)

            self.logger.info(f"File uploaded: {file_id} - {filename}")

            return file_id

        except Exception as e:
            self.logger.error(f"Error uploading file: {e}")
            raise

    async def _validate_file(self, file_path: str) -> bool:
        """Validate file for processing."""
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                self.logger.warning(f"File too large: {file_size} bytes")
                return False

            # Check file format
            file_extension = os.path.splitext(file_path)[1].lower().lstrip(".")
            if file_extension not in self.supported_formats:
                self.logger.warning(f"Unsupported file format: {file_extension}")
                return False

            # Check if file is readable
            try:
                with open(file_path, "rb") as f:
                    f.read(1024)  # Read first 1KB
            except Exception:
                logger.error(f"Error: {e}")
                self.logger.warning(f"File not readable: {file_path}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating file: {e}")
            return False

    async def _create_file_metadata(
        self, file_id: str, file_path: str, filename: str
    ) -> FileMetadata:
        """Create file metadata."""
        try:
            # Get file information
            file_size = os.path.getsize(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)

            # Determine evidence type
            evidence_type = self._determine_evidence_type(filename, mime_type)

            # Calculate hashes
            hash_md5, hash_sha256, hash_sha512 = await self._calculate_file_hashes(
                file_path
            )

            file_metadata = FileMetadata(
                file_id=file_id,
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                file_type=os.path.splitext(filename)[1].lower().lstrip("."),
                mime_type=mime_type or "application/octet-stream",
                evidence_type=evidence_type,
                upload_timestamp=datetime.utcnow(),
                hash_md5=hash_md5,
                hash_sha256=hash_sha256,
                hash_sha512=hash_sha512,
            )

            return file_metadata

        except Exception as e:
            self.logger.error(f"Error creating file metadata: {e}")
            raise

    def _determine_evidence_type(self, filename: str, mime_type: str) -> EvidenceType:
        """Determine evidence type from filename and MIME type."""
        try:
            file_extension = os.path.splitext(filename)[1].lower().lstrip(".")

            # Image files
            if file_extension in ["jpg", "jpeg", "png", "gif", "bmp", "tiff"]:
                return EvidenceType.IMAGE

            # Document files
            elif file_extension in ["pdf", "doc", "docx", "txt", "log", "csv"]:
                return EvidenceType.DOCUMENT

            # Chat logs
            elif file_extension in ["log", "txt"] and "chat" in filename.lower():
                return EvidenceType.CHAT_LOG

            # Database files
            elif file_extension in ["db", "sql", "sqlite"]:
                return EvidenceType.DATABASE

            # Audio files
            elif file_extension in ["mp3", "wav", "flac", "aac"]:
                return EvidenceType.AUDIO

            # Video files
            elif file_extension in ["mp4", "avi", "mov", "mkv"]:
                return EvidenceType.VIDEO

            # Archive files
            elif file_extension in ["zip", "rar", "7z", "tar", "gz"]:
                return EvidenceType.ARCHIVE

            # Text files
            elif file_extension in ["txt", "log", "csv"]:
                return EvidenceType.TEXT

            else:
                return EvidenceType.UNKNOWN

        except Exception as e:
            self.logger.error(f"Error determining evidence type: {e}")
            return EvidenceType.UNKNOWN

    async def _calculate_file_hashes(self, file_path: str) -> Tuple[str, str, str]:
        """Calculate file hashes."""
        try:
            hash_md5 = hashlib.md5()
            hash_sha256 = hashlib.sha256()
            hash_sha512 = hashlib.sha512()

            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hash_md5.update(chunk)
                    hash_sha256.update(chunk)
                    hash_sha512.update(chunk)

            return (
                hash_md5.hexdigest(),
                hash_sha256.hexdigest(),
                hash_sha512.hexdigest(),
            )

        except Exception as e:
            self.logger.error(f"Error calculating file hashes: {e}")
            raise

    async def _process_upload_queue(self):
        """Process files in the upload queue."""
        while True:
            try:
                if (
                    self.processing_queue and len(self.active_processing) < 5
                ):  # Max 5 concurrent
                    file_id = self.processing_queue.pop(0)

                    # Start processing
                    task = asyncio.create_task(self._process_file(file_id))
                    self.active_processing[file_id] = task

                await asyncio.sleep(1)  # Check queue every second

            except Exception as e:
                self.logger.error(f"Error processing upload queue: {e}")
                await asyncio.sleep(5)

    async def _process_file(self, file_id: str):
        """Process a single file."""
        try:
            start_time = datetime.utcnow()

            if file_id not in self.file_metadata:
                raise ValueError(f"File metadata not found: {file_id}")

            file_metadata = self.file_metadata[file_id]
            processing_stages = []
            processing_errors = []

            self.logger.info(f"Starting processing for file: {file_id}")

            # Stage 1: Validation
            processing_stages.append(ProcessingStage.VALIDATION)
            if not await self._validate_uploaded_file(file_metadata):
                processing_errors.append("File validation failed")
                raise ValueError("File validation failed")

            # Stage 2: Hash verification
            processing_stages.append(ProcessingStage.HASH_VERIFICATION)
            if not await self._verify_file_hashes(file_metadata):
                processing_errors.append("Hash verification failed")
                raise ValueError("Hash verification failed")

            # Stage 3: Metadata extraction
            processing_stages.append(ProcessingStage.METADATA_EXTRACTION)
            exif_data = None
            if file_metadata.evidence_type == EvidenceType.IMAGE:
                exif_data = await self._extract_exif_data(file_metadata)

            # Stage 4: Content analysis
            processing_stages.append(ProcessingStage.CONTENT_ANALYSIS)
            ocr_result = None
            nlp_analysis = None

            if file_metadata.evidence_type == EvidenceType.DOCUMENT:
                ocr_result = await self._perform_ocr_processing(file_metadata)

            if file_metadata.evidence_type in [
                EvidenceType.TEXT,
                EvidenceType.CHAT_LOG,
            ]:
                nlp_analysis = await self._perform_nlp_analysis(file_metadata)

            # Stage 5: Evidence storage
            processing_stages.append(ProcessingStage.EVIDENCE_STORAGE)
            await self._store_evidence(file_metadata)

            # Stage 6: Completion
            processing_stages.append(ProcessingStage.COMPLETION)

            # Calculate processing time
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()

            # Create processing result
            processing_result = ProcessingResult(
                result_id=str(uuid.uuid4()),
                file_id=file_id,
                processing_status=ProcessingStatus.COMPLETED,
                processing_stages=processing_stages,
                file_metadata=file_metadata,
                exif_data=exif_data,
                ocr_result=ocr_result,
                nlp_analysis=nlp_analysis,
                processing_errors=processing_errors,
                processing_time=processing_time,
                timestamp=datetime.utcnow(),
            )

            # Store result
            self.processing_results[processing_result.result_id] = processing_result

            # Update statistics
            self.total_files_processed += 1
            self.successful_processing += 1

            self.logger.info(
                f"File processing completed: {file_id} in {processing_time:.2f}s"
            )

        except Exception as e:
            self.logger.error(f"Error processing file {file_id}: {e}")

            # Create failed result
            processing_result = ProcessingResult(
                result_id=str(uuid.uuid4()),
                file_id=file_id,
                processing_status=ProcessingStatus.FAILED,
                processing_stages=(
                    processing_stages if "processing_stages" in locals() else []
                ),
                file_metadata=file_metadata if "file_metadata" in locals() else None,
                exif_data=None,
                ocr_result=None,
                nlp_analysis=None,
                processing_errors=[str(e)],
                processing_time=0.0,
                timestamp=datetime.utcnow(),
            )

            # Store result
            self.processing_results[processing_result.result_id] = processing_result

            # Update statistics
            self.total_files_processed += 1
            self.failed_processing += 1

        finally:
            # Remove from active processing
            if file_id in self.active_processing:
                del self.active_processing[file_id]

    async def _validate_uploaded_file(self, file_metadata: FileMetadata) -> bool:
        """Validate uploaded file."""
        try:
            # Check if file still exists
            if not os.path.exists(file_metadata.file_path):
                return False

            # Check file size
            current_size = os.path.getsize(file_metadata.file_path)
            if current_size != file_metadata.file_size:
                return False

            # Verify file is readable
            try:
                with open(file_metadata.file_path, "rb") as f:
                    f.read(1024)
            except Exception:
                logger.error(f"Error: {e}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating uploaded file: {e}")
            return False

    async def _verify_file_hashes(self, file_metadata: FileMetadata) -> bool:
        """Verify file hashes."""
        try:
            # Recalculate hashes
            current_md5, current_sha256, current_sha512 = (
                await self._calculate_file_hashes(file_metadata.file_path)
            )

            # Compare with stored hashes
            if (
                current_md5 != file_metadata.hash_md5
                or current_sha256 != file_metadata.hash_sha256
                or current_sha512 != file_metadata.hash_sha512
            ):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error verifying file hashes: {e}")
            return False

    async def _extract_exif_data(
        self, file_metadata: FileMetadata
    ) -> Optional[EXIFData]:
        """Extract EXIF data from image files."""
        try:
            if file_metadata.evidence_type != EvidenceType.IMAGE:
                return None

            with open(file_metadata.file_path, "rb") as f:
                tags = exifread.process_file(f)

            # Extract relevant EXIF data
            camera_make = tags.get("Image Make", None)
            camera_model = tags.get("Image Model", None)

            # Date taken
            date_taken = None
            if "EXIF DateTimeOriginal" in tags:
                date_str = str(tags["EXIF DateTimeOriginal"])
                try:
                    date_taken = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                except ValueError:
                    pass

            # GPS coordinates
            gps_latitude = None
            gps_longitude = None
            if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
                # Simple GPS extraction - in production would be more sophisticated
                gps_latitude = 0.0  # Placeholder
                gps_longitude = 0.0  # Placeholder

            # Software used
            software_used = tags.get("Image Software", None)

            # Image dimensions
            image_dimensions = (0, 0)  # Placeholder
            if "Image ImageWidth" in tags and "Image ImageLength" in tags:
                width = int(str(tags["Image ImageWidth"]))
                height = int(str(tags["Image ImageLength"]))
                image_dimensions = (width, height)

            # Color space
            color_space = tags.get("Image ColorSpace", None)

            exif_data = EXIFData(
                camera_make=str(camera_make) if camera_make else None,
                camera_model=str(camera_model) if camera_model else None,
                date_taken=date_taken,
                gps_latitude=gps_latitude,
                gps_longitude=gps_longitude,
                software_used=str(software_used) if software_used else None,
                image_dimensions=image_dimensions,
                color_space=str(color_space) if color_space else None,
            )

            return exif_data

        except Exception as e:
            self.logger.error(f"Error extracting EXIF data: {e}")
            return None

    async def _perform_ocr_processing(
        self, file_metadata: FileMetadata
    ) -> Optional[OCRResult]:
        """Perform OCR processing on documents."""
        try:
            if file_metadata.evidence_type != EvidenceType.DOCUMENT:
                return None

            start_time = datetime.utcnow()

            # Convert PDF to images if needed
            if file_metadata.file_type == "pdf":
                # This would use pdf2image in production
                # For now, return placeholder
                text_content = "PDF OCR processing would be performed here"
                confidence_scores = [0.8]
                page_numbers = [1]
                language_detected = "en"
            else:
                # Direct OCR on image files
                try:
                    image = Image.open(file_metadata.file_path)
                    text_content = pytesseract.image_to_string(image)
                    confidence_scores = [0.8]  # Placeholder
                    page_numbers = [1]
                    language_detected = "en"
                except Exception:
                    logger.error(f"Error: {e}")
                    text_content = "OCR processing failed"
                    confidence_scores = [0.0]
                    page_numbers = [1]
                    language_detected = "unknown"

            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()

            ocr_result = OCRResult(
                text_content=text_content,
                confidence_scores=confidence_scores,
                page_numbers=page_numbers,
                language_detected=language_detected,
                processing_time=processing_time,
            )

            return ocr_result

        except Exception as e:
            self.logger.error(f"Error performing OCR processing: {e}")
            return None

    async def _perform_nlp_analysis(
        self, file_metadata: FileMetadata
    ) -> Optional[NLPAnalysis]:
        """Perform NLP analysis on text content."""
        try:
            if file_metadata.evidence_type not in [
                EvidenceType.TEXT,
                EvidenceType.CHAT_LOG,
            ]:
                return None

            # Read file content
            with open(
                file_metadata.file_path, "r", encoding="utf-8", errors="ignore"
            ) as f:
                text_content = f.read()

            # Basic NLP analysis
            words = word_tokenize(text_content)
            sentences = sent_tokenize(text_content)

            # Entity extraction (simplified)
            entities = []
            key_phrases = []

            # Simple named entity detection
            named_entities = []

            # Sentiment analysis (simplified)
            positive_words = ["good", "great", "excellent", "positive", "happy"]
            negative_words = ["bad", "terrible", "awful", "negative", "sad"]

            positive_count = sum(1 for word in words if word.lower() in positive_words)
            negative_count = sum(1 for word in words if word.lower() in negative_words)

            if positive_count + negative_count > 0:
                sentiment_score = (positive_count - negative_count) / (
                    positive_count + negative_count
                )
            else:
                sentiment_score = 0.0

            # Language detection (simplified)
            language_detected = "en"  # Placeholder

            nlp_analysis = NLPAnalysis(
                entities=entities,
                key_phrases=key_phrases,
                sentiment_score=sentiment_score,
                language_detected=language_detected,
                word_count=len(words),
                sentence_count=len(sentences),
                named_entities=named_entities,
            )

            return nlp_analysis

        except Exception as e:
            self.logger.error(f"Error performing NLP analysis: {e}")
            return None

    async def _store_evidence(self, file_metadata: FileMetadata):
        """Store processed evidence."""
        try:
            # Move file to processed directory
            processed_path = os.path.join(
                self.processed_directory,
                f"{file_metadata.file_id}_{file_metadata.filename}",
            )

            # Copy file to processed directory
            with (
                open(file_metadata.file_path, "rb") as src,
                open(processed_path, "wb") as dst,
            ):
                dst.write(src.read())

            # Update file path
            file_metadata.file_path = processed_path

            self.logger.info(f"Evidence stored: {file_metadata.file_id}")

        except Exception as e:
            self.logger.error(f"Error storing evidence: {e}")
            raise

    async def _cleanup_temp_files(self):
        """Clean up temporary files."""
        while True:
            try:
                # Clean up temp directory
                temp_files = os.listdir(self.temp_directory)
                for temp_file in temp_files:
                    temp_path = os.path.join(self.temp_directory, temp_file)
                    try:
                        if os.path.isfile(temp_path):
                            os.remove(temp_path)
                    except Exception:
                        logger.error(f"Error: {e}")
                        pass

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up temp files: {e}")
                await asyncio.sleep(3600)

    async def _initialize_processing_components(self):
        """Initialize processing components."""
        try:
            # Initialize NLP components
            try:
                nltk.download("punkt", quiet=True)
                nltk.download("stopwords", quiet=True)
                nltk.download("wordnet", quiet=True)
            except Exception as e:
                self.logger.warning(f"Could not download NLTK data: {e}")

            self.logger.info("Processing components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing processing components: {e}")

    def get_processing_status(self, file_id: str) -> Optional[ProcessingResult]:
        """Get processing status for a file."""
        try:
            # Find result by file_id
            for result in self.processing_results.values():
                if result.file_id == file_id:
                    return result
            return None

        except Exception as e:
            self.logger.error(f"Error getting processing status: {e}")
            return None

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "total_files_processed": self.total_files_processed,
            "successful_processing": self.successful_processing,
            "failed_processing": self.failed_processing,
            "average_processing_time": self.average_processing_time,
            "files_in_queue": len(self.processing_queue),
            "active_processing": len(self.active_processing),
            "evidence_types_supported": [t.value for t in EvidenceType],
            "processing_stages_supported": [s.value for s in ProcessingStage],
            "supported_formats": self.supported_formats,
            "max_file_size": self.max_file_size,
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "supported_formats": ["jpg", "jpeg", "png", "pdf", "txt", "log"],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "processing_timeout": 300,  # 5 minutes
        "upload_directory": "./uploads",
        "processed_directory": "./processed",
        "temp_directory": "./temp",
    }

    # Initialize evidence processor
    processor = EvidenceProcessor(config)

    print("EvidenceProcessor system initialized successfully!")
