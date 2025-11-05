"""
Todoist Task Hydration System

A Python package for transforming vague Todoist tasks into detailed,
actionable plans using Claude AI.
"""

__version__ = "1.0.0"

from .todoist_api import TodoistAPI, TodoistAPIError
from .hydrator import TaskHydrator, TaskHydrationError, HydratedTask
from .notebooklm_export import NotebookLMExporter

__all__ = [
    'TodoistAPI',
    'TodoistAPIError',
    'TaskHydrator',
    'TaskHydrationError',
    'HydratedTask',
    'NotebookLMExporter',
]
