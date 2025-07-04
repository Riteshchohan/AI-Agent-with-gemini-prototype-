import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from rich import print

# Load environment variables
load_dotenv()

class BlogSparkAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-1.5-flash"  # Using a working model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        
        self.state_file = "agent_state.json"
        self.state = self.load_state()
        if not self.state:
            self.state = {
                "history": [],
                "niches": [],
                "user_preferences": {"tone": "friendly", "complexity": "medium"}
            }
            self.save_state()

    def generate_content(self, prompt):
        """Direct API call to Gemini"""
        url = f"{self.base_url}?key={self.api_key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"API Error: {str(e)}"

    def load_state(self):
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def input_understanding(self, user_input):
        prompt = f"""
        Analyze the user's query to extract:
        1. Core topic (e.g., "sustainability," "remote work")
        2. Desired tone (e.g., "inspirational," "analytical")
        3. Specific constraints (e.g., "under 500 words," "for beginners")

        Output ONLY JSON: {{"topic": string, "tone": string, "constraints": string}}

        User Input: "{user_input}"
        """
        try:
            response = self.generate_content(prompt)
            return json.loads(response.strip())
        except Exception as e:
            print(f"[red]Error parsing input:[/red] {e}")
            return {"topic": "general", "tone": "neutral", "constraints": ""}

    def update_state(self, analysis):
        # Ensure state has required keys
        for key in ["niches", "history"]:
            if key not in self.state:
                self.state[key] = []
                
        # Update niches
        topic = analysis.get("topic", "")
        if topic and topic not in self.state["niches"]:
            self.state["niches"].append(topic)
            
        # Update history
        self.state["history"].append({
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "user_input": analysis.get("user_input", "")
        })
        # Keep only last 3 prompts
        self.state["history"] = self.state["history"][-3:]
        self.save_state()

    def plan_task(self, analysis):
        niches = self.state.get("niches", [])
        history = self.state.get("history", [])
        history_topics = [h['analysis'].get('topic', '') for h in history]
        
        prompt = f"""
        You are BlogSpark, a writing prompt assistant. Plan how to generate a prompt based on:

        ### USER REQUEST ###
        Topic: {analysis.get('topic', 'general')}
        Tone: {analysis.get('tone', 'neutral')}
        Constraints: {analysis.get('constraints', 'none')}

        ### AGENT STATE ###
        Niches: {', '.join(niches)}
        Last Prompts: {history_topics}

        ### PLANNING STEPS ###
        1. If no topic, select from niches or trending topics
        2. Avoid repeating last 3 prompts
        3. Structure: [Hook] + [Question] + [Challenge]
        4. Add tip if constraints exist
        5. Adjust for tone: {'Use emojis for casual' if analysis.get('tone') == 'casual' else 'Be concise for professional'}

        Output ONLY the final prompt structure in plain text.
        """
        return self.generate_content(prompt)

    def generate_output(self, plan):
        tone = self.state.get("user_preferences", {}).get("tone", "friendly")
        
        prompt = f"""
        Generate a writing prompt using this structure:

        {plan}

        Format output EXACTLY as:
        ✨ **Prompt Idea**: [Hook sentence]
        ❓ **Explore**: [Open-ended question]
        ⚡ **Challenge**: [Actionable task]
        💡 **Tip**: [Brief advice]

        Use tone: {tone}
        """
        return self.generate_content(prompt)

    def run(self, user_input):
        analysis = self.input_understanding(user_input)
        analysis["user_input"] = user_input
        self.update_state(analysis)
        plan = self.plan_task(analysis)
        return self.generate_output(plan)

# CLI interface
if __name__ == "__main__":
    agent = BlogSparkAgent()
    print("[bold green]BlogSpark AI Agent[/bold green] - Ready to spark your creativity!")
    print("Type your request (e.g. 'fun prompt about sustainable fashion for beginners')")
    print("Type 'exit' to quit\n")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                print("Agent: Please enter a valid request")
                continue
            response = agent.run(user_input)
            print(f"\n[bold cyan]BlogSpark:[/bold cyan]\n{response}\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")

    print("\nSession ended. Your preferences are saved for next time!")