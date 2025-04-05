# Mark Musk - CreditChek API Assistant

Mark Musk is an AI-powered developer assistant designed to help software engineers integrate CreditChek's REST API products quickly and efficiently. The bot provides a conversational interface where developers can ask questions about the API, understand endpoints, and get sample code snippets in various programming languages.

## Features

- 🤖 Conversational AI interface for API documentation
- 💻 Code snippets in multiple programming languages (Python, NodeJS, PHP Laravel, GoLang)
- 📚 Comprehensive API endpoint documentation
- 🚀 10x faster API integration
- 🔍 Context-aware responses
- 💡 Best practices and error handling guidance

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Pinecone API key and environment

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd creditchek
```

2. Create and activate a virtual environment:
```bash
python -m venv markmusk_env
source markmusk_env/bin/activate  # On Windows: markmusk_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
Edit the `.env` file and add your API keys and configuration.

## Running the Application

1. Make sure your virtual environment is activated
2. Run the Streamlit application:
```bash
streamlit run src/app.py
```

## Usage

1. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)
2. Start asking questions about CreditChek's API
3. Get instant responses with relevant code snippets
4. Use the expandable code sections to view implementation examples

## Example Queries

- "How do I authenticate with the CreditChek API?"
- "Show me how to integrate the credit score endpoint"
- "What are the required parameters for identity verification?"
- "Give me a Python example for bank statement analysis"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For any questions or issues, please contact the CreditChek support team or open an issue in this repository. 