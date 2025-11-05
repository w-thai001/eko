"""
Todoist API Wrapper with retry logic and error handling.
"""
import os
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('todoist_hydrate.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TodoistAPIError(Exception):
    """Custom exception for Todoist API errors."""
    pass


class TodoistAPI:
    """
    Clean wrapper for Todoist REST API v2.
    Handles authentication, requests, and error handling with exponential backoff.
    """

    BASE_URL = "https://api.todoist.com/rest/v2"
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1.0  # seconds

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Todoist API client.

        Args:
            api_token: Todoist API token. If None, reads from TODOIST_API_TOKEN env var.

        Raises:
            TodoistAPIError: If no API token is provided or found.
        """
        self.api_token = api_token or os.getenv("TODOIST_API_TOKEN")
        if not self.api_token:
            raise TodoistAPIError(
                "No API token provided. Set TODOIST_API_TOKEN environment variable "
                "or pass api_token parameter."
            )

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        logger.info("Todoist API client initialized")

    def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with exponential backoff retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object

        Raises:
            TodoistAPIError: If request fails after all retries
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        delay = self.INITIAL_RETRY_DELAY

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    timeout=30,
                    **kwargs
                )

                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', delay))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                # Raise for bad status codes
                response.raise_for_status()
                return response

            except RequestException as e:
                if attempt < self.MAX_RETRIES:
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.MAX_RETRIES + 1}): {e}. "
                        f"Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Request failed after {self.MAX_RETRIES + 1} attempts: {e}")
                    raise TodoistAPIError(f"Request failed: {e}") from e

        raise TodoistAPIError("Unexpected error in retry logic")

    def get_all_tasks(
        self,
        project_id: Optional[str] = None,
        label: Optional[str] = None,
        filter_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all tasks with optional filtering.

        Args:
            project_id: Filter by project ID
            label: Filter by label name (e.g., "@analyze")
            filter_query: Custom Todoist filter query

        Returns:
            List of task dictionaries
        """
        params = {}

        if project_id:
            params['project_id'] = project_id

        if label:
            params['label'] = label

        if filter_query:
            params['filter'] = filter_query

        try:
            response = self._request_with_retry('GET', '/tasks', params=params)
            tasks = response.json()
            logger.info(f"Retrieved {len(tasks)} tasks")
            return tasks
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            raise TodoistAPIError(f"Failed to get tasks: {e}") from e

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Get a specific task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task dictionary
        """
        try:
            response = self._request_with_retry('GET', f'/tasks/{task_id}')
            task = response.json()
            logger.info(f"Retrieved task: {task_id}")
            return task
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise TodoistAPIError(f"Failed to get task: {e}") from e

    def create_task(
        self,
        content: str,
        description: Optional[str] = None,
        project_id: Optional[str] = None,
        due_string: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: int = 1,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new task.

        Args:
            content: Task title/content
            description: Task description
            project_id: Project ID to add task to
            due_string: Due date in natural language (e.g., "tomorrow")
            due_date: Due date in YYYY-MM-DD format
            priority: Priority (1-4, where 4 is highest)
            labels: List of label names

        Returns:
            Created task dictionary
        """
        data = {
            "content": content,
            "priority": priority
        }

        if description:
            data["description"] = description

        if project_id:
            data["project_id"] = project_id

        if due_string:
            data["due_string"] = due_string
        elif due_date:
            data["due_date"] = due_date

        if labels:
            data["labels"] = labels

        try:
            response = self._request_with_retry('POST', '/tasks', json=data)
            task = response.json()
            logger.info(f"Created task: {task['id']}")
            return task
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise TodoistAPIError(f"Failed to create task: {e}") from e

    def update_task(
        self,
        task_id: str,
        content: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
        priority: Optional[int] = None,
        due_string: Optional[str] = None,
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing task.

        Args:
            task_id: Task ID
            content: New task title/content
            description: New task description
            labels: New list of labels
            priority: New priority (1-4)
            due_string: Due date in natural language
            due_date: Due date in YYYY-MM-DD format

        Returns:
            Updated task dictionary
        """
        data = {}

        if content is not None:
            data["content"] = content

        if description is not None:
            data["description"] = description

        if labels is not None:
            data["labels"] = labels

        if priority is not None:
            data["priority"] = priority

        if due_string is not None:
            data["due_string"] = due_string
        elif due_date is not None:
            data["due_date"] = due_date

        if not data:
            logger.warning(f"No update fields provided for task {task_id}")
            return self.get_task(task_id)

        try:
            response = self._request_with_retry('POST', f'/tasks/{task_id}', json=data)
            task = response.json()
            logger.info(f"Updated task: {task_id}")
            return task
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            raise TodoistAPIError(f"Failed to update task: {e}") from e

    def add_comment(
        self,
        task_id: str,
        content: str,
        attachment: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Add a comment to a task.

        Args:
            task_id: Task ID
            content: Comment content
            attachment: Optional attachment dict with 'resource_type' and 'file_url'

        Returns:
            Created comment dictionary
        """
        data = {
            "task_id": task_id,
            "content": content
        }

        if attachment:
            data["attachment"] = attachment

        try:
            response = self._request_with_retry('POST', '/comments', json=data)
            comment = response.json()
            logger.info(f"Added comment to task: {task_id}")
            return comment
        except Exception as e:
            logger.error(f"Failed to add comment to task {task_id}: {e}")
            raise TodoistAPIError(f"Failed to add comment: {e}") from e

    def get_comments(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get all comments for a task.

        Args:
            task_id: Task ID

        Returns:
            List of comment dictionaries
        """
        params = {"task_id": task_id}

        try:
            response = self._request_with_retry('GET', '/comments', params=params)
            comments = response.json()
            logger.info(f"Retrieved {len(comments)} comments for task: {task_id}")
            return comments
        except Exception as e:
            logger.error(f"Failed to get comments for task {task_id}: {e}")
            raise TodoistAPIError(f"Failed to get comments: {e}") from e

    def close_task(self, task_id: str) -> bool:
        """
        Close (complete) a task.

        Args:
            task_id: Task ID

        Returns:
            True if successful
        """
        try:
            self._request_with_retry('POST', f'/tasks/{task_id}/close')
            logger.info(f"Closed task: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to close task {task_id}: {e}")
            raise TodoistAPIError(f"Failed to close task: {e}") from e
