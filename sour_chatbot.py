import requests
import json
import sys
import time

class SOURChatbot:
    def __init__(self):
        self.api_url = "http://localhost:11434/api/generate"
        self.model = "codellama"
        print("🤖 SOUR: Hello! I'm SOUR, your coding assistant powered by CodeLlama.")
        print("Type 'exit' to end the conversation.\n")
        self._check_ollama_connection()

    def _check_ollama_connection(self):
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                print("✅ Connected to Ollama successfully!")
            else:
                print("❌ Could not connect to Ollama. Please make sure it's running.")
                sys.exit(1)
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to Ollama. Please make sure it's running.")
            print("   Run 'ollama serve' in a terminal if Ollama is not running.")
            sys.exit(1)

    def generate_response(self, prompt):
        try:
            print("\n🤖 SOUR: Thinking...")
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(self.api_url, json=data, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Sorry, I could not generate a response.')
            else:
                return f"Error: Received status code {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Lost connection to Ollama. Please make sure Ollama is still running."
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model is taking too long to respond."
        except Exception as e:
            return f"Error: {str(e)}"

    def run(self):
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    print("\n🤖 SOUR: Goodbye! Have a great day!")
                    break
                    
                if not user_input:
                    print("🤖 SOUR: Please type something!")
                    continue
                
                response = self.generate_response(user_input)
                print(f"\n🤖 SOUR: {response}")
                
            except KeyboardInterrupt:
                print("\n\n🤖 SOUR: Goodbye! Have a great day!")
                break
            except Exception as e:
                print(f"\n🤖 SOUR: An error occurred: {str(e)}")

if __name__ == "__main__":
    chatbot = SOURChatbot()
    chatbot.run()
