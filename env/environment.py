from .models import Observation, Action, Reward
from .tasks import TASKS, grade_task
from .reward import calculate_reward

class QueryOptimizationEnv:
    def __init__(self):
        self.current_task_id = None
        self.step_number = 0
        self.cumulative_score = 0.0
        self.history = []
        self.is_done = True
        
    def reset(self, task_id: int) -> Observation:
        if task_id not in TASKS:
            raise ValueError(f"Task ID {task_id} not found.")
            
        task = TASKS[task_id]
        self.current_task_id = task_id
        self.step_number = 0
        self.cumulative_score = 0.0
        self.history = []
        self.is_done = False
        
        return Observation(
            task_id=task_id,
            query=task["query"],
            schema_context=task["schema_context"],
            hint=task["hint"],
            step_number=self.step_number,
            max_steps=task["max_steps"]
        )
        
    def step(self, action: Action) -> tuple:
        if self.is_done:
            raise RuntimeError("Episode is already done. Call reset().")
            
        self.step_number += 1
        grader_result = grade_task(self.current_task_id, action.rewritten_query)
        task_max_steps = TASKS[self.current_task_id]["max_steps"]
        
        reward_val, breakdown = calculate_reward(
            grader_result, self.step_number, task_max_steps, action.is_done
        )
        
        self.cumulative_score += reward_val
        self.history.append({
            "step": self.step_number,
            "action": action.model_dump(),
            "reward": reward_val
        })
        
        if self.step_number >= task_max_steps or action.is_done:
            self.is_done = True
            
        obs = Observation(
            task_id=self.current_task_id,
            query=action.rewritten_query,
            schema_context=TASKS[self.current_task_id]["schema_context"],
            hint=TASKS[self.current_task_id]["hint"],
            step_number=self.step_number,
            max_steps=task_max_steps
        )
        
        reward = Reward(
            score=reward_val,
            breakdown=breakdown,
            feedback=grader_result.get("feedback", "")
        )
        
        return obs, reward, self.is_done, {"grader_score": grader_result.get("score")}

    def state(self) -> dict:
        return {
            "current_task_id": self.current_task_id,
            "step_number": self.step_number,
            "cumulative_score": self.cumulative_score,
            "history": self.history,
            "is_done": self.is_done
        }
