import requests
import sys
import time
import random

def chat_with_sour():
    """Main function to interact with SOUR chatbot"""
    print("\\n🤖 SOUR: Hello! I'm SOUR, your coding assistant powered by CodeLlama.")
    print("Type 'exit' to end the conversation.\\n")

    max_retries = 3
    min_backoff = 1  # seconds

    while True:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\\n🤖 SOUR: Goodbye! Have a great day!")
                break
                
            if not user_input:
                print("🤖 SOUR: Please type something!")
                continue

            last_error = None
            backoff_time = min_backoff

            for attempt in range(max_retries):
                try:
                    # Send request to Ollama
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "codellama",
                            "prompt": user_input,
                            "stream": False,
                            "context_window": 512,   # Minimal context for faster response
                            "num_predict": 128,      # Minimal prediction for faster response
                            "temperature": 0.2,      # Very focused responses
                            "top_p": 1.0,           # Use all tokens for better quality
                            "repeat_penalty": 1.5    # Strong repetition prevention
                        },
                        timeout=15
                    )

                    if response.status_code == 200:
                        result = response.json()
                        print(f"\\n🤖 SOUR: {result['response']}\\n")
                        break
                    else:
                        last_error = f"Received status code {response.status_code}"
                        print(f"\\n❌ Error: {last_error}")
                except requests.exceptions.Timeout:
                    last_error = "Request timed out. Please try again."
                    print(f"\\n❌ Error: {last_error}")
                except requests.exceptions.ConnectionError:
                    last_error = "Could not connect to Ollama. Please make sure Ollama is running with CodeLlama model."
                    print(f"\\n❌ Error: {last_error}")
                except Exception as e:
                    last_error = str(e)
                    print(f"\\n❌ Error: {last_error}")

                if attempt < max_retries - 1:
                    jitter = random.uniform(0, 0.2)
                    time.sleep(backoff_time + jitter)
                    backoff_time *= 2
                else:
                    print(f"\\n❌ Failed after {max_retries} attempts. Last error: {last_error}")

        except KeyboardInterrupt:
            print("\\n\\n🤖 SOUR: Goodbye! Have a great day!")
            break

if __name__ == "__main__":
    chat_with_sour()
