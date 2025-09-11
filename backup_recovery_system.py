#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Backup and Recovery System
=========================

Comprehensive backup system:
- Incremental backups every 5 minutes
- Full backups daily
- Point-in-time recovery
- Backup verification
"""

import os
import sys
import json
import shutil
import gzip
import tarfile
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupRecoverySystem:
    def __init__(self, workspace_root: str = "/Users/Arief/Desktop/Nexus"):
        self.workspace_root = Path(workspace_root)
        self.backup_dir = self.workspace_root / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup configuration
        self.config = {
            'incremental_interval': 300,  # 5 minutes
            'full_backup_interval': 86400,  # 24 hours
            'retention_days': 30,
            'compression': True,
            'verification': True
        }
        
        # Critical files to backup
        self.critical_files = [
            'master_todo.md',
            'nexus_comprehensive_sot.json',
            'nexus_events.json',
            'nexus_sot_config.json',
            'nexus_integration_config.json',
            'nexus_sync_status.json',
            'python_version_sot.json'
        ]
        
        # Critical directories to backup
        self.critical_dirs = [
            'NEXUS_app',
            'nexus_python_env',
            'logs',
            'config'
        ]
        
        # Backup tracking
        self.backup_history = []
        self.last_incremental = None
        self.last_full = None
        
        # Threading
        self.backup_thread = None
        self.running = False
        
        # Load backup history
        self._load_backup_history()
    
    def _load_backup_history(self):
        """Load backup history from file"""
        history_file = self.backup_dir / "backup_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.backup_history = json.load(f)
            except Exception as e:
                logger.error(f"Error loading backup history: {e}")
                self.backup_history = []
    
    def _save_backup_history(self):
        """Save backup history to file"""
        history_file = self.backup_dir / "backup_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.backup_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving backup history: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _get_file_list(self, base_path: Path, pattern: str = "**/*") -> List[Path]:
        """Get list of files matching pattern"""
        files = []
        try:
            for file_path in base_path.glob(pattern):
                if file_path.is_file():
                    files.append(file_path)
        except Exception as e:
            logger.error(f"Error getting file list: {e}")
        return files
    
    def create_incremental_backup(self) -> Dict[str, Any]:
        """Create incremental backup of critical files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"incremental_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        backup_info = {
            'type': 'incremental',
            'timestamp': timestamp,
            'backup_path': str(backup_path),
            'files': [],
            'total_size': 0,
            'compressed_size': 0,
            'verification': {}
        }
        
        logger.info(f"Creating incremental backup: {backup_name}")
        
        # Backup critical files
        for file_name in self.critical_files:
            source_file = self.workspace_root / file_name
            if source_file.exists():
                dest_file = backup_path / file_name
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(source_file, dest_file)
                    file_size = source_file.stat().st_size
                    file_hash = self._calculate_file_hash(source_file)
                    
                    backup_info['files'].append({
                        'name': file_name,
                        'size': file_size,
                        'hash': file_hash,
                        'backed_up': True
                    })
                    
                    backup_info['total_size'] += file_size
                    
                except Exception as e:
                    logger.error(f"Error backing up {file_name}: {e}")
                    backup_info['files'].append({
                        'name': file_name,
                        'size': 0,
                        'hash': '',
                        'backed_up': False,
                        'error': str(e)
                    })
        
        # Compress backup if enabled
        if self.config['compression']:
            compressed_file = self.backup_dir / f"{backup_name}.tar.gz"
            try:
                with tarfile.open(compressed_file, "w:gz") as tar:
                    tar.add(backup_path, arcname=backup_name)
                
                backup_info['compressed_size'] = compressed_file.stat().st_size
                backup_info['compressed_file'] = str(compressed_file)
                
                # Remove uncompressed directory
                shutil.rmtree(backup_path)
                backup_info['backup_path'] = str(compressed_file)
                
            except Exception as e:
                logger.error(f"Error compressing backup: {e}")
        
        # Verify backup if enabled
        if self.config['verification']:
            backup_info['verification'] = self._verify_backup(backup_info)
        
        # Update tracking
        self.last_incremental = backup_info
        self.backup_history.append(backup_info)
        self._save_backup_history()
        
        logger.info(f"Incremental backup completed: {backup_name}")
        return backup_info
    
    def create_full_backup(self) -> Dict[str, Any]:
        """Create full backup of critical directories"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"full_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        backup_info = {
            'type': 'full',
            'timestamp': timestamp,
            'backup_path': str(backup_path),
            'directories': [],
            'total_size': 0,
            'compressed_size': 0,
            'verification': {}
        }
        
        logger.info(f"Creating full backup: {backup_name}")
        
        # Backup critical directories
        for dir_name in self.critical_dirs:
            source_dir = self.workspace_root / dir_name
            if source_dir.exists():
                dest_dir = backup_path / dir_name
                
                try:
                    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
                    
                    # Calculate directory size
                    dir_size = sum(f.stat().st_size for f in source_dir.rglob('*') if f.is_file())
                    
                    backup_info['directories'].append({
                        'name': dir_name,
                        'size': dir_size,
                        'backed_up': True
                    })
                    
                    backup_info['total_size'] += dir_size
                    
                except Exception as e:
                    logger.error(f"Error backing up directory {dir_name}: {e}")
                    backup_info['directories'].append({
                        'name': dir_name,
                        'size': 0,
                        'backed_up': False,
                        'error': str(e)
                    })
        
        # Also backup critical files
        for file_name in self.critical_files:
            source_file = self.workspace_root / file_name
            if source_file.exists():
                dest_file = backup_path / file_name
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(source_file, dest_file)
                    file_size = source_file.stat().st_size
                    backup_info['total_size'] += file_size
                    
                except Exception as e:
                    logger.error(f"Error backing up {file_name}: {e}")
        
        # Compress backup if enabled
        if self.config['compression']:
            compressed_file = self.backup_dir / f"{backup_name}.tar.gz"
            try:
                with tarfile.open(compressed_file, "w:gz") as tar:
                    tar.add(backup_path, arcname=backup_name)
                
                backup_info['compressed_size'] = compressed_file.stat().st_size
                backup_info['compressed_file'] = str(compressed_file)
                
                # Remove uncompressed directory
                shutil.rmtree(backup_path)
                backup_info['backup_path'] = str(compressed_file)
                
            except Exception as e:
                logger.error(f"Error compressing backup: {e}")
        
        # Verify backup if enabled
        if self.config['verification']:
            backup_info['verification'] = self._verify_backup(backup_info)
        
        # Update tracking
        self.last_full = backup_info
        self.backup_history.append(backup_info)
        self._save_backup_history()
        
        logger.info(f"Full backup completed: {backup_name}")
        return backup_info
    
    def _verify_backup(self, backup_info: Dict[str, Any]) -> Dict[str, Any]:
        """Verify backup integrity"""
        verification = {
            'verified': True,
            'errors': [],
            'file_checks': []
        }
        
        try:
            backup_path = Path(backup_info['backup_path'])
            
            # If compressed, extract temporarily for verification
            if backup_info.get('compressed_file'):
                temp_dir = self.backup_dir / f"temp_verify_{backup_info['timestamp']}"
                temp_dir.mkdir(exist_ok=True)
                
                with tarfile.open(backup_info['compressed_file'], "r:gz") as tar:
                    tar.extractall(temp_dir)
                
                verify_path = temp_dir / backup_info['timestamp']
            else:
                verify_path = backup_path
            
            # Verify files
            for file_info in backup_info.get('files', []):
                if file_info.get('backed_up', False):
                    file_path = verify_path / file_info['name']
                    if file_path.exists():
                        # Check file size
                        if file_path.stat().st_size == file_info['size']:
                            # Check hash if available
                            if file_info.get('hash'):
                                current_hash = self._calculate_file_hash(file_path)
                                if current_hash == file_info['hash']:
                                    verification['file_checks'].append({
                                        'file': file_info['name'],
                                        'verified': True
                                    })
                                else:
                                    verification['file_checks'].append({
                                        'file': file_info['name'],
                                        'verified': False,
                                        'error': 'Hash mismatch'
                                    })
                                    verification['verified'] = False
                            else:
                                verification['file_checks'].append({
                                    'file': file_info['name'],
                                    'verified': True
                                })
                        else:
                            verification['file_checks'].append({
                                'file': file_info['name'],
                                'verified': False,
                                'error': 'Size mismatch'
                            })
                            verification['verified'] = False
                    else:
                        verification['file_checks'].append({
                            'file': file_info['name'],
                            'verified': False,
                            'error': 'File not found'
                        })
                        verification['verified'] = False
            
            # Clean up temporary directory
            if backup_info.get('compressed_file') and temp_dir.exists():
                shutil.rmtree(temp_dir)
                
        except Exception as e:
            verification['verified'] = False
            verification['errors'].append(str(e))
            logger.error(f"Error verifying backup: {e}")
        
        return verification
    
    def restore_backup(self, backup_info: Dict[str, Any], restore_path: Optional[Path] = None) -> bool:
        """Restore from backup"""
        if restore_path is None:
            restore_path = self.workspace_root
        
        logger.info(f"Restoring backup: {backup_info['timestamp']}")
        
        try:
            backup_file = Path(backup_info['backup_path'])
            
            if backup_file.suffix == '.gz':
                # Extract compressed backup
                temp_dir = self.backup_dir / f"temp_restore_{backup_info['timestamp']}"
                temp_dir.mkdir(exist_ok=True)
                
                with tarfile.open(backup_file, "r:gz") as tar:
                    tar.extractall(temp_dir)
                
                source_path = temp_dir / backup_info['timestamp']
            else:
                source_path = backup_file
            
            # Restore files
            for file_info in backup_info.get('files', []):
                if file_info.get('backed_up', False):
                    source_file = source_path / file_info['name']
                    dest_file = restore_path / file_info['name']
                    
                    if source_file.exists():
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, dest_file)
                        logger.info(f"Restored file: {file_info['name']}")
            
            # Restore directories
            for dir_info in backup_info.get('directories', []):
                if dir_info.get('backed_up', False):
                    source_dir = source_path / dir_info['name']
                    dest_dir = restore_path / dir_info['name']
                    
                    if source_dir.exists():
                        if dest_dir.exists():
                            shutil.rmtree(dest_dir)
                        shutil.copytree(source_dir, dest_dir)
                        logger.info(f"Restored directory: {dir_info['name']}")
            
            # Clean up temporary directory
            if backup_file.suffix == '.gz' and temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            logger.info("Backup restoration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
        
        backups_to_remove = []
        for backup in self.backup_history:
            backup_date = datetime.strptime(backup['timestamp'], "%Y%m%d_%H%M%S")
            if backup_date < cutoff_date:
                backups_to_remove.append(backup)
        
        for backup in backups_to_remove:
            try:
                backup_path = Path(backup['backup_path'])
                if backup_path.exists():
                    if backup_path.is_file():
                        backup_path.unlink()
                    else:
                        shutil.rmtree(backup_path)
                    
                    logger.info(f"Removed old backup: {backup['timestamp']}")
                
                self.backup_history.remove(backup)
                
            except Exception as e:
                logger.error(f"Error removing old backup {backup['timestamp']}: {e}")
        
        self._save_backup_history()
    
    def start_automatic_backups(self):
        """Start automatic backup process"""
        if self.running:
            logger.warning("Automatic backups already running")
            return
        
        self.running = True
        self.backup_thread = threading.Thread(target=self._backup_loop)
        self.backup_thread.daemon = True
        self.backup_thread.start()
        logger.info("Automatic backups started")
    
    def stop_automatic_backups(self):
        """Stop automatic backup process"""
        self.running = False
        if self.backup_thread:
            self.backup_thread.join()
        logger.info("Automatic backups stopped")
    
    def _backup_loop(self):
        """Main backup loop"""
        last_incremental = time.time()
        last_full = time.time()
        
        while self.running:
            current_time = time.time()
            
            # Check if incremental backup is needed
            if current_time - last_incremental >= self.config['incremental_interval']:
                try:
                    self.create_incremental_backup()
                    last_incremental = current_time
                except Exception as e:
                    logger.error(f"Error creating incremental backup: {e}")
            
            # Check if full backup is needed
            if current_time - last_full >= self.config['full_backup_interval']:
                try:
                    self.create_full_backup()
                    last_full = current_time
                    # Clean up old backups after full backup
                    self.cleanup_old_backups()
                except Exception as e:
                    logger.error(f"Error creating full backup: {e}")
            
            time.sleep(60)  # Check every minute
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Get backup system status"""
        return {
            'running': self.running,
            'last_incremental': self.last_incremental,
            'last_full': self.last_full,
            'total_backups': len(self.backup_history),
            'config': self.config,
            'backup_dir': str(self.backup_dir)
        }

