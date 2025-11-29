# TURN - Project Manager Career Platform

A comprehensive FastAPI-based platform for project managers to showcase their work, find opportunities, and build professional networks.

##  System Architecture

```mermaid
graph TB
    %% Client Layer
    subgraph "Client Layer"
        WEB[Web Application]
        MOBILE[Mobile App]
        API_CLIENT[API Clients]
    end

    %% Load Balancer & Reverse Proxy
    LB[Nginx Load Balancer<br/>Rate Limiting & SSL]

    %% API Gateway Layer
    subgraph "API Gateway"
        FASTAPI[FastAPI Application<br/>Python 3.11+]
        CORS[CORS Middleware]
        AUTH_MW[Authentication Middleware]
        TRUSTED[Trusted Host Middleware]
    end

    %% Service Layer
    subgraph "Core Services"
        AUTH_SVC[Authentication Service<br/>JWT + OTP]
        USER_SVC[User Management Service]
        PROJECT_SVC[Project Service]
        CV_SVC[CV Builder Service]
        JOB_SVC[Job Board Service]
        EMAIL_SVC[Email Service<br/>Resend Integration]
        OTP_SVC[OTP Service<br/>Email + SMS]
    end

    %% Database Layer
    subgraph "Data Layer"
        PG[(PostgreSQL 15<br/>Primary Database)]
        REDIS[(Redis<br/>Cache + Sessions)]
    end

    %% External Services
    subgraph "External Services"
        RESEND[Resend<br/>Email Delivery]
        STRIPE[Stripe<br/>Payments]
        TWILIO[Twilio<br/>SMS + Voice]
        AWS_S3[AWS S3<br/>File Storage]
        GCS[Google Cloud Storage<br/>Alternative Storage]
    end

    %% Infrastructure Layer
    subgraph "Infrastructure"
        DOCKER[Docker Containers]
        ALEMBIC[Alembic<br/>DB Migrations]
        LOGS[Logging System]
        HEALTH[Health Checks]
    end

    %% Connections - Client to Load Balancer
    WEB --> LB
    MOBILE --> LB
    API_CLIENT --> LB

    %% Load Balancer to API Gateway
    LB --> FASTAPI

    %% API Gateway Internal Flow
    FASTAPI --> CORS
    CORS --> AUTH_MW
    AUTH_MW --> TRUSTED

    %% API Gateway to Services
    FASTAPI --> AUTH_SVC
    FASTAPI --> USER_SVC
    FASTAPI --> PROJECT_SVC
    FASTAPI --> CV_SVC
    FASTAPI --> JOB_SVC

    %% Service Dependencies
    AUTH_SVC --> EMAIL_SVC
    AUTH_SVC --> OTP_SVC
    USER_SVC --> EMAIL_SVC
    JOB_SVC --> EMAIL_SVC

    %% Services to Database
    AUTH_SVC --> PG
    USER_SVC --> PG
    PROJECT_SVC --> PG
    CV_SVC --> PG
    JOB_SVC --> PG

    %% Services to Cache
    AUTH_SVC --> REDIS
    USER_SVC --> REDIS
    OTP_SVC --> REDIS

    %% External Service Connections
    EMAIL_SVC --> RESEND
    AUTH_SVC --> STRIPE
    OTP_SVC --> TWILIO
    PROJECT_SVC --> AWS_S3
    CV_SVC --> GCS

    %% Infrastructure Connections
    FASTAPI --> DOCKER
    PG --> ALEMBIC
    FASTAPI --> LOGS
    FASTAPI --> HEALTH

    %% Styling
    classDef client fill:#e1f5fe
    classDef gateway fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef database fill:#fff3e0
    classDef external fill:#fce4ec
    classDef infra fill:#f1f8e9

    class WEB,MOBILE,API_CLIENT client
    class LB,FASTAPI,CORS,AUTH_MW,TRUSTED gateway
    class AUTH_SVC,USER_SVC,PROJECT_SVC,CV_SVC,JOB_SVC,EMAIL_SVC,OTP_SVC service
    class PG,REDIS database
    class RESEND,STRIPE,TWILIO,AWS_S3,GCS external
    class DOCKER,ALEMBIC,LOGS,HEALTH infra
```

