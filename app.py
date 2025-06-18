from flask import Flask, render_template, request, jsonify
import requests
import logging
import re
import time
import json
import random
import os
from threading import Lock

app = Flask(__name__)

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
request_lock = Lock()
last_request_time = {}
MIN_REQUEST_INTERVAL = 0.5  # Reduced minimum time between requests

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

def chunk_prompt(prompt, max_length=100):  # Reduced chunk size for faster processing
    """Break down long prompts into smaller, manageable chunks"""
    words = prompt.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
            
    if current_chunk:
        chunks.append(' '.join(current_chunk))
        
    return chunks

def generate_response_with_retry(prompt, max_retries=5, client_ip=None):  # Increased retries for better reliability
    """Attempt to generate a response with retries and chunking for long prompts"""
    # Optimized handling for social media website requests
    if "website" in prompt.lower() and " social media" in prompt.lower():
        template_prompt = """Complete this HTML template with social media links:
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
            background: #f0f2f5;
        }
        .social-links {
            display: flex;
            gap: 20px;
        }
        .social-links a {
            color: #1877f2;
            font-size: 24px;
            transition: transform 0.3s;
        }
        .social-links a:hover {
            transform: scale(1.2);
        }
    </style>
</head>
<body>
    <div class="social-links">
        <!-- Add links for Twitter, Facebook, and Instagram using Font Awesome icons -->
    </div>
</body>
</html>"""
        try:
            response, last_error = generate_single_response(template_prompt, max_retries, client_ip)
            if response:
                return response, None
            logger.warning("Failed to generate social media website response")
        except Exception as e:
            logger.error(f"Error generating social media website: {str(e)}")
        return None, "Error generating social media website"
        
    # For other types of prompts, use regular chunking
    elif len(prompt) > 150:
        chunks = chunk_prompt(prompt)
        responses = []
        last_error = None
        
        for chunk in chunks:
            try:
                chunk_response, chunk_error = generate_single_response(chunk, max_retries, client_ip)
                if chunk_response:
                    responses.append(chunk_response)
                else:
                    last_error = chunk_error
                    logger.warning(f"Failed to generate response for chunk: {chunk}")
            except Exception as e:
                last_error = str(e)
                logger.error(f"Error processing chunk: {str(e)}")
                
        if responses:
            return ' '.join(responses), None
        return None, last_error
    else:
        return generate_single_response(prompt, max_retries, client_ip)

def generate_single_response(prompt, max_retries=5, client_ip=None):
    """Generate response for a single prompt with retries and rate limiting"""
    if client_ip:
        with request_lock:
            current_time = time.time()
            if client_ip in last_request_time:
                time_since_last = current_time - last_request_time[client_ip]
                if time_since_last < MIN_REQUEST_INTERVAL:
                    time.sleep(MIN_REQUEST_INTERVAL - time_since_last)
            last_request_time[client_ip] = current_time
    
    last_error = None
    backoff_time = 1  # Reduced initial backoff time
    
    for attempt in range(max_retries):
        try:
            OLLAMA_API_URL = os.environ.get('OLLAMA_API_URL', 'http://localhost:11434')
               response = requests.post(f"{OLLAMA_API_URL}/api/generate", ...)
                json={
                    "model": "codellama",
                    "prompt": prompt,
                    "stream": False,  # Disable streaming for now as we need to modify response handling
                    "context_window": 512,   # Minimal context for fastest responses
                    "num_predict": 256,      # Very concise responses
                    "temperature": 0.8,      # More deterministic responses
                    "top_p": 0.8,           # More deterministic token selection
                    "repeat_penalty": 1.1,   # Lighter repetition prevention
                    "stop": ["</code>", "```", "\n\n\n"],  # Clean response endings
                    "num_ctx": 512          # Minimal context window for fastest processing
                },
                timeout=120  # Increased timeout for complex responses
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict):
                    return result.get('response', ''), None
                return str(result), None
                
            last_error = f"API returned status code {response.status_code}"
            
        except requests.exceptions.Timeout:
            last_error = "Request timed out"
            logger.warning(f"Timeout on attempt {attempt+1} for prompt: {prompt}")
        except requests.exceptions.ConnectionError:
            last_error = "Could not connect to Ollama"
            logger.warning(f"Connection error on attempt {attempt+1} for prompt: {prompt}")
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Exception on attempt {attempt+1} for prompt: {prompt} - {last_error}")
            
        # Exponential backoff with jitter
        if attempt < max_retries - 1:
            jitter = random.uniform(0, 0.5)  # Increased jitter range
            time.sleep(backoff_time + jitter)
            backoff_time *= 1.5  # Gentler backoff multiplier
            
    logger.error(f"Failed after {max_retries} attempts. Last error: {last_error}")
    return None, last_error

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    last_error = None  # Initialize last_error to avoid NameError
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        client_ip = request.remote_addr
        
        if not user_message:
            return jsonify({"error": "Please enter a message"}), 400
            
        logger.info(f"Received message from {client_ip}: {user_message}")
        
        # Enhance the prompt for better responses
        keywords = ['code', 'function', 'class', 'example', 'python', 'javascript', 'html', 'css']
        is_code_request = any(keyword in user_message.lower() for keyword in keywords)
        
        if is_code_request:
            enhanced_prompt = f"""Please provide a clear and concise code example for: {user_message}

Requirements:
1. Start with a brief explanation of the solution
2. Include well-commented code with clear variable names
3. Add example usage showing input and output
4. Keep the code simple and efficient
5. Use Python best practices and PEP 8 style

Format the response like this:
[Explanation of the solution]

[CODE]
# Your code here
[/CODE]

[Example usage]"""
        else:
            enhanced_prompt = f"""Please help with: {user_message}

If code would be helpful, include:
1. Clear explanation of the concept
2. Relevant code examples in this format:
   [CODE]
   # Your code here
   [/CODE]
3. Key points to understand
4. Common pitfalls to avoid"""
            
        # Generate response with improved error handling
        response_text, last_error = generate_response_with_retry(enhanced_prompt, client_ip=client_ip)
        
        if response_text:
            formatted_response = format_code_response(response_text)
            logger.info("Response generated successfully")
            return jsonify({"response": formatted_response})
        else:
            error_msg = f"I apologize, but I couldn't generate a response. Error: {last_error}\n\nPlease try:\n" \
                       "1. Breaking down your question into smaller parts\n" \
                       "2. Being more specific about what you need\n" \
                       "3. Asking for simpler examples first\n" \
                       "4. Waiting a moment before trying again"
            logger.error(f"Failed to generate response. Last error: {last_error}")
            return jsonify({"error": error_msg}), 500
            
    except requests.exceptions.Timeout:
        error_msg = "The request timed out. This usually means the model needs more time to generate a good response.\n\n" \
                   "Please try:\n" \
                   "1. Breaking down your question into smaller parts\n" \
                   "2. Being more specific\n" \
                   "3. Asking for simpler examples first\n" \
                   "4. Waiting a moment before trying again"
        logger.error(f"Request timeout after 5 attempts")
        return jsonify({"error": error_msg}), 504
        
    except requests.exceptions.ConnectionError:
        error_msg = "Could not connect to the AI model. This usually means Ollama is not running.\n\n" \
                   "Please ensure:\n" \
                   "1. Ollama is running (check Task Manager)\n" \
                   "2. CodeLlama model is installed (run: ollama pull codellama)\n" \
                   "3. Your system has enough resources (at least 8GB RAM)\n" \
                   "4. Try again in a few moments"
        logger.error("Connection error to Ollama API")
        return jsonify({"error": error_msg}), 503
        
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}\n\nPlease try again in a few moments."
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