def main():
    """Main function"""
    backup_system = BackupRecoverySystem()
    
    print("💾 Backup and Recovery System")
    print("=" * 40)
    
    # Create initial backup
    print("Creating initial incremental backup...")
    incremental = backup_system.create_incremental_backup()
    print(f"✅ Incremental backup created: {incremental['timestamp']}")
    print(f"   Files backed up: {len([f for f in incremental['files'] if f['backed_up']])}")
    print(f"   Total size: {incremental['total_size']} bytes")
    
    # Create full backup
    print("\nCreating full backup...")
    full = backup_system.create_full_backup()
    print(f"✅ Full backup created: {full['timestamp']}")
    print(f"   Directories backed up: {len([d for d in full['directories'] if d['backed_up']])}")
    print(f"   Total size: {full['total_size']} bytes")
    
    # Show status
    status = backup_system.get_backup_status()
    print(f"\n📊 Backup Status:")
    print(f"   Total backups: {status['total_backups']}")
    print(f"   Backup directory: {status['backup_dir']}")
    print(f"   Auto-backup running: {status['running']}")
    
    # Start automatic backups
    print("\n🔄 Starting automatic backups...")
    backup_system.start_automatic_backups()
    print("✅ Automatic backups started (will run in background)")

if __name__ == "__main__":
    main()
