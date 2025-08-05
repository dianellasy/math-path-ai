

# 🎓 MathPath AI - Cal Poly Math Placement Assistant
A Streamlit-based AI chatbot that helps Cal Poly SLO students with math placement questions and provides personalized guidance based on their academic records.

With 5,500 incoming students at Cal Poly SLO, students must be placed in a college math course. Many students have questions as to how they are being placed and if they need to take the Math Placement Exam (MAPE). Over 750+ emails and calls are directed to one staff member to answer questions about math placement. To combat the slow responses for the multiple repetitive questions, we created a chatbot that would answer students' most pressing, frequently asked questions regarding math placement in SLO. 

[![View Presentation](https://img.shields.io/badge/View_Presentation-Click_Here-blue?style=for-the-badge&logo=canva)](https://www.canva.com/design/DAGuxeqEl0M/GzGb4GXGAS9IBDf2XVSHuQ/view?utm_content=DAGuxeqEl0M&utm_campaign=designshare&utm_medium=link&utm_source=viewer)

---

## 📚 Table of Contents
1. [Features](#-features)
2. [Architecture](#-architecture)
3. [Setup Instructions](#-setup-instructions)
   - [Technologies Used](#-technologies-used)
   - [Prerequisites](#-prerequisites)
   - [Installation](#-installation)
4. [Usage](#usage)
   - [Test Emails](#test-emails)

---

## ✨ Features

- **Student Authentication**: Email-based sign-in using mock student data
- **Personalized Responses**: Contextual answers based on student records
- **AWS Bedrock Integration**: Connects to Bedrock models and a knowledge base
- **Citation System**: Displays source policies and metadata
- **Real-Time Chat Interface**: Interactive Streamlit UI
- **Separation of Concerns**: Clear UI/backend division for collaboration

---

## 🧱 Architecture

### Backend Developer (`backend.py`)
- AWS Bedrock + Knowledge Base integration  
- Prompt engineering & data validation  
- Core logic for interpreting user input  
- Student status flag derivation

### UI Developer (`ui.py`)
- Streamlit app frontend  
- Chat interface and styling  
- User sign-in and experience flow  
- Presentation of AI-generated answers

---

## ⚙️ Setup Instructions
### 🧰 Technologies Used

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-app-red?logo=streamlit)
![Boto3](https://img.shields.io/badge/Boto3-AWS%20SDK-orange?logo=amazon-aws)
![Dotenv](https://img.shields.io/badge/python--dotenv-env%20management-brightgreen)

### 🔑 Prerequisites

- **Python 3.8+** (3.13 recommended)
- **Git**
- **AWS CLI v2**
- **AWS Account** with Bedrock + Knowledge Base access
- **Text Editor** (VS Code, Sublime, etc.)

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/dianellasy/math-path-ai.git
cd math-path-ai

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```


## Usage

1. **Sign In**: Enter your Cal Poly email address
2. **Ask Questions**: Ask about your math placement status, requirements, or policies
3. **Get Personalized Answers**: The AI uses your student record to provide relevant information

### Test Emails
Use these test emails to try the system:
- `alex.martinez@example.com`
- `jordan.lee@example.com`
- `nina.wu@example.com`

