#!/bin/bash

# AI Productivity Suite - Project Initialization Script
# This script sets up the complete project structure

echo "=========================================="
echo "AI Productivity Suite - Project Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if Python is installed
echo "Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi
print_success "Python 3 found"

# Create project directory structure
echo ""
echo "Creating project structure..."

# Create all necessary directories
directories=(
    "src/agents"
    "src/tools"
    "src/memory"
    "src/models"
    "src/orchestration"
    "src/observability"
    "src/utils"
    "config"
    "scripts"
    "tests"
    "docs"
    "data/chroma"
    "logs"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    touch "$dir/__init__.py" 2>/dev/null
done

print_success "Project structure created"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -eq 0 ]; then
    print_success "Virtual environment created"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

if [ $? -eq 0 ]; then
    print_success "Virtual environment activated"
else
    print_warning "Could not activate virtual environment automatically"
    echo "Please run: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
echo "(This may take a few minutes...)"

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    print_success ".env file created"
    print_warning "Please edit .env and add your GOOGLE_API_KEY"
else
    print_warning ".env file already exists"
fi

# Check if PostgreSQL is running
echo ""
echo "Checking database services..."
if command -v pg_isready &> /dev/null; then
    if pg_isready > /dev/null 2>&1; then
        print_success "PostgreSQL is running"
    else
        print_warning "PostgreSQL is not running. Please start it:"
        echo "  macOS: brew services start postgresql"
        echo "  Ubuntu: sudo service postgresql start"
        echo "  Docker: docker-compose up -d postgres"
    fi
else
    print_warning "PostgreSQL not found. Install it or use Docker"
fi

# Check if Redis is running
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is running"
    else
        print_warning "Redis is not running. Please start it:"
        echo "  macOS: brew services start redis"
        echo "  Ubuntu: sudo service redis-server start"
        echo "  Docker: docker-compose up -d redis"
    fi
else
    print_warning "Redis not found. Install it or use Docker"
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Summary"
echo "=========================================="
print_success "Project structure created"
print_success "Virtual environment created"
print_success "Dependencies installed"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GOOGLE_API_KEY"
echo "2. Start PostgreSQL and Redis (if not running)"
echo "3. Run: python scripts/setup_db.py"
echo "4. Run: python src/main.py"
echo ""
echo "For detailed instructions, see README.md or QUICKSTART.md"
echo "=========================================="