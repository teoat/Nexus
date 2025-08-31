#!/usr/bin/env python3
"""
OCR Processor - Comprehensive OCR Processing for Documents and Images

This module implements the OCRProcessor class that provides
comprehensive OCR processing capabilities for the Evidence Agent
in the forensic platform.
"""

import asyncio
import json
import logging
import os
import shutil
import tempfile
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# OCR Libraries
try:
    import fitz  # PyMuPDF
    import pdf2image
    import PyPDF2
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# PDF Processing Libraries
try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

from ...taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class DocumentType(Enum):
    """Types of documents for OCR processing."""

    PDF = "pdf"  # PDF documents
    IMAGE = "image"  # Image files
    SCANNED_DOCUMENT = "scanned_document"  # Scanned documents
    HANDWRITTEN = "handwritten"  # Handwritten text
    PRINTED_TEXT = "printed_text"  # Printed text
    MIXED_CONTENT = "mixed_content"  # Mixed content types
    UNKNOWN = "unknown"  # Unknown document type


class OCRStatus(Enum):
    """Status of OCR processing."""

    PENDING = "pending"  # Processing pending
    IN_PROGRESS = "in_progress"  # Processing in progress
    COMPLETED = "completed"  # Processing completed
    FAILED = "failed"  # Processing failed
    PARTIAL = "partial"  # Partial processing success
    NO_TEXT_FOUND = "no_text_found"  # No text found in document


class OCRQuality(Enum):
    """Quality of OCR results."""

    EXCELLENT = "excellent"  # 95-100% accuracy
    GOOD = "good"  # 85-94% accuracy
    FAIR = "fair"  # 70-84% accuracy
    POOR = "poor"  # 50-69% accuracy
    VERY_POOR = "very_poor"  # Below 50% accuracy
    UNKNOWN = "unknown"  # Quality unknown


class Language(Enum):
    """Supported languages for OCR."""

    ENGLISH = "eng"  # English
    SPANISH = "spa"  # Spanish
    FRENCH = "fra"  # French
    GERMAN = "deu"  # German
    CHINESE = "chi_sim"  # Simplified Chinese
    JAPANESE = "jpn"  # Japanese
    KOREAN = "kor"  # Korean
    ARABIC = "ara"  # Arabic
    RUSSIAN = "rus"  # Russian
    MULTI = "multi"  # Multiple languages


