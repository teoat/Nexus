# Nexus Platform

## 🚀 Overview

Nexus Platform is a sophisticated forensic and reconciliation platform with a multi-agent AI architecture designed for enterprise-level fraud detection, forensic analysis, and financial reconciliation.

## 📁 Project Structure

```
NexusX/
├── backend/                    # Backend services
│   ├── ai_engine/              # AI engine services
│   │   ├── models/             # ML models
│   │   └── services/           # AI microservices
│   ├── api_gateway/            # API Gateway service
│   ├── controllers/            # Business logic controllers
│   ├── models/                 # Data models
│   └── services/               # Business logic services
├── config/                     # Configuration files
│   ├── env_configs/            # Environment-specific configurations
│   └── python/                 # Python configuration
├── docker/                     # Docker infrastructure
│   ├── services/               # Service-specific Docker files
│   │   ├── ai-engine/          # AI Engine Docker setup
│   │   ├── api-gateway/        # API Gateway Docker setup
│   │   ├── forensic-analysis/  # Forensic Analysis Docker setup
│   │   ├── fraud-detection/    # Fraud Detection Docker setup
│   │   └── frenly-ai/          # Frenly AI Docker setup
│   ├── config/                 # Docker configurations
│   └── data/                   # Docker volumes and data
├── docs/                       # Documentation
│   └── architecture/           # Architecture documentation
├── frontend/                   # Frontend application
│   ├── components/             # Reusable UI components
│   ├── pages/                  # Page components
│   ├── styles/                 # CSS styles
│   ├── index.html              # Homepage
│   ├── dashboard.html          # System dashboard
│   ├── quickstart.html         # User onboarding guide
│   └── user-guide.html         # Comprehensive documentation
├── scripts/                    # Utility scripts
│   ├── deployment/             # Deployment scripts
│   └── setup/                  # Setup scripts
├── tests/                      # Test suite
│   ├── integration/            # Integration tests
│   └── unit/                   # Unit tests
├── activate_nexus_env.ps1      # PowerShell env activation script
├── activate_nexus_env.sh       # Unix/Mac env activation script
├── docker-compose.yml          # Docker Compose file
├── nexus_python.ps1            # PowerShell Python launcher
├── nexus_python.sh             # Unix/Mac Python launcher
├── python_config.yaml          # Python configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🛠️ Technology Stack

- **Backend**: Python 3.12, FastAPI
- **Databases**: PostgreSQL, Neo4j, Redis, MinIO
- **Messaging**: RabbitMQ
- **Frontend**: HTML5, CSS3, JavaScript
- **Containerization**: Docker, Docker Compose
- **AI/ML**: OpenAI, Anthropic, Custom ML models
- **Monitoring**: Prometheus, Grafana, Alertmanager

## 🔧 Development Setup

### Prerequisites

- Python 3.12
- Docker and Docker Compose
- Node.js (for frontend development tooling)

### Python Environment Setup

1. **Activate the virtual environment**:

   ```bash
   # Unix/Mac
   ./activate_nexus_env.sh

   # PowerShell
   .\activate_nexus_env.ps1
   ```

2. **Direct Python execution**:

   ```bash
   # Unix/Mac
   ./nexus_python.sh your_script.py

   # PowerShell
   .\nexus_python.ps1 your_script.py
   ```

### Docker Setup

1. **Start the entire platform**:

   ```bash
   docker-compose up -d
   ```

2. **Start specific services**:

   ```bash
   docker-compose up -d api-gateway ai-engine
   ```

## 🚀 Key Features

1. **Multi-Agent AI System**
   - Specialized agents for fraud detection, forensic analysis, and reconciliation
   - Well-defined agent communication protocols

2. **Microservices Design**
   - Clear service separation (API Gateway, AI Services, Business Logic)
   - Independent service scaling capabilities

3. **Multi-Database Strategy**
   - PostgreSQL for transactional data
   - Neo4j for graph relationships
   - DuckDB for analytics
   - Redis for caching
   - MinIO for object storage

4. **User Experience**
   - Interactive platform tutorials
   - Role-based user guidance
   - Progress tracking and certification
   - Contextual help and tooltips

## 📊 System Architecture

### Core Components

1. **API Gateway**
   - Entry point for all client requests
   - Handles authentication and authorization
   - Routes requests to appropriate services

2. **AI Engine**
   - Processes AI-related requests
   - Manages machine learning models
   - Provides inference capabilities

3. **Fraud Detection**
   - Analyzes transactions for suspicious patterns
   - Implements real-time fraud detection algorithms

4. **Forensic Analysis**
   - Performs deep analysis of suspicious activities
   - Reconstructs transaction sequences

5. **Frenly AI**
   - Meta-agent for system coordination
   - Provides natural language interface

## 📚 Documentation

- **ARCHITECTURE.md**: Detailed system architecture documentation
- **PYTHON_CONSOLIDATION_GUIDE.md**: Python environment setup guide
- **COMPREHENSIVE_SYSTEM_ANALYSIS.md**: System analysis and improvements
- **SYSTEM_ANALYSIS_AND_IMPROVEMENTS.md**: Detailed improvement plan
- **WEBPAGES_IMPLEMENTATION_SUMMARY.md**: Web interface implementation details

## 📝 Contributing

Please see CONTRIBUTING.md for the contribution guidelines.

## 📄 License

[License details to be added]

## 📧 Contact

[Contact information to be added]
