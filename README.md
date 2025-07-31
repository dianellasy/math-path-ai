# MathPath AI - Cal Poly Math Placement Assistant

A Streamlit-based AI chatbot that helps Cal Poly students with math placement questions and provides personalized guidance based on their academic records.

## Features

- **Student Authentication**: Email-based sign-in with mock student database
- **Personalized Responses**: Uses full student records to provide contextual answers
- **AWS Bedrock Integration**: Leverages knowledge base for policy and FAQ responses
- **Citation System**: Shows sources for policy-related information
- **Real-time Chat Interface**: Modern chat UI with message history

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
   AWS_DEFAULT_REGION=us-west-2
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   KNOWLEDGE_BASE_ID=kb-xxxxxxxx
   BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
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
├── app.py                 # Main Streamlit application
├── chatbot.py            # AWS Bedrock integration
├── ui.py                 # Alternative UI implementation
├── mock_students.json    # Mock student database
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## Architecture

- **Frontend**: Streamlit web interface
- **Backend**: AWS Bedrock Agent Runtime
- **Data**: Mock student database (JSON)
- **AI**: Knowledge Base + Student Context

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

[Add your license information here]