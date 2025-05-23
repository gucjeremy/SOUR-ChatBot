from flask import Flask, render_template, request, jsonify
import requests
import logging
import re

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_code_response(response):
    # If response already contains our markers, return as is
    if '[PYTHON]' in response:
        return response
        
    # Check if response contains markdown code blocks
    code_pattern = r'```(?:python)?\n(.*?)```'
    matches = re.findall(code_pattern, response, re.DOTALL)
    
    if matches:
        # Replace code blocks with our custom markers
        formatted_response = response
        for code_block in matches:
            formatted_response = formatted_response.replace(
                f'```python\n{code_block}```',
                f'[PYTHON]{code_block.strip()}[/PYTHON]'
            ).replace(
                f'```\n{code_block}```',
                f'[PYTHON]{code_block.strip()}[/PYTHON]'
            )
        return formatted_response
    
    # If no code blocks found but response looks like code
    if any(keyword in response for keyword in ['def ', 'class ', 'print(', 'return ', 'import ']):
        # Extract the code part
        lines = response.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            if any(keyword in line for keyword in ['def ', 'class ', 'print(', 'return ', 'import ']):
                in_code = True
            if in_code:
                code_lines.append(line)
                
        if code_lines:
            code_block = '\n'.join(code_lines)
            return f'Here\'s a Python function to solve your problem:\n\n[PYTHON]{code_block.strip()}[/PYTHON]'
    
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        logger.info(f"Received message: {user_message}")
        
        # Enhance the prompt to encourage code examples
        enhanced_prompt = f"{user_message}\nPlease provide a complete code example with comments."
        
        # Call Ollama API with increased timeout
        ollama_response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "codellama",
                "prompt": enhanced_prompt,
                "stream": False,
                "context_window": 4096,  # Increased context window
                "num_predict": 1024      # Increased token limit
            },
            timeout=60  # Increased timeout to 60 seconds
        )
        
        logger.info(f"Ollama status code: {ollama_response.status_code}")
        
        if ollama_response.status_code == 200:
            result = ollama_response.json()
            response_text = result.get('response', 'Sorry, I could not generate a response.')
            formatted_response = format_code_response(response_text)
            logger.info(f"Response generated successfully")
            return jsonify({"response": formatted_response})
        else:
            error_msg = f"Error: Received status code {ollama_response.status_code}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 500
            
    except requests.exceptions.Timeout:
        error_msg = "Error: Request to Ollama timed out. For complex questions, please try breaking them down into smaller parts."
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 504
    except requests.exceptions.ConnectionError:
        error_msg = "Error: Could not connect to Ollama. Please ensure Ollama is running with the CodeLlama model."
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 503
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"Unexpected error: {error_msg}")
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True)
