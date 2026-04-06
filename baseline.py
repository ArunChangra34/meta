import os
import requests
from openai import OpenAI
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

BASE_URL = "http://localhost:7860"

def run_task(task_id):
    res = requests.post(f"{BASE_URL}/reset", json={"task_id": task_id})
    if res.status_code != 200:
        print(f"Failed to reset task {task_id}: {res.text}")
        return 0.0
        
    obs = res.json()
    
    prompt = f"""You are a SQL expert. Rewrite this query to improve it.
Query: {obs['query']}
Schema: {obs['schema_context']}
Hint: {obs['hint']}
Return ONLY a JSON response in the following format:
{{"rewritten_query": "YOUR_SQL", "explanation": "YOUR_REASONING", "is_done": true}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
    except openai.AuthenticationError as e:
        print(f"Failed to authenticate with OpenAI: Your API key is invalid or not provided correctly.")
        print(f"Details: {e}")
        return 0.0
    
    try:
        action_data = json.loads(response.choices[0].message.content)
        if "is_done" not in action_data:
            action_data["is_done"] = True
    except Exception as e:
        print(f"Failed to parse LLM response: {e}")
        return 0.0
        
    res = requests.post(f"{BASE_URL}/step", json=action_data)
    if res.status_code != 200:
        print(f"Failed to step task {task_id}: {res.text}")
        return 0.0
        
    step_data = res.json()
    return step_data["reward"]["score"]

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY environment variable is required.")
        exit(1)
        
    print("Running baseline...")
    scores = {}
    for task_id in [1, 2, 3]:
        score = run_task(task_id)
        scores[f"Task {task_id}"] = score
        print(f"Task {task_id} Score: {score}")
        
    print("\nBaseline Results:")
    for task, score in scores.items():
        print(f"{task}: {score:.2f}")
