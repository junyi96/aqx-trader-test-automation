#!/bin/bash
# Setup script for AQX Trader Test Automation Framework

echo "=========================================="
echo "AQX Trader Test Automation Framework Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python -m venv .venv
echo "Virtual environment created!"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo "Virtual environment activated!"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Dependencies installed!"
echo ""

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install
echo "Browsers installed!"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ".env file created! Please edit it with your credentials."
else
    echo ".env file already exists."
fi
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p reports screenshots traces logs
echo "Directories created!"
echo ""

echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: source .venv/bin/activate"
echo "3. Run tests: pytest"
echo ""
echo "For more information, see README_NEW.md"