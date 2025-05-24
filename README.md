# SOUR - CodeLlama-powered Coding Assistant

SOUR is a web-based coding assistant powered by CodeLlama that provides clear, well-formatted code examples and explanations.

## Features

- 🚀 Real-time code generation and formatting
- 💡 Intelligent response handling
- 🎨 Syntax highlighting for multiple languages
- ⚡ Optimized performance with request queuing
- 🛠️ Error recovery and graceful degradation

## Requirements

- Python 3.8+
- Ollama with CodeLlama model installed
- 8GB RAM minimum

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sour.git
cd sour
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is running with CodeLlama model:
```bash
ollama pull codellama
ollama run codellama
```

## Usage

1. Start the server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Start asking coding questions!

## Example Queries

- "Write a Python function to calculate factorial using recursion"
- "Create a simple HTML template with CSS flexbox"
- "Show me how to implement binary search in Python"

## Response Format

Responses include:
1. Brief explanation of the solution
2. Well-commented code examples
3. Example usage with input/output
4. Best practices and common pitfalls

## Error Handling

The system includes:
- Automatic retry with exponential backoff
- Request rate limiting
- Graceful degradation
- User-friendly error messages

## Contributing

Feel free to open issues or submit pull requests with improvements!

## License

MIT License - feel free to use and modify as needed.
