#!/usr/bin/env python3
"""
Command-line interface for Todoist task hydration system.
"""
import sys
import json
import argparse
import logging
from typing import Optional
from datetime import datetime
from pathlib import Path

from todoist_api import TodoistAPI, TodoistAPIError
from hydrator import TaskHydrator, TaskHydrationError, HydratedTask
from notebooklm_export import NotebookLMExporter

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


class TodoistHydrateCLI:
    """Main CLI application."""

    def __init__(self):
        """Initialize CLI with API clients."""
        try:
            self.todoist = TodoistAPI()
            self.hydrator = TaskHydrator()
            self.exporter = NotebookLMExporter()
            logger.info("CLI initialized successfully")
        except (TodoistAPIError, TaskHydrationError) as e:
            logger.error(f"Failed to initialize CLI: {e}")
            print(f"Error: {e}", file=sys.stderr)
            print("\nMake sure you have set the required environment variables:")
            print("  - TODOIST_API_TOKEN")
            print("  - ANTHROPIC_API_KEY")
            sys.exit(1)

    def hydrate_task(self, task_id: str, update_todoist: bool = True) -> None:
        """
        Hydrate a specific task.

        Args:
            task_id: Task ID to hydrate
            update_todoist: Whether to update the task in Todoist with hydrated content
        """
        try:
            print(f"\n🔍 Fetching task {task_id}...")
            task = self.todoist.get_task(task_id)

            print(f"📝 Task: {task['content']}")
            print(f"   Labels: {', '.join(task.get('labels', []))}")

            due_date = None
            if task.get('due'):
                due_date = task['due'].get('date')
                print(f"   Due: {due_date}")

            print("\n🧠 Hydrating with Claude...")
            hydrated = self.hydrator.hydrate_task(
                task_id=task_id,
                task_content=task['content'],
                labels=task.get('labels', []),
                due_date=due_date
            )

            # Display results
            print(f"\n✅ Hydration complete!")
            print(f"\n📋 Refined Title: {hydrated.refined_title}")
            print(f"⏱️  Total Estimate: {hydrated.total_estimate_minutes} minutes ({hydrated.total_estimate_minutes / 60:.1f} hours)")
            print(f"🎯 Complexity: {hydrated.complexity}/5")
            print(f"📊 Confidence: {hydrated.confidence}")

            print(f"\n📍 Action Items ({len(hydrated.action_items)}):")
            for action in sorted(hydrated.action_items, key=lambda x: x.sequence):
                print(f"  {action.sequence}. {action.item} (~{action.estimated_minutes} min)")

            if hydrated.dependencies:
                print(f"\n🔗 Dependencies:")
                for dep in hydrated.dependencies:
                    print(f"  - {dep}")

            print(f"\n✓ Success Criteria:")
            for criterion in hydrated.success_criteria:
                print(f"  - {criterion}")

            if hydrated.risks:
                print(f"\n⚠️  Risks:")
                for risk in hydrated.risks:
                    print(f"  - {risk.blocker}")
                    print(f"    → {risk.mitigation}")

            # Update Todoist if requested
            if update_todoist:
                print("\n💾 Updating Todoist task...")
                description = self.hydrator.format_for_todoist(hydrated)

                self.todoist.update_task(
                    task_id=task_id,
                    description=description
                )

                # Add hydration label
                labels = task.get('labels', [])
                if 'hydrated' not in labels:
                    labels.append('hydrated')
                    self.todoist.update_task(task_id=task_id, labels=labels)

                print("✅ Task updated in Todoist")

            # Save to JSON
            output_file = f"hydrated_{task_id}.json"
            with open(output_file, 'w') as f:
                json.dump(hydrated.model_dump(), f, indent=2)
            print(f"\n💾 Saved hydration to: {output_file}")

        except (TodoistAPIError, TaskHydrationError) as e:
            logger.error(f"Failed to hydrate task: {e}")
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)

    def batch_hydrate(self, label: str, update_todoist: bool = True) -> None:
        """
        Hydrate all tasks with a specific label.

        Args:
            label: Label to filter tasks by
            update_todoist: Whether to update tasks in Todoist
        """
        try:
            print(f"\n🔍 Fetching tasks with label '{label}'...")
            tasks = self.todoist.get_all_tasks(label=label)

            if not tasks:
                print(f"No tasks found with label '{label}'")
                return

            print(f"Found {len(tasks)} tasks to hydrate\n")

            success_count = 0
            error_count = 0

            for i, task in enumerate(tasks, 1):
                task_id = task['id']
                print(f"\n{'=' * 60}")
                print(f"[{i}/{len(tasks)}] Task ID: {task_id}")
                print(f"{'=' * 60}")

                try:
                    self.hydrate_task(task_id, update_todoist=update_todoist)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to hydrate task {task_id}: {e}")
                    print(f"❌ Error: {e}", file=sys.stderr)
                    error_count += 1
                    continue

            print(f"\n{'=' * 60}")
            print(f"✅ Batch hydration complete!")
            print(f"   Successful: {success_count}")
            print(f"   Errors: {error_count}")
            print(f"{'=' * 60}")

        except TodoistAPIError as e:
            logger.error(f"Failed to fetch tasks: {e}")
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)

    def export_task(self, task_id: str) -> None:
        """
        Export a completed task to NotebookLM format.

        Args:
            task_id: Task ID to export
        """
        try:
            print(f"\n🔍 Fetching task {task_id}...")
            task = self.todoist.get_task(task_id)

            # Load hydration data if available
            hydration_file = f"hydrated_{task_id}.json"
            if Path(hydration_file).exists():
                print(f"📂 Loading hydration data from {hydration_file}...")
                with open(hydration_file, 'r') as f:
                    hydration_data = json.load(f)
                hydrated = HydratedTask(**hydration_data)
            else:
                print(f"⚠️  No hydration data found. Generating now...")
                hydrated = self.hydrator.hydrate_task(
                    task_id=task_id,
                    task_content=task['content'],
                    labels=task.get('labels', []),
                    due_date=task.get('due', {}).get('date') if task.get('due') else None
                )

            # Get comments for learnings
            print("📝 Fetching task comments...")
            comments = self.todoist.get_comments(task_id)

            # Parse learnings from comments (if any follow a specific format)
            learnings = None
            for comment in comments:
                content = comment.get('content', '')
                if 'LEARNINGS:' in content.upper():
                    # Simple parsing - in production you might want more sophisticated parsing
                    learnings = {'what_went_well': 'See comments', 'what_took_longer': '', 'blockers_encountered': ''}
                    break

            # Prompt for actual time if not in comments
            print("\n⏱️  Enter actual time spent (in minutes), or press Enter to skip:")
            actual_minutes_input = input("> ").strip()
            actual_minutes = int(actual_minutes_input) if actual_minutes_input else None

            # Export
            print("\n📤 Generating NotebookLM export...")
            filepath = self.exporter.export_task(
                task_id=task_id,
                original_task=task['content'],
                hydrated=hydrated,
                labels=task.get('labels', []),
                actual_minutes=actual_minutes,
                learnings=learnings
            )

            print(f"\n✅ Exported to: {filepath}")

        except (TodoistAPIError, TaskHydrationError) as e:
            logger.error(f"Failed to export task: {e}")
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"\n❌ Invalid input: {e}", file=sys.stderr)
            sys.exit(1)

    def analyze_calibration(self) -> None:
        """Show calibration statistics from recent task exports."""
        try:
            print("\n📊 Analyzing task estimation calibration...")

            export_dir = Path("./exports")
            if not export_dir.exists():
                print("❌ No exports directory found. Export some tasks first.")
                return

            # Find all export files
            export_files = list(export_dir.glob("*.md"))

            if not export_files:
                print("❌ No export files found. Export some completed tasks first.")
                return

            print(f"Found {len(export_files)} export files")

            # Parse export files for statistics
            # In a production system, you'd store this data in a database
            # For now, we'll generate a simple report

            print("\n📈 Recent exports:")
            for export_file in sorted(export_files)[-10:]:  # Last 10
                print(f"  - {export_file.name}")

            print("\n💡 Tip: To generate detailed calibration stats, run:")
            print("   python -c \"from notebooklm_export import NotebookLMExporter; exporter = NotebookLMExporter(); exporter.export_calibration_stats([])\"")

            print("\n📝 Note: For full calibration analysis, you need to track actual time spent on tasks.")
            print("   Add a comment to completed tasks with format: 'ACTUAL_TIME: X minutes'")

        except Exception as e:
            logger.error(f"Failed to analyze calibration: {e}")
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Todoist Task Hydration System - Transform vague tasks into actionable plans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Hydrate a specific task
  python cli.py hydrate abc123

  # Hydrate without updating Todoist
  python cli.py hydrate abc123 --no-update

  # Hydrate all tasks with a label
  python cli.py batch --label @analyze

  # Export a completed task
  python cli.py export abc123

  # Show calibration statistics
  python cli.py analyze
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Hydrate command
    hydrate_parser = subparsers.add_parser('hydrate', help='Hydrate a specific task')
    hydrate_parser.add_argument('task_id', help='Task ID to hydrate')
    hydrate_parser.add_argument(
        '--no-update',
        action='store_true',
        help='Do not update the task in Todoist'
    )

    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Hydrate all tasks with a label')
    batch_parser.add_argument('--label', required=True, help='Label to filter tasks by (e.g., @analyze)')
    batch_parser.add_argument(
        '--no-update',
        action='store_true',
        help='Do not update tasks in Todoist'
    )

    # Export command
    export_parser = subparsers.add_parser('export', help='Export completed task to NotebookLM format')
    export_parser.add_argument('task_id', help='Task ID to export')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Show calibration statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    cli = TodoistHydrateCLI()

    # Execute command
    if args.command == 'hydrate':
        cli.hydrate_task(args.task_id, update_todoist=not args.no_update)
    elif args.command == 'batch':
        cli.batch_hydrate(args.label, update_todoist=not args.no_update)
    elif args.command == 'export':
        cli.export_task(args.task_id)
    elif args.command == 'analyze':
        cli.analyze_calibration()


if __name__ == '__main__':
    main()
