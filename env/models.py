from pydantic import BaseModel, Field
from typing import Optional, Dict

class Observation(BaseModel):
    task_id: int = Field(description="The ID of the current task.")
    query: str = Field(description="The SQL query to optimise or fix.")
    schema_context: str = Field(description="The DDL schema of the tables involved.")
    hint: Optional[str] = Field(default=None, description="Optional natural-language hint.")
    step_number: int = Field(description="The current step number in this episode.")
    max_steps: int = Field(description="The maximum allowed steps for this task.")

class Action(BaseModel):
    rewritten_query: str = Field(description="The rewritten SQL query.")
    explanation: str = Field(description="Explanation of the changes made.")
    is_done: bool = Field(description="True if the task is complete, False otherwise.")

class Reward(BaseModel):
    score: float = Field(description="Score between 0.0 and 1.0.")
    breakdown: Dict[str, float] = Field(description="Breakdown of partial scores.")
    feedback: str = Field(description="Feedback on the latest action.")
