#!/bin/bash

# Setup script for RAG Test Case Management System

echo "=================================================="
echo "RAG Test Case Management System - Setup"
echo "=================================================="

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version

# Create virtual environment (optional but recommended)
echo ""
read -p "Create virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your Azure OpenAI credentials!"
    echo ""
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p chroma_db knowledge_base output
echo "✓ Created directories"

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Azure OpenAI credentials"
echo "2. Run the application: streamlit run app.py"
echo "3. Or try the example: python example.py"
echo ""
