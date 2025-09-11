#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🗄️ Database Migration and Backup System for Nexus Platform
Comprehensive database management with automated migrations and backups
"""

import asyncio
import logging
import os
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncpg
import psycopg2
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import boto3
from botocore.exceptions import ClientError
import json
import gzip

logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Database migration and backup management system"""
    
    def __init__(
        """
          Init  
        
        
        Args:
            database_url: Description of database_url
            backup_storage: Description of backup_storage
            s3_bucket: Description of s3_bucket
            backup_retention_days: Description of backup_retention_days
    
        Example:
            TBD: Add usage example
        """
        self,
        database_url: str,
        backup_storage: str = "local",
        s3_bucket: str = None,
        backup_retention_days: int = 30
    ):
        self.database_url = database_url
        self.backup_storage = backup_storage
        self.s3_bucket = s3_bucket
        self.backup_retention_days = backup_retention_days
        self.backup_dir = Path("/backups/nexus")
        self.migration_dir = Path(__file__).parent / "migrations"
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 client if using S3
        if backup_storage == "s3" and s3_bucket:
            self.s3_client = boto3.client('s3')
        else:
            self.s3_client = None
    
    async def run_migrations(self, target_version: str = "head") -> bool:
        """Run database migrations"""
        try:
            logger.info(f"Running database migrations to {target_version}")
            
            # Use Alembic to run migrations
            result = subprocess.run([
                "alembic", "upgrade", target_version
            ], capture_output=True, text=True, cwd=self.migration_dir.parent)
            
            if result.returncode != 0:
                logger.error(f"Migration failed: {result.stderr}")
                return False
            
            logger.info("Database migrations completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            return False
    
    async def create_backup(self, backup_name: str = None) -> str:
        """Create database backup"""
        if not backup_name:
            backup_name = f"nexus_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            logger.info(f"Creating database backup: {backup_name}")
            
            # Parse database URL
            db_config = self._parse_database_url()
            
            # Create backup file
            backup_file = self.backup_dir / f"{backup_name}.sql"
            
            # Run pg_dump
            cmd = [
                "pg_dump",
                "-h", db_config["host"],
                "-p", str(db_config["port"]),
                "-U", db_config["user"],
                "-d", db_config["database"],
                "-f", str(backup_file),
                "--verbose",
                "--no-password"
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config["password"]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Backup failed: {result.stderr}")
                return None
            
            # Compress backup
            compressed_file = f"{backup_file}.gz"
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed file
            backup_file.unlink()
            backup_file = Path(compressed_file)
            
            # Upload to S3 if configured
            if self.backup_storage == "s3" and self.s3_client:
                await self._upload_to_s3(backup_file, backup_name)
            
            logger.info(f"Backup created successfully: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    async def restore_backup(self, backup_file: str) -> bool:
        """Restore database from backup"""
        try:
            logger.info(f"Restoring database from backup: {backup_file}")
            
            # Parse database URL
            db_config = self._parse_database_url()
            
            # Check if backup file exists
            backup_path = Path(backup_file)
            if not backup_path.exists():
                # Try to download from S3
                if self.backup_storage == "s3" and self.s3_client:
                    backup_path = await self._download_from_s3(backup_file)
                    if not backup_path:
                        logger.error("Backup file not found")
                        return False
                else:
                    logger.error("Backup file not found")
                    return False
            
            # Decompress if needed
            if backup_path.suffix == '.gz':
                decompressed_file = backup_path.with_suffix('')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(decompressed_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path = decompressed_file
            
            # Restore database
            cmd = [
                "psql",
                "-h", db_config["host"],
                "-p", str(db_config["port"]),
                "-U", db_config["user"],
                "-d", db_config["database"],
                "-f", str(backup_path)
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = db_config["password"]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Restore failed: {result.stderr}")
                return False
            
            logger.info("Database restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups"""
        backups = []
        
        try:
            if self.backup_storage == "s3" and self.s3_client:
                # List S3 backups
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix="nexus_backup_"
                )
                
                for obj in response.get('Contents', []):
                    backups.append({
                        "name": obj['Key'],
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'],
                        "storage": "s3"
                    })
            else:
                # List local backups
                for backup_file in self.backup_dir.glob("nexus_backup_*.sql.gz"):
                    stat = backup_file.stat()
                    backups.append({
                        "name": backup_file.name,
                        "size": stat.st_size,
                        "last_modified": datetime.fromtimestamp(stat.st_mtime),
                        "storage": "local",
                        "path": str(backup_file)
                    })
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x['last_modified'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    async def cleanup_old_backups(self) -> int:
        """Clean up old backups based on retention policy"""
        try:
            logger.info("Cleaning up old backups...")
            
            cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
            deleted_count = 0
            
            if self.backup_storage == "s3" and self.s3_client:
                # Clean up S3 backups
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix="nexus_backup_"
                )
                
                for obj in response.get('Contents', []):
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        self.s3_client.delete_object(
                            Bucket=self.s3_bucket,
                            Key=obj['Key']
                        )
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {obj['Key']}")
            else:
                # Clean up local backups
                for backup_file in self.backup_dir.glob("nexus_backup_*.sql.gz"):
                    if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff_date:
                        backup_file.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {backup_file}")
            
            logger.info(f"Cleaned up {deleted_count} old backups")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")
            return 0
    
    async def verify_database_integrity(self) -> bool:
        """Verify database integrity"""
        try:
            logger.info("Verifying database integrity...")
            
            # Parse database URL
            db_config = self._parse_database_url()
            
            # Connect to database
            conn = await asyncpg.connect(
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"]
            )
            
            try:
                # Check database size
                size_result = await conn.fetchval("SELECT pg_database_size(current_database())")
                logger.info(f"Database size: {size_result / (1024**3):.2f} GB")
                
                # Check table counts
                tables = await conn.fetch("""
                    SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
                    FROM pg_stat_user_tables
                    ORDER BY n_tup_ins DESC
                """)
                
                logger.info("Table statistics:")
                for table in tables:
                    logger.info(f"  {table['schemaname']}.{table['tablename']}: "
                              f"{table['n_tup_ins']} inserts, "
                              f"{table['n_tup_upd']} updates, "
                              f"{table['n_tup_del']} deletes")
                
                # Check for corruption
                corruption_check = await conn.fetchval("SELECT COUNT(*) FROM pg_stat_database WHERE datname = current_database()")
                if corruption_check == 0:
                    logger.error("Database corruption detected")
                    return False
                
                logger.info("Database integrity check passed")
                return True
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Error verifying database integrity: {e}")
            return False
    
    async def optimize_database(self) -> bool:
        """Optimize database performance"""
        try:
            logger.info("Optimizing database...")
            
            # Parse database URL
            db_config = self._parse_database_url()
            
            # Connect to database
            conn = await asyncpg.connect(
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"]
            )
            
            try:
                # Update table statistics
                await conn.execute("ANALYZE")
                logger.info("Updated table statistics")
                
                # Vacuum tables
                await conn.execute("VACUUM ANALYZE")
                logger.info("Vacuumed and analyzed tables")
                
                # Reindex if needed
                index_stats = await conn.fetch("""
                    SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
                    FROM pg_stat_user_indexes
                    WHERE idx_tup_read > 0
                    ORDER BY idx_tup_read DESC
                """)
                
                for stat in index_stats:
                    if stat['idx_tup_fetch'] / stat['idx_tup_read'] < 0.1:
                        logger.info(f"Reindexing {stat['indexname']} (low efficiency)")
                        await conn.execute(f"REINDEX INDEX {stat['indexname']}")
                
                logger.info("Database optimization completed")
                return True
                
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return False
    
    def _parse_database_url(self) -> Dict[str, Any]:
        """Parse database URL into components"""
        # Simple URL parsing for postgresql://user:password@host:port/database
        url = self.database_url.replace("postgresql://", "")
        
        if "@" in url:
            auth, host_db = url.split("@", 1)
            if ":" in auth:
                user, password = auth.split(":", 1)
            else:
                user, password = auth, ""
        else:
            user, password = "", ""
            host_db = url
        
        if "/" in host_db:
            host_port, database = host_db.split("/", 1)
        else:
            host_port, database = host_db, ""
        
        if ":" in host_port:
            host, port = host_port.split(":", 1)
            port = int(port)
        else:
            host, port = host_port, 5432
        
        return {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database
        }
    
    async def _upload_to_s3(self, file_path: Path, backup_name: str) -> bool:
        """Upload backup to S3"""
        try:
            s3_key = f"nexus_backup_{backup_name}.sql.gz"
            
            self.s3_client.upload_file(
                str(file_path),
                self.s3_bucket,
                s3_key
            )
            
            logger.info(f"Backup uploaded to S3: s3://{self.s3_bucket}/{s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            return False
    
    async def _download_from_s3(self, backup_name: str) -> Optional[Path]:
        """Download backup from S3"""
        try:
            s3_key = f"nexus_backup_{backup_name}.sql.gz"
            local_path = self.backup_dir / f"{backup_name}.sql.gz"
            
            self.s3_client.download_file(
                self.s3_bucket,
                s3_key,
                str(local_path)
            )
            
            logger.info(f"Backup downloaded from S3: {local_path}")
            return local_path
            
        except ClientError as e:
            logger.error(f"Error downloading from S3: {e}")
            return None

# CLI interface
async def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Nexus Platform Database Management")
    parser.add_argument("--database-url", required=True, help="Database URL")
    parser.add_argument("--action", choices=["migrate", "backup", "restore", "list", "cleanup", "verify", "optimize"], required=True, help="Action to perform")
    parser.add_argument("--backup-name", help="Backup name for backup/restore operations")
    parser.add_argument("--backup-file", help="Backup file path for restore operation")
    parser.add_argument("--target-version", default="head", help="Target migration version")
    parser.add_argument("--storage", choices=["local", "s3"], default="local", help="Backup storage type")
    parser.add_argument("--s3-bucket", help="S3 bucket for backup storage")
    parser.add_argument("--retention-days", type=int, default=30, help="Backup retention days")
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator(
        database_url=args.database_url,
        backup_storage=args.storage,
        s3_bucket=args.s3_bucket,
        backup_retention_days=args.retention_days
    )
    
    if args.action == "migrate":
        success = await migrator.run_migrations(args.target_version)
        print("Migration successful" if success else "Migration failed")
    
    elif args.action == "backup":
        backup_path = await migrator.create_backup(args.backup_name)
        print(f"Backup created: {backup_path}" if backup_path else "Backup failed")
    
    elif args.action == "restore":
        if not args.backup_file:
            print("Error: --backup-file is required for restore operation")
            return
        success = await migrator.restore_backup(args.backup_file)
        print("Restore successful" if success else "Restore failed")
    
    elif args.action == "list":
        backups = await migrator.list_backups()
        print(f"Found {len(backups)} backups:")
        for backup in backups:
            print(f"  {backup['name']} ({backup['size']} bytes, {backup['last_modified']})")
    
    elif args.action == "cleanup":
        deleted = await migrator.cleanup_old_backups()
        print(f"Cleaned up {deleted} old backups")
    
    elif args.action == "verify":
        success = await migrator.verify_database_integrity()
        print("Database integrity check passed" if success else "Database integrity check failed")
    
    elif args.action == "optimize":
        success = await migrator.optimize_database()
        print("Database optimization completed" if success else "Database optimization failed")

if __name__ == "__main__":
    asyncio.run(main())
