#!/bin/bash

echo "=================================="
echo "Slack-CATestDriveApp Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✓ Python found: $python_version"
else
    echo "✗ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if ODBC Driver is installed
echo ""
echo "Checking ODBC Driver 17 for SQL Server..."
if command -v odbcinst &> /dev/null; then
    odbc_drivers=$(odbcinst -q -d)
    if echo "$odbc_drivers" | grep -q "ODBC Driver 17 for SQL Server"; then
        echo "✓ ODBC Driver 17 for SQL Server is installed"
    else
        echo "✗ ODBC Driver 17 for SQL Server not found"
        echo "  Please install it from: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server"
    fi
else
    echo "⚠ odbcinst command not found. Cannot verify ODBC driver installation."
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
if [[ $? -eq 0 ]]; then
    echo "✓ Virtual environment created"
else
    echo "✗ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [[ $? -eq 0 ]]; then
    echo "✓ Dependencies installed successfully"
else
    echo "✗ Failed to install dependencies"
    exit 1
fi

# Check if .env exists
echo ""
if [ -f ".env" ]; then
    echo "✓ .env file found"
else
    echo "⚠ .env file not found"
    echo "  Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠ IMPORTANT: Please edit .env and add your Slack tokens:"
    echo "  - SLACK_BOT_TOKEN (starts with xoxb-)"
    echo "  - SLACK_APP_TOKEN (starts with xapp-)"
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Slack tokens"
echo "2. Set up your Slack app at https://api.slack.com/apps"
echo "3. Run the app with: python app.py"
echo ""
echo "For detailed instructions, see README.md"
