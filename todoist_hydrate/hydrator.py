"""
Task hydration module using Claude API to transform vague tasks into detailed plans.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from anthropic import Anthropic, APIError
from pydantic import BaseModel, Field, ValidationError

# Configure logging
logger = logging.getLogger(__name__)


class ActionItem(BaseModel):
    """Individual action item within a task."""
    item: str = Field(..., description="Specific action to take")
    estimated_minutes: int = Field(..., description="Estimated time in minutes")
    sequence: int = Field(..., description="Order of execution")


class Risk(BaseModel):
    """Potential blocker and mitigation strategy."""
    blocker: str = Field(..., description="Potential blocking issue")
    mitigation: str = Field(..., description="Strategy to address the blocker")


class HydratedTask(BaseModel):
    """Structured output from task hydration."""
    refined_title: str = Field(..., description="Clear, action-oriented task title")
    action_items: List[ActionItem] = Field(..., description="Sequential action items")
    total_estimate_minutes: int = Field(..., description="Total estimated time")
    confidence: str = Field(..., description="Confidence level: high, medium, or low")
    complexity: int = Field(..., ge=1, le=5, description="Complexity rating 1-5")
    dependencies: List[str] = Field(default_factory=list, description="Required prerequisites")
    success_criteria: List[str] = Field(..., description="Measurable outcomes")
    risks: List[Risk] = Field(default_factory=list, description="Potential blockers and mitigations")


class TaskHydrationError(Exception):
    """Custom exception for task hydration errors."""
    pass


class TaskHydrator:
    """
    Transforms vague tasks into detailed, structured plans using Claude API.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize task hydrator.

        Args:
            api_key: Anthropic API key. If None, reads from ANTHROPIC_API_KEY env var.
            model: Claude model to use.

        Raises:
            TaskHydrationError: If no API key is provided or found.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise TaskHydrationError(
                "No API key provided. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        logger.info(f"Task hydrator initialized with model: {model}")

    def _build_prompt(
        self,
        task_content: str,
        labels: List[str],
        due_date: Optional[str] = None
    ) -> str:
        """
        Build the prompt for Claude API.

        Args:
            task_content: Original vague task description
            labels: Current task labels
            due_date: Optional due date

        Returns:
            Formatted prompt string
        """
        schema = HydratedTask.model_json_schema()

        prompt = f"""You are an expert task analyst. Transform this vague task into a well-specified, actionable plan.

TASK: {task_content}
CURRENT LABELS: {', '.join(labels) if labels else 'None'}
DUE DATE: {due_date if due_date else 'Not specified'}

Provide a structured analysis with:
1. Refined title (action-oriented, specific)
2. Sequential action items (each ≤ 90 minutes)
3. Time estimates (realistic + 25% buffer)
4. Complexity rating (1=routine, 5=novel)
5. Dependencies (what must happen first)
6. Success criteria (measurable outcomes)
7. Risks (likely blockers + mitigations)

Apply these principles:
- Use reference class forecasting (multiply intuitive estimates by 1.6x for novel tasks)
- Break complex work into ≤ 90-minute chunks
- Flag low-confidence estimates explicitly
- Consider context switching overhead (add 15 min per interruption expected)
- Be realistic about time estimates - add buffer for unknowns
- For complexity 4-5 tasks, be extra conservative with time estimates

Output ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Remember:
- action_items: array of objects with 'item' (string), 'estimated_minutes' (integer), 'sequence' (integer)
- total_estimate_minutes: sum of all action item estimates
- confidence: must be exactly "high", "medium", or "low"
- complexity: integer from 1 to 5
- dependencies: array of strings
- success_criteria: array of strings
- risks: array of objects with 'blocker' (string) and 'mitigation' (string)
"""
        return prompt

    def hydrate_task(
        self,
        task_id: str,
        task_content: str,
        labels: List[str],
        due_date: Optional[str] = None,
        max_tokens: int = 4096
    ) -> HydratedTask:
        """
        Hydrate a task using Claude API.

        Args:
            task_id: Task ID (for logging)
            task_content: Original vague task description
            labels: Current task labels
            due_date: Optional due date
            max_tokens: Maximum tokens for Claude response

        Returns:
            HydratedTask object with structured task information

        Raises:
            TaskHydrationError: If hydration fails
        """
        logger.info(f"Hydrating task {task_id}: {task_content[:50]}...")

        prompt = self._build_prompt(task_content, labels, due_date)

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.5,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract response text
            response_text = response.content[0].text
            logger.debug(f"Claude response: {response_text[:200]}...")

            # Parse JSON response
            try:
                response_json = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response_text}")
                raise TaskHydrationError(f"Invalid JSON response from Claude: {e}") from e

            # Validate and create HydratedTask
            try:
                hydrated_task = HydratedTask(**response_json)
                logger.info(
                    f"Successfully hydrated task {task_id}: "
                    f"{len(hydrated_task.action_items)} actions, "
                    f"{hydrated_task.total_estimate_minutes} minutes"
                )
                return hydrated_task
            except ValidationError as e:
                logger.error(f"Failed to validate hydrated task: {e}")
                raise TaskHydrationError(f"Invalid hydration output: {e}") from e

        except APIError as e:
            logger.error(f"Claude API error: {e}")
            raise TaskHydrationError(f"Claude API error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during hydration: {e}")
            raise TaskHydrationError(f"Hydration failed: {e}") from e

    def hydrate_to_json(
        self,
        task_id: str,
        task_content: str,
        labels: List[str],
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Hydrate a task and return as dictionary.

        Args:
            task_id: Task ID
            task_content: Original task content
            labels: Current labels
            due_date: Optional due date

        Returns:
            Dictionary representation of hydrated task
        """
        hydrated = self.hydrate_task(task_id, task_content, labels, due_date)
        return hydrated.model_dump()

    def format_for_todoist(self, hydrated: HydratedTask) -> str:
        """
        Format hydrated task as markdown for Todoist description.

        Args:
            hydrated: HydratedTask object

        Returns:
            Markdown-formatted string
        """
        lines = [
            f"# {hydrated.refined_title}",
            "",
            f"**Estimated Time:** {hydrated.total_estimate_minutes} minutes ({hydrated.total_estimate_minutes / 60:.1f} hours)",
            f"**Complexity:** {hydrated.complexity}/5",
            f"**Confidence:** {hydrated.confidence}",
            "",
            "## Action Items",
            ""
        ]

        for action in sorted(hydrated.action_items, key=lambda x: x.sequence):
            lines.append(f"{action.sequence}. {action.item} (~{action.estimated_minutes} min)")

        if hydrated.dependencies:
            lines.extend([
                "",
                "## Dependencies",
                ""
            ])
            for dep in hydrated.dependencies:
                lines.append(f"- {dep}")

        lines.extend([
            "",
            "## Success Criteria",
            ""
        ])
        for criterion in hydrated.success_criteria:
            lines.append(f"- {criterion}")

        if hydrated.risks:
            lines.extend([
                "",
                "## Risks & Mitigations",
                ""
            ])
            for risk in hydrated.risks:
                lines.append(f"**{risk.blocker}**")
                lines.append(f"→ Mitigation: {risk.mitigation}")
                lines.append("")

        return "\n".join(lines)
