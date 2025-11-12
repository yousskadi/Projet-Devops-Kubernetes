#!/bin/bash
# Setup script for development environment

set -e

echo "🚀 Setting up development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11 or higher is required. Current version: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=storedb
DB_USER=admin
DB_PASSWORD=password

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_RELOAD=true

# Security
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=true

# PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=storedb

# PGAdmin
PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin
EOF
    echo "✅ .env file created. Please update it with your configuration."
else
    echo "✅ .env file already exists."
fi

# Initialize Alembic
echo "🗄️  Initializing Alembic..."
alembic init alembic || echo "Alembic already initialized"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head || echo "No migrations to run"

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v || echo "Tests failed, but continuing..."

echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the development server, run:"
echo "  uvicorn app:app --reload"
echo ""
echo "To run tests, run:"
echo "  pytest tests/ -v"

