# Complete Setup Guide - AI Productivity Suite

## 🎯 Project Overview

This is a complete, production-ready **AI Personal Productivity & Workflow Suite** built with Google ADK, demonstrating advanced agentic AI concepts.

### Key Features:
- ✅ Multi-agent architecture with specialized agents
- ✅ Task management with AI-powered prioritization
- ✅ Session & long-term memory management
- ✅ Vector-based semantic search
- ✅ Agent-to-agent communication
- ✅ RESTful API with FastAPI
- ✅ Comprehensive observability & logging
- ✅ Modular, scalable code structure

---

## 📁 Complete File Structure

```
productivity-suite/
├── README.md                          # Main documentation
├── QUICKSTART.md                      # Quick start guide
├── COMPLETE_SETUP_GUIDE.md           # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── .gitignore                        # Git ignore rules
├── docker-compose.yml                # Docker configuration
├── Dockerfile                        # Container image
├── init_project.sh                   # Setup script
│
├── config/
│   ├── __init__.py
│   ├── settings.py                   # App configuration
│   └── logging_config.py             # Logging setup
│
├── src/
│   ├── __init__.py
│   ├── main.py                       # FastAPI application
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Base agent class
│   │   └── task_manager_agent.py    # Task management agent
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── google_search_tool.py    # Web search tool
│   │   └── code_execution_tool.py   # Code execution tool
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── session_manager.py       # Session management (Redis)
│   │   ├── memory_bank.py           # Long-term memory (PostgreSQL)
│   │   └── vector_store.py          # Vector DB (ChromaDB)
│   │
│   └── models/
│       ├── __init__.py
│       ├── schemas.py               # Pydantic models
│       └── database.py              # SQLAlchemy models
│
├── scripts/
│   └── setup_db.py                  # Database initialization
│
└── tests/
    ├── __init__.py
    └── test_agents.py               # Agent tests
```

---

## 🚀 Installation Methods

### Method 1: Automated Setup (Recommended)

```bash
# 1. Create project directory
mkdir productivity-suite
cd productivity-suite

# 2. Copy all files to this directory
#    (Use the artifacts I provided above)

# 3. Run setup script
chmod +x init_project.sh
./init_project.sh

# 4. Configure environment
nano .env  # Add your GOOGLE_API_KEY

# 5. Initialize database
python scripts/setup_db.py

# 6. Start application
python src/main.py
```

### Method 2: Manual Setup

#### Step 1: Create Virtual Environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 3: Setup Databases

**PostgreSQL:**
```bash
# macOS
brew install postgresql
brew services start postgresql
createdb productivity_db

# Ubuntu
sudo apt-get install postgresql
sudo service postgresql start
sudo -u postgres createdb productivity_db

# Windows
# Download from postgresql.org and install
# Create database using pgAdmin or psql
```

**Redis:**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo service redis-server start

# Windows
# Use WSL or download from redis.io
```

#### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env and add:
# GOOGLE_API_KEY=your-actual-key
```

#### Step 5: Initialize Database
```bash
python scripts/setup_db.py
```

#### Step 6: Run Application
```bash
cd src
python main.py
```

### Method 3: Docker Setup

```bash
# 1. Create .env file with GOOGLE_API_KEY

# 2. Start all services
docker-compose up -d

# 3. Initialize database
docker-compose exec app python scripts/setup_db.py

# 4. View logs
docker-compose logs -f app

# Access API at http://localhost:8000
```

---

## 🧪 Testing the Application

### 1. Check Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-27T...",
  "version": "1.0.0"
}
```

### 2. Create a User
```bash
curl -X POST "http://localhost:8000/api/users/create?name=John%20Doe&email=john@example.com"
```

Save the `user_id` from the response!

### 3. Create a Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "action": "create",
    "data": {
      "title": "Complete project documentation",
      "description": "Write comprehensive API docs",
      "priority": "high",
      "due_date": "2025-12-01T17:00:00"
    }
  }'
```

### 4. List Tasks
```bash
curl "http://localhost:8000/api/tasks/YOUR_USER_ID"
```

### 5. Chat with AI
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "message": "Show me my tasks"
  }'
```

### 6. Complete a Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "action": "complete",
    "data": {
      "task_id": "TASK_ID_FROM_LIST"
    }
  }'
```

---

## 📖 API Documentation

Once running, access interactive API docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎓 Understanding the Code

### Agent Architecture

The system uses a **multi-agent architecture** where each agent has specific responsibilities:

1. **BaseAgent** (`src/agents/base_agent.py`)
   - Abstract base class for all agents
   - Handles execution, logging, error handling
   - Provides LLM interface and context management

