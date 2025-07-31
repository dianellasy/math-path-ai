#!/bin/bash

# 🎓 MathPath AI - Quick Setup Script
# This script automates the setup process for new team members

echo "🚀 Welcome to MathPath AI Setup!"
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

echo "✅ Git found: $(git --version)"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "⚠️  AWS CLI not found. You'll need to install it manually:"
    echo "   macOS: brew install awscli"
    echo "   Or download from: https://aws.amazon.com/cli/"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ AWS CLI found: $(aws --version)"
fi

# Create virtual environment
echo ""
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: You need to edit the .env file with your AWS credentials!"
    echo "   Open .env and update the following values:"
    echo "   - AWS_DEFAULT_REGION=us-west-2"
    echo "   - AWS_PROFILE=calpoly"
    echo "   - KNOWLEDGE_BASE_ID=O6LIPBUDTM"
    echo "   - BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0"
    echo ""
    read -p "Press Enter when you've updated the .env file..."
else
    echo "✅ .env file already exists"
fi

# Test AWS configuration
echo ""
echo "🔐 Testing AWS configuration..."
if aws configure list --profile calpoly &> /dev/null; then
    echo "✅ AWS profile 'calpoly' found"
else
    echo "⚠️  AWS profile 'calpoly' not found"
    echo "   You'll need to configure AWS credentials:"
    echo "   aws configure --profile calpoly"
    echo "   OR"
    echo "   aws configure sso"
fi

# Test Bedrock connection
echo ""
echo "🧪 Testing AWS Bedrock connection..."
python3 -c "from backend import get_bedrock_client; client = get_bedrock_client(); print('✅ AWS Bedrock client created successfully!')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ AWS Bedrock connection successful!"
else
    echo "❌ AWS Bedrock connection failed"
    echo "   Please check your AWS credentials and .env file"
fi

echo ""
echo "🎉 Setup complete!"
echo "=================="
echo ""
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the app: streamlit run ui.py"
echo "3. Open browser to: http://localhost:8501"
echo ""
echo "Test emails:"
echo "- alex.martinez@example.com"
echo "- jordan.lee@example.com"
echo "- nina.wu@example.com"
echo ""
echo "For detailed instructions, see: TEAMMATE_SETUP_GUIDE.md" 