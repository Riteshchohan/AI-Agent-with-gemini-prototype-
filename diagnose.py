import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def check_gemini_models():
    """Check available Gemini models and their capabilities"""
    print("\n[ Gemini API Configuration Check ]")
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Verify API key
    if not api_key or len(api_key) < 30:
        print(f"\nERROR: Invalid API key format - {api_key}")
        print("1. Get your API key from: https://aistudio.google.com/app/apikey")
        print("2. Create a .env file with: GEMINI_API_KEY=your_actual_key_here")
        print("3. Ensure .env is in the same folder as this script")
        return None
    
    print(f"API Key: Found ({api_key[:10]}...{api_key[-6:]})")
    
    # Configure manually to ensure key is set
    try:
        genai.configure(api_key=api_key)
        print("API Configuration: Successful")
    except Exception as e:
        print(f"Configuration Error: {str(e)}")
        return None
    
    # List available models
    try:
        print("\nFetching available models...")
        models = genai.list_models()
        
        if not models:
            print("No models found. Possible region restrictions.")
            return None
            
        working_models = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                working_models.append(m.name)
                print(f"- {m.name}")
        
        if not working_models:
            print("\nERROR: No models support generateContent method")
            return None
            
        # Test the first working model
        test_model = working_models[0]
        print(f"\nTesting model: {test_model}")
        model = genai.GenerativeModel(test_model)
        response = model.generate_content("Say exactly 'test ok'")
        
        if response.text.strip().lower() == "test ok":
            print("Test Successful!")
            return test_model
        else:
            print(f"Test Failed: Unexpected response - '{response.text}'")
            return None
            
    except Exception as e:
        print(f"\nAPI Error: {str(e)}")
        print("Possible solutions:")
        print("- Use VPN if in restricted region")
        print("- Upgrade SDK: pip install --upgrade google-generativeai")
        print("- Check API key permissions at https://aistudio.google.com/app/apikey")
        return None

if __name__ == "__main__":
    print("\n=== Gemini API Diagnostic Tool ===")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("\nCRITICAL: .env file not found in current directory")
        print("Create a .env file with your API key:")
        print("echo GEMINI_API_KEY=your_key_here > .env")
        sys.exit(1)
    
    working_model = check_gemini_models()
    
    if working_model:
        print(f"\nSUCCESS! Use this model in your code:")
        print(f"genai.configure(api_key=os.getenv('GEMINI_API_KEY'))")
        print(f"model = genai.GenerativeModel('{working_model}')")
    else:
        print("\nDIAGNOSIS FAILED: Gemini API not accessible")
        print("Alternative solution: Use direct API calls instead of SDK")
        
        # Offer to create simplified version
        create_simple = input("\nCreate simple API version? (y/n): ").lower()
        if create_simple == 'y':
            with open("simple_gemini_agent.py", "w") as f:
                f.write("""import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class SimpleGeminiAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
    def query_gemini(self, prompt):
        url = f"{self.base_url}?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"API Error: {str(e)}"
    
    def run(self, user_input):
        # Your custom prompt logic here
        prompt = f"Create a writing prompt about: {user_input}"
        return self.query_gemini(prompt)

if __name__ == "__main__":
    agent = SimpleGeminiAgent()
    print("Simple Gemini Agent - Type 'exit' to quit")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = agent.run(user_input)
        print(f"Agent: {response}\\n")
""")
            print("Created simple_gemini_agent.py with direct API access")