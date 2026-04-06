from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from env import QueryOptimizationEnv, Observation, Action, Reward
from env.tasks import TASKS
import subprocess
import os

app = FastAPI(title="SQL Query Optimizer Env")
env = QueryOptimizationEnv()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "SQL Query Optimizer Environment API is running!"}

class ResetRequest(BaseModel):
    task_id: int

@app.post("/reset", response_model=Observation)
def reset_env(request: ResetRequest):
    try:
        obs = env.reset(request.task_id)
        return obs
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step")
def step_env(action: Action):
    try:
        obs, reward, done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": reward.model_dump(),
            "done": done,
            "info": info
        }
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def get_state():
    return env.state()

@app.get("/tasks")
def list_tasks():
    return TASKS

@app.get("/grader")
def get_grader():
    state = env.state()
    if not state.get("is_done", False):
        raise HTTPException(status_code=400, detail="Episode not done.")
    return {"score": state.get("cumulative_score", 0.0)}

@app.post("/baseline")
def run_baseline():
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY is not set.")
    try:
        result = subprocess.run(["python", "baseline.py"], capture_output=True, text=True, check=True)
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Baseline failed: {e.stderr}")