2. **TaskManagerAgent** (`src/agents/task_manager_agent.py`)
   - Manages task CRUD operations
   - AI-powered task extraction from natural language
   - Prioritization and suggestions

### Memory System

Three-tier memory architecture:

1. **Session Memory** (Redis)
   - Short-term conversation context
   - Active session data
   - TTL-based expiration

2. **Long-term Memory** (PostgreSQL)
   - User profiles, tasks, events
   - Historical data
   - Relational queries

3. **Vector Memory** (ChromaDB)
   - Semantic search capabilities
   - Embeddings for tasks and notes
   - Similarity-based retrieval

### Tool System

Modular tool architecture:

1. **GoogleSearchTool** - Web information retrieval
2. **CodeExecutionTool** - Safe Python execution
3. **CalendarTool** - Schedule management (extendable)
4. **EmailTool** - Email operations (extendable)

---

## 🔧 Development Workflow

### Adding a New Agent

1. Create file in `src/agents/`
2. Extend `BaseAgent`
3. Implement `process()` method
4. Register in orchestrator

Example:
```python
from src.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MyAgent",
            description="What this agent does"
        )
    
    async def process(self, user_id: str, input_data: dict):
        # Your logic here
        return {"result": "success"}
```

### Adding a New Tool

1. Create file in `src/tools/`
2. Implement tool interface
3. Add to agent's tool list

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_agents.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

---

## 🐛 Troubleshooting

### Database Connection Issues

**Problem**: `connection refused` to PostgreSQL
```bash
# Check if running
pg_isready

# Start PostgreSQL
brew services start postgresql  # macOS
sudo service postgresql start   # Ubuntu
```

**Problem**: Wrong credentials
```bash
# Update .env file
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/productivity_db
```

### Redis Connection Issues

**Problem**: Can't connect to Redis
```bash
# Check if running
redis-cli ping  # Should return PONG

# Start Redis
brew services start redis  # macOS
sudo service redis-server start  # Ubuntu
```

### Google API Issues

**Problem**: Invalid API key
```bash
# Verify key is set
cat .env | grep GOOGLE_API_KEY

# Test key
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('OK')"
```

### Import Errors

**Problem**: Module not found
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt

# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## 📊 Monitoring & Observability

### View Logs

```bash
# Application logs
tail -f logs/app.log

# Docker logs
docker-compose logs -f app
```

### Database Queries

```bash
# Connect to PostgreSQL
psql -U postgres -d productivity_db

# List tables
\dt

# Query tasks
SELECT * FROM tasks LIMIT 10;
```

### Redis Monitoring

```bash
# Connect to Redis
redis-cli

# View keys
KEYS session:*

# Get session data
GET session:user123:conversation_context
```

---

## 🚢 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Use strong `SECRET_KEY`
- [ ] Setup proper database credentials
- [ ] Configure CORS properly
- [ ] Enable HTTPS
- [ ] Setup monitoring (Prometheus/Grafana)
- [ ] Configure backups
- [ ] Setup logging aggregation

### Deploy to Cloud

**Google Cloud Platform:**
```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/productivity-suite

# Deploy to Cloud Run
gcloud run deploy productivity-suite \
  --image gcr.io/PROJECT_ID/productivity-suite \
  --platform managed \
  --region us-central1
```

**AWS:**
```bash
# Build image
docker build -t productivity-suite .

# Push to ECR
# Deploy to ECS/EKS
```

---

## 📚 Additional Resources

- [Google ADK Documentation](https://ai.google.dev/adk)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [ChromaDB Documentation](https://docs.trychroma.com/)

---

## 🤝 Next Steps

1. ✅ Complete setup and test basic functionality
2. ✅ Add more agents (Calendar, Email, Notes)
3. ✅ Implement agent orchestration patterns
4. ✅ Add frontend UI (React/Vue)
5. ✅ Setup CI/CD pipeline
6. ✅ Add comprehensive tests
7. ✅ Deploy to production

---

## 💡 Tips for Success

1. **Start Simple**: Get basic task management working first
2. **Test Incrementally**: Test each component as you build
3. **Use API Docs**: Swagger UI is your friend
4. **Check Logs**: Always monitor logs during development
5. **Iterate**: Add features one at a time

---

## ✅ Success Criteria

Your setup is successful when:
- ✅ Health endpoint returns 200 OK
- ✅ You can create a user
- ✅ You can create and list tasks
- ✅ Chat endpoint responds
- ✅ Database queries work
- ✅ Redis sessions persist

---

**Need Help?** Review the code comments, check logs, and ensure all services are running!

Happy coding! 🚀