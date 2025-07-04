import os
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
        print(f"Agent: {response}\n")
