#!/bin/bash

# Set the backup directory
BACKUP_DIR=/Users/Arief/Desktop/Nexus/backups

# Set the database connection details
DB_USER=${POSTGRES_USER:-nexus_user}
DB_PASSWORD=${POSTGRES_PASSWORD:-nexus_password}
DB_NAME=${POSTGRES_DB:-nexus_db}
DB_HOST=localhost
DB_PORT=${POSTGRES_PORT:-5432}

# Create the backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create the backup file
BACKUP_FILE=$BACKUP_DIR/$(date +%Y-%m-%d_%H-%M-%S).sql.gz

# Run pg_dump
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILE

# Delete backups older than 7 days
find $BACKUP_DIR -type f -mtime +7 -name '*.sql.gz' -delete
