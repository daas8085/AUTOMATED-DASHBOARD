#!/bin/bash

# Automated Dashboard Setup Script

set -e  # Exit on error

echo "🚀 Setting up Automated Dashboard..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_message "Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [[ $python_major -lt 3 ]] || [[ $python_major -eq 3 && $python_minor -lt 9 ]]; then
    print_error "Python 3.9 or higher is required. Found Python $python_version"
    exit 1
fi

print_message "Python $python_version detected."

# Create virtual environment
print_message "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_message "Virtual environment created."
else
    print_message "Virtual environment already exists."
fi

# Activate virtual environment
print_message "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_message "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_message "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_message "Production dependencies installed."
else
    print_error "requirements.txt not found!"
    exit 1
fi

if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
    print_message "Development dependencies installed."
fi

# Install pre-commit hooks
print_message "Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    print_message "Pre-commit hooks installed."
fi

# Create necessary directories
print_message "Creating project directories..."
mkdir -p data
mkdir -p logs
mkdir -p infrastructure/airflow_logs
mkdir -p infrastructure/airflow_config

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_message "Creating .env file from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please update .env file with your configuration."
    else
        print_error ".env.example not found!"
    fi
else
    print_message ".env file already exists."
fi

# Initialize database
print_message "Initializing database..."
if [ -f "scripts/init_db.py" ]; then
    python scripts/init_db.py
else
    print_warning "Database initialization script not found."
fi

# Generate sample data
print_message "Generating sample data..."
if [ -f "scripts/generate_data.py" ]; then
    python scripts/generate_data.py
else
    print_warning "Data generation script not found."
fi

# Set execute permissions for scripts
print_message "Setting execute permissions..."
chmod +x scripts/*.sh 2>/dev/null || true

# Run tests
print_message "Running tests..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short || print_warning "Some tests failed."
else
    print_warning "pytest not found. Skipping tests."
fi

print_message ""
print_message "🎉 Setup completed successfully!"
print_message ""
print_message "Next steps:"
print_message "1. Update .env file with your configuration"
print_message "2. Run 'make docker-up' to start Docker services"
print_message "3. Run 'make run' to start the dashboard locally"
print_message "4. Access dashboard at http://localhost:8501"
print_message ""
print_message "For Docker deployment:"
print_message "  - Dashboard: http://localhost:8501"
print_message "  - Airflow: http://localhost:8080"
print_message "  - Grafana: http://localhost:3000 (admin/admin)"
print_message ""