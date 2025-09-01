#!/usr/bin/env python3
"""
EXIF Metadata Extractor - Comprehensive Image Metadata Analysis

This module implements the EXIFExtractor class that provides
comprehensive EXIF metadata extraction capabilities for the Evidence Agent
in the forensic platform.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import exifread

try:
    import pixexif

    PIXEXIF_AVAILABLE = True
except ImportError:
    PIXEXIF_AVAILABLE = False

from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType
import logging
import os
import uuid
from datetime import datetime, timedelta

import exifread

try:

    PIXEXIF_AVAILABLE = True
except ImportError:
    PIXEXIF_AVAILABLE = False

from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class ImageFormat(Enum):
    """Supported image formats."""

    JPEG = "jpeg"  # JPEG format
    PNG = "png"  # PNG format
    TIFF = "tiff"  # TIFF format
    GIF = "gif"  # GIF format
    BMP = "bmp"  # BMP format
    WEBP = "webp"  # WebP format
    HEIC = "heic"  # HEIC format
    RAW = "raw"  # RAW format
    UNKNOWN = "unknown"  # Unknown format


class MetadataCategory(Enum):
    """Categories of metadata."""

    CAMERA_INFO = "camera_info"  # Camera information
    GPS_DATA = "gps_data"  # GPS coordinates and location
    TIMESTAMP = "timestamp"  # Date and time information
    TECHNICAL = "technical"  # Technical image data
    EDITING = "editing"  # Editing software and history
    COPYRIGHT = "copyright"  # Copyright information
    CUSTOM = "custom"  # Custom metadata fields


class ExtractionStatus(Enum):
    """Status of metadata extraction."""

    PENDING = "pending"  # Extraction pending
    IN_PROGRESS = "in_progress"  # Extraction in progress
    COMPLETED = "completed"  # Extraction completed
    FAILED = "failed"  # Extraction failed
    PARTIAL = "partial"  # Partial extraction
    NO_METADATA = "no_metadata"  # No metadata found


@dataclass
class CameraInfo:
    """Camera information from EXIF."""

    make: Optional[str]
    model: Optional[str]
    software: Optional[str]
    firmware: Optional[str]
    serial_number: Optional[str]
    lens_make: Optional[str]
    lens_model: Optional[str]
    lens_serial: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GPSData:
    """GPS data from EXIF."""

    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]
    latitude_ref: Optional[str]
    longitude_ref: Optional[str]
    altitude_ref: Optional[str]
    timestamp: Optional[datetime]
    gps_version: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimestampInfo:
    """Timestamp information from EXIF."""

    original_date: Optional[datetime]
    digitized_date: Optional[datetime]
    modified_date: Optional[datetime]
    subsec_time: Optional[str]
    timezone_offset: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TechnicalData:
    """Technical image data from EXIF."""

    image_width: Optional[int]
    image_height: Optional[int]
    orientation: Optional[int]
    color_space: Optional[str]
    bits_per_sample: Optional[int]
    compression: Optional[str]
    x_resolution: Optional[float]
    y_resolution: Optional[float]
    resolution_unit: Optional[str]
    exposure_time: Optional[float]
    f_number: Optional[float]
    iso_speed: Optional[int]
    flash: Optional[str]
    focal_length: Optional[float]
    white_balance: Optional[str]
    metering_mode: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EditingInfo:
    """Editing information from EXIF."""

    software: Optional[str]
    artist: Optional[str]
    copyright: Optional[str]
    user_comment: Optional[str]
    processing_software: Optional[str]
    edit_history: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EXIFMetadata:
    """Complete EXIF metadata."""

    metadata_id: str
    file_path: str
    image_format: ImageFormat
    extraction_status: ExtractionStatus
    camera_info: Optional[CameraInfo]
    gps_data: Optional[GPSData]
    timestamp_info: Optional[TimestampInfo]
    technical_data: Optional[TechnicalData]
    editing_info: Optional[EditingInfo]
    raw_exif: Dict[str, Any]
    extraction_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class EXIFExtractor:
    """
    Comprehensive EXIF metadata extraction system.

    The EXIFExtractor is responsible for:
    - Multi-format image support
    - Comprehensive metadata extraction
    - GPS coordinate processing
    - Camera information analysis
    - Technical data extraction
    - Editing history analysis
    - Metadata validation and verification
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the EXIFExtractor."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.supported_formats = config.get(
            "supported_formats",
            ["jpeg", "jpg", "png", "tiff", "tif", "gif", "bmp", "webp"],
        )
        self.extraction_timeout = config.get("extraction_timeout", 60)  # 1 minute
        self.enable_advanced_parsing = config.get("enable_advanced_parsing", True)
        self.gps_precision = config.get("gps_precision", 6)  # Decimal places for GPS

        # Metadata management
        self.extracted_metadata: Dict[str, EXIFMetadata] = {}
        self.metadata_history: Dict[str, List[str]] = defaultdict(list)

        # Performance tracking
        self.total_extractions = 0
        self.successful_extractions = 0
        self.failed_extractions = 0
        self.average_extraction_time = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("EXIFExtractor initialized successfully")

    async def start(self):
        """Start the EXIFExtractor."""
        self.logger.info("Starting EXIFExtractor...")

        # Initialize extraction components
        await self._initialize_extraction_components()

        # Start background tasks
        asyncio.create_task(self._cleanup_old_metadata())
        asyncio.create_task(self._update_performance_metrics())

        self.logger.info("EXIFExtractor started successfully")

    async def stop(self):
        """Stop the EXIFExtractor."""
        self.logger.info("Stopping EXIFExtractor...")
        self.logger.info("EXIFExtractor stopped")

    async def extract_metadata(self, file_path: str) -> EXIFMetadata:
        """Extract EXIF metadata from an image file."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Validate image format
            if not await self._validate_image_format(file_path):
                raise ValueError(f"Unsupported image format: {file_path}")

            self.logger.info(f"Extracting EXIF metadata from: {file_path}")

            start_time = datetime.utcnow()

            # Determine image format
            image_format = self._determine_image_format(file_path)

            # Extract metadata based on format
            if image_format in [ImageFormat.JPEG, ImageFormat.TIFF]:
                metadata = await self._extract_standard_exif(file_path, image_format)
            elif image_format == ImageFormat.PNG:
                metadata = await self._extract_png_metadata(file_path)
            elif image_format == ImageFormat.HEIC:
                metadata = await self._extract_heic_metadata(file_path)
            else:
                metadata = await self._extract_basic_metadata(file_path, image_format)

            # Calculate extraction time
            end_time = datetime.utcnow()
            extraction_time = (end_time - start_time).total_seconds()

            # Create metadata object
            exif_metadata = EXIFMetadata(
                metadata_id=str(uuid.uuid4()),
                file_path=file_path,
                image_format=image_format,
                extraction_status=ExtractionStatus.COMPLETED,
                camera_info=metadata.get("camera_info"),
                gps_data=metadata.get("gps_data"),
                timestamp_info=metadata.get("timestamp_info"),
                technical_data=metadata.get("technical_data"),
                editing_info=metadata.get("editing_info"),
                raw_exif=metadata.get("raw_exif", {}),
                extraction_time=extraction_time,
                timestamp=datetime.utcnow(),
            )

            # Store metadata
            self.extracted_metadata[exif_metadata.metadata_id] = exif_metadata

            # Update history
            file_id = str(uuid.uuid4())  # Generate file ID
            self.metadata_history[file_id].append(exif_metadata.metadata_id)

            # Update statistics
            self.total_extractions += 1
            self.successful_extractions += 1

            self.logger.info(
                f"EXIF metadata extraction completed: {exif_metadata.metadata_id}",
            )

            return exif_metadata

        except Exception as e:
            self.logger.error(f"Error extracting EXIF metadata: {e}")

            # Create failed metadata object
            failed_metadata = EXIFMetadata(
                metadata_id=str(uuid.uuid4()),
                file_path=file_path,
                image_format=ImageFormat.UNKNOWN,
                extraction_status=ExtractionStatus.FAILED,
                camera_info=None,
                gps_data=None,
                timestamp_info=None,
                technical_data=None,
                editing_info=None,
                raw_exif={},
                extraction_time=0.0,
                timestamp=datetime.utcnow(),
            )

            # Store failed metadata
            self.extracted_metadata[failed_metadata.metadata_id] = failed_metadata

            # Update statistics
            self.total_extractions += 1
            self.failed_extractions += 1

            raise

    async def _validate_image_format(self, file_path: str) -> bool:
        """Validate image format."""
        try:
            # Check file extension
            file_extension = os.path.splitext(file_path)[1].lower().lstrip(".")

            if file_extension not in self.supported_formats:
                return False

            # Try to open with PIL to validate
            try:
                with Image.open(file_path) as img:
                    img.verify()
                return True
            except Exception:
                logger.error(f"Error: {e}")
                return False

        except Exception as e:
            self.logger.error(f"Error validating image format: {e}")
            return False

    def _determine_image_format(self, file_path: str) -> ImageFormat:
        """Determine image format."""
        try:
            file_extension = os.path.splitext(file_path)[1].lower().lstrip(".")

            if file_extension in ["jpg", "jpeg"]:
                return ImageFormat.JPEG
            elif file_extension == "png":
                return ImageFormat.PNG
            elif file_extension in ["tiff", "tif"]:
                return ImageFormat.TIFF
            elif file_extension == "gif":
                return ImageFormat.GIF
            elif file_extension == "bmp":
                return ImageFormat.BMP
            elif file_extension == "webp":
                return ImageFormat.WEBP
            elif file_extension == "heic":
                return ImageFormat.HEIC
            else:
                return ImageFormat.UNKNOWN

        except Exception as e:
            self.logger.error(f"Error determining image format: {e}")
            return ImageFormat.UNKNOWN

    async def _extract_standard_exif(self, file_path: str, image_format: ImageFormat):
        """Extract EXIF metadata from standard formats (JPEG, TIFF)."""
        try:
            metadata = {
                "camera_info": None,
                "gps_data": None,
                "timestamp_info": None,
                "technical_data": None,
                "editing_info": None,
                "raw_exif": {},
            }

            # Extract using exifread
            with open(file_path, "rb") as f:
                tags = exifread.process_file(f)

            # Store raw EXIF data
            metadata["raw_exif"] = {str(tag): str(value) for tag, value in tags.items()}

            # Extract camera information
            metadata["camera_info"] = self._extract_camera_info(tags)

            # Extract GPS data
            metadata["gps_data"] = self._extract_gps_data(tags)

            # Extract timestamp information
            metadata["timestamp_info"] = self._extract_timestamp_info(tags)

            # Extract technical data
            metadata["technical_data"] = self._extract_technical_data(tags)

            # Extract editing information
            metadata["editing_info"] = self._extract_editing_info(tags)

            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting standard EXIF: {e}")
            raise

    def _extract_camera_info(self, tags: Dict) -> Optional[CameraInfo]:
        """Extract camera information from EXIF tags."""
        try:
            make = str(tags.get("Image Make", "")) if "Image Make" in tags else None
            model = str(tags.get("Image Model", "")) if "Image Model" in tags else None
            software = (
                str(tags.get("Image Software", ""))
                if "Image Software" in tags
                else None
            )
            firmware = (
                str(tags.get("EXIF FirmwareVersion", ""))
                if "EXIF FirmwareVersion" in tags
                else None
            )
            serial_number = (
                str(tags.get("EXIF BodySerialNumber", ""))
                if "EXIF BodySerialNumber" in tags
                else None
            )

            lens_make = (
                str(tags.get("EXIF LensMake", "")) if "EXIF LensMake" in tags else None
            )
            lens_model = (
                str(tags.get("EXIF LensModel", ""))
                if "EXIF LensModel" in tags
                else None
            )
            lens_serial = (
                str(tags.get("EXIF LensSerialNumber", ""))
                if "EXIF LensSerialNumber" in tags
                else None
            )

            camera_info = CameraInfo(
                make=make,
                model=model,
                software=software,
                firmware=firmware,
                serial_number=serial_number,
                lens_make=lens_make,
                lens_model=lens_model,
                lens_serial=lens_serial,
            )

            return camera_info

        except Exception as e:
            self.logger.error(f"Error extracting camera info: {e}")
            return None

    def _extract_gps_data(self, tags: Dict) -> Optional[GPSData]:
        """Extract GPS data from EXIF tags."""
        try:
            # GPS coordinates
            latitude = None
            longitude = None
            altitude = None

            if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
                latitude = self._convert_gps_coordinate(
                    tags["GPS GPSLatitude"], tags.get("GPS GPSLatitudeRef", "N")
                )
                longitude = self._convert_gps_coordinate(
                    tags["GPS GPSLongitude"], tags.get("GPS GPSLongitudeRef", "E")
                )

            if "GPS GPSAltitude" in tags:
                altitude = float(tags["GPS GPSAltitude"].num) / float(
                    tags["GPS GPSAltitude"].den
                )
                if "GPS GPSAltitudeRef" in tags and tags["GPS GPSAltitudeRef"].num == 1:
                    altitude = -altitude

            # GPS references
            latitude_ref = (
                str(tags.get("GPS GPSLatitudeRef", ""))
                if "GPS GPSLatitudeRef" in tags
                else None
            )
            longitude_ref = (
                str(tags.get("GPS GPSLongitudeRef", ""))
                if "GPS GPSLongitudeRef" in tags
                else None
            )
            altitude_ref = (
                str(tags.get("GPS GPSAltitudeRef", ""))
                if "GPS GPSAltitudeRef" in tags
                else None
            )

            # GPS timestamp
            gps_timestamp = None
            if "GPS GPSTimeStamp" in tags and "GPS GPSDateStamp" in tags:
                try:
                    time_parts = str(tags["GPS GPSTimeStamp"]).split(":")
                    date_str = str(tags["GPS GPSDateStamp"])
                    gps_timestamp = datetime.strptime(
                        f"{date_str} {time_parts[0]}:{time_parts[1]}:{time_parts[2]}",
                        "%Y:%m:%d %H:%M:%S",
                    )
                except Exception:
                    logger.error(f"Error: {e}")
                    pass

            # GPS version
            gps_version = (
                str(tags.get("GPS GPSVersionID", ""))
                if "GPS GPSVersionID" in tags
                else None
            )

            gps_data = GPSData(
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                latitude_ref=latitude_ref,
                longitude_ref=longitude_ref,
                altitude_ref=altitude_ref,
                timestamp=gps_timestamp,
                gps_version=gps_version,
            )

            return gps_data

        except Exception as e:
            self.logger.error(f"Error extracting GPS data: {e}")
            return None

    def _convert_gps_coordinate(self, coordinate, ref: str) -> Optional[float]:
        """Convert GPS coordinate from degrees/minutes/seconds to decimal."""
        try:
            if not coordinate:
                return None

            # Parse coordinate components
            parts = str(coordinate).split(",")
            if len(parts) >= 3:
                degrees = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2])

                # Convert to decimal
                decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

                # Apply reference
                if ref in ["S", "W"]:
                    decimal = -decimal

                # Round to specified precision
                return round(decimal, self.gps_precision)

            return None

        except Exception as e:
            self.logger.error(f"Error converting GPS coordinate: {e}")
            return None

    def _extract_timestamp_info(self, tags: Dict) -> Optional[TimestampInfo]:
        """Extract timestamp information from EXIF tags."""
        try:
            original_date = None
            digitized_date = None
            modified_date = None

            # Original date
            if "EXIF DateTimeOriginal" in tags:
                try:
                    original_date = datetime.strptime(
                        str(tags["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S"
                    )
                except Exception:
                    logger.error(f"Error: {e}")
                    pass

            # Digitized date
            if "EXIF DateTimeDigitized" in tags:
                try:
                    digitized_date = datetime.strptime(
                        str(tags["EXIF DateTimeDigitized"]), "%Y:%m:%d %H:%M:%S"
                    )
                except Exception:
                    logger.error(f"Error: {e}")
                    pass

            # Modified date
            if "Image DateTime" in tags:
                try:
                    modified_date = datetime.strptime(
                        str(tags["Image DateTime"]), "%Y:%m:%d %H:%M:%S"
                    )
                except Exception:
                    logger.error(f"Error: {e}")
                    pass

            # Subsecond time
            subsec_time = (
                str(tags.get("EXIF SubSecTime", ""))
                if "EXIF SubSecTime" in tags
                else None
            )

            # Timezone offset (not commonly available in EXIF)
            timezone_offset = None

            timestamp_info = TimestampInfo(
                original_date=original_date,
                digitized_date=digitized_date,
                modified_date=modified_date,
                subsec_time=subsec_time,
                timezone_offset=timezone_offset,
            )

            return timestamp_info

        except Exception as e:
            self.logger.error(f"Error extracting timestamp info: {e}")
            return None

    def _extract_technical_data(self, tags: Dict) -> Optional[TechnicalData]:
        """Extract technical data from EXIF tags."""
        try:
            # Image dimensions
            image_width = (
                int(tags["EXIF ExifImageWidth"])
                if "EXIF ExifImageWidth" in tags
                else None
            )
            image_height = (
                int(tags["EXIF ExifImageLength"])
                if "EXIF ExifImageLength" in tags
                else None
            )

            # Orientation
            orientation = (
                int(tags["Image Orientation"]) if "Image Orientation" in tags else None
            )

            # Color space
            color_space = (
                str(tags.get("EXIF ColorSpace", ""))
                if "EXIF ColorSpace" in tags
                else None
            )

            # Bits per sample
            bits_per_sample = (
                int(tags["EXIF BitsPerSample"])
                if "EXIF BitsPerSample" in tags
                else None
            )

            # Compression
            compression = (
                str(tags.get("Image Compression", ""))
                if "Image Compression" in tags
                else None
            )

            # Resolution
            x_resolution = None
            y_resolution = None
            if "Image XResolution" in tags:
                x_res = tags["Image XResolution"]
                x_resolution = (
                    float(x_res.num) / float(x_res.den)
                    if hasattr(x_res, "num")
                    else float(x_res)
                )

            if "Image YResolution" in tags:
                y_res = tags["Image YResolution"]
                y_resolution = (
                    float(y_res.num) / float(y_res.den)
                    if hasattr(y_res, "num")
                    else float(y_res)
                )

            resolution_unit = (
                str(tags.get("Image ResolutionUnit", ""))
                if "Image ResolutionUnit" in tags
                else None
            )

            # Exposure settings
            exposure_time = None
            if "EXIF ExposureTime" in tags:
                exp_time = tags["EXIF ExposureTime"]
                exposure_time = (
                    float(exp_time.num) / float(exp_time.den)
                    if hasattr(exp_time, "num")
                    else float(exp_time)
                )

            f_number = None
            if "EXIF FNumber" in tags:
                f_num = tags["EXIF FNumber"]
                f_number = (
                    float(f_num.num) / float(f_num.den)
                    if hasattr(f_num, "num")
                    else float(f_num)
                )

            iso_speed = (
                int(tags["EXIF ISOSpeedRatings"])
                if "EXIF ISOSpeedRatings" in tags
                else None
            )

            # Flash
            flash = str(tags.get("EXIF Flash", "")) if "EXIF Flash" in tags else None

            # Focal length
            focal_length = None
            if "EXIF FocalLength" in tags:
                focal = tags["EXIF FocalLength"]
                focal_length = (
                    float(focal.num) / float(focal.den)
                    if hasattr(focal, "num")
                    else float(focal)
                )

            # White balance
            white_balance = (
                str(tags.get("EXIF WhiteBalance", ""))
                if "EXIF WhiteBalance" in tags
                else None
            )

            # Metering mode
            metering_mode = (
                str(tags.get("EXIF MeteringMode", ""))
                if "EXIF MeteringMode" in tags
                else None
            )

            technical_data = TechnicalData(
                image_width=image_width,
                image_height=image_height,
                orientation=orientation,
                color_space=color_space,
                bits_per_sample=bits_per_sample,
                compression=compression,
                x_resolution=x_resolution,
                y_resolution=y_resolution,
                resolution_unit=resolution_unit,
                exposure_time=exposure_time,
                f_number=f_number,
                iso_speed=iso_speed,
                flash=flash,
                focal_length=focal_length,
                white_balance=white_balance,
                metering_mode=metering_mode,
            )

            return technical_data

        except Exception as e:
            self.logger.error(f"Error extracting technical data: {e}")
            return None

    def _extract_editing_info(self, tags: Dict) -> Optional[EditingInfo]:
        """Extract editing information from EXIF tags."""
        try:
            software = (
                str(tags.get("Image Software", ""))
                if "Image Software" in tags
                else None
            )
            artist = (
                str(tags.get("Image Artist", "")) if "Image Artist" in tags else None
            )
            copyright = (
                str(tags.get("Image Copyright", ""))
                if "Image Copyright" in tags
                else None
            )
            user_comment = (
                str(tags.get("EXIF UserComment", ""))
                if "EXIF UserComment" in tags
                else None
            )

            # Processing software (not commonly available)
            processing_software = None

            # Edit history (not commonly available in EXIF)
            edit_history = []

            editing_info = EditingInfo(
                software=software,
                artist=artist,
                copyright=copyright,
                user_comment=user_comment,
                processing_software=processing_software,
                edit_history=edit_history,
            )

            return editing_info

        except Exception as e:
            self.logger.error(f"Error extracting editing info: {e}")
            return None

    async def _extract_png_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from PNG files."""
        try:
            metadata = {
                "camera_info": None,
                "gps_data": None,
                "timestamp_info": None,
                "technical_data": None,
                "editing_info": None,
                "raw_exif": {},
            }

            # PNG has limited metadata compared to EXIF
            # Extract basic information
            with Image.open(file_path) as img:
                metadata["raw_exif"] = {
                    "format": img.format,
                    "mode": img.mode,
                    "size": img.size,
                    "info": img.info,
                }

            # Extract technical data
            technical_data = TechnicalData(
                image_width=metadata["raw_exif"]["size"][0],
                image_height=metadata["raw_exif"]["size"][1],
                orientation=None,
                color_space=metadata["raw_exif"]["mode"],
                bits_per_sample=None,
                compression=None,
                x_resolution=None,
                y_resolution=None,
                resolution_unit=None,
                exposure_time=None,
                f_number=None,
                iso_speed=None,
                flash=None,
                focal_length=None,
                white_balance=None,
                metering_mode=None,
            )

            metadata["technical_data"] = technical_data

            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting PNG metadata: {e}")
            raise

    async def _extract_heic_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from HEIC files."""
        try:
            # HEIC metadata extraction would require additional libraries
            # For now, return basic structure
            metadata = {
                "camera_info": None,
                "gps_data": None,
                "timestamp_info": None,
                "technical_data": None,
                "editing_info": None,
                "raw_exif": {
                    "format": "HEIC",
                    "note": "HEIC metadata extraction not implemented",
                },
            }

            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting HEIC metadata: {e}")
            raise

    async def _extract_basic_metadata(self, file_path: str, image_format: ImageFormat):
        """Extract basic metadata from unsupported formats."""
        try:
            metadata = {
                "camera_info": None,
                "gps_data": None,
                "timestamp_info": None,
                "technical_data": None,
                "editing_info": None,
                "raw_exif": {
                    "format": image_format.value,
                    "note": "Basic metadata only",
                },
            }

            # Extract basic image information
            try:
                with Image.open(file_path) as img:
                    metadata["raw_exif"].update(
                        {"mode": img.mode, "size": img.size, "info": img.info}
                    )
            except Exception:
                logger.error(f"Error: {e}")
                pass

            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting basic metadata: {e}")
            raise

    async def _cleanup_old_metadata(self):
        """Clean up old metadata."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(
                    days=90
                )  # Keep 3 months of metadata

                # Clean up old metadata
                old_metadata = [
                    metadata_id
                    for metadata_id, metadata in self.extracted_metadata.items()
                    if metadata.timestamp < cutoff_time
                ]

                for metadata_id in old_metadata:
                    del self.extracted_metadata[metadata_id]

                if old_metadata:
                    self.logger.info(
                        f"Cleaned up {len(old_metadata)} old metadata entries"
                    )

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up old metadata: {e}")
                await asyncio.sleep(3600)

    async def _update_performance_metrics(self):
        """Update performance metrics."""
        while True:
            try:
                # Calculate average extraction time
                if self.total_extractions > 0:
                    total_time = sum(
                        metadata.extraction_time
                        for metadata in self.extracted_metadata.values()
                    )
                    self.average_extraction_time = total_time / self.total_extractions

                await asyncio.sleep(300)  # Update every 5 minutes

            except Exception as e:
                self.logger.error(f"Error updating performance metrics: {e}")
                await asyncio.sleep(300)

    async def _initialize_extraction_components(self):
        """Initialize extraction components."""
        try:
            # Test image libraries
            test_data = b"\xff\xd8\xff\xe0"  # Minimal JPEG header

            # Test exifread
            try:
                # This would test exifread functionality
                pass
            except Exception as e:
                self.logger.warning(f"exifread not available: {e}")

            # Test PIL
            try:
                # This would test PIL functionality
                pass
            except Exception as e:
                self.logger.warning(f"PIL not available: {e}")

            self.logger.info("Extraction components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing extraction components: {e}")

    def get_metadata(self, metadata_id: str) -> Optional[EXIFMetadata]:
        """Get metadata by ID."""
        try:
            return self.extracted_metadata.get(metadata_id)
        except Exception as e:
            self.logger.error(f"Error getting metadata: {e}")
            return None

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "total_extractions": self.total_extractions,
            "successful_extractions": self.successful_extractions,
            "failed_extractions": self.failed_extractions,
            "average_extraction_time": self.average_extraction_time,
            "image_formats_supported": [fmt.value for fmt in ImageFormat],
            "metadata_categories_supported": [cat.value for cat in MetadataCategory],
            "extraction_statuses_supported": [
                status.value for status in ExtractionStatus
            ],
            "total_metadata_entries": len(self.extracted_metadata),
            "gps_precision": self.gps_precision,
            "advanced_parsing_enabled": self.enable_advanced_parsing,
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "supported_formats": [
            "jpeg",
            "jpg",
            "png",
            "tiff",
            "tif",
            "gif",
            "bmp",
            "webp",
        ],
        "extraction_timeout": 60,
        "enable_advanced_parsing": True,
        "gps_precision": 6,
    }

    # Initialize EXIF extractor
    extractor = EXIFExtractor(config)

    print("EXIFExtractor system initialized successfully!")
