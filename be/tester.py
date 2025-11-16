from scrape.browser import create_task, get_task
import time
import json

# Create a new task
print("Creating new browser automation task...")
task_response = create_task(
    agent="gemini",
    prompt="What text does the homepage of example.com say?",
    mode="text",
    step_limit=10
)
print(f"Task created: {task_response}\n")

TASK_ID = task_response.get("taskId")
if not TASK_ID:
    print("Error: No taskId returned from task creation")
    exit(1)

print(f"Task ID: {TASK_ID}")
print("Polling for task completion...\n")

# Poll until 'answer' appears in response
max_attempts = 60
poll_interval = 2
attempt = 0
final_result = None

while attempt < max_attempts:
    attempt += 1
    try:
        task_status = get_task(TASK_ID)
        
        # Print current status
        status = task_status.get("status", "unknown")
        print(f"[Attempt {attempt}] Status: {status}")
        
        # Check if 'answer' is in the response - if so, task is done
        response_str = json.dumps(task_status).lower()
        if 'answer' in response_str:
            print("\n✅ Task completed! (Answer found)")
            final_result = task_status
            break
        
        # Wait before next poll
        time.sleep(poll_interval)
        print()
        
    except Exception as e:
        print(f"Error polling task status: {e}")
        break

# Print final response
print("=" * 60)
print("FINAL RESPONSE:")
print("=" * 60)
if final_result:
    print(json.dumps(final_result, indent=2))
else:
    print("Task did not complete within the polling window.")
    try:
        last_status = get_task(TASK_ID)
        print(json.dumps(last_status, indent=2))
    except Exception as e:
        print(f"Error retrieving final status: {e}")