### Architecture Components

####  **Request Flow**
1. **Client Request** → Nginx Load Balancer
2. **Load Balancer** → FastAPI Application  
3. **Middleware Pipeline** → Authentication & Validation
4. **Route Handler** → Business Logic Service
5. **Service Layer** → Database & External APIs
6. **Response** → Client (JSON/HTML)

####  **Security Layer**
- **Nginx**: Rate limiting, SSL termination, request filtering
- **JWT Authentication**: Stateless token-based auth
- **CORS Middleware**: Cross-origin request control
- **Input Validation**: Pydantic v2 schemas
- **OTP Verification**: Multi-factor authentication

####  **Data Management**
- **PostgreSQL**: Primary relational database with async operations
- **Redis**: Session storage, caching, and OTP temporary storage
- **Alembic**: Database schema migrations
- **SQLAlchemy 2.0+**: Modern ORM with type hints

####  **Integration Points**
- **Resend**: Professional email delivery and templates
- **Stripe**: Secure payment processing
- **Twilio**: SMS and voice communications
- **AWS S3/GCS**: Scalable file storage solutions

##  Features

- **User Management**: Complete authentication system with JWT tokens, email verification, and OTP support
- **Project Portfolio**: Showcase and manage professional projects
- **CV Builder**: Create and manage professional CVs with multiple formats
- **Job Board**: Browse and apply for project management positions
- **Community**: Professional networking and discussions
- **Industry Insights**: Career guidance and industry-specific information
- **Email Notifications**: Resend integration for transactional emails
- **External Integrations**: Stripe payments, Twilio SMS, AWS/GCS storage

## 🛠️ Tech Stack

- **Backend**: FastAPI 0.104.1 (Python 3.11+)
- **Database**: PostgreSQL with asyncpg
- **ORM**: SQLAlchemy 2.0+ with async support
- **Validation**: Pydantic v2 with `from_attributes=True`
- **Authentication**: JWT with bcrypt password hashing
- **Email**: Resend for transactional emails
- **Payments**: Stripe integration
- **SMS**: Twilio integration  
- **Storage**: AWS S3 / Google Cloud Storage
- **Caching**: Redis support
- **Testing**: pytest with async support

##  Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis (optional, for caching)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Turn_Backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
cp env_template.txt .env
```

Update the `.env` file with your actual configuration values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/turn_db

# JWT Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Service (Resend)
RESEND_API_KEY=re_your_resend_api_key

# Payment Service (Stripe)
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# SMS Service (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-s3-bucket

# Google Cloud Storage (optional)
GOOGLE_CLOUD_CREDENTIALS_PATH=path/to/credentials.json
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_BUCKET=your-gcs-bucket

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
```

### 5. Database Setup

#### Option A: Using Alembic (Recommended)

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

#### Option B: Direct Table Creation

```bash
# Create all tables
python init_db.py create

# Drop all tables (if needed)
python init_db.py drop
```

##  Running the Application

### Development Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

##  API Documentation

### Authentication Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - User login with email/password
- `POST /auth/refresh` - Refresh JWT tokens
- `POST /auth/send-login-otp` - Send OTP for passwordless login
- `POST /auth/verify-login-otp` - Verify OTP and login
- `POST /auth/request-password-reset` - Request password reset
- `POST /auth/send-password-reset-otp` - Send OTP for password reset
- `POST /auth/reset-password-with-otp` - Reset password with OTP
- `POST /auth/verify-email/{token}` - Verify email address
- `POST /auth/resend-verification-email` - Resend verification email
- `POST /auth/change-password` - Change user password
- `POST /auth/logout` - User logout

### User Management

- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `DELETE /users/me` - Delete user account
- `GET /users/{user_id}` - Get user by ID
- `GET /users/` - List users (with pagination)

