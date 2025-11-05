# Todoist Task Hydration System

A production-ready Python system for transforming vague Todoist tasks into detailed, actionable plans using Claude AI. Perfect for improving task clarity, estimation accuracy, and productivity tracking.

## Features

- **🧠 AI-Powered Task Hydration**: Uses Claude to transform vague tasks into detailed action plans
- **⏱️ Smart Time Estimation**: Applies reference class forecasting and adds realistic buffers
- **📊 Calibration Tracking**: Export completed tasks and analyze estimation accuracy
- **🔄 Batch Processing**: Hydrate multiple tasks at once using labels
- **💾 NotebookLM Export**: Format completed tasks for pattern analysis and learning
- **🔁 Automatic Retry Logic**: Handles API failures with exponential backoff
- **📝 Comprehensive Logging**: Track all operations for debugging and analysis
- **🌐 Webhook Server**: REST API for Fellou integration with dashboard and auto-Todoist updates
- **📈 Pattern Analysis**: Auto-generates insights when 10+ similar tasks are completed

## What Gets Generated

For each vague task, the system produces:

- **Refined Title**: Clear, action-oriented description
- **Action Items**: Sequential steps (each ≤90 minutes)
- **Time Estimates**: Realistic estimates with 25% buffer
- **Complexity Rating**: 1-5 scale (1=routine, 5=novel)
- **Dependencies**: Prerequisites that must be completed first
- **Success Criteria**: Measurable outcomes to verify completion
- **Risk Analysis**: Likely blockers with mitigation strategies

## Installation

### Prerequisites

- Python 3.8 or higher
- Todoist account with API access
- Anthropic API key (Claude)

### Setup

1. **Clone or download this directory**

```bash
cd todoist_hydrate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys
# TODOIST_API_TOKEN: Get from https://todoist.com/prefs/integrations
# ANTHROPIC_API_KEY: Get from https://console.anthropic.com/
```

4. **Make CLI executable (optional)**

```bash
chmod +x cli.py
```

## Usage

### Command Overview

```bash
python cli.py hydrate <task_id>          # Hydrate a specific task
python cli.py batch --label @analyze     # Hydrate all tasks with label
python cli.py export <task_id>           # Export to NotebookLM format
python cli.py analyze                    # Show calibration statistics
```

### 1. Hydrate a Single Task

Transform a vague task into a detailed plan:

```bash
python cli.py hydrate 7234567890
```

**Output:**
```
🔍 Fetching task 7234567890...
📝 Task: Fix the authentication bug
   Labels: bug, urgent
   Due: 2025-11-10

🧠 Hydrating with Claude...

✅ Hydration complete!

📋 Refined Title: Debug and fix authentication token expiration issue in user login flow
⏱️  Total Estimate: 120 minutes (2.0 hours)
🎯 Complexity: 3/5
📊 Confidence: medium

📍 Action Items (4):
  1. Reproduce authentication bug in development environment (~20 min)
  2. Review authentication token generation and validation code (~30 min)
  3. Identify root cause and implement fix (~45 min)
  4. Test fix and verify across different user scenarios (~25 min)

✓ Success Criteria:
  - Users can log in successfully without token expiration errors
  - Existing sessions remain valid for expected duration
  - All authentication tests pass

⚠️  Risks:
  - Token generation logic may be in multiple places
    → Search codebase for all token-related code before starting

💾 Updating Todoist task...
✅ Task updated in Todoist
💾 Saved hydration to: hydrated_7234567890.json
```

The task description in Todoist will be updated with the full hydration details.

**Options:**

```bash
# Hydrate without updating Todoist (just generate the plan)
python cli.py hydrate 7234567890 --no-update
```

### 2. Batch Hydrate Multiple Tasks

Hydrate all tasks with a specific label:

```bash
python cli.py batch --label @analyze
```

This will:
1. Fetch all tasks with the `@analyze` label
2. Hydrate each task sequentially
3. Update each task in Todoist with hydration details
4. Add a `hydrated` label to processed tasks
5. Save JSON files for each hydration

**Options:**

```bash
# Batch process without updating Todoist
python cli.py batch --label @analyze --no-update
```

### 3. Export Completed Task for Analysis

Export a completed task to NotebookLM format:

```bash
python cli.py export 7234567890
```

You'll be prompted to enter actual time spent:

```
⏱️  Enter actual time spent (in minutes), or press Enter to skip:
> 145

📤 Generating NotebookLM export...
✅ Exported to: ./exports/2025-11-05_7234567890_Bug_Fix.md
```

The export includes:
- Original vs. refined task
- Estimated vs. actual time
- Estimation accuracy percentage
- Action items completed
- Learnings section (populated from comments)
- Pattern classification for analysis

### 4. Analyze Calibration

Review your estimation accuracy:

```bash
python cli.py analyze
```

This shows:
- Recent export files
- Overall estimation accuracy
- Breakdown by complexity level
- Recommendations for improvement

## Webhook Server (Fellou Integration)

The system includes a Flask-based webhook server for automated task hydration via Fellou or other automation tools.

### Start the Server

```bash
# Quick start
./start_server.sh

# Or manually
python server.py
```

Server starts on `http://localhost:5000` with:
- 📊 **Dashboard**: Real-time stats and quick hydrate form
- 🔌 **REST API**: Three endpoints for automation
- ⚡ **Auto-update**: Tasks are automatically updated in Todoist
- 📈 **Pattern analysis**: Auto-generates insights from completed tasks

### API Endpoints

**POST /hydrate** - Hydrate a task
```bash
curl -X POST http://localhost:5000/hydrate \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "123",
    "task_content": "Fix bug",
    "labels": ["bug"]
  }'
```

**POST /log-completion** - Log task completion
```bash
curl -X POST http://localhost:5000/log-completion \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "123",
    "actual_minutes": 145,
    "outcome": "completed"
  }'
```

**GET /stats** - Get calibration statistics
```bash
curl http://localhost:5000/stats
```

### Features

- ✅ **Automatic Todoist updates**: Description, labels, comments
- ⚡ **Background processing**: Non-blocking operations
- 🛡️ **Rate limiting**: 10 requests/minute protection
- 📊 **Live dashboard**: View stats and recent hydrations
- 📁 **Pattern files**: Auto-generated when 10+ similar tasks completed
- 🔄 **CORS enabled**: Works with browser-based automation

**Full documentation**: See [WEBHOOK_DEPLOYMENT.md](WEBHOOK_DEPLOYMENT.md)

## File Structure

```
todoist_hydrate/
├── __init__.py              # Package initialization
├── todoist_api.py           # Todoist API wrapper with retry logic
├── hydrator.py              # Claude-powered task hydration
├── notebooklm_export.py     # Export formatting for analysis
├── stats_tracker.py         # Statistics and pattern analysis
├── cli.py                   # Command-line interface
├── server.py                # Flask webhook server
├── start_server.sh          # Quick server startup script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── README.md                # This file
├── QUICKSTART.md            # 5-minute setup guide
├── WEBHOOK_DEPLOYMENT.md    # Webhook server documentation
├── verify_setup.py          # Setup verification tool
├── todoist_hydrate.log      # Application log file
├── server.log               # Server request log
├── stats_data.json          # Persistent stats storage
├── notebooklm_sources/      # NotebookLM exports and patterns
│   ├── completed_tasks/     # Task completion records
│   └── patterns/            # Auto-generated pattern files
└── hydrated_*.json          # Cached hydration data
```

## API Reference

### TodoistAPI

```python
from todoist_api import TodoistAPI

api = TodoistAPI()  # Reads TODOIST_API_TOKEN from env

# Get all tasks
tasks = api.get_all_tasks()

# Get tasks with label
tasks = api.get_all_tasks(label="@analyze")

# Get specific task
task = api.get_task("task_id")

# Create task
new_task = api.create_task(
    content="Task title",
    description="Task details",
    labels=["important"],
    priority=3
)

# Update task
updated = api.update_task(
    task_id="task_id",
    description="New description",
    labels=["updated"]
)

# Add comment
api.add_comment("task_id", "This is a comment")

# Close task
api.close_task("task_id")
```

### TaskHydrator

```python
from hydrator import TaskHydrator

hydrator = TaskHydrator()  # Reads ANTHROPIC_API_KEY from env

# Hydrate a task
hydrated = hydrator.hydrate_task(
    task_id="123",
    task_content="Fix the bug",
    labels=["bug"],
    due_date="2025-11-10"
)

# Access hydrated data
print(hydrated.refined_title)
print(hydrated.total_estimate_minutes)
print(hydrated.complexity)

for action in hydrated.action_items:
    print(f"{action.sequence}. {action.item} ({action.estimated_minutes} min)")

# Format for Todoist
markdown = hydrator.format_for_todoist(hydrated)
```

