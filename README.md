# MathPath AI - Cal Poly Math Placement Assistant

A Streamlit-based AI chatbot that helps Cal Poly students with math placement questions and provides personalized guidance based on their academic records.

## Features

- **Student Authentication**: Email-based sign-in with mock student database
- **Personalized Responses**: Uses full student records to provide contextual answers
- **AWS Bedrock Integration**: Leverages knowledge base for policy and FAQ responses
- **Citation System**: Shows sources for policy-related information
- **Real-time Chat Interface**: Modern chat UI with message history

## Architecture

### **Backend Developer** (`backend.py`)
- AWS Bedrock integration
- Student data processing
- Business logic
- AI prompt engineering
- Data validation

### **UI Developer** (`ui.py`)
- Streamlit interface
- User experience
- Styling and animations
- Chat interface
- Visual design

## Setup

### Prerequisites
- Python 3.8+
- AWS Account with Bedrock access
- AWS Knowledge Base configured

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd math-path-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file with:
   ```
   AWS_DEFAULT_REGION=your_region_here
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   KNOWLEDGE_BASE_ID=kb-xxxxxxxx
   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
   ```

4. **Run the application**
   ```bash
   streamlit run ui.py
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

## Project Structure

```
math-path-ai/
├── ui.py                 # Main Streamlit UI (UI Developer)
├── backend.py            # Business logic & AWS integration (Backend Developer)
├── mock_students.json    # Mock student database
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Development Workflow

### For Backend Developer:
- Work on `backend.py`
- Add new AI features
- Improve data processing
- Test with `python -c "from backend import *; print('Backend working!')"`

### For UI Developer:
- Work on `ui.py`
- Improve user experience
- Add new UI components
- Test with `streamlit run ui.py`

### Collaboration:
- Backend developer exposes new functions in `backend.py`
- UI developer imports and uses them in `ui.py`
- Clear separation of concerns

## API Reference (Backend Functions)

### Core Functions:
- `load_students()` - Load student database
- `validate_environment()` - Check environment variables
- `authenticate_student(email, db)` - Authenticate student
- `process_user_question(student, question)` - Main processing function

### Data Processing:
- `derive_flags(student)` - Extract student status flags
- `compose_full_prompt(student, question)` - Create AI prompts

### AWS Integration:
- `get_bedrock_client()` - Create AWS client
- `ask_bedrock(prompt)` - Make Bedrock API calls

## Contributing

1. Create a feature branch
2. Work on your respective files (backend.py or ui.py)
3. Test thoroughly
4. Submit a pull request