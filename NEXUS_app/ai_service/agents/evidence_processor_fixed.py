#!/usr/bin/env python3
"""
Fixed Evidence Agent Processing Pipeline
Priority: NORMAL | Duration: 16-20 hours
"""

import hashlib
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FileMetadata:
    """File metadata information"""

    file_path: str
    file_name: str
    file_size: int
    file_type: str
    hash_md5: str
    hash_sha256: str
    created_time: datetime
    modified_time: datetime
    accessed_time: datetime


@dataclass
class ProcessingResult:
    """Result of file processing"""

    file_path: str
    success: bool
    metadata: Optional[FileMetadata]
    extracted_data: Dict[str, Any]
    processing_time: float
    error_message: Optional[str]


class EvidenceProcessor:
    """Fixed evidence processing pipeline"""

    def __init__(self):
        """__init__ function."""
        self.processed_files: List[str] = []
        self.processing_stats = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "total_processing_time": 0.0,
        }

        logger.info("Evidence Processor initialized successfully")

    def process_file(self, file_path: str) -> ProcessingResult:
        """Process a single fileProcess a single file"""
        start_time = datetime.now()

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return ProcessingResult(
                    file_path=file_path,
                    success=False,
                    metadata=None,
                    extracted_data={},
                    processing_time=0.0,
                    error_message="File not found",
                )

            # Get file metadata
            metadata = self._extract_file_metadata(file_path)

            # Extract data based on file type
            extracted_data = self._extract_file_data(file_path, metadata.file_type)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Update stats
            self.processing_stats["total_files"] += 1
            self.processing_stats["successful"] += 1
            self.processing_stats["total_processing_time"] += processing_time

            # Add to processed files
            self.processed_files.append(file_path)

            return ProcessingResult(
                file_path=file_path,
                success=True,
                metadata=metadata,
                extracted_data=extracted_data,
                processing_time=processing_time,
                error_message=None,
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self.processing_stats["total_files"] += 1
            self.processing_stats["failed"] += 1

            logger.error(f"Error processing file {file_path}: {e}")

            return ProcessingResult(
                file_path=file_path,
                success=False,
                metadata=None,
                extracted_data={},
                processing_time=processing_time,
                error_message=str(e),
            )

    def _extract_file_metadata(self, file_path: str) -> FileMetadata:
        """Extract basic file metadataExtract basic file metadata"""
        stat = os.stat(file_path)

        # Calculate hashes
        md5_hash = hashlib.md5()
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
                sha256_hash.update(chunk)

        return FileMetadata(
            file_path=file_path,
            file_name=os.path.basename(file_path),
            file_size=stat.st_size,
            file_type=self._get_file_type(file_path),
            hash_md5=md5_hash.hexdigest(),
            hash_sha256=sha256_hash.hexdigest(),
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            accessed_time=datetime.fromtimestamp(stat.st_atime),
        )

    def _get_file_type(self, file_path: str) -> str:
        """Determine file type based on extensionDetermine file type based on extension"""
        ext = Path(file_path).suffix.lower()

        if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
            return "image"
        elif ext in [".pdf"]:
            return "pdf"
        elif ext in [".txt", ".log"]:
            return "text"
        elif ext in [".doc", ".docx"]:
            return "document"
        elif ext in [".xls", ".xlsx"]:
            return "spreadsheet"
        elif ext in [".zip", ".rar", ".7z"]:
            return "archive"
        else:
            return "unknown"

    def _extract_file_data(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Extract data based on file typeExtract data based on file type"""
        extracted_data = {
            "file_type": file_type,
            "extraction_method": "basic",
            "extracted_at": datetime.now().isoformat(),
        }

        try:
            if file_type == "text":
                extracted_data.update(self._extract_text_data(file_path))
            elif file_type == "image":
                extracted_data.update(self._extract_image_data(file_path))
            elif file_type == "pdf":
                extracted_data.update(self._extract_pdf_data(file_path))
            else:
                extracted_data["extraction_method"] = "metadata_only"

        except Exception as e:
            extracted_data["extraction_error"] = str(e)
            extracted_data["extraction_method"] = "error"

        return extracted_data

    def _extract_text_data(self, file_path: str) -> Dict[str, Any]:
        """Extract data from text filesExtract data from text files"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            return {
                "content_length": len(content),
                "line_count": len(content.splitlines()),
                "word_count": len(content.split()),
                "sample_content": (
                    content[:500] + "..." if len(content) > 500 else content
                ),
            }
        except Exception as e:
            return {"text_extraction_error": str(e)}

    def _extract_image_data(self, file_path: str) -> Dict[str, Any]:
        """Extract data from image filesExtract data from image files"""
        try:
            # Basic image info (without PIL dependency)
            return {
                "image_processing": "basic_metadata_only",
                "note": "Full image processing requires PIL/Pillow library",
            }
        except Exception as e:
            return {"image_extraction_error": str(e)}

    def _extract_pdf_data(self, file_path: str) -> Dict[str, Any]:
        """Extract data from PDF filesExtract data from PDF files"""
        try:
            # Basic PDF info (without PyPDF2 dependency)
            return {
                "pdf_processing": "basic_metadata_only",
                "note": "Full PDF processing requires PyPDF2 or similar library",
            }
        except Exception as e:
            return {"pdf_extraction_error": str(e)}

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statisticsGet processing statistics"""
        avg_time = 0.0
        if self.processing_stats["successful"] > 0:
            avg_time = (
                self.processing_stats["total_processing_time"]
                / self.processing_stats["successful"]
            )

        return {
            "total_files": self.processing_stats["total_files"],
            "successful": self.processing_stats["successful"],
            "failed": self.processing_stats["failed"],
            "success_rate": self.processing_stats["successful"]
            / max(self.processing_stats["total_files"], 1),
            "average_processing_time": avg_time,
            "total_processing_time": self.processing_stats["total_processing_time"],
            "processed_files": len(self.processed_files),
        }

    def export_processing_report(self) -> Dict[str, Any]:
        """Export comprehensive processing reportExport comprehensive processing report"""
        return {
            "report_generated": datetime.now().isoformat(),
            "processor_version": "1.0.0",
            "processing_stats": self.get_processing_stats(),
            "processed_files": self.processed_files,
            "system_info": {"platform": os.name, "current_directory": os.getcwd()},
        }


def main():
    """Test the evidence processorTest the evidence processor"""
    print("🧪 Testing Fixed Evidence Agent Processing Pipeline")
    print("=" * 60)

    # Create processor
    processor = EvidenceProcessor()

    # Test with a sample file (create one if needed)
    test_file = "test_sample.txt"

    # Create a test file
    with open(test_file, "w") as f:
        f.write("This is a test file for evidence processing.\n")
        f.write("It contains multiple lines of text.\n")
        f.write("This will be processed by the evidence agent.\n")

    print(f"📁 Created test file: {test_file}")

    # Process the file
    print("\n🔍 Processing file...")
    result = processor.process_file(test_file)

    if result.success:
        print("✅ File processed successfully!")
        print(f"📊 File size: {result.metadata.file_size} bytes")
        print(f"🔐 MD5 Hash: {result.metadata.hash_md5}")
        print(f"⏱️  Processing time: {result.processing_time:.3f} seconds")

        print("\n📋 Extracted Data:")
        for key, value in result.extracted_data.items():
            print(f"  {key}: {value}")
    else:
        print(f"❌ File processing failed: {result.error_message}")

    # Get processing stats
    print("\n📈 Processing Statistics:")
    stats = processor.get_processing_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Export report
    print("\n📤 Exporting processing report...")
    report = processor.export_processing_report()
    print(f"  Report generated: {report['report_generated']}")
    print(f"  Total files processed: {report['processing_stats']['total_files']}")

    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\n🧹 Cleaned up test file: {test_file}")

    print("\n✅ Evidence Agent test completed!")


if __name__ == "__main__":
    main()
