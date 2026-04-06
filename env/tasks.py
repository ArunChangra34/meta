import sqlglot

TASKS = {
    1: {
        "id": 1,
        "name": "fix-broken-join",
        "query": "SELECT users.name, orders.amount FROM users JOIN orders WHERE users.id = 1;",
        "schema_context": "CREATE TABLE users (id INT, name VARCHAR);\nCREATE TABLE orders (id INT, user_id INT, amount DECIMAL);",
        "hint": "The JOIN is missing an ON clause.",
        "max_steps": 3
    },
    2: {
        "id": 2,
        "name": "eliminate-n-plus-one",
        "query": "SELECT name, (SELECT count(*) FROM orders WHERE orders.user_id = users.id) AS order_count FROM users;",
        "schema_context": "CREATE TABLE users (id INT, name VARCHAR);\nCREATE TABLE orders (id INT, user_id INT, amount DECIMAL);",
        "hint": "Use a JOIN and GROUP BY instead of a correlated subquery.",
        "max_steps": 3
    },
    3: {
        "id": 3,
        "name": "full-optimization",
        "query": "SELECT DISTINCT * FROM events WHERE cast(date as varchar) = '2023-01-01';",
        "schema_context": "CREATE TABLE events (id INT, type VARCHAR, date DATE);\nCREATE INDEX idx_date ON events(date);",
        "hint": "Avoid using DISTINCT unnecessarily, explicit columns are better than *, and don't cast indexed columns.",
        "max_steps": 5
    }
}

def grade_task(task_id: int, query: str) -> dict:
    try:
        parsed = sqlglot.parse_one(query)
    except Exception as e:
        return {"score": 0.0, "feedback": f"SQL parsing failed: {e}"}

    original_query = TASKS[task_id]["query"]
    score = 0.0
    feedback = ""

    if task_id == 1:
        upper_q = query.upper()
        if "ON " in upper_q and "USERS.ID = ORDERS.USER_ID" in upper_q.replace(" ", ""):
            score = 1.0
            feedback = "Great! You added the missing ON clause."
        else:
            score = 0.2
            feedback = "The query parses but is still lacking the correct ON clause."

    elif task_id == 2:
        upper_q = query.upper()
        if "JOIN " in upper_q and "GROUP BY " in upper_q:
            score = 1.0
            feedback = "Excellent! You eliminated the correlated subquery."
        else:
            score = 0.2
            feedback = "The query parses but does not seem to use a JOIN and GROUP BY."

    elif task_id == 3:
        upper_q = query.upper()
        sub_scores = 0.0
        if "DISTINCT " not in upper_q:
            sub_scores += 0.33
        if "*" not in upper_q:
            sub_scores += 0.33
        if "CAST(" not in upper_q and "CAST (" not in upper_q:
            sub_scores += 0.34
        
        score = min(sub_scores, 1.0)
        feedback = f"Sub-scores: No DISTINCT, explicit columns, no CAST function. Total: {score:.2f}"
    
    return {"score": score, "feedback": feedback}
