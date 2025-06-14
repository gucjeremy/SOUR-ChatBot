from flask import Flask, render_template, request, jsonify
import requests
import logging
import re
import time
import json
import random
from threading import Lock
import os

app = Flask(__name__, template_folder='../templates')

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
request_lock = Lock()
last_request_time = {}
MIN_REQUEST_INTERVAL = 0.5

def format_code_response(response):
    if not response:
        return "I apologize, but I couldn't generate a response. Please try again with a simpler question."
        
    # If response already contains our markers, return as is
    if '[CODE]' in response:
        return response
        
    # Check if response contains markdown code blocks
    code_patterns = {
        'html': r'```(?:html)?\n(.*?)```',
        'css': r'```(?:css)?\n(.*?)```',
        'python': r'```(?:python)?\n(.*?)```'
    }
    
    formatted_response = response
    
    for lang, pattern in code_patterns.items():
        matches = re.findall(pattern, response, re.DOTALL)
        if matches:
            for code_block in matches:
                formatted_response = formatted_response.replace(
                    f'```{lang}\n{code_block}```',
                    f'[CODE]{code_block.strip()}[/CODE]'
                ).replace(
                    f'```\n{code_block}```',
                    f'[CODE]{code_block.strip()}[/CODE]'
                )
    
    # If no code blocks found but response looks like code
    if not '[CODE]' in formatted_response:
        code_indicators = {
            'html': ['<html', '<body', '<div', '<p', '<script', '<style'],
            'css': ['{', 'body {', '.class', '#id', '@media'],
            'python': ['def ', 'class ', 'print(', 'return ', 'import ']
        }
        
        for lang, indicators in code_indicators.items():
            if any(indicator in formatted_response for indicator in indicators):
                lines = formatted_response.split('\n')
                code_lines = []
                in_code = False
                
                for line in lines:
                    if any(indicator in line for indicator in indicators):
                        in_code = True
                    if in_code:
                        code_lines.append(line)
                        
                if code_lines:
                    code_block = '\n'.join(code_lines)
                    formatted_response = f'Here\'s the {lang.upper()} code:\n\n[CODE]{code_block.strip()}[/CODE]'
                    break
    
    return formatted_response

def generate_fallback_response(prompt):
    """Generate a fallback response when external API is not available"""
    if "website" in prompt.lower() and "social media" in prompt.lower():
        return """Here's a simple social media website template:

[CODE]
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Links</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        body { 
            display: flex; 
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: Arial, sans-serif;
        }
        .social-container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            text-align: center;
        }
        .social-links {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 20px;
        }
        .social-links a {
            color: #333;
            font-size: 30px;
            transition: transform 0.3s, color 0.3s;
            padding: 15px;
            border-radius: 50%;
            background: #f8f9fa;
        }
        .social-links a:hover {
            transform: scale(1.2);
        }
        .social-links a.facebook:hover { color: #1877f2; }
        .social-links a.twitter:hover { color: #1da1f2; }
        .social-links a.instagram:hover { color: #e4405f; }
        h1 { color: #333; margin-bottom: 10px; }
        p { color: #666; }
    </style>
</head>
<body>
    <div class="social-container">
        <h1>Connect With Us</h1>
        <p>Follow us on social media</p>
        <div class="social-links">
            <a href="https://facebook.com" class="facebook" target="_blank">
                <i class="fab fa-facebook-f"></i>
            </a>
            <a href="https://twitter.com" class="twitter" target="_blank">
                <i class="fab fa-twitter"></i>
            </a>
            <a href="https://instagram.com" class="instagram" target="_blank">
                <i class="fab fa-instagram"></i>
            </a>
        </div>
    </div>
</body>
</html>
[/CODE]

This creates a responsive social media links page with hover effects and modern styling."""

    elif any(keyword in prompt.lower() for keyword in ['python', 'function', 'code']):
        return """I'd be happy to help with Python code! Here's a basic example:

[CODE]
def hello_world(name="World"):
    \"\"\"
    A simple function that returns a greeting
    \"\"\"
    return f"Hello, {name}!"

# Example usage
print(hello_world())  # Output: Hello, World!
print(hello_world("Alice"))  # Output: Hello, Alice!
[/CODE]

For more specific help, please describe what you'd like to build and I'll provide a tailored solution."""

    else:
        return """I'm SOUR, your coding assistant! I can help you with:

• Python programming and best practices
• Web development (HTML, CSS, JavaScript)
• Code examples and explanations
• Debugging and optimization tips
• Project structure and design patterns

Please ask me a specific coding question and I'll provide detailed examples with explanations!"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        client_ip = request.remote_addr
        
        if not user_message:
            return jsonify({"error": "Please enter a message"}), 400
            
        logger.info(f"Received message from {client_ip}: {user_message}")
        
        # For Vercel deployment, we'll use fallback responses since Ollama won't be available
        # In a production environment, you would integrate with a cloud-based AI service
        response_text = generate_fallback_response(user_message)
        formatted_response = format_code_response(response_text)
        
        logger.info("Response generated successfully")
        return jsonify({"response": formatted_response})
            
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}\n\nPlease try again in a few moments."
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"error": error_msg}), 500

# For Vercel deployment
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)
