#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔄 Reconciliation Engine - Core logic for data reconciliation
"""

import asyncio
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import uuid
from dataclasses import dataclass
from difflib import SequenceMatcher
import json

from sqlalchemy.orm import Session
from database.models.reconciliation import (
    ReconciliationJob, ReconciliationDiscrepancy, HumanJudgment,
    ReconciliationStatus, EvidenceType
)
from models.reconciliation import ReconciliationResult, MatchingRule

logger = logging.getLogger(__name__)

@dataclass
class MatchResult:
    """Result of matching two records"""
    is_match: bool
    confidence: float
    differences: Dict[str, Any]
    matching_fields: List[str]

class ReconciliationEngine:
    """Core reconciliation engine for processing data discrepancies"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.matching_algorithms = {
            'exact': self._exact_match,
            'fuzzy': self._fuzzy_match,
            'numeric': self._numeric_match,
            'date': self._date_match,
            'custom': self._custom_match
        }
    
    async def process_reconciliation(
        self, 
        job_id: uuid.UUID, 
        source_data: List[Dict[str, Any]], 
        target_data: List[Dict[str, Any]],
        db: Session = None
    ):
        """Process reconciliation job"""
        try:
            logger.info(f"Starting reconciliation for job {job_id}")
            
            # Update job status
            if db:
                job = db.query(ReconciliationJob).filter(ReconciliationJob.id == job_id).first()
                if job:
                    job.status = ReconciliationStatus.IN_PROGRESS
                    job.started_at = datetime.utcnow()
                    job.total_records = len(source_data) + len(target_data)
                    db.commit()
            
            # Perform reconciliation
            result = await self._reconcile_data(source_data, target_data, job_id, db)
            
            # Update job with results
            if db and job:
                job.matched_records = result.matched_records
                job.unmatched_records = result.unmatched_records
                job.discrepancy_count = len(result.discrepancies)
                job.confidence_score = result.confidence_score
                job.status = ReconciliationStatus.COMPLETED if not result.requires_human_judgment else ReconciliationStatus.REQUIRES_HUMAN_JUDGMENT
                job.completed_at = datetime.utcnow()
                db.commit()
            
            logger.info(f"Reconciliation completed for job {job_id}")
            return result
            
        except Exception as e:
            logger.error(f"Reconciliation failed for job {job_id}: {str(e)}")
            if db:
                job = db.query(ReconciliationJob).filter(ReconciliationJob.id == job_id).first()
                if job:
                    job.status = ReconciliationStatus.FAILED
                    db.commit()
            raise
    
    async def _reconcile_data(
        self, 
        source_data: List[Dict[str, Any]], 
        target_data: List[Dict[str, Any]], 
        job_id: uuid.UUID,
        db: Session = None
    ) -> ReconciliationResult:
        """Reconcile source and target data"""
        
        matched_records = 0
        unmatched_records = 0
        discrepancies = []
        total_confidence = 0.0
        
        # Create lookup for target data
        target_lookup = {self._get_record_key(record): record for record in target_data}
        
        # Process source records
        for source_record in source_data:
            source_key = self._get_record_key(source_record)
            target_record = target_lookup.get(source_key)
            
            if target_record:
                # Records exist in both systems - check for differences
                match_result = await self._compare_records(source_record, target_record)
                
                if match_result.is_match:
                    matched_records += 1
                else:
                    # Create discrepancy
                    discrepancy = await self._create_discrepancy(
                        job_id, source_record, target_record, 
                        match_result, "mismatch", db
                    )
                    discrepancies.append(discrepancy)
                    unmatched_records += 1
                
                total_confidence += match_result.confidence
            else:
                # Record exists only in source
                discrepancy = await self._create_discrepancy(
                    job_id, source_record, None, 
                    None, "missing_in_target", db
                )
                discrepancies.append(discrepancy)
                unmatched_records += 1
        
        # Check for records that exist only in target
        source_keys = {self._get_record_key(record) for record in source_data}
        for target_record in target_data:
            target_key = self._get_record_key(target_record)
            if target_key not in source_keys:
                discrepancy = await self._create_discrepancy(
                    job_id, None, target_record, 
                    None, "missing_in_source", db
                )
                discrepancies.append(discrepancy)
                unmatched_records += 1
        
        # Calculate overall confidence
        total_records = len(source_data) + len(target_data)
        confidence_score = total_confidence / total_records if total_records > 0 else 0.0
        
        # Determine if human judgment is required
        requires_human_judgment = (
            len(discrepancies) > 0 and 
            confidence_score < 0.8  # Threshold for human review
        )
        
        return ReconciliationResult(
            job_id=job_id,
            total_records=total_records,
            matched_records=matched_records,
            unmatched_records=unmatched_records,
            discrepancies=discrepancies,
            confidence_score=confidence_score,
            processing_time=0.0,  # Would be calculated in real implementation
            requires_human_judgment=requires_human_judgment
        )
    
    async def _compare_records(
        self, 
        source_record: Dict[str, Any], 
        target_record: Dict[str, Any]
    ) -> MatchResult:
        """Compare two records and determine if they match"""
        
        differences = {}
        matching_fields = []
        total_confidence = 0.0
        field_count = 0
        
        # Get all unique field names
        all_fields = set(source_record.keys()) | set(target_record.keys())
        
        for field in all_fields:
            source_value = source_record.get(field)
            target_value = target_record.get(field)
            
            if source_value == target_value:
                matching_fields.append(field)
                total_confidence += 1.0
            else:
                differences[field] = {
                    'source': source_value,
                    'target': target_value,
                    'difference_type': self._get_difference_type(source_value, target_value)
                }
            
            field_count += 1
        
        confidence = total_confidence / field_count if field_count > 0 else 0.0
        is_match = confidence >= 0.95  # 95% threshold for exact match
        
        return MatchResult(
            is_match=is_match,
            confidence=confidence,
            differences=differences,
            matching_fields=matching_fields
        )
    
    async def _create_discrepancy(
        self, 
        job_id: uuid.UUID, 
        source_record: Optional[Dict[str, Any]], 
        target_record: Optional[Dict[str, Any]], 
        match_result: Optional[MatchResult],
        discrepancy_type: str,
        db: Session = None
    ) -> Dict[str, Any]:
        """Create a discrepancy record"""
        
        # Determine severity based on discrepancy type and confidence
        severity = self._determine_severity(discrepancy_type, match_result)
        
        # Create description
        description = self._create_discrepancy_description(
            discrepancy_type, source_record, target_record, match_result
        )
        
        discrepancy_data = {
            'job_id': job_id,
            'discrepancy_type': discrepancy_type,
            'severity': severity,
            'description': description,
            'source_record_id': source_record.get('id') if source_record else None,
            'target_record_id': target_record.get('id') if target_record else None,
            'source_data': source_record,
            'target_data': target_record,
            'difference_details': match_result.differences if match_result else None,
            'status': ReconciliationStatus.PENDING
        }
        
        # Save to database if available
        if db:
            discrepancy = ReconciliationDiscrepancy(**discrepancy_data)
            db.add(discrepancy)
            db.commit()
            db.refresh(discrepancy)
            discrepancy_data['id'] = discrepancy.id
        
        return discrepancy_data
    
    def _get_record_key(self, record: Dict[str, Any]) -> str:
        """Generate a unique key for record matching"""
        # Use ID if available, otherwise create composite key
        if 'id' in record:
            return str(record['id'])
        
        # Create composite key from common fields
        key_fields = ['email', 'username', 'account_number', 'transaction_id']
        key_parts = []
        for field in key_fields:
            if field in record and record[field]:
                key_parts.append(str(record[field]))
        
        return '|'.join(key_parts) if key_parts else str(hash(json.dumps(record, sort_keys=True)))
    
    def _get_difference_type(self, source_value: Any, target_value: Any) -> str:
        """Determine the type of difference between two values"""
        if source_value is None and target_value is not None:
            return 'missing_in_source'
        elif source_value is not None and target_value is None:
            return 'missing_in_target'
        elif isinstance(source_value, (int, float)) and isinstance(target_value, (int, float)):
            return 'numeric_difference'
        elif isinstance(source_value, str) and isinstance(target_value, str):
            return 'text_difference'
        else:
            return 'type_difference'
    
    def _determine_severity(self, discrepancy_type: str, match_result: Optional[MatchResult]) -> str:
        """Determine severity of discrepancy"""
        if discrepancy_type in ['missing_in_source', 'missing_in_target']:
            return 'high'
        elif match_result and match_result.confidence < 0.5:
            return 'critical'
        elif match_result and match_result.confidence < 0.8:
            return 'high'
        else:
            return 'medium'
    
    def _create_discrepancy_description(
        self, 
        discrepancy_type: str, 
        source_record: Optional[Dict[str, Any]], 
        target_record: Optional[Dict[str, Any]], 
        match_result: Optional[MatchResult]
    ) -> str:
        """Create human-readable description of discrepancy"""
        
        if discrepancy_type == 'missing_in_target':
            return f"Record exists in source but not in target: {source_record.get('id', 'unknown')}"
        elif discrepancy_type == 'missing_in_source':
            return f"Record exists in target but not in source: {target_record.get('id', 'unknown')}"
        elif discrepancy_type == 'mismatch' and match_result:
            diff_count = len(match_result.differences)
            return f"Records match but have {diff_count} field differences (confidence: {match_result.confidence:.2f})"
        else:
            return f"Discrepancy of type: {discrepancy_type}"
    
    # Matching algorithm implementations
    def _exact_match(self, value1: Any, value2: Any) -> Tuple[bool, float]:
        """Exact matching algorithm"""
        is_match = value1 == value2
        confidence = 1.0 if is_match else 0.0
        return is_match, confidence
    
    def _fuzzy_match(self, value1: str, value2: str, threshold: float = 0.8) -> Tuple[bool, float]:
        """Fuzzy string matching algorithm"""
        if not isinstance(value1, str) or not isinstance(value2, str):
            return self._exact_match(value1, value2)
        
        similarity = SequenceMatcher(None, value1.lower(), value2.lower()).ratio()
        is_match = similarity >= threshold
        return is_match, similarity
    
    def _numeric_match(self, value1: Any, value2: Any, tolerance: float = 0.01) -> Tuple[bool, float]:
        """Numeric matching with tolerance"""
        try:
            num1 = float(value1)
            num2 = float(value2)
            difference = abs(num1 - num2)
            max_value = max(abs(num1), abs(num2))
            
            if max_value == 0:
                is_match = difference == 0
                confidence = 1.0 if is_match else 0.0
            else:
                relative_difference = difference / max_value
                is_match = relative_difference <= tolerance
                confidence = 1.0 - relative_difference
            
            return is_match, confidence
        except (ValueError, TypeError):
            return self._exact_match(value1, value2)
    
    def _date_match(self, value1: Any, value2: Any, tolerance_days: int = 1) -> Tuple[bool, float]:
        """Date matching with tolerance"""
        try:
            from datetime import datetime
            date1 = datetime.fromisoformat(str(value1).replace('Z', '+00:00'))
            date2 = datetime.fromisoformat(str(value2).replace('Z', '+00:00'))
            
            difference = abs((date1 - date2).total_seconds())
            tolerance_seconds = tolerance_days * 24 * 60 * 60
            
            is_match = difference <= tolerance_seconds
            confidence = 1.0 - (difference / tolerance_seconds) if tolerance_seconds > 0 else 1.0
            
            return is_match, confidence
        except (ValueError, TypeError):
            return self._exact_match(value1, value2)
    
    def _custom_match(self, value1: Any, value2: Any, rule: Dict[str, Any]) -> Tuple[bool, float]:
        """Custom matching algorithm based on rule configuration"""
        # This would implement custom matching logic based on rule configuration
        # For now, fall back to exact matching
        return self._exact_match(value1, value2)
