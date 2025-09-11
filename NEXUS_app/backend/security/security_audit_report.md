
# 🔒 Security Audit Report
**Generated:** 2025-09-10T07:21:19.655764
**Security Score:** 0/100

## 📊 Check Results

### ❌ Dependencies
**Status:** FAIL
**Message:** Found 0 vulnerable dependencies

### ❌ Authentication
**Status:** FAIL
**Message:** N/A
**Issues:**
- Using weak HS256 algorithm instead of RS256

### ❌ Input Validation
**Status:** FAIL
**Message:** N/A
**Issues:**
- Potential SQL injection in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/alembic/autogenerate/api.py
- Potential SQL injection in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/api/health.py

### ❌ File Upload
**Status:** FAIL
**Message:** N/A
**Issues:**
- File type validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/s3transfer/upload.py
- File type validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/azure/storage/blob/_shared/uploads.py
- File size validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/azure/storage/blob/_shared/uploads.py
- File type validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/azure/storage/blob/_shared/uploads_async.py
- File size validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/azure/storage/blob/_shared/uploads_async.py
- File size validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/google/resumable_media/requests/upload.py
- File size validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/google/_async_resumable_media/requests/upload.py

### ❌ Database
**Status:** FAIL
**Message:** N/A
**Issues:**
- Database SSL not configured

### ❌ Api Security
**Status:** FAIL
**Message:** N/A
**Issues:**
- CORS allows all origins (*)

### ❌ Environment
**Status:** FAIL
**Message:** N/A
**Issues:**
- .env file not found - using environment variables

### ❌ Security Headers
**Status:** FAIL
**Message:** N/A
**Issues:**
- Security headers not implemented

## 🚨 Vulnerabilities Found
- Using weak HS256 algorithm instead of RS256
- Potential SQL injection in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/alembic/autogenerate/api.py
- Potential SQL injection in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/api/health.py
- File type validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/s3transfer/upload.py
- File type validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/azure/storage/blob/_shared/uploads.py
- File size validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/azure/storage/blob/_shared/uploads.py
- File type validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/azure/storage/blob/_shared/uploads_async.py
- File size validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/azure/storage/blob/_shared/uploads_async.py
- File size validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/google/resumable_media/requests/upload.py
- File size validation missing in /Users/Arief/Desktop/Nexus/NEXUS_app/backend/nexus_env/lib/python3.11/site-packages/google/_async_resumable_media/requests/upload.py
- Database SSL not configured
- CORS allows all origins (*)
- .env file not found - using environment variables
- Security headers not implemented