### Projects

- `POST /projects/` - Create new project
- `GET /projects/` - List projects
- `GET /projects/{project_id}` - Get project details
- `PUT /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project
- `POST /projects/{project_id}/collaborate` - Add collaborator

### CV Management

- `POST /cv/` - Create CV
- `GET /cv/` - List user CVs
- `GET /cv/{cv_id}` - Get CV details
- `PUT /cv/{cv_id}` - Update CV
- `DELETE /cv/{cv_id}` - Delete CV
- `GET /cv/{cv_id}/export` - Export CV (PDF/DOCX)

### Job Board

- `GET /jobs/` - List job postings
- `GET /jobs/{job_id}` - Get job details
- `POST /jobs/{job_id}/apply` - Apply for job
- `GET /jobs/applications/` - Get user applications
- `GET /jobs/recommendations/` - Get job recommendations

##  Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run in verbose mode
pytest -v
```

##  Database Migrations

### Create New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration for custom changes
alembic revision -m "Description of changes"
```

### Apply Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade revision_id

# Downgrade to previous migration
alembic downgrade -1
```

### Migration History

```bash
# Show current migration
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic show head
```

##  Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **Email Verification**: Mandatory email verification for new accounts
- **OTP Support**: One-time passwords for enhanced security
- **Rate Limiting**: API rate limiting (implement with Redis)
- **CORS Configuration**: Configurable cross-origin requests
- **Input Validation**: Pydantic schemas for request validation

##  Email Templates

The application includes HTML email templates for:

- **Welcome Email**: Sent after user registration
- **Email Verification**: Email address confirmation
- **Password Reset**: Secure password reset with tokens
- **Job Alerts**: Personalized job recommendations
- **OTP Codes**: Verification codes for various purposes

##  Docker Deployment

The TURN platform is fully containerized with Docker for easy deployment and scaling.

### Quick Start with Docker

```bash
# Development environment
scripts/docker.sh dev      # Linux/macOS
scripts/docker.bat dev     # Windows

# Production environment  
scripts/docker.sh prod     # Linux/macOS
scripts/docker.bat prod    # Windows
```

### Docker Services

Our Docker setup includes:

| Service | Description | Port | Purpose |
|---------|-------------|------|---------|
| **app** | FastAPI Application | 8000 | Main API server |
| **db** | PostgreSQL Database | 5432 | Primary data storage |
| **redis** | Redis Cache | 6379 | Session & OTP storage |
| **nginx** | Reverse Proxy | 80/443 | Load balancing & SSL |
| **pgadmin** | Database Admin | 5050 | DB management (dev only) |
| **redis-commander** | Redis GUI | 8081 | Cache management (dev only) |

### Development Environment

```bash
# Start development stack with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --profile development up -d

# View logs
docker-compose logs -f app

# Access services
# API: http://localhost:8000
# Docs: http://localhost:8000/docs  
# pgAdmin: http://localhost:5050 (admin@turn.com / admin123)
# Redis Commander: http://localhost:8081
```

### Production Environment

```bash
# Start production stack with Nginx
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --profile production up -d

# Scale application
docker-compose up -d --scale app=3

# View production logs
docker-compose logs --tail=100 -f app
```

### Docker Management Scripts

We provide convenient management scripts:

**Linux/macOS (`scripts/docker.sh`):**
```bash
./scripts/docker.sh dev          # Start development environment
./scripts/docker.sh prod         # Start production environment
./scripts/docker.sh stop         # Stop all services
./scripts/docker.sh logs app     # View app logs
./scripts/docker.sh db-migrate   # Run database migrations
./scripts/docker.sh db-reset     # Reset database
./scripts/docker.sh health       # Check service health
./scripts/docker.sh clean        # Clean up containers/volumes
```

**Windows (`scripts/docker.bat`):**
```batch
scripts\docker.bat dev          # Start development environment
scripts\docker.bat prod         # Start production environment  
scripts\docker.bat stop         # Stop all services
scripts\docker.bat logs app     # View app logs
scripts\docker.bat db-migrate   # Run database migrations
scripts\docker.bat health       # Check service health
```

