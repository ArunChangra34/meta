import os
import urllib.request
import urllib.error
from openai import OpenAI
import json

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# Setting up OpenAI client (either original or configured via variables)
client = OpenAI(
    api_key=HF_TOKEN or os.environ.get("OPENAI_API_KEY", "dummy"),
    base_url=API_BASE_URL if API_BASE_URL != "<your-active-endpoint>" else None
)

ENV_URL = "http://localhost:7860"

def run_task(task_id):
    # Output structured logs
    print("START")
    
    try:
        req = urllib.request.Request(
            f"{ENV_URL}/reset", 
            data=json.dumps({"task_id": task_id}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() != 200:
                print("END")
                return
            obs = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print("END")
        return
        
    prompt = f"""You are a SQL expert. Rewrite this query to improve it.
Query: {obs['query']}
Schema: {obs['schema_context']}
Hint: {obs['hint']}
Return ONLY a JSON response in the following format:
{{"rewritten_query": "YOUR_SQL", "explanation": "YOUR_REASONING", "is_done": true}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME if MODEL_NAME != "<your-active-model>" else "gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        action_data = json.loads(response.choices[0].message.content)
        if "is_done" not in action_data:
            action_data["is_done"] = True
    except Exception as e:
        action_data = {"rewritten_query": obs['query'], "explanation": f"Fallback due to err: {e}", "is_done": True}

    print(f"STEP: {json.dumps(action_data)}")
        
    try:
        req_step = urllib.request.Request(
            f"{ENV_URL}/step", 
            data=json.dumps(action_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req_step, timeout=10) as response:
            pass
    except Exception:
        pass

    print("END")

if __name__ == "__main__":
    for task_id in [1, 2, 3]:
        run_task(task_id)
