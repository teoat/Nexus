#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Centralized Data Manager for Nexus Platform
Manages all data storage, synchronization, and consistency across components.
"""

import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class DataType(Enum):
    """Types of data managed by the system"""
    AGENTS = "agents"
    TASKS = "tasks"
    WORKSPACES = "workspaces"
    DECISIONS = "decisions"
    KNOWLEDGE = "knowledge"
    WORKFLOWS = "workflows"
    INSTANCES = "instances"
    SESSIONS = "sessions"
    MESSAGES = "messages"
    METRICS = "metrics"
    CONFIG = "config"

@dataclass
class DataRecord:
    """Standardized data record structure"""
    id: str
    type: DataType
    data: Dict[str, Any]
    created_at: str
    updated_at: str
    version: int = 1
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """
          Post Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        if self.metadata is None:
            self.metadata = {}

class CentralizedDataManager:
    """Centralized data management system"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.data_dir = self.workspace_path / ".nexus" / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Data storage
        self.data: Dict[DataType, Dict[str, DataRecord]] = {}
        self.data_locks: Dict[DataType, threading.Lock] = {}
        
        # Synchronization
        self.sync_queue = []
        self.sync_lock = threading.Lock()
        self.sync_thread = None
        self.running = True
        
        # Initialize data types
        for data_type in DataType:
            self.data[data_type] = {}
            self.data_locks[data_type] = threading.Lock()
        
        # Load existing data
        self.load_all_data()
        
        # Start synchronization thread
        self.start_sync_thread()
    
    def load_all_data(self):
        """Load all data from storage files"""
        try:
            for data_type in DataType:
                file_path = self.data_dir / f"{data_type.value}.json"
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        for record_id, record_data in data.items():
                            record = DataRecord(**record_data)
                            self.data[data_type][record_id] = record
                    logger.info(f"Loaded {len(self.data[data_type])} {data_type.value} records")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def save_data_type(self, data_type: DataType):
        """
        Save Data Type
        
        
        Args:
            data_type: Description of data_type
    
        Example:
            TBD: Add usage example
        """
        try:
            with self.data_locks[data_type]:
                file_path = self.data_dir / f"{data_type.value}.json"
                data = {}
                for record_id, record in self.data[data_type].items():
                    record_dict = asdict(record)
                    # Convert enum to string for JSON serialization
                    record_dict['type'] = record.type.value
                    data[record_id] = record_dict
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving {data_type.value} data: {e}")
    
    def save_all_data(self):
        """Save all data to storage files"""
        for data_type in DataType:
            self.save_data_type(data_type)
    
    def create_record(self, data_type: DataType, data: Dict[str, Any], record_id: str = None) -> str:
        """Create a new data record"""
        if record_id is None:
            record_id = str(uuid.uuid4())
        
        now = datetime.now().isoformat()
        record = DataRecord(
            id=record_id,
            type=data_type,
            data=data,
            created_at=now,
            updated_at=now,
            version=1
        )
        
        with self.data_locks[data_type]:
            self.data[data_type][record_id] = record
        
        # Queue for synchronization
        self.queue_sync(data_type, record_id, "create")
        
        logger.debug(f"Created {data_type.value} record: {record_id}")
        return record_id
    
    def get_record(self, data_type: DataType, record_id: str) -> Optional[DataRecord]:
        """Get a data record by ID"""
        with self.data_locks[data_type]:
            return self.data[data_type].get(record_id)
    
    def update_record(self, data_type: DataType, record_id: str, data: Dict[str, Any]) -> bool:
        """Update a data record"""
        with self.data_locks[data_type]:
            if record_id not in self.data[data_type]:
                return False
            
            record = self.data[data_type][record_id]
            record.data.update(data)
            record.updated_at = datetime.now().isoformat()
            record.version += 1
            
            # Queue for synchronization
            self.queue_sync(data_type, record_id, "update")
            
            logger.debug(f"Updated {data_type.value} record: {record_id}")
            return True
    
    def delete_record(self, data_type: DataType, record_id: str) -> bool:
        """Delete a data record"""
        with self.data_locks[data_type]:
            if record_id not in self.data[data_type]:
                return False
            
            del self.data[data_type][record_id]
            
            # Queue for synchronization
            self.queue_sync(data_type, record_id, "delete")
            
            logger.debug(f"Deleted {data_type.value} record: {record_id}")
            return True
    
    def get_records_by_type(self, data_type: DataType) -> List[DataRecord]:
        """
        Retrieve records by type
        
        
        Args:
            data_type: Description of data_type
    
        Returns:
            Unknown: Description of return value
    
        Example:
            TBD: Add usage example
        """
        with self.data_locks[data_type]:
            return list(self.data[data_type].values())
    
    def search_records(self, data_type: DataType, query: Dict[str, Any]) -> List[DataRecord]:
        """Search records by query criteria"""
        results = []
        with self.data_locks[data_type]:
            for record in self.data[data_type].values():
                if self._matches_query(record.data, query):
                    results.append(record)
        return results
    
    def _matches_query(self, data: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if data matches query criteria"""
        for key, value in query.items():
            if key not in data or data[key] != value:
                return False
        return True
    
    def queue_sync(self, data_type: DataType, record_id: str, operation: str):
        """Queue a record for synchronization"""
        with self.sync_lock:
            self.sync_queue.append({
                "data_type": data_type,
                "record_id": record_id,
                "operation": operation,
                "timestamp": datetime.now().isoformat()
            })
    
    def start_sync_thread(self):
        """Start the synchronization thread"""
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
    
    def _sync_worker(self):
        """Synchronization worker thread"""
        while self.running:
            try:
                with self.sync_lock:
                    if self.sync_queue:
                        sync_item = self.sync_queue.pop(0)
                    else:
                        sync_item = None
                
                if sync_item:
                    self._process_sync_item(sync_item)
                else:
                    time.sleep(0.1)  # Small delay when no items to process
                    
            except Exception as e:
                logger.error(f"Error in sync worker: {e}")
                time.sleep(1)
    
    def _process_sync_item(self, sync_item: Dict[str, Any]):
        """Process a synchronization item"""
        try:
            data_type = sync_item["data_type"]
            operation = sync_item["operation"]
            
            if operation == "create":
                self.save_data_type(data_type)
            elif operation == "update":
                self.save_data_type(data_type)
            elif operation == "delete":
                self.save_data_type(data_type)
                
        except Exception as e:
            logger.error(f"Error processing sync item: {e}")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system data metrics"""
        metrics = {}
        for data_type in DataType:
            with self.data_locks[data_type]:
                metrics[data_type.value] = {
                    "count": len(self.data[data_type]),
                    "last_updated": max(
                        [record.updated_at for record in self.data[data_type].values()],
                        default="never"
                    )
                }
        
        metrics["sync_queue_size"] = len(self.sync_queue)
        metrics["total_records"] = sum(len(records) for records in self.data.values())
        
        return metrics
    
    def cleanup_old_records(self, data_type: DataType, days_old: int = 30):
        """Clean up old records"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        records_to_delete = []
        
        with self.data_locks[data_type]:
            for record_id, record in self.data[data_type].items():
                record_date = datetime.fromisoformat(record.updated_at).timestamp()
                if record_date < cutoff_date:
                    records_to_delete.append(record_id)
        
        for record_id in records_to_delete:
            self.delete_record(data_type, record_id)
        
        logger.info(f"Cleaned up {len(records_to_delete)} old {data_type.value} records")
    
    def shutdown(self):
        """Shutdown the data manager"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        
        # Save all data before shutdown
        self.save_all_data()
        logger.info("Data manager shutdown complete")
