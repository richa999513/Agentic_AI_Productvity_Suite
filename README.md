# AI Personal Productivity & Workflow Suite

A comprehensive multi-agent AI system for personal productivity management, built with Google ADK. This project demonstrates advanced agentic AI concepts including agent orchestration, memory management, tool usage, and agent-to-agent communication.

## 🎯 Features

- **Multi-Agent Architecture**: Specialized agents for tasks, calendar, emails, notes, and analytics
- **Intelligent Task Management**: AI-powered task creation, prioritization, and suggestions
- **Semantic Search**: Vector-based search across tasks and notes
- **Session & Long-term Memory**: Redis for sessions, PostgreSQL for persistent data
- **Agent-to-Agent Communication**: Structured A2A messaging protocol
- **Observability**: Comprehensive logging, metrics, and tracing
- **RESTful API**: FastAPI-based endpoints for all operations

## 🏗️ Architecture

```
User Interface
      ↓
FastAPI Application
      ↓
Agent Orchestrator
      ↓
┌─────────────┬──────────────┬─────────────┬────────────┐
│   Task      │   Calendar   │    Email    │   Note     │
│  Manager    │    Agent     │    Agent    │   Agent    │
└─────────────┴──────────────┴─────────────┴────────────┘
      ↓              ↓              ↓            ↓
┌─────────────────────────────────────────────────────┐
│              Tools Layer                             │
│  • Google Search  • Code Execution  • Notifications  │
└─────────────────────────────────────────────────────┘
      ↓
┌─────────────────────────────────────────────────────┐
│              Memory & Storage                        │
│  • Redis (Sessions)  • PostgreSQL  • ChromaDB       │
└─────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Google API Key (for Gemini/ADK)
- VS Code (recommended)

## 🚀 Installation & Setup

### Step 1: Clone and Setup Environment

```bash
# Create project directory
mkdir productivity-suite
cd productivity-suite

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Required: GOOGLE_API_KEY, DATABASE_URL, REDIS_URL
```

**Important Environment Variables:**
```env
GOOGLE_API_KEY=your-actual-api-key-here
DATABASE_URL=postgresql://postgres:password@localhost:5432/productivity_db
REDIS_URL=redis://localhost:6379/0
```

### Step 4: Setup Databases

#### PostgreSQL Setup

```bash
# Install PostgreSQL (if not already installed)
# On macOS: brew install postgresql
# On Ubuntu: sudo apt-get install postgresql
# On Windows: Download from postgresql.org

# Start PostgreSQL service
# On macOS: brew services start postgresql
# On Ubuntu: sudo service postgresql start
# On Windows: Start from Services

# Create database
psql -U postgres -c "CREATE DATABASE productivity_db;"

# Run database initialization
python scripts/setup_db.py
```

#### Redis Setup

```bash
# Install Redis (if not already installed)
# On macOS: brew install redis
# On Ubuntu: sudo apt-get install redis-server
# On Windows: Use WSL or download from redis.io

# Start Redis
# On macOS: brew services start redis
# On Ubuntu: sudo service redis-server start
# On Windows: redis-server
```

### Step 5: Initialize Database Schema

Create `scripts/setup_db.py`:

```python
"""Initialize database schema."""
from src.models.database import Base
from src.memory.memory_bank import memory_bank

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(memory_bank.engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
```

Run:
```bash
python scripts/setup_db.py
```

### Step 6: Verify Installation

```bash
# Test imports
python -c "import google.generativeai; print('Google ADK: OK')"
python -c "import sqlalchemy; print('SQLAlchemy: OK')"
python -c "import redis; print('Redis: OK')"
python -c "import chromadb; print('ChromaDB: OK')"
```

## 🏃 Running the Application

### Development Mode

```bash
# Start the FastAPI server
cd src
python main.py

# Or using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Production Mode

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🧪 Testing the System

### 1. Check Health

```bash
curl http://localhost:8000/health
```

### 2. Create a User

```bash
curl -X POST "http://localhost:8000/api/users/create?name=John Doe&email=john@example.com"
```

Response:
```json
{
  "user_id": "uuid-here",
  "name": "John Doe",
  "email": "john@example.com",
  "message": "User created successfully"
}
```

### 3. Create a Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your-user-id",
    "action": "create",
    "data": {
      "title": "Complete project proposal",
      "description": "Write and submit Q4 project proposal",
      "priority": "high",
      "due_date": "2025-12-01T17:00:00"
    }
  }'
```

### 4. List Tasks

```bash
curl -X GET "http://localhost:8000/api/tasks/your-user-id"
```

### 5. Chat with AI Assistant

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "your-user-id",
    "message": "Show me my tasks"
  }'
```

## 📚 API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🗂️ Project Structure

```
productivity-suite/
├── config/                 # Configuration files
│   ├── settings.py        # Application settings
│   └── logging_config.py  # Logging configuration
├── src/
│   ├── agents/            # Agent implementations
│   │   ├── base_agent.py
│   │   └── task_manager_agent.py
│   ├── tools/             # Tool implementations
│   │   ├── google_search_tool.py
│   │   └── code_execution_tool.py
│   ├── memory/            # Memory management
│   │   ├── session_manager.py
│   │   ├── memory_bank.py
│   │   └── vector_store.py
│   ├── models/            # Data models
│   │   ├── schemas.py
│   │   └── database.py
│   └── main.py            # FastAPI application
├── scripts/               # Utility scripts
│   └── setup_db.py
├── tests/                 # Test files
├── .env.example          # Example environment file
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Formatting

```bash
# Install dev dependencies
pip install black flake8 mypy

# Format code
black src/

# Lint
flake8 src/

# Type check
mypy src/
```

## 🐳 Docker Support (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: productivity_db
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6
    ports:
      - "6379:6379"

  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/productivity_db
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./src:/app/src

volumes:
  postgres_data:
```

Run:
```bash
docker-compose up -d
```

## 🎓 Learning Objectives Demonstrated

This project demonstrates:

1. **Agent Design Patterns**
   - Base agent abstraction
   - Specialized agent implementations
   - Agent-to-agent communication

2. **Memory Management**
   - Short-term memory (Redis sessions)
   - Long-term memory (PostgreSQL)
   - Vector memory (ChromaDB for semantic search)

3. **Tool Integration**
   - Google Search for information retrieval
   - Code execution for computations
   - Custom API integrations

4. **Observability**
   - Structured logging
   - Execution tracking
   - Performance metrics

5. **Scalability**
   - Modular architecture
   - Database optimization
   - Async/await patterns

## 🚧 Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check if PostgreSQL is running
pg_isready

# Verify connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

**2. Redis Connection Error**
```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG
```

**3. Google API Key Error**
```bash
# Verify API key is set
echo $GOOGLE_API_KEY

# Test with simple script
python -c "import google.generativeai as genai; genai.configure(api_key='your-key'); print('OK')"
```

**4. Import Errors**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## 📖 Next Steps

1. **Add More Agents**: Calendar, Email, Note agents
2. **Implement Orchestration**: Complex multi-agent workflows
3. **Add UI**: React/Vue frontend
4. **Deploy**: Cloud deployment (GCP, AWS, Azure)
5. **Monitoring**: Prometheus + Grafana setup

## 🤝 Contributing

This is a learning project. Feel free to extend and modify!

## 📄 License

MIT License - Feel free to use for learning and development

## 🙏 Acknowledgments

- Built with Google ADK
- Inspired by multi-agent AI research
- Based on productivity management best practices