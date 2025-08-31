#!/usr/bin/env python3
"""
Hash Verifier - Comprehensive Hash Verification and Integrity Checking

This module implements the HashVerifier class that provides
comprehensive hash verification capabilities for the Evidence Agent
in the forensic platform.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from ..taskmaster.models.job import Job, JobPriority, JobStatus, JobType


class HashAlgorithm(Enum):
    """Supported hash algorithms."""

    MD5 = "md5"  # MD5 hash (128-bit)
    SHA1 = "sha1"  # SHA-1 hash (160-bit)
    SHA256 = "sha256"  # SHA-256 hash (256-bit)
    SHA512 = "sha512"  # SHA-512 hash (512-bit)
    SHA3_256 = "sha3_256"  # SHA3-256 hash (256-bit)
    SHA3_512 = "sha3_512"  # SHA3-512 hash (512-bit)
    BLAKE2B = "blake2b"  # BLAKE2b hash (variable)
    BLAKE2S = "blake2s"  # BLAKE2s hash (variable)
    RIPEMD160 = "ripemd160"  # RIPEMD-160 hash (160-bit)


class VerificationStatus(Enum):
    """Status of hash verification."""

    PENDING = "pending"  # Verification pending
    IN_PROGRESS = "in_progress"  # Verification in progress
    VERIFIED = "verified"  # Hash verified successfully
    FAILED = "failed"  # Hash verification failed
    MISMATCH = "mismatch"  # Hash mismatch detected
    CORRUPTED = "corrupted"  # File appears corrupted
    UNKNOWN = "unknown"  # Verification status unknown


class IntegrityLevel(Enum):
    """Level of integrity verification."""

    BASIC = "basic"  # Basic hash verification
    ENHANCED = "enhanced"  # Enhanced verification with multiple algorithms
    COMPREHENSIVE = "comprehensive"  # Comprehensive verification with all algorithms
    FORENSIC = "forensic"  # Forensic-grade verification


@dataclass
class HashResult:
    """Result of hash calculation."""

    algorithm: HashAlgorithm
    hash_value: str
    hash_length: int
    calculation_time: float
    file_size: int
    chunk_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Result of hash verification."""

    verification_id: str
    file_id: str
    file_path: str
    expected_hashes: Dict[HashAlgorithm, str]
    calculated_hashes: Dict[HashAlgorithm, HashResult]
    verification_status: VerificationStatus
    integrity_level: IntegrityLevel
    verification_time: float
    timestamp: datetime
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HashDatabase:
    """Database of known hashes."""

    hash_id: str
    hash_value: str
    algorithm: HashAlgorithm
    file_info: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class HashVerifier:
    """
    Comprehensive hash verification system.

    The HashVerifier is responsible for:
    - Multiple hash algorithm support
    - File integrity verification
    - Hash database management
    - Forensic-grade verification
    - Performance optimization
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize the HashVerifier."""
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.default_algorithms = config.get(
            "default_algorithms",
            [HashAlgorithm.MD5, HashAlgorithm.SHA256, HashAlgorithm.SHA512],
        )
        self.chunk_size = config.get("chunk_size", 8192)  # 8KB chunks
        self.verification_timeout = config.get("verification_timeout", 300)  # 5 minutes
        self.enable_parallel_processing = config.get("enable_parallel_processing", True)

        # Hash management
        self.hash_database: Dict[str, HashDatabase] = {}
        self.verification_results: Dict[str, VerificationResult] = {}
        self.verification_history: Dict[str, List[str]] = defaultdict(list)

        # Performance tracking
        self.total_verifications = 0
        self.successful_verifications = 0
        self.failed_verifications = 0
        self.average_verification_time = 0.0

        # Event loop
        self.loop = asyncio.get_event_loop()

        self.logger.info("HashVerifier initialized successfully")

    async def start(self):
        """Start the HashVerifier."""
        self.logger.info("Starting HashVerifier...")

        # Initialize verification components
        await self._initialize_verification_components()

        # Start background tasks
        asyncio.create_task(self._cleanup_old_results())
        asyncio.create_task(self._update_performance_metrics())

        self.logger.info("HashVerifier started successfully")

    async def stop(self):
        """Stop the HashVerifier."""
        self.logger.info("Stopping HashVerifier...")
        self.logger.info("HashVerifier stopped")

    async def calculate_file_hashes(
        self, file_path: str, algorithms: List[HashAlgorithm] = None
    ):
        """Calculate hashes for a file using specified algorithms."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            if not algorithms:
                algorithms = self.default_algorithms

            self.logger.info(f"Calculating hashes for file: {file_path}")

            # Get file information
            file_size = os.path.getsize(file_path)

            # Calculate hashes
            hash_results = {}

            if self.enable_parallel_processing:
                # Parallel hash calculation
                tasks = []
                for algorithm in algorithms:
                    task = asyncio.create_task(
                        self._calculate_hash_parallel(file_path, algorithm, file_size)
                    )
                    tasks.append(task)

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self.logger.error(
                            f"Error calculating {algorithms[i].value} hash: {result}"
                        )
                    else:
                        hash_results[algorithms[i]] = result
            else:
                # Sequential hash calculation
                for algorithm in algorithms:
                    try:
                        hash_result = await self._calculate_hash_sequential(
                            file_path, algorithm, file_size
                        )
                        hash_results[algorithm] = hash_result
                    except Exception as e:
                        self.logger.error(
                            f"Error calculating {algorithm.value} hash: {e}"
                        )

            self.logger.info(
                f"Hash calculation completed for {len(hash_results)} algorithms"
            )

            return hash_results

        except Exception as e:
            self.logger.error(f"Error calculating file hashes: {e}")
            raise

    async def _calculate_hash_parallel(
        self, file_path: str, algorithm: HashAlgorithm, file_size: int
    ):
        """Calculate hash using parallel processing."""
        try:
            start_time = datetime.utcnow()

            # Initialize hash object
            hash_obj = hashlib.new(algorithm.value)

            # Calculate hash in chunks
            with open(file_path, "rb") as f:
                while chunk := f.read(self.chunk_size):
                    hash_obj.update(chunk)

            hash_value = hash_obj.hexdigest()

            end_time = datetime.utcnow()
            calculation_time = (end_time - start_time).total_seconds()

            hash_result = HashResult(
                algorithm=algorithm,
                hash_value=hash_value,
                hash_length=len(hash_value),
                calculation_time=calculation_time,
                file_size=file_size,
                chunk_size=self.chunk_size,
            )

            return hash_result

        except Exception as e:
            self.logger.error(f"Error in parallel hash calculation: {e}")
            raise

    async def _calculate_hash_sequential(
        self, file_path: str, algorithm: HashAlgorithm, file_size: int
    ) -> HashResult:
        """Calculate hash using sequential processing."""
        try:
            start_time = datetime.utcnow()

            # Initialize hash object
            hash_obj = hashlib.new(algorithm.value)

            # Calculate hash in chunks
            with open(file_path, "rb") as f:
                while chunk := f.read(self.chunk_size):
                    hash_obj.update(chunk)

            hash_value = hash_obj.hexdigest()

            end_time = datetime.utcnow()
            calculation_time = (end_time - start_time).total_seconds()

            hash_result = HashResult(
                algorithm=algorithm,
                hash_value=hash_value,
                hash_length=len(hash_value),
                calculation_time=calculation_time,
                file_size=file_size,
                chunk_size=self.chunk_size,
            )

            return hash_result

        except Exception as e:
            self.logger.error(f"Error in sequential hash calculation: {e}")
            raise

    async def verify_file_integrity(
        self,
        file_path: str,
        expected_hashes: Dict[HashAlgorithm, str],
        integrity_level: IntegrityLevel = IntegrityLevel.ENHANCED,
    ) -> VerificationResult:
        """Verify file integrity using expected hashes."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            self.logger.info(f"Verifying file integrity: {file_path}")

            # Generate verification ID
            verification_id = str(uuid.uuid4())

            # Calculate current hashes
            algorithms = list(expected_hashes.keys())
            calculated_hashes = await self.calculate_file_hashes(file_path, algorithms)

            # Verify hashes
            verification_status = VerificationStatus.VERIFIED
            errors = []
            warnings = []

            for algorithm, expected_hash in expected_hashes.items():
                if algorithm in calculated_hashes:
                    calculated_hash = calculated_hashes[algorithm]
                    if calculated_hash.hash_value.lower() != expected_hash.lower():
                        verification_status = VerificationStatus.MISMATCH
                        errors.append(
                            f"Hash mismatch for {algorithm.value}: expected {expected_hash}, got {calculated_hash.hash_value}"
                        )
                else:
                    verification_status = VerificationStatus.FAILED
                    errors.append(f"Could not calculate {algorithm.value} hash")

            # Check for corruption indicators
            if verification_status == VerificationStatus.VERIFIED:
                if await self._check_file_corruption(file_path):
                    verification_status = VerificationStatus.CORRUPTED
                    warnings.append("File corruption indicators detected")

            # Calculate verification time
            verification_time = sum(
                hash_result.calculation_time
                for hash_result in calculated_hashes.values()
            )

            # Create verification result
            verification_result = VerificationResult(
                verification_id=verification_id,
                file_id=str(uuid.uuid4()),  # Generate file ID
                file_path=file_path,
                expected_hashes=expected_hashes,
                calculated_hashes=calculated_hashes,
                verification_status=verification_status,
                integrity_level=integrity_level,
                verification_time=verification_time,
                timestamp=datetime.utcnow(),
                errors=errors,
                warnings=warnings,
            )

            # Store result
            self.verification_results[verification_id] = verification_result

            # Update history
            file_id = verification_result.file_id
            self.verification_history[file_id].append(verification_id)

            # Update statistics
            self.total_verifications += 1
            if verification_status == VerificationStatus.VERIFIED:
                self.successful_verifications += 1
            else:
                self.failed_verifications += 1

            self.logger.info(
                f"File integrity verification completed: {verification_id} - Status: {verification_status.value}",
            )

            return verification_result

        except Exception as e:
            self.logger.error(f"Error verifying file integrity: {e}")
            raise

    async def _check_file_corruption(self, file_path: str) -> bool:
        """Check for file corruption indicators."""
        try:
            # Basic corruption checks
            file_size = os.path.getsize(file_path)

            # Check if file size is reasonable
            if file_size == 0:
                return True  # Empty file might indicate corruption

            # Try to read the entire file
            try:
                with open(file_path, "rb") as f:
                    # Read in chunks to avoid memory issues
                    while f.read(self.chunk_size):
                        pass
            except Exception:
                logger.error(f"Error: {e}")
                return True  # Read error indicates corruption

            # Check file permissions
            if not os.access(file_path, os.R_OK):
                return True  # Cannot read file

            return False

        except Exception as e:
            self.logger.error(f"Error checking file corruption: {e}")
            return True  # Assume corrupted on error

    async def add_hash_to_database(
        self, hash_value: str, algorithm: HashAlgorithm, file_info: str, source: str
    ) -> str:
        """Add a hash to the database."""
        try:
            hash_id = str(uuid.uuid4())

            hash_database_entry = HashDatabase(
                hash_id=hash_id,
                hash_value=hash_value,
                algorithm=algorithm,
                file_info=file_info,
                source=source,
                timestamp=datetime.utcnow(),
            )

            # Store in database
            self.hash_database[hash_id] = hash_database_entry

            self.logger.info(f"Hash added to database: {hash_id} - {algorithm.value}")

            return hash_id

        except Exception as e:
            self.logger.error(f"Error adding hash to database: {e}")
            raise

    async def search_hash_database(
        self, hash_value: str, algorithm: HashAlgorithm = None
    ):
        """Search for a hash in the database."""
        try:
            results = []

            for hash_entry in self.hash_database.values():
                if hash_entry.hash_value.lower() == hash_value.lower():
                    if algorithm is None or hash_entry.algorithm == algorithm:
                        results.append(hash_entry)

            self.logger.info(f"Hash search completed: {len(results)} results found")

            return results

        except Exception as e:
            self.logger.error(f"Error searching hash database: {e}")
            return []

    async def verify_hash_against_database(
        self, file_path: str, algorithm: HashAlgorithm = None
    ) -> List[HashDatabase]:
        """Verify file hash against database."""
        try:
            # Calculate file hash
            algorithms = [algorithm] if algorithm else [HashAlgorithm.SHA256]
            calculated_hashes = await self.calculate_file_hashes(file_path, algorithms)

            # Search database for matches
            matches = []
            for calc_algorithm, hash_result in calculated_hashes.items():
                if algorithm is None or calc_algorithm == algorithm:
                    database_matches = await self.search_hash_database(
                        hash_result.hash_value, calc_algorithm
                    )
                    matches.extend(database_matches)

            self.logger.info(
                f"Database verification completed: {len(matches)} matches found"
            )

            return matches

        except Exception as e:
            self.logger.error(f"Error verifying hash against database: {e}")
            return []

    async def generate_hmac(
        self,
        file_path: str,
        secret_key: str,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    ):
        """Generate HMAC for a file."""
        try:
            # Generate HMAC
            with open(file_path, "rb") as f:
                file_content = f.read()

            hmac_obj = hmac.new(
                secret_key.encode(), file_content, hashlib.new(algorithm.value)
            )
            hmac_value = hmac_obj.hexdigest()

            self.logger.info(f"HMAC generated for file: {file_path}")

            return hmac_value

        except Exception as e:
            self.logger.error(f"Error generating HMAC: {e}")
            raise

    async def verify_hmac(
        self,
        file_path: str,
        expected_hmac: str,
        secret_key: str,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    ) -> bool:
        """Verify HMAC for a file."""
        try:
            # Generate current HMAC
            current_hmac = await self.generate_hmac(file_path, secret_key, algorithm)

            # Compare HMACs
            is_valid = hmac.compare_digest(current_hmac, expected_hmac)

            self.logger.info(f"HMAC verification completed: {is_valid}")

            return is_valid

        except Exception as e:
            self.logger.error(f"Error verifying HMAC: {e}")
            return False

    async def generate_checksum_file(
        self,
        directory_path: str,
        output_file: str,
        algorithms: List[HashAlgorithm] = None,
    ) -> str:
        """Generate checksum file for a directory."""
        try:
            if not algorithms:
                algorithms = self.default_algorithms

            checksum_data = {}

            # Process all files in directory
            for root, dirs, files in os.walk(directory_path):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, directory_path)

                    try:
                        # Calculate hashes for file
                        file_hashes = await self.calculate_file_hashes(
                            file_path, algorithms
                        )

                        # Store hash data
                        checksum_data[relative_path] = {
                            algorithm.value: hash_result.hash_value
                            for algorithm, hash_result in file_hashes.items()
                        }

                    except Exception as e:
                        self.logger.warning(f"Could not process file {file_path}: {e}")

            # Write checksum file
            with open(output_file, "w") as f:
                json.dump(checksum_data, f, indent=2)

            self.logger.info(f"Checksum file generated: {output_file}")

            return output_file

        except Exception as e:
            self.logger.error(f"Error generating checksum file: {e}")
            raise

    async def verify_checksum_file(self, checksum_file: str, directory_path: str):
        """Verify files against a checksum file."""
        try:
            # Read checksum file
            with open(checksum_file, "r") as f:
                checksum_data = json.load(f)

            verification_results = {}

            # Verify each file
            for relative_path, expected_hashes in checksum_data.items():
                file_path = os.path.join(directory_path, relative_path)

                if os.path.exists(file_path):
                    # Convert hash algorithms
                    algorithms = []
                    expected_hash_dict = {}

                    for alg_str, hash_value in expected_hashes.items():
                        try:
                            algorithm = HashAlgorithm(alg_str)
                            algorithms.append(algorithm)
                            expected_hash_dict[algorithm] = hash_value
                        except ValueError:
                            self.logger.warning(f"Unknown hash algorithm: {alg_str}")

                    if algorithms:
                        # Verify file
                        verification_result = await self.verify_file_integrity(
                            file_path, expected_hash_dict
                        )
                        verification_results[relative_path] = verification_result
                else:
                    self.logger.warning(f"File not found: {file_path}")

            self.logger.info(
                f"Checksum verification completed: {len(verification_results)} files verified"
            )

            return verification_results

        except Exception as e:
            self.logger.error(f"Error verifying checksum file: {e}")
            raise

    async def _cleanup_old_results(self):
        """Clean up old verification results."""
        while True:
            try:
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(
                    days=30
                )  # Keep 30 days of results

                # Clean up old results
                old_results = [
                    verification_id
                    for verification_id, result in self.verification_results.items()
                    if result.timestamp < cutoff_time
                ]

                for verification_id in old_results:
                    del self.verification_results[verification_id]

                if old_results:
                    self.logger.info(
                        f"Cleaned up {len(old_results)} old verification results"
                    )

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                self.logger.error(f"Error cleaning up old results: {e}")
                await asyncio.sleep(3600)

    async def _update_performance_metrics(self):
        """Update performance metrics."""
        while True:
            try:
                # Calculate average verification time
                if self.total_verifications > 0:
                    total_time = sum(
                        result.verification_time
                        for result in self.verification_results.values()
                    )
                    self.average_verification_time = (
                        total_time / self.total_verifications
                    )

                await asyncio.sleep(300)  # Update every 5 minutes

            except Exception as e:
                self.logger.error(f"Error updating performance metrics: {e}")
                await asyncio.sleep(300)

    async def _initialize_verification_components(self):
        """Initialize verification components."""
        try:
            # Initialize hash algorithms
            await self._initialize_hash_algorithms()

            self.logger.info("Verification components initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing verification components: {e}")

    async def _initialize_hash_algorithms(self):
        """Initialize hash algorithms."""
        try:
            # Test hash algorithms
            test_data = b"test"
            for algorithm in HashAlgorithm:
                try:
                    hash_obj = hashlib.new(algorithm.value)
                    hash_obj.update(test_data)
                    hash_obj.hexdigest()
                    self.logger.debug(
                        f"Hash algorithm {algorithm.value} initialized successfully",
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Hash algorithm {algorithm.value} not available: {e}",
                    )

            self.logger.info("Hash algorithms initialized")

        except Exception as e:
            self.logger.error(f"Error initializing hash algorithms: {e}")

    def get_verification_status(
        self, verification_id: str
    ) -> Optional[VerificationResult]:
        """Get verification status by ID."""
        try:
            return self.verification_results.get(verification_id)
        except Exception as e:
            self.logger.error(f"Error getting verification status: {e}")
            return None

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            "total_verifications": self.total_verifications,
            "successful_verifications": self.successful_verifications,
            "failed_verifications": self.failed_verifications,
            "average_verification_time": self.average_verification_time,
            "hash_algorithms_supported": [alg.value for alg in HashAlgorithm],
            "integrity_levels_supported": [level.value for level in IntegrityLevel],
            "verification_statuses_supported": [
                status.value for status in VerificationStatus
            ],
            "hash_database_size": len(self.hash_database),
            "verification_results_count": len(self.verification_results),
            "chunk_size": self.chunk_size,
            "parallel_processing_enabled": self.enable_parallel_processing,
        }


# Example usage and testing
if __name__ == "__main__":
    # Configuration
    config = {
        "default_algorithms": ["md5", "sha256", "sha512"],
        "chunk_size": 8192,
        "verification_timeout": 300,
        "enable_parallel_processing": True,
    }

    # Initialize hash verifier
    verifier = HashVerifier(config)

    print("HashVerifier system initialized successfully!")
