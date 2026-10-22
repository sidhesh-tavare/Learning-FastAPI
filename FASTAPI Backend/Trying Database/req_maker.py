import random
import httpx

# Ensure this matches your Uvicorn host address port exactly
API_URL = "http://127.0.0.1:8000/tasks"
NUM_TASKS = 7

ACTION_VERBS = ["Review", "Fix", "Update", "Write", "Deploy", "Test", "Design", "Clean", "Organise", "Refactor"]
NOUNS = ["database schema", "API documentation", "auth bug", "landing page", "frontend styles", "unit tests", "CI/CD pipeline"]
URGENCIES = ["immediately", "by Friday", "before the sprint ends", "asap"]

def generate_random_task():
    verb = random.choice(ACTION_VERBS)
    noun = random.choice(NOUNS)
    urgency = random.choice(URGENCIES)
    
    return {
        "title": f"{verb} {noun}",
        "description": f"Please {verb.lower()} the {noun} {urgency}."  # Always providing a valid string
    }

def populate_tasks():
    print(f"🚀 Starting population of {NUM_TASKS} random tasks...")
    success_count = 0
    
    # Using a shared client session stops connection exhaustion
    with httpx.Client() as client:
        for i in range(1, NUM_TASKS + 1):
            task_data = generate_random_task()
            try:
                response = client.post(API_URL, json=task_data)
                if response.status_code == 201:
                    print(f" ✅ [{i}/{NUM_TASKS}] Created: {task_data['title']}")
                    success_count += 1
                else:
                    print(f" ❌ [{i}/{NUM_TASKS}] Server error ({response.status_code}): {response.text}")
            except httpx.RequestError as e:
                print(f" ❌ [{i}/{NUM_TASKS}] Connection refused. Server might be down: {e}")
                
    print(f"\n🎉 Done! Successfully created {success_count}/{NUM_TASKS} tasks.")


if __name__ == "__main__":
    populate_tasks()
