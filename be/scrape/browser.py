"""
Browser Cash API client library.

This module provides a Python interface to the Browser Cash Agent API.
Responses from the API typically include node references in the format:
@node (1-1352)
"""

import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

BROWSER_AGENT_API_KEY = os.getenv("BROWSER_CASH_AGENT_API_KEY")
BROWSER_CASH_API_BASE = os.getenv("BROWSER_CASH_API_BASE")


def create_task(
    agent: str = "gemini",
    prompt: str = "",
    mode: str = "text",
    step_limit: int = 10
) -> Dict[str, Any]:
    """
    Create a new browser automation task.
    
    Args:
        agent: The agent to use (default: "gemini")
        prompt: The task prompt/question
        mode: The mode of operation (default: "text")
        step_limit: Maximum number of steps (default: 10)
    
    Returns:
        Dict containing task information, typically including:
        - taskId: The unique task identifier
        - Other response fields that may include node references like @node (1-1352)
    
    Raises:
        requests.RequestException: If the API request fails
    """
    resp = requests.post(
        BROWSER_CASH_API_BASE + "/v1/task/create",
        headers={
            "Authorization": f"Bearer {BROWSER_AGENT_API_KEY}",
            "content-type": "application/json",
        },
        json={
            "agent": agent,
            "prompt": prompt,
            "mode": mode,
            "stepLimit": step_limit
        },
    )
    resp.raise_for_status()
    return resp.json()


def get_task(task_id: str) -> Dict[str, Any]:
    """
    Retrieve the status and results of a task.
    
    Args:
        task_id: The unique task identifier
    
    Returns:
        Dict containing task status and results, which may include:
        - Status information
        - Results with node references in format @node (1-1352)
        - Other task metadata
    
    Raises:
        requests.RequestException: If the API request fails
    """
    resp = requests.get(
        f"{BROWSER_CASH_API_BASE}/v1/task/{task_id}",
        headers={"Authorization": f"Bearer {BROWSER_AGENT_API_KEY}"},
    )
    resp.raise_for_status()
    return resp.json()


def list_tasks(page_size: int = 20, page: int = 1) -> Dict[str, Any]:
    """
    List all tasks with pagination.
    
    Args:
        page_size: Number of tasks per page (default: 20)
        page: Page number (default: 1)
    
    Returns:
        Dict containing a list of tasks, where each task may include:
        - taskId: The unique task identifier
        - Status and metadata
        - Results with node references like @node (1-1352)
    
    Raises:
        requests.RequestException: If the API request fails
    """
    resp = requests.get(
        f"{BROWSER_CASH_API_BASE}/v1/task/list",
        headers={"Authorization": f"Bearer {BROWSER_AGENT_API_KEY}"},
        params={"pageSize": page_size, "page": page},
    )
    resp.raise_for_status()
    return resp.json()

