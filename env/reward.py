def calculate_reward(grader_result: dict, step_number: int, task_max_steps: int, is_done: bool) -> tuple:
    score = grader_result.get("score", 0.0)
    
    reward_score = score
    breakdown = {"grader_score": score}
    
    if step_number > task_max_steps:
        penalty = 0.02 * (step_number - task_max_steps)
        reward_score -= penalty
        breakdown["step_penalty"] = -penalty
        
    if score == 0.0:
        reward_score -= 0.1
        breakdown["invalid_penalty"] = -0.1
        
    reward_score = max(0.0, min(1.0, reward_score))
    
    return reward_score, breakdown
