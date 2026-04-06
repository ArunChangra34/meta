---
title: Sql Query Optimizer
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# SQL Query Optimizer Env

## 1. Environment Description & Motivation
A realistic code-review environment where an AI agent reviews and optimizes SQL queries. Tests semantic understanding of SQL, schema context, and best practices.

## 2. Action Space
- `rewritten_query` (str): The optimized SQL query.
- `explanation` (str): Developer reasoning.
- `is_done` (bool): Signals completion of the task.

## 3. Observation Space
- `task_id` (int): Target task identifier.
- `query` (str): Query to fix.
- `schema_context` (str): Database DDL involved.
- `hint` (str): Instructions on what's wrong.
- `step_number` (int): Current step in episode.
- `max_steps` (int): Limits per task.

## 4. Task Descriptions
- **Task 1 (Easy):** Fix a broken JOIN clause (missing ON).
- **Task 2 (Medium):** Eliminate N+1 from a correlated subquery.
- **Task 3 (Hard):** Full schema optimization (remove DISTINCT, avoid *, no casts on indexed columns).

## 5. Setup & Usage
**Locally:**
```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 7860
```

**Docker:**
```bash
docker build -t sql-optimizer-env .
docker run -p 7860:7860 sql-optimizer-env
```

## 6. Baseline Scores
Using `gpt-3.5-turbo`:
- Task 1: ~1.0
- Task 2: ~1.0
- Task 3: ~1.0
