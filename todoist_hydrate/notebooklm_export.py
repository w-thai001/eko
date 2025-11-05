"""
NotebookLM export module for formatting completed tasks for analysis and learning.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from hydrator import HydratedTask

# Configure logging
logger = logging.getLogger(__name__)


class NotebookLMExporter:
    """
    Formats completed tasks for NotebookLM ingestion and pattern analysis.
    """

    def __init__(self, export_dir: str = "./exports"):
        """
        Initialize NotebookLM exporter.

        Args:
            export_dir: Directory to save export files
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"NotebookLM exporter initialized. Export dir: {self.export_dir}")

    def _classify_task_type(
        self,
        hydrated: HydratedTask,
        original_task: str
    ) -> str:
        """
        Auto-classify task type for pattern matching.

        Args:
            hydrated: Hydrated task object
            original_task: Original task content

        Returns:
            Task type classification
        """
        # Simple heuristic-based classification
        content_lower = original_task.lower()

        if any(word in content_lower for word in ['bug', 'fix', 'error', 'issue', 'broken']):
            return "Bug Fix"
        elif any(word in content_lower for word in ['feature', 'add', 'implement', 'create', 'build']):
            return "Feature Development"
        elif any(word in content_lower for word in ['refactor', 'improve', 'optimize', 'cleanup', 'reorganize']):
            return "Refactoring"
        elif any(word in content_lower for word in ['research', 'investigate', 'explore', 'analyze', 'study']):
            return "Research"
        elif any(word in content_lower for word in ['test', 'qa', 'verify', 'validate']):
            return "Testing"
        elif any(word in content_lower for word in ['doc', 'documentation', 'write', 'guide']):
            return "Documentation"
        elif any(word in content_lower for word in ['meet', 'call', 'discuss', 'review']):
            return "Meeting/Communication"
        else:
            if hydrated.complexity <= 2:
                return "Routine Task"
            elif hydrated.complexity >= 4:
                return "Complex Project"
            else:
                return "General Task"

    def _calculate_accuracy(
        self,
        estimated_minutes: int,
        actual_minutes: Optional[int]
    ) -> Optional[float]:
        """
        Calculate estimation accuracy percentage.

        Args:
            estimated_minutes: Estimated time
            actual_minutes: Actual time spent

        Returns:
            Accuracy percentage or None if actual time not available
        """
        if actual_minutes is None or actual_minutes == 0:
            return None

        # Calculate accuracy as 100 - absolute percentage error
        error = abs(estimated_minutes - actual_minutes) / actual_minutes
        accuracy = max(0, 100 - (error * 100))
        return round(accuracy, 1)

    def export_task(
        self,
        task_id: str,
        original_task: str,
        hydrated: HydratedTask,
        labels: List[str],
        actual_minutes: Optional[int] = None,
        learnings: Optional[Dict[str, str]] = None,
        completion_date: Optional[datetime] = None
    ) -> str:
        """
        Export a completed task to NotebookLM format.

        Args:
            task_id: Task ID
            original_task: Original vague task description
            hydrated: HydratedTask object
            labels: Task labels
            actual_minutes: Actual time spent (if known)
            learnings: Optional dict with 'what_went_well', 'what_took_longer', 'blockers_encountered'
            completion_date: Task completion date

        Returns:
            Path to exported markdown file
        """
        if completion_date is None:
            completion_date = datetime.now()

        date_str = completion_date.strftime("%Y-%m-%d")
        task_type = self._classify_task_type(hydrated, original_task)

        # Calculate accuracy if actual time is available
        accuracy = self._calculate_accuracy(hydrated.total_estimate_minutes, actual_minutes)

        # Build markdown content
        lines = [
            f"# Task Completion Record: {date_str}",
            "",
            f"**Task ID:** {task_id}",
            f"**Task Type:** {task_type}",
            "",
            f"## Task: {hydrated.refined_title}",
            "",
            f"- **Original**: {original_task}",
            f"- **Estimated**: {hydrated.total_estimate_minutes} minutes ({hydrated.total_estimate_minutes / 60:.1f} hours)",
        ]

        if actual_minutes is not None:
            lines.append(f"- **Actual**: {actual_minutes} minutes ({actual_minutes / 60:.1f} hours)")
            if accuracy is not None:
                lines.append(f"- **Accuracy**: {accuracy}%")
                if accuracy >= 80:
                    lines.append("  - ✅ Excellent estimation")
                elif accuracy >= 60:
                    lines.append("  - ⚠️ Good estimation, room for improvement")
                else:
                    lines.append("  - ❌ Significant estimation error - review assumptions")
        else:
            lines.append("- **Actual**: Not tracked")
            lines.append("- **Accuracy**: N/A")

        lines.extend([
            f"- **Complexity**: {hydrated.complexity}/5",
            f"- **Confidence**: {hydrated.confidence}",
            f"- **Labels**: {', '.join(labels) if labels else 'None'}",
            "",
            "## Action Items Completed",
            ""
        ])

        for action in sorted(hydrated.action_items, key=lambda x: x.sequence):
            lines.append(f"- [x] {action.item} (~{action.estimated_minutes} min)")

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
                "## Identified Risks",
                ""
            ])
            for risk in hydrated.risks:
                lines.append(f"- **{risk.blocker}**")
                lines.append(f"  - Mitigation: {risk.mitigation}")

        # Add learnings section
        lines.extend([
            "",
            "## Learnings",
            ""
        ])

        if learnings:
            if learnings.get('what_went_well'):
                lines.append(f"**What went well**: {learnings['what_went_well']}")
            else:
                lines.append("**What went well**: Not recorded")

            lines.append("")

            if learnings.get('what_took_longer'):
                lines.append(f"**What took longer than expected**: {learnings['what_took_longer']}")
            else:
                lines.append("**What took longer than expected**: Not recorded")

            lines.append("")

            if learnings.get('blockers_encountered'):
                lines.append(f"**Blockers encountered**: {learnings['blockers_encountered']}")
            else:
                lines.append("**Blockers encountered**: None reported")
        else:
            lines.extend([
                "**What went well**: Not recorded",
                "",
                "**What took longer than expected**: Not recorded",
                "",
                "**Blockers encountered**: None reported"
            ])

        lines.extend([
            "",
            "## Pattern Classification",
            "",
            f"**Type**: {task_type}",
            f"**Complexity**: {hydrated.complexity}/5",
            f"**Confidence Level**: {hydrated.confidence}",
            ""
        ])

        # Add tags for pattern matching
        tags = [
            f"complexity-{hydrated.complexity}",
            f"confidence-{hydrated.confidence}",
            task_type.lower().replace(' ', '-').replace('/', '-')
        ]

        if actual_minutes and accuracy:
            if accuracy >= 80:
                tags.append("accurate-estimate")
            elif accuracy < 60:
                tags.append("inaccurate-estimate")

        lines.append(f"**Tags**: {', '.join(tags)}")

        # Write to file
        filename = f"{date_str}_{task_id}_{task_type.replace(' ', '_').replace('/', '_')}.md"
        filepath = self.export_dir / filename

        content = "\n".join(lines)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Exported task to: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to export task: {e}")
            raise

    def export_calibration_stats(
        self,
        export_records: List[Dict[str, Any]],
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate calibration statistics from multiple export records.

        Args:
            export_records: List of dicts with 'estimated_minutes', 'actual_minutes', 'complexity', etc.
            output_file: Optional custom output filename

        Returns:
            Path to statistics file
        """
        if not export_records:
            logger.warning("No export records provided for calibration stats")
            return ""

        # Filter records with actual time
        valid_records = [r for r in export_records if r.get('actual_minutes') is not None]

        if not valid_records:
            logger.warning("No records with actual time tracked")
            return ""

        # Calculate statistics
        total_tasks = len(valid_records)
        total_estimated = sum(r['estimated_minutes'] for r in valid_records)
        total_actual = sum(r['actual_minutes'] for r in valid_records)

        avg_accuracy = sum(
            self._calculate_accuracy(r['estimated_minutes'], r['actual_minutes']) or 0
            for r in valid_records
        ) / total_tasks

        # Group by complexity
        by_complexity = {}
        for r in valid_records:
            complexity = r.get('complexity', 3)
            if complexity not in by_complexity:
                by_complexity[complexity] = []
            by_complexity[complexity].append(r)

        # Build report
        lines = [
            "# Task Estimation Calibration Report",
            "",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Total Tasks Analyzed**: {total_tasks}",
            "",
            "## Overall Statistics",
            "",
            f"- **Total Estimated Time**: {total_estimated} minutes ({total_estimated / 60:.1f} hours)",
            f"- **Total Actual Time**: {total_actual} minutes ({total_actual / 60:.1f} hours)",
            f"- **Overall Accuracy**: {avg_accuracy:.1f}%",
            f"- **Estimation Ratio**: {total_actual / total_estimated:.2f}x actual vs. estimated",
            "",
            "## Breakdown by Complexity",
            ""
        ]

        for complexity in sorted(by_complexity.keys()):
            records = by_complexity[complexity]
            est = sum(r['estimated_minutes'] for r in records)
            act = sum(r['actual_minutes'] for r in records)
            acc = sum(
                self._calculate_accuracy(r['estimated_minutes'], r['actual_minutes']) or 0
                for r in records
            ) / len(records)

            lines.extend([
                f"### Complexity {complexity}/5",
                f"- Tasks: {len(records)}",
                f"- Average Accuracy: {acc:.1f}%",
                f"- Estimation Ratio: {act / est:.2f}x",
                ""
            ])

        lines.extend([
            "## Recommendations",
            ""
        ])

        if avg_accuracy >= 80:
            lines.append("✅ Your estimations are well-calibrated. Keep up the good work!")
        elif avg_accuracy >= 60:
            lines.append("⚠️ Your estimations are decent but could be improved.")
            lines.append("- Consider adding more buffer for unfamiliar tasks")
            lines.append("- Track blockers and interruptions more carefully")
        else:
            lines.append("❌ Your estimations need significant improvement.")
            lines.append("- Apply 1.6x multiplier for novel tasks (complexity 4-5)")
            lines.append("- Break down tasks into smaller chunks")
            lines.append("- Review past similar tasks before estimating")

        # Save report
        if output_file is None:
            output_file = f"calibration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        filepath = self.export_dir / output_file

        content = "\n".join(lines)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Generated calibration report: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to generate calibration report: {e}")
            raise
