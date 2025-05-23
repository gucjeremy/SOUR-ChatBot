# SOUR Chatbot

SOUR is a simple chatbot powered by CodeLlama through Ollama, designed to help with coding-related questions and tasks.

## Prerequisites

1. Install [Python](https://www.python.org/downloads/) (version 3.7 or higher)
2. Install [Ollama](https://ollama.ai/)
3. Pull the CodeLlama model by running:
```bash
ollama pull codellama
```

## Setup

1. Install the required Python packages:
```bash
pip install -r requirements.txt
```

2. Make sure Ollama is running with CodeLlama model

## Running the Chatbot

1. Start the chatbot:
```bash
python sour_chatbot.py
```

2. Start chatting with SOUR! Type your questions or coding problems, and SOUR will respond using the CodeLlama model.

3. To exit the chat, type 'exit' or press Ctrl+C.

## Features

- 🤖 Powered by CodeLlama model
- 💬 Interactive command-line interface
- ⚡ Real-time responses
- 🛠 Error handling and connection management

## Notes

- Ensure Ollama is running before starting the chatbot
- The chatbot connects to Ollama's API at `localhost:11434`
- Internet connection is not required as Ollama runs locally