### Container Architecture

```mermaid
graph TB
    subgraph "Docker Network"
        subgraph "Frontend Layer"
            NGINX[Nginx Container<br/>Port 80/443]
        end
        
        subgraph "Application Layer"
            APP1[FastAPI Container 1<br/>Port 8000]
            APP2[FastAPI Container 2<br/>Port 8000] 
            APP3[FastAPI Container 3<br/>Port 8000]
        end
        
        subgraph "Data Layer"
            DB[PostgreSQL Container<br/>Port 5432]
            REDIS[Redis Container<br/>Port 6379]
        end
        
        subgraph "Development Tools"
            PGADMIN[pgAdmin Container<br/>Port 5050]
            REDIS_CMD[Redis Commander<br/>Port 8081]
        end
    end
    
    NGINX --> APP1
    NGINX --> APP2  
    NGINX --> APP3
    APP1 --> DB
    APP2 --> DB
    APP3 --> DB
    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS
    PGADMIN --> DB
    REDIS_CMD --> REDIS
```

### Production Deployment

#### 1. Environment Setup
```bash
# Copy environment template
cp env_template.txt .env

# Configure production values
nano .env
```

#### 2. SSL Configuration (Production)
```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy SSL certificates
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem

# Update nginx.conf for HTTPS
```

#### 3. Deploy to Production
```bash
# Build and deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --profile production up -d

# Run migrations
docker-compose exec app alembic upgrade head

# Check health
docker-compose exec app curl http://localhost:8000/health
```

#### 4. Scaling
```bash
# Scale FastAPI application
docker-compose up -d --scale app=4

# Check running containers
docker-compose ps
```

### Monitoring & Maintenance

#### Health Checks
```bash
# Check all services
scripts/docker.sh health

# Individual service check
docker-compose exec app curl http://localhost:8000/health
docker-compose exec db pg_isready -U postgres
docker-compose exec redis redis-cli ping
```

#### Log Management
```bash
# View real-time logs
docker-compose logs -f app

# View last 100 lines
docker-compose logs --tail=100 app

# Export logs
docker-compose logs app > app.log
```

#### Database Operations
```bash
# Backup database
docker-compose exec db pg_dump -U postgres turn_db > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres turn_db < backup.sql

# Run migrations
docker-compose exec app alembic upgrade head
```

#### Security Considerations

- **Environment Variables**: Never commit `.env` files
- **SSL Certificates**: Use proper SSL in production
- **Database Security**: Change default passwords
- **Network Isolation**: Use Docker networks
- **Regular Updates**: Keep images updated

##  Development

### Code Style

The project follows these conventions:
- **Formatting**: Black code formatter
- **Linting**: Flake8 for code quality
- **Type Hints**: MyPy for static type checking
- **Import Sorting**: isort for import organization

### Project Structure

```
Turn_Backend/
├── app/
│   ├── api/               # API route modules (deprecated, moved to routes/)
│   ├── routes/            # API route modules
│   ├── core/              # Core application configuration
│   ├── database/          # Database models and connection
│   ├── schemas/           # Pydantic schemas for validation
│   ├── services/          # Business logic and service layer
│   └── main.py           # FastAPI application entry point
├── migrations/            # Alembic database migrations
├── tests/                # Test suite
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
├── env_template.txt      # Environment variables template
├── init_db.py           # Database initialization script
└── README.md            # This file
```

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

##  License

This project is licensed under the MIT License - see the LICENSE file for details.

##  Support

For support and questions:
- Create an issue on GitHub
- Email: support@turn-platform.com
- Documentation: http://localhost:8000/docs

##  Version History

- **v1.0.0** - Initial release with complete API functionality
- **v1.1.0** - Added OTP authentication and external service integrations
- **v1.2.0** - Enhanced email templates and job recommendation system

---


**Built by the TURNVE Team**
