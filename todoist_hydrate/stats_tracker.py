"""
Statistics tracking and pattern analysis for task hydration system.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

from hydrator import HydratedTask

# Configure logging
logger = logging.getLogger(__name__)


class StatsTracker:
    """
    Tracks hydration statistics and calibration data.
    """

    def __init__(self, data_file: str = "./stats_data.json"):
        """
        Initialize stats tracker.

        Args:
            data_file: Path to JSON file for persistent storage
        """
        self.data_file = Path(data_file)
        self.data = self._load_data()
        logger.info(f"Stats tracker initialized with {len(self.data.get('hydrations', {}))} hydrations")

    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load stats data: {e}")
                return self._empty_data()
        return self._empty_data()

    def _empty_data(self) -> Dict[str, Any]:
        """Return empty data structure."""
        return {
            "hydrations": {},
            "completions": {},
            "patterns": []
        }

    def _save_data(self):
        """Save data to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save stats data: {e}")

    def track_hydration(
        self,
        task_id: str,
        task_content: str,
        hydrated: HydratedTask,
        labels: List[str]
    ):
        """
        Track a task hydration.

        Args:
            task_id: Task ID
            task_content: Original task content
            hydrated: Hydrated task object
            labels: Task labels
        """
        self.data["hydrations"][task_id] = {
            "task_content": task_content,
            "hydrated": hydrated.model_dump(),
            "labels": labels,
            "timestamp": datetime.now().isoformat(),
            "completed": False
        }
        self._save_data()
        logger.info(f"Tracked hydration for task {task_id}")

    def track_completion(
        self,
        task_id: str,
        actual_minutes: Optional[int],
        outcome: str
    ):
        """
        Track task completion.

        Args:
            task_id: Task ID
            actual_minutes: Actual time spent
            outcome: "completed" or "abandoned"
        """
        if task_id in self.data["hydrations"]:
            self.data["hydrations"][task_id]["completed"] = True
            self.data["hydrations"][task_id]["actual_minutes"] = actual_minutes
            self.data["hydrations"][task_id]["outcome"] = outcome
            self.data["hydrations"][task_id]["completion_timestamp"] = datetime.now().isoformat()

            # Add to completions list
            self.data["completions"][task_id] = {
                "actual_minutes": actual_minutes,
                "outcome": outcome,
                "timestamp": datetime.now().isoformat()
            }

            self._save_data()
            logger.info(f"Tracked completion for task {task_id}")
        else:
            logger.warning(f"Cannot track completion - no hydration found for task {task_id}")

    def get_hydration(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get hydration data for a task."""
        return self.data["hydrations"].get(task_id)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics.

        Returns:
            Dictionary with stats including totals, accuracy, patterns, etc.
        """
        hydrations = self.data["hydrations"]
        total_hydrated = len(hydrations)

        # Count completed tasks
        completed = [h for h in hydrations.values() if h.get("completed")]
        total_completed = len(completed)

        # Calculate accuracy for tasks with actual time
        tracked_completions = [
            h for h in completed
            if h.get("actual_minutes") is not None and h.get("outcome") == "completed"
        ]

        avg_accuracy = None
        calibration_factor = None

        if tracked_completions:
            accuracies = []
            total_estimated = 0
            total_actual = 0

            for h in tracked_completions:
                estimated = h["hydrated"]["total_estimate_minutes"]
                actual = h["actual_minutes"]

                if actual > 0:
                    error = abs(estimated - actual) / actual
                    accuracy = max(0, 100 - (error * 100))
                    accuracies.append(accuracy)

                    total_estimated += estimated
                    total_actual += actual

            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)

            if total_estimated > 0:
                calibration_factor = total_actual / total_estimated

        # Group by task type/pattern
        patterns = self._analyze_patterns(hydrations)

        # Get recent hydrations (last 10)
        recent = sorted(
            [
                {
                    "task_id": task_id,
                    "task_content": h["task_content"],
                    "refined_title": h["hydrated"].get("refined_title"),
                    "estimated_minutes": h["hydrated"]["total_estimate_minutes"],
                    "complexity": h["hydrated"]["complexity"],
                    "timestamp": h["timestamp"]
                }
                for task_id, h in hydrations.items()
            ],
            key=lambda x: x["timestamp"],
            reverse=True
        )[:10]

        return {
            "total_hydrated": total_hydrated,
            "total_completed": total_completed,
            "avg_accuracy": avg_accuracy,
            "calibration_factor": calibration_factor,
            "patterns": patterns,
            "recent_hydrations": recent
        }

    def _analyze_patterns(self, hydrations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patterns in hydrated tasks."""
        # Group by complexity
        by_complexity = defaultdict(list)

        for h in hydrations.values():
            complexity = h["hydrated"]["complexity"]
            by_complexity[complexity].append(h)

        patterns = []
        for complexity, tasks in sorted(by_complexity.items()):
            if not tasks:
                continue

            # Calculate average estimated time
            avg_estimated = sum(
                t["hydrated"]["total_estimate_minutes"] for t in tasks
            ) / len(tasks)

            # Calculate average actual time (if available)
            completed_tasks = [
                t for t in tasks
                if t.get("completed") and t.get("actual_minutes") is not None
            ]

            avg_actual = None
            if completed_tasks:
                avg_actual = sum(t["actual_minutes"] for t in completed_tasks) / len(completed_tasks)

            patterns.append({
                "type": f"Complexity {complexity}/5",
                "count": len(tasks),
                "avg_estimated_minutes": round(avg_estimated, 1),
                "avg_actual_minutes": round(avg_actual, 1) if avg_actual else None
            })

        return patterns


class PatternAnalyzer:
    """
    Analyzes completed tasks and generates pattern reports.
    """

    def __init__(
        self,
        stats_tracker: Optional[StatsTracker] = None,
        patterns_dir: str = "./notebooklm_sources/patterns"
    ):
        """
        Initialize pattern analyzer.

        Args:
            stats_tracker: StatsTracker instance (creates new if None)
            patterns_dir: Directory for pattern files
        """
        self.stats_tracker = stats_tracker or StatsTracker()
        self.patterns_dir = Path(patterns_dir)
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Pattern analyzer initialized")

    def analyze_and_update(self):
        """
        Analyze patterns and update pattern files.
        Generates new pattern files when 10+ similar tasks are completed.
        """
        try:
            hydrations = self.stats_tracker.data["hydrations"]

            # Group by labels
            by_label = defaultdict(list)
            for task_id, h in hydrations.items():
                if h.get("completed"):
                    for label in h.get("labels", []):
                        if label not in ["processed", "hydrated"]:
                            by_label[label].append((task_id, h))

            # Generate pattern files for labels with 10+ tasks
            for label, tasks in by_label.items():
                if len(tasks) >= 10:
                    self._generate_pattern_file(label, tasks)

            # Generate overall patterns
            self._generate_overall_patterns(hydrations)

        except Exception as e:
            logger.error(f"Failed to analyze patterns: {e}")

    def _generate_pattern_file(self, label: str, tasks: List[tuple]):
        """Generate a pattern file for a specific label."""
        try:
            filename = f"{label.replace('@', '').replace(' ', '_')}_patterns.md"
            filepath = self.patterns_dir / filename

            # Calculate statistics
            total_tasks = len(tasks)
            total_estimated = sum(t[1]["hydrated"]["total_estimate_minutes"] for t in tasks)
            avg_estimated = total_estimated / total_tasks

            completed_with_time = [
                t for t in tasks
                if t[1].get("actual_minutes") is not None
            ]

            avg_actual = None
            accuracy = None

            if completed_with_time:
                total_actual = sum(t[1]["actual_minutes"] for t in completed_with_time)
                avg_actual = total_actual / len(completed_with_time)

                if total_estimated > 0:
                    error = abs(total_estimated - total_actual) / total_actual
                    accuracy = max(0, 100 - (error * 100))

            # Group by complexity
            by_complexity = defaultdict(int)
            for t in tasks:
                complexity = t[1]["hydrated"]["complexity"]
                by_complexity[complexity] += 1

            # Build markdown content
            lines = [
                f"# {label.title()} Task Patterns",
                "",
                f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"**Total Tasks**: {total_tasks}",
                "",
                "## Time Estimates",
                "",
                f"- **Average Estimated Time**: {avg_estimated:.1f} minutes ({avg_estimated/60:.1f} hours)",
            ]

            if avg_actual:
                lines.extend([
                    f"- **Average Actual Time**: {avg_actual:.1f} minutes ({avg_actual/60:.1f} hours)",
                    f"- **Estimation Accuracy**: {accuracy:.1f}%",
                ])

            lines.extend([
                "",
                "## Complexity Distribution",
                ""
            ])

            for complexity in sorted(by_complexity.keys()):
                count = by_complexity[complexity]
                percentage = (count / total_tasks) * 100
                lines.append(f"- **Complexity {complexity}/5**: {count} tasks ({percentage:.1f}%)")

            lines.extend([
                "",
                "## Recommendations",
                ""
            ])

            if avg_actual and avg_estimated > 0:
                ratio = avg_actual / avg_estimated
                if ratio > 1.2:
                    lines.append(f"⚠️ Tasks consistently take longer than estimated (avg {ratio:.2f}x). Consider:")
                    lines.append(f"- Applying a {ratio:.2f}x multiplier for similar tasks")
                    lines.append("- Breaking down tasks into smaller chunks")
                    lines.append("- Identifying common blockers")
                elif ratio < 0.8:
                    lines.append(f"✅ Estimates are conservative (avg {ratio:.2f}x actual). Consider:")
                    lines.append("- Reducing buffers slightly")
                    lines.append("- Taking on more complex variations")
                else:
                    lines.append("✅ Estimates are well-calibrated for this task type!")

            lines.extend([
                "",
                "## Sample Tasks",
                ""
            ])

            # Show up to 5 sample tasks
            for i, (task_id, task_data) in enumerate(tasks[:5], 1):
                lines.append(f"### {i}. {task_data.get('task_content', 'Unknown')}")
                lines.append(f"- **Estimated**: {task_data['hydrated']['total_estimate_minutes']} min")
                if task_data.get('actual_minutes'):
                    lines.append(f"- **Actual**: {task_data['actual_minutes']} min")
                lines.append(f"- **Complexity**: {task_data['hydrated']['complexity']}/5")
                lines.append("")

            # Write file
            content = "\n".join(lines)
            with open(filepath, 'w') as f:
                f.write(content)

            logger.info(f"Generated pattern file: {filepath}")

        except Exception as e:
            logger.error(f"Failed to generate pattern file for {label}: {e}")

    def _generate_overall_patterns(self, hydrations: Dict[str, Any]):
        """Generate overall calibration report."""
        try:
            filepath = self.patterns_dir / "calibration_report.md"

            stats = self.stats_tracker.get_stats()

            lines = [
                "# Overall Task Calibration Report",
                "",
                f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                f"**Total Tasks Hydrated**: {stats['total_hydrated']}",
                f"**Total Tasks Completed**: {stats['total_completed']}",
                "",
                "## Statistics",
                ""
            ]

            if stats['avg_accuracy'] is not None:
                lines.append(f"- **Average Accuracy**: {stats['avg_accuracy']:.1f}%")

            if stats['calibration_factor'] is not None:
                lines.append(f"- **Calibration Factor**: {stats['calibration_factor']:.2f}x")

            lines.extend([
                "",
                "## Patterns by Complexity",
                ""
            ])

            for pattern in stats['patterns']:
                lines.append(f"### {pattern['type']}")
                lines.append(f"- **Count**: {pattern['count']} tasks")
                lines.append(f"- **Avg Estimated**: {pattern['avg_estimated_minutes']} min")
                if pattern['avg_actual_minutes']:
                    lines.append(f"- **Avg Actual**: {pattern['avg_actual_minutes']} min")
                lines.append("")

            lines.extend([
                "## Insights",
                ""
            ])

            if stats['avg_accuracy']:
                if stats['avg_accuracy'] >= 80:
                    lines.append("✅ **Excellent calibration** - Your estimates are highly accurate!")
                elif stats['avg_accuracy'] >= 60:
                    lines.append("⚠️ **Good calibration** - Room for improvement in accuracy")
                else:
                    lines.append("❌ **Poor calibration** - Significant estimation errors")

            if stats['calibration_factor']:
                if stats['calibration_factor'] > 1.5:
                    lines.append(f"- Tasks take {stats['calibration_factor']:.2f}x longer than estimated")
                    lines.append("- Consider applying a global multiplier to estimates")
                elif stats['calibration_factor'] < 0.7:
                    lines.append(f"- Tasks take {stats['calibration_factor']:.2f}x less time than estimated")
                    lines.append("- Your estimates may be too conservative")
                else:
                    lines.append("- Overall timing is well-calibrated")

            # Write file
            content = "\n".join(lines)
            with open(filepath, 'w') as f:
                f.write(content)

            logger.info(f"Generated calibration report: {filepath}")

        except Exception as e:
            logger.error(f"Failed to generate calibration report: {e}")
