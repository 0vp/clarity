# Browser Cash API Response Documentation

This document logs the JSON response structures for each `@node` reference returned by the Browser Cash API.

## Response Format

API responses may include node references in the format: `@node (1-1545)`

**Completion Signal:** When a response contains the key `"answer"`, the task is complete and includes the final result with node references like `@node (1-1545)`.

## Response Logs

### Task Creation Response (`create_task`)

**Endpoint:** `POST /v1/task/create`

**Example Response:**
```json
{
  "taskId": "string",
  "status": "string",
  "@node (1-1352)": {
    // Response structure to be documented
  }
}
```

**Documented Nodes:**
- `@node (1-1352)`: [Description of what this node contains]

---

### Task Status Response (`get_task`)

**Endpoint:** `GET /v1/task/{taskId}`

**Example Response:**
```json
{
  "taskId": "string",
  "status": "string",
  "answer": "...",
  "@node (1-1545)": {
    // Final response structure with answer
  }
}
```

**Documented Nodes:**
- `@node (1-1545)`: Final response node containing the answer when task is completed. This node appears in the response when the task has finished processing and contains the answer to the prompt.

---

### `@node (1-1545)`

**Context:** Final response from `get_task` when task is completed (indicated by presence of `"answer"` key)

**Structure:**
```json
{
  "taskId": "string",
  "status": "completed",
  "answer": "The answer text from the browser automation",
  "@node (1-1545)": {
    // Node data containing structured response information
  }
}
```

**Fields:**
- `answer`: The final answer text returned by the browser agent
- `@node (1-1545)`: Structured node reference containing additional response data

**Example Usage:**
```python
response = get_task(task_id)
if 'answer' in json.dumps(response).lower():
    answer = response.get("answer")
    node_data = response.get("@node (1-1545)")
    print(f"Answer: {answer}")
```

**Notes:**
- This node appears in the final response when the task is complete
- The presence of `"answer"` key indicates task completion
- Node reference format: `@node (1-1545)` where numbers may vary

---

### Task List Response (`list_tasks`)

**Endpoint:** `GET /v1/task/list`

**Example Response:**
```json
{
  "tasks": [
    {
      "taskId": "string",
      "status": "string",
      "@node (1-1352)": {
        // Response structure to be documented
      }
    }
  ],
  "page": 1,
  "pageSize": 20
}
```

**Documented Nodes:**
- `@node (1-1352)`: [Description of what this node contains]

---

## Node Reference Format

When documenting a node, use the following template:

### `@node (N-M)`

**Context:** [Which endpoint/function returns this node]

**Structure:**
```json
{
  // Actual JSON structure observed
}
```

**Fields:**
- `fieldName`: Description of the field
- `anotherField`: Description of another field

**Example Usage:**
```python
# How to access this node in code
response = get_task(task_id)
if 'answer' in json.dumps(response).lower():
    # Task is complete
    node_data = response.get("@node (1-1545)")
    answer = response.get("answer")
```

**Notes:**
- Any additional observations or important information

---

## How to Update This Document

1. When you receive a response with a `@node` reference, copy the actual JSON structure
2. Add it to the appropriate section above
3. Document what each field represents
4. Include any relevant code examples for accessing the data