@dataclass
class OCRPage:
    """OCR results for a single page."""

    page_number: int
    text_content: str
    confidence_scores: List[float]
    bounding_boxes: List[Dict[str, Any]]
    language_detected: str
    processing_time: float
    image_path: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OCRResult:
    """Complete OCR processing result."""

    result_id: str
    document_path: str
    document_type: DocumentType
    ocr_status: OCRStatus
    ocr_quality: OCRQuality
    total_pages: int
    pages: List[OCRPage]
    languages_detected: List[str]
    total_text_length: int
    average_confidence: float
    processing_time: float
    timestamp: datetime
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OCRConfiguration:
    """Configuration for OCR processing."""

    languages: List[Language]
    page_segmentation_mode: int
    ocr_engine_mode: int
    confidence_threshold: float
    enable_preprocessing: bool
    enable_postprocessing: bool
    max_pages: int
    timeout_per_page: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class OCRProcessor:
    """
    Comprehensive OCR processing system.

    The OCRProcessor is responsible for:
    - Multi-format document processing (PDF, Images)
    - Advanced text extraction and recognition
    - Multi-language support
    - Quality assessment and confidence scoring
    - Pre and post-processing optimization
    - Batch processing capabilities
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the OCRProcessor."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.default_languages = config.get("default_languages", [Language.ENGLISH])
        self.confidence_threshold = config.get("confidence_threshold", 60.0)
        self.enable_preprocessing = config.get("enable_preprocessing", True)
        self.enable_postprocessing = config.get("enable_postprocessing", True)
        self.max_pages = config.get("max_pages", 100)
        self.timeout_per_page = config.get("timeout_per_page", 60)  # seconds

        # OCR management
        self.ocr_results: Dict[str, OCRResult] = {}
        self.processing_queue: List[str] = []
        self.active_processing: Dict[str, asyncio.Task] = {}

        # Performance tracking
        self.total_documents_processed = 0
        self.successful_processing = 0
        self.failed_processing = 0
        self.average_processing_time = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        # Check OCR availability
        self._check_ocr_availability()

        self.logger.info("OCRProcessor initialized successfully")

    def _check_ocr_availability(self):
        """Check if OCR libraries are available."""
        if not TESSERACT_AVAILABLE:
            self.logger.warning(
                "Tesseract OCR not available - OCR functionality will be limited",
            )

        if not PDFPLUMBER_AVAILABLE:
            self.logger.warning(
                "PDFPlumber not available - PDF text extraction will be limited",
            )

    async def start(self):
        """Start the OCRProcessor."""
        self.logger.info("Starting OCRProcessor...")

        # Initialize OCR components
        await self._initialize_ocr_components()

        # Start background tasks
        asyncio.create_task(self._process_ocr_queue())
        asyncio.create_task(self._cleanup_temp_files())

        self.logger.info("OCRProcessor started successfully")

    async def stop(self):
        """Stop the OCRProcessor."""
        self.logger.info("Stopping OCRProcessor...")

        # Cancel active processing
        for task in self.active_processing.values():
            task.cancel()

        self.logger.info("OCRProcessor stopped")

    async def process_document(
        self,
        document_path: str,
        languages: List[Language] = None,
        config: OCRConfiguration = None,
    ) -> OCRResult:
        """Process a document with OCR."""
        try:
            if not os.path.exists(document_path):
                raise FileNotFoundError(f"Document not found: {document_path}")

            if not languages:
                languages = self.default_languages

            if not config:
                config = self._create_default_config(languages)

            self.logger.info(f"Starting OCR processing for document: {document_path}")

            # Determine document type
            document_type = self._determine_document_type(document_path)

            # Process based on document type
            if document_type == DocumentType.PDF:
                result = await self._process_pdf_document(document_path, config)
            elif document_type in [DocumentType.IMAGE, DocumentType.SCANNED_DOCUMENT]:
                result = await self._process_image_document(document_path, config)
            else:
                result = await self._process_unknown_document(document_path, config)

            # Store result
            self.ocr_results[result.result_id] = result

            # Update statistics
            self.total_documents_processed += 1
            if result.ocr_status == OCRStatus.COMPLETED:
                self.successful_processing += 1
            else:
                self.failed_processing += 1

            self.logger.info(
                f"OCR processing completed: {result.result_id} - Status: {result.ocr_status.value}",
            )

            return result

        except Exception as e:
            self.logger.error(f"Error processing document: {e}")
            raise

    def _create_default_config(self, languages: List[Language]) -> OCRConfiguration:
        """Create default OCR configuration."""
        return OCRConfiguration(
            languages=languages,
            page_segmentation_mode=3,  # Fully automatic page segmentation
            ocr_engine_mode=3,  # Default OCR engine
            confidence_threshold=self.confidence_threshold,
            enable_preprocessing=self.enable_preprocessing,
            enable_postprocessing=self.enable_postprocessing,
            max_pages=self.max_pages,
            timeout_per_page=self.timeout_per_page,
        )

    def _determine_document_type(self, document_path: str) -> DocumentType:
        """Determine the type of document."""
        try:
            file_extension = os.path.splitext(document_path)[1].lower().lstrip(".")

            if file_extension == "pdf":
                return DocumentType.PDF
            elif file_extension in ["jpg", "jpeg", "png", "tiff", "tif", "bmp"]:
                return DocumentType.IMAGE
            else:
                return DocumentType.UNKNOWN

        except Exception as e:
            self.logger.error(f"Error determining document type: {e}")
            return DocumentType.UNKNOWN

    async def _process_pdf_document(self, document_path: str, config: OCRConfiguration):
        """Process a PDF document with OCR."""
        try:
            start_time = datetime.utcnow()

            # Extract text using PDF libraries first
            extracted_text = await self._extract_pdf_text(document_path)

            if extracted_text and len(extracted_text.strip()) > 100:
                # PDF has extractable text, use it directly
                return await self._create_text_result(
                    document_path, DocumentType.PDF, extracted_text, start_time
                )
            else:
                # PDF needs OCR processing
                return await self._ocr_pdf_document(document_path, config, start_time)

        except Exception as e:
            self.logger.error(f"Error processing PDF document: {e}")
            raise

    async def _extract_pdf_text(self, document_path: str) -> str:
        """Extract text from PDF using various methods."""
        try:
            # Try PDFPlumber first
            if PDFPLUMBER_AVAILABLE:
                try:
                    with pdfplumber.open(document_path) as pdf:
                        text = ""
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                        if text.strip():
                            return text
                except Exception as e:
                    self.logger.debug(f"PDFPlumber extraction failed: {e}")

            # Try PyMuPDF
            try:
                import fitz

                doc = fitz.open(document_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                if text.strip():
                    return text
            except Exception as e:
                self.logger.debug(f"PyMuPDF extraction failed: {e}")

            # Try PyPDF2
            try:
                with open(document_path, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    if text.strip():
                        return text
            except Exception as e:
                self.logger.debug(f"PyPDF2 extraction failed: {e}")

            return ""

        except Exception as e:
            self.logger.error(f"Error extracting PDF text: {e}")
            return ""

    async def _ocr_pdf_document(
        self, document_path: str, config: OCRConfiguration, start_time: datetime
    ):
        """Perform OCR on PDF document."""
        try:
            # Convert PDF to images
            images = await self._convert_pdf_to_images(document_path)

            if not images:
                raise ValueError("Could not convert PDF to images")

            # Process each page
            pages = []
            total_text_length = 0
            languages_detected = set()
            total_confidence = 0.0

            for i, image in enumerate(images[: config.max_pages]):
                try:
                    # Preprocess image
                    if config.enable_preprocessing:
                        image = await self._preprocess_image(image)

                    # Perform OCR
                    page_result = await self._perform_ocr_on_image(image, i + 1, config)
                    pages.append(page_result)

                    # Update statistics
                    total_text_length += len(page_result.text_content)
                    languages_detected.add(page_result.language_detected)
                    total_confidence += sum(page_result.confidence_scores) / len(
                        page_result.confidence_scores
                    )

                except Exception as e:
                    self.logger.warning(f"Error processing page {i + 1}: {e}")
                    # Create failed page result
                    failed_page = OCRPage(
                        page_number=i + 1,
                        text_content="",
                        confidence_scores=[0.0],
                        bounding_boxes=[],
                        language_detected="unknown",
                        processing_time=0.0,
                        image_path=None,
                    )
                    pages.append(failed_page)

            # Calculate final statistics
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()

            # Determine OCR status and quality
            ocr_status = self._determine_ocr_status(pages)
            ocr_quality = self._determine_ocr_quality(
                total_confidence / len(pages) if pages else 0.0
            )

            # Create result
            result = OCRResult(
                result_id=str(uuid.uuid4()),
                document_path=document_path,
                document_type=DocumentType.PDF,
                ocr_status=ocr_status,
                ocr_quality=ocr_quality,
                total_pages=len(pages),
                pages=pages,
                languages_detected=list(languages_detected),
                total_text_length=total_text_length,
                average_confidence=total_confidence / len(pages) if pages else 0.0,
                processing_time=processing_time,
                timestamp=datetime.utcnow(),
                errors=[],
                warnings=[],
            )

            return result

        except Exception as e:
            self.logger.error(f"Error in PDF OCR processing: {e}")
            raise

    async def _convert_pdf_to_images(self, document_path: str) -> List[Image.Image]:
        """Convert PDF to images for OCR processing."""
        try:
            # Use pdf2image to convert PDF to images
            images = pdf2image.convert_from_path(document_path, dpi=300)
            return images

        except Exception as e:
            self.logger.error(f"Error converting PDF to images: {e}")
            return []

    async def _process_image_document(
        self, document_path: str, config: OCRConfiguration
    ):
        """Process an image document with OCR."""
        try:
            start_time = datetime.utcnow()

            # Load image
            image = Image.open(document_path)

            # Preprocess image
            if config.enable_preprocessing:
                image = await self._preprocess_image(image)

            # Perform OCR
            page_result = await self._perform_ocr_on_image(image, 1, config)

            # Calculate statistics
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()

            # Determine OCR status and quality
            ocr_status = self._determine_ocr_status([page_result])
            ocr_quality = self._determine_ocr_quality(
                sum(page_result.confidence_scores) / len(page_result.confidence_scores)
            )

            # Create result
            result = OCRResult(
                result_id=str(uuid.uuid4()),
                document_path=document_path,
                document_type=DocumentType.IMAGE,
                ocr_status=ocr_status,
                ocr_quality=ocr_quality,
                total_pages=1,
                pages=[page_result],
                languages_detected=[page_result.language_detected],
                total_text_length=len(page_result.text_content),
                average_confidence=sum(page_result.confidence_scores)
                / len(page_result.confidence_scores),
                processing_time=processing_time,
                timestamp=datetime.utcnow(),
                errors=[],
                warnings=[],
            )

            return result

        except Exception as e:
            self.logger.error(f"Error processing image document: {e}")
            raise

    async def _process_unknown_document(
        self, document_path: str, config: OCRConfiguration
    ):
        """Process an unknown document type."""
        try:
            # Try to treat as image
            try:
                image = Image.open(document_path)
                return await self._process_image_document(document_path, config)
            except Exception:
                self.logger.error(f"Error: {e}")
                pass

            # Create failed result
            result = OCRResult(
                result_id=str(uuid.uuid4()),
                document_path=document_path,
                document_type=DocumentType.UNKNOWN,
                ocr_status=OCRStatus.FAILED,
                ocr_quality=OCRQuality.UNKNOWN,
                total_pages=0,
                pages=[],
                languages_detected=[],
                total_text_length=0,
                average_confidence=0.0,
                processing_time=0.0,
                timestamp=datetime.utcnow(),
                errors=["Unsupported document type"],
                warnings=[],
            )

            return result

        except Exception as e:
            self.logger.error(f"Error processing unknown document: {e}")
            raise

    async def _create_text_result(
        self,
        document_path: str,
        document_type: DocumentType,
        extracted_text: str,
        start_time: datetime,
    ) -> OCRResult:
        """Create result for documents with extractable text."""
        try:
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()

            # Create page result
            page_result = OCRPage(
                page_number=1,
                text_content=extracted_text,
                confidence_scores=[100.0],  # High confidence for extracted text
                bounding_boxes=[],
                language_detected="en",  # Assume English
                processing_time=processing_time,
                image_path=None,
            )

            # Create result
            result = OCRResult(
                result_id=str(uuid.uuid4()),
                document_path=document_path,
                document_type=document_type,
                ocr_status=OCRStatus.COMPLETED,
                ocr_quality=OCRQuality.EXCELLENT,
                total_pages=1,
                pages=[page_result],
                languages_detected=["en"],
                total_text_length=len(extracted_text),
                average_confidence=100.0,
                processing_time=processing_time,
                timestamp=datetime.utcnow(),
                errors=[],
                warnings=[],
            )

            return result

        except Exception as e:
            self.logger.error(f"Error creating text result: {e}")
            raise

    async def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale if needed
            if image.mode != "L":
                image = image.convert("L")

            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)

            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)

            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))

            return image

        except Exception as e:
            self.logger.error(f"Error preprocessing image: {e}")
            return image

    async def _perform_ocr_on_image(
        self, image: Image.Image, page_number: int, config: OCRConfiguration
    ) -> OCRPage:
        """Perform OCR on a single image."""
        try:
            start_time = datetime.utcnow()

            # Configure Tesseract
            custom_config = (
                f"--oem {config.ocr_engine_mode} --psm {config.page_segmentation_mode}"
            )

            # Add language configuration
            languages = "+".join([lang.value for lang in config.languages])
            if languages:
                custom_config += f" -l {languages}"

            # Perform OCR
            ocr_data = pytesseract.image_to_data(
                image, config=custom_config, output_type=pytesseract.Output.DICT
            )

            # Extract text and confidence scores
            text_content = ""
            confidence_scores = []
            bounding_boxes = []

            for i in range(len(ocr_data["text"])):
                text = ocr_data["text"][i]
                confidence = ocr_data["conf"][i]

                if text.strip() and confidence > config.confidence_threshold:
                    text_content += text + " "
                    confidence_scores.append(confidence)

                    # Store bounding box
                    bbox = {
                        "x": ocr_data["left"][i],
                        "y": ocr_data["top"][i],
                        "width": ocr_data["width"][i],
                        "height": ocr_data["height"][i],
                        "text": text,
                        "confidence": confidence,
                    }
                    bounding_boxes.append(bbox)

            # Post-process text
            if config.enable_postprocessing:
                text_content = await self._postprocess_text(text_content)

            # Determine language
            language_detected = self._detect_language(text_content)

            # Calculate processing time
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()

            # Save image to temp file
            temp_dir = tempfile.gettempdir()
            image_path = os.path.join(
                temp_dir, f"ocr_page_{page_number}_{uuid.uuid4()}.png"
            )
            image.save(image_path)

            page_result = OCRPage(
                page_number=page_number,
                text_content=text_content.strip(),
                confidence_scores=confidence_scores,
                bounding_boxes=bounding_boxes,
                language_detected=language_detected,
                processing_time=processing_time,
                image_path=image_path,
            )

            return page_result

        except Exception as e:
            self.logger.error(f"Error performing OCR on image: {e}")
            raise

    async def _postprocess_text(self, text: str) -> str:
        """Post-process extracted text."""
        try:
            # Remove extra whitespace
            text = " ".join(text.split())

            # Fix common OCR errors
            text = text.replace("|", "I")
            text = text.replace("0", "O")  # Context-dependent
            text = text.replace("1", "l")  # Context-dependent

            return text

        except Exception as e:
            self.logger.error(f"Error post-processing text: {e}")
            return text

    def _detect_language(self, text: str) -> str:
        """Detect language of text."""
        try:
            # Simple language detection based on character sets
            if not text:
                return "unknown"

            # Count characters from different scripts
            latin_chars = sum(1 for c in text if ord(c) < 128)
            total_chars = len(text)

            if total_chars == 0:
                return "unknown"

            latin_ratio = latin_chars / total_chars

            if latin_ratio > 0.9:
                return "en"  # Assume English for Latin text
            elif latin_ratio > 0.7:
                return "multi"  # Mixed content
            else:
                return "unknown"  # Non-Latin script

        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            return "unknown"

    def _determine_ocr_status(self, pages: List[OCRPage]) -> OCRStatus:
        """Determine overall OCR status."""
        try:
            if not pages:
                return OCRStatus.FAILED

            successful_pages = sum(1 for page in pages if page.text_content.strip())
            total_pages = len(pages)

            if successful_pages == 0:
                return OCRStatus.NO_TEXT_FOUND
            elif successful_pages == total_pages:
                return OCRStatus.COMPLETED
            elif successful_pages > 0:
                return OCRStatus.PARTIAL
            else:
                return OCRStatus.FAILED

        except Exception as e:
            self.logger.error(f"Error determining OCR status: {e}")
            return OCRStatus.UNKNOWN

    def _determine_ocr_quality(self, average_confidence: float) -> OCRQuality:
        """Determine OCR quality based on confidence scores."""
        try:
            if average_confidence >= 95:
                return OCRQuality.EXCELLENT
            elif average_confidence >= 85:
                return OCRQuality.GOOD
            elif average_confidence >= 70:
                return OCRQuality.FAIR
            elif average_confidence >= 50:
                return OCRQuality.POOR
            else:
                return OCRQuality.VERY_POOR

        except Exception as e:
            self.logger.error(f"Error determining OCR quality: {e}")
            return OCRQuality.UNKNOWN

    async def _process_ocr_queue(self):
        """Process documents in the OCR queue."""
        while True:
            try:
                if (
                    self.processing_queue and len(self.active_processing) < 3
                ):  # Max 3 concurrent
                    document_path = self.processing_queue.pop(0)

                    # Start processing
                    task = asyncio.create_task(
                        self._process_document_async(document_path)
                    )
                    self.active_processing[document_path] = task

                await asyncio.sleep(1)  # Check queue every second

            except Exception as e:
                self.logger.error(f"Error processing OCR queue: {e}")
                await asyncio.sleep(5)

    async def _process_document_async(self, document_path: str):
        """Process document asynchronously."""
        try:
            await self.process_document(document_path)
        except Exception as e:
            self.logger.error(f"Error in async document processing: {e}")
        finally:
            # Remove from active processing
            if document_path in self.active_processing:
                del self.active_processing[document_path]

    async def _cleanup_temp_files(self):
        """Clean up temporary files."""
        while True:
            try:
                # Clean up temp directory
                temp_dir = tempfile.gettempdir()
                temp_files = [
                    f for f in os.listdir(temp_dir) if f.startswith("ocr_page_")
                ]

                for temp_file in temp_files:
                    temp_path = os.path.join(temp_dir, temp_file)
                    try:
                        if os.path.isfile(temp_path):
                            # Check if file is older than 1 hour
                            if datetime.utcnow() - datetime.fromtimestamp(
                                os.path.getmtime(temp_path)
                            ) > timedelta(hours=1):
                                os.remove(temp_path)
                    except Exception:
                        self.logger.error(f"Error: {e}")
                        pass

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up temp files: {e}")
                await asyncio.sleep(3600)

    async def _initialize_ocr_components(self):
        """Initialize OCR components."""
        try:
            # Test Tesseract availability
            if TESSERACT_AVAILABLE:
                try:
                    # Test Tesseract
                    version = pytesseract.get_tesseract_version()
                    self.logger.info(f"Tesseract version: {version}")
                except Exception as e:
                    self.logger.warning(f"Tesseract not working: {e}")

            self.logger.info("OCR components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing OCR components: {e}")

    def get_ocr_result(self, result_id: str) -> Optional[OCRResult]:
        """Get OCR result by ID."""
        try:
            return self.ocr_results.get(result_id)
        except Exception as e:
            self.logger.error(f"Error getting OCR result: {e}")
            return None

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "total_documents_processed": self.total_documents_processed,
            "successful_processing": self.successful_processing,
            "failed_processing": self.failed_processing,
            "average_processing_time": self.average_processing_time,
            "document_types_supported": [dt.value for dt in DocumentType],
            "ocr_statuses_supported": [status.value for status in OCRStatus],
            "ocr_qualities_supported": [quality.value for quality in OCRQuality],
            "languages_supported": [lang.value for lang in Language],
            "total_ocr_results": len(self.ocr_results),
            "documents_in_queue": len(self.processing_queue),
            "active_processing": len(self.active_processing),
            "tesseract_available": TESSERACT_AVAILABLE,
            "pdfplumber_available": PDFPLUMBER_AVAILABLE,
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "default_languages": ["eng"],
        "confidence_threshold": 60.0,
        "enable_preprocessing": True,
        "enable_postprocessing": True,
        "max_pages": 100,
        "timeout_per_page": 60,
    }

    # Initialize OCR processor
    processor = OCRProcessor(config)

    print("OCRProcessor system initialized successfully!")
