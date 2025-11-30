# Quick Start Guide - AI Productivity Suite

Get up and running in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- PostgreSQL installed and running
- Redis installed and running
- Google API Key

## Step-by-Step Setup

### 1. Environment Setup (2 minutes)

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your-actual-key-here
```

**Minimum Required Configuration:**
```env
GOOGLE_API_KEY=your-google-api-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/productivity_db
REDIS_URL=redis://localhost:6379/0
```

### 3. Start Database Services (30 seconds)

```bash
# Start PostgreSQL (if not running)
# macOS: brew services start postgresql
# Ubuntu: sudo service postgresql start
# Windows: Start from Services or use Docker

# Start Redis (if not running)
# macOS: brew services start redis
# Ubuntu: sudo service redis-server start
# Windows: redis-server or use Docker
```

**OR use Docker Compose:**
```bash
docker-compose up -d postgres redis
```

### 4. Initialize Database (30 seconds)

```bash
python scripts/setup_db.py
```

When prompted, type `y` to seed sample data. This creates a test user for you.

### 5. Start Application (30 seconds)

```bash
cd src
python main.py
```

Your API is now running at: `http://localhost:8000`

## Quick Test

### 1. Open your browser or use curl

**Check Health:**
```bash
curl http://localhost:8000/health
```

**Get API Documentation:**
Open browser: `http://localhost:8000/docs`

### 2. Test with Sample User

The setup script creates a test user. The user ID is saved in `.user_id` file.

```bash
# Get your user ID
cat .user_id

# Or manually get it from setup output
```

**Create a Task:**
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "PASTE_YOUR_USER_ID_HERE",
    "action": "create",
    "data": {
      "title": "Test Task",
      "description": "My first task",
      "priority": "high"
    }
  }'
```

**List Tasks:**
```bash
curl http://localhost:8000/api/tasks/PASTE_YOUR_USER_ID_HERE
```

**Chat with AI:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "PASTE_YOUR_USER_ID_HERE",
    "message": "Show me my tasks"
  }'
```

## Using the Interactive API Docs

1. Open `http://localhost:8000/docs` in your browser
2. Click on any endpoint (e.g., `/api/tasks`)
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. See the response!

## Common Commands

```bash
# Start application
python src/main.py

# Run with auto-reload (development)
uvicorn src.main:app --reload

# Run tests
pytest tests/ -v

# Check logs
tail -f logs/app.log

# Reset database
python scripts/setup_db.py
```

## Docker Quick Start

If you prefer Docker:

```bash
# Start everything
docker-compose up -d

# Initialize database
docker-compose exec app python scripts/setup_db.py

# View logs
docker-compose logs -f app

# Stop everything
docker-compose down
```

## Troubleshooting

**Problem: Can't connect to PostgreSQL**
```bash
# Check if running
pg_isready

# If not, start it
brew services start postgresql  # macOS
```

**Problem: Can't connect to Redis**
```bash
# Check if running
redis-cli ping

# Should return: PONG
```

**Problem: Import errors**
```bash
# Make sure you're in the virtual environment
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: Google API key error**
```bash
# Verify key is set
echo $GOOGLE_API_KEY

# Or check .env file
cat .env | grep GOOGLE_API_KEY
```

## Next Steps

1. ✅ Explore the API docs at `/docs`
2. ✅ Create your own user
3. ✅ Test task creation and management
4. ✅ Try the chat interface
5. ✅ Review the code in `src/agents/`
6. ✅ Add more agents (Calendar, Email, etc.)
7. ✅ Build a frontend UI

## Getting Help

- Check `README.md` for detailed documentation
- Review code comments in `src/`
- Look at example requests in API docs
- Check logs in `logs/app.log`

## Example Workflow

```bash
# 1. Create user
curl -X POST "http://localhost:8000/api/users/create?name=John&email=john@test.com"
# Save the user_id from response

# 2. Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "action": "create",
    "data": {"title": "Complete presentation", "priority": "high"}
  }'

# 3. List tasks
curl http://localhost:8000/api/tasks/YOUR_USER_ID

# 4. Complete task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "action": "complete",
    "data": {"task_id": "TASK_ID_FROM_PREVIOUS_RESPONSE"}
  }'
```

## VS Code Setup

1. Open project in VS Code
2. Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter" → Choose venv
3. Install recommended extensions:
   - Python
   - Pylance
   - REST Client (for testing APIs)

Happy coding! 🚀