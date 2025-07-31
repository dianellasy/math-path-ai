# 🎓 MathPath AI - Teammate Setup Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [AWS Configuration](#aws-configuration)
5. [Testing & Verification](#testing--verification)
6. [Troubleshooting](#troubleshooting)
7. [Project Structure](#project-structure)
8. [Development Workflow](#development-workflow)

---

## 🚀 Project Overview

**MathPath AI** is a Cal Poly math placement chatbot that provides personalized assistance to students. The application uses AWS Bedrock for AI-powered responses and includes student authentication, personalized data, and policy information.

### ✨ Key Features
- **Student Authentication** - Email-based sign-in system
- **AI-Powered Responses** - AWS Bedrock integration
- **Personalized Answers** - Based on individual student records
- **Policy Information** - From Cal Poly knowledge base
- **Clean UI** - Professional Cal Poly branding
- **Team Collaboration** - Separated UI/Backend architecture

---

## 🔧 Prerequisites

### Required Software
- **Python 3.8+** (3.13 recommended)
- **Git** (for cloning repository)
- **AWS CLI** (for AWS configuration)
- **Text Editor** (VS Code, Sublime, etc.)

### Required Accounts
- **GitHub Account** (to access repository)
- **AWS Account** (with Bedrock access)
- **Cal Poly SSO** (for AWS authentication)

---

## 📥 Step-by-Step Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/dianellasy/math-path-ai.git

# Navigate to project directory
cd math-path-ai

# Switch to the working branch
git checkout yash
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Create Environment File

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your values
nano .env  # or use your preferred editor
```

**Add this content to `.env`:**
```bash
AWS_DEFAULT_REGION=us-west-2
AWS_PROFILE=calpoly
KNOWLEDGE_BASE_ID=O6LIPBUDTM
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

---

## 🔐 AWS Configuration

### Option A: AWS SSO (Recommended)

```bash
# Install AWS CLI (if not already installed)
brew install awscli  # On macOS
# OR download from https://aws.amazon.com/cli/

# Configure SSO profile
aws configure sso

# Enter the following details:
# Profile name: calpoly
# SSO start URL: [Your Cal Poly SSO URL]
# SSO region: us-west-2
# Role name: [Your AWS role]
# Account ID: [Your AWS account ID]
```

### Option B: AWS Access Keys (Alternative)

```bash
# Configure AWS credentials
aws configure --profile calpoly

# Enter your credentials:
# AWS Access Key ID: [Your access key]
# AWS Secret Access Key: [Your secret key]
# Default region: us-west-2
# Default output format: json
```

### Verify AWS Configuration

```bash
# Check your AWS configuration
aws configure list --profile calpoly

# Test AWS SSO login (if using SSO)
aws sso login --profile calpoly
```

---

## ✅ Testing & Verification

### 1. Test AWS Bedrock Connection

```bash
# Test Bedrock client creation
python3 -c "from backend import get_bedrock_client; client = get_bedrock_client(); print('✅ AWS Bedrock client created successfully!')"
```

### 2. Test Environment Variables

```bash
# Test environment loading
python3 -c "from backend import validate_environment; validate_environment(); print('✅ Environment variables are valid!')"
```

### 3. Run the Application

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run the application
streamlit run ui.py
```

### 4. Test the Application

1. **Open your browser** to `http://localhost:8501`
2. **Enter a test email:**
   - `alex.martinez@example.com`
   - `jordan.lee@example.com`
   - `nina.wu@example.com`
3. **Ask test questions:**
   - "What's my current status?"
   - "Have you received my SAT scores?"
   - "When is my MAPE scheduled?"
   - "What math placement policies apply to me?"

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Issue: "streamlit command not found"
```bash
# Solution: Activate virtual environment
source venv/bin/activate
pip install streamlit
```

#### Issue: "AWS credentials not found"
```bash
# Solution: Configure AWS
aws configure --profile calpoly
# OR
aws sso login --profile calpoly
```

#### Issue: "Module not found" errors
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

#### Issue: "Port already in use"
```bash
# Solution: Use different port
streamlit run ui.py --server.port 8502
```

#### Issue: "Bedrock client creation failed"
```bash
# Solution: Check AWS configuration
aws configure list --profile calpoly
aws sso login --profile calpoly  # if using SSO
```

### Environment Variables Checklist

Ensure your `.env` file contains:
- ✅ `AWS_DEFAULT_REGION=us-west-2`
- ✅ `AWS_PROFILE=calpoly`
- ✅ `KNOWLEDGE_BASE_ID=O6LIPBUDTM`
- ✅ `BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0`

---

## 📁 Project Structure

```
math-path-ai/
├── ui.py                 # Main Streamlit UI (UI Developer)
├── backend.py            # Business logic & AWS integration (Backend Developer)
├── mock_students.json    # Student database with test data
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .env                 # Your environment variables (create this)
├── .gitignore          # Git ignore rules
├── README.md           # Project documentation
└── calpoly-logo.png    # Cal Poly branding assets
```

### File Descriptions

- **`ui.py`**: Main Streamlit application with user interface
- **`backend.py`**: AWS Bedrock integration and business logic
- **`mock_students.json`**: Test student data for development
- **`requirements.txt`**: Python package dependencies
- **`.env`**: Environment variables (create from `.env.example`)

---

## 👥 Development Workflow

### For UI Developer
- **Primary file**: `ui.py`
- **Focus areas**: User interface, styling, user experience
- **Dependencies**: Streamlit components, CSS styling

### For Backend Developer
- **Primary file**: `backend.py`
- **Focus areas**: AWS integration, business logic, data processing
- **Dependencies**: AWS SDK, data processing libraries

### Collaboration Guidelines
1. **Work on separate files** to avoid conflicts
2. **Test changes locally** before pushing
3. **Use the same AWS credentials** for consistency
4. **Follow the existing code structure**

---

## 🎯 Quick Start Commands

```bash
# Complete setup in one go
git clone https://github.com/dianellasy/math-path-ai.git
cd math-path-ai
git checkout yash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
aws sso login --profile calpoly
streamlit run ui.py
```

---

## 📞 Support

### If You Need Help
1. **Check this guide** for common solutions
2. **Verify AWS credentials** with `aws configure list --profile calpoly`
3. **Test Bedrock connection** with the Python test command
4. **Check environment variables** in your `.env` file

### Contact Information
- **Repository**: https://github.com/dianellasy/math-path-ai
- **Branch**: `yash`
- **Main Developer**: Yash

---

## 🎉 Success Checklist

- ✅ Repository cloned successfully
- ✅ Virtual environment created and activated
- ✅ Dependencies installed
- ✅ Environment file created with correct values
- ✅ AWS credentials configured
- ✅ Bedrock connection tested successfully
- ✅ Application runs without errors
- ✅ Can authenticate with test emails
- ✅ Can ask questions and receive responses

**Congratulations! You're ready to develop MathPath AI! 🚀** 