### NotebookLMExporter

```python
from notebooklm_export import NotebookLMExporter

exporter = NotebookLMExporter(export_dir="./exports")

# Export a task
filepath = exporter.export_task(
    task_id="123",
    original_task="Fix the bug",
    hydrated=hydrated_task,
    labels=["bug"],
    actual_minutes=145,
    learnings={
        "what_went_well": "Clear reproduction steps",
        "what_took_longer": "Finding all token generation code",
        "blockers_encountered": "Outdated documentation"
    }
)

# Generate calibration report
records = [
    {"estimated_minutes": 120, "actual_minutes": 145, "complexity": 3},
    {"estimated_minutes": 60, "actual_minutes": 55, "complexity": 2},
]
report_path = exporter.export_calibration_stats(records)
```

## Best Practices

### Estimation Principles

The hydrator applies these principles automatically:

1. **Reference Class Forecasting**: Multiplies estimates by 1.6x for novel tasks
2. **Breaking Down Work**: Splits tasks into ≤90-minute chunks
3. **Buffer Addition**: Adds 25% buffer to base estimates
4. **Context Switching**: Accounts for interruptions (15 min overhead)

### Labeling Strategy

Suggested Todoist labels:

- `@analyze` - Tasks to be hydrated
- `hydrated` - Tasks that have been processed (added automatically)
- `@review` - Completed tasks to export for analysis

### Workflow

1. **Create vague tasks** in Todoist as they come to mind
2. **Add @analyze label** to tasks you want to hydrate
3. **Run batch hydration** daily or weekly:
   ```bash
   python cli.py batch --label @analyze
   ```
4. **Work on hydrated tasks** using the detailed action items
5. **Export completed tasks** for learning:
   ```bash
   python cli.py export <task_id>
   ```
6. **Review calibration** monthly to improve estimates:
   ```bash
   python cli.py analyze
   ```

## Troubleshooting

### "No API token provided" Error

Make sure your `.env` file exists and contains valid keys:

```bash
cat .env
# Should show:
# TODOIST_API_TOKEN=your_token_here
# ANTHROPIC_API_KEY=your_key_here
```

Load environment variables:

```bash
# Option 1: Use python-dotenv (automatic in code)
# Option 2: Export manually
export TODOIST_API_TOKEN="your_token"
export ANTHROPIC_API_KEY="your_key"
```

### Rate Limiting

The system automatically handles rate limits with:
- Exponential backoff retry (3 attempts)
- Respect for `Retry-After` headers

If you hit limits frequently:
- Reduce batch size
- Add delays between requests
- Check your API tier limits

### JSON Parsing Errors

If Claude returns invalid JSON:
1. Check your API key is valid
2. Review `todoist_hydrate.log` for details
3. The system will retry automatically
4. Report persistent issues with example tasks

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests (when test suite is added)
pytest tests/
```

### Extending the System

**Add Custom Task Classifications:**

Edit `notebooklm_export.py`:

```python
def _classify_task_type(self, hydrated, original_task):
    # Add your custom classification logic
    if 'ml' in original_task.lower():
        return "Machine Learning"
    # ...
```

**Customize Hydration Prompts:**

Edit `hydrator.py`:

```python
def _build_prompt(self, task_content, labels, due_date):
    # Modify prompt template
    # Add domain-specific instructions
    # Adjust estimation principles
```

## License

This project is provided as-is for personal and commercial use.

## Support

For issues, questions, or contributions:
1. Check `todoist_hydrate.log` for error details
2. Review this README
3. Open an issue with:
   - Error message
   - Command that failed
   - Relevant log excerpts

## Changelog

### v1.0.0 (2025-11-05)
- Initial release
- Core hydration functionality
- Batch processing
- NotebookLM export
- Calibration tracking
- CLI interface

## Acknowledgments

- **Todoist** for task management API
- **Anthropic** for Claude AI
- Inspired by principles from "The Checklist Manifesto" and "Thinking, Fast and Slow"
