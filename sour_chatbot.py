import requests
import sys

def chat_with_sour():
    """Main function to interact with SOUR chatbot"""
    print("\n🤖 SOUR: Hello! I'm SOUR, your coding assistant powered by CodeLlama.")
    print("Type 'exit' to end the conversation.\n")

    while True:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("\n🤖 SOUR: Goodbye! Have a great day!")
                break
                
            if not user_input:
                print("🤖 SOUR: Please type something!")
                continue

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
                print(f"\n🤖 SOUR: {result['response']}\n")
            else:
                print(f"\n❌ Error: Received status code {response.status_code}")

        except requests.exceptions.Timeout:
            print("\n❌ Error: Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Could not connect to Ollama. Please make sure Ollama is running with CodeLlama model.")
        except KeyboardInterrupt:
            print("\n\n🤖 SOUR: Goodbye! Have a great day!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    chat_with_sour()
