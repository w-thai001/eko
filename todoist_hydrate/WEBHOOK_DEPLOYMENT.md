# Webhook Server Deployment Guide

Complete guide to deploying and using the Todoist Task Hydration webhook server for Fellou integration.

## Overview

The webhook server provides a REST API that Fellou (or any client) can call to:
- Hydrate Todoist tasks with AI-powered analysis
- Log task completions and track estimation accuracy
- View calibration statistics and patterns

## Quick Start

### 1. Install Dependencies

```bash
cd todoist_hydrate
pip install -r requirements.txt
```

This installs:
- Core dependencies (anthropic, requests, pydantic)
- Web server (Flask, flask-cors)
- All required libraries

### 2. Configure Environment

Make sure your `.env` file has both API keys:

```bash
# .env file
TODOIST_API_TOKEN=your_todoist_token
ANTHROPIC_API_KEY=your_anthropic_key
```

### 3. Start the Server

```bash
python server.py
```

You should see:

```
INFO - Starting Todoist Task Hydration Server on port 5000
INFO - Dashboard: http://localhost:5000
INFO - Rate limit: 10 requests per minute
 * Running on http://0.0.0.0:5000
```

### 4. Test the Server

Open your browser to: **http://localhost:5000**

You should see the dashboard with:
- Current statistics
- Quick hydrate form
- Recent hydrations
- API endpoint documentation

## API Endpoints

### POST /hydrate

Hydrate a Todoist task with AI analysis.

**Request:**
```json
{
  "task_id": "7234567890",
  "task_content": "Fix the authentication bug",
  "labels": ["bug", "urgent"],
  "due_date": "2025-11-10"
}
```

**Response:**
```json
{
  "status": "success",
  "hydrated_task": {
    "refined_title": "Debug and fix authentication token expiration issue",
    "formatted_description": "# Debug and fix...\n\n## Action Items...",
    "suggested_labels": ["bug", "urgent", "processed"],
    "estimated_minutes": 120,
    "complexity": 3,
    "confidence": "medium",
    "action_items": [
      {
        "item": "Reproduce authentication bug in development",
        "estimated_minutes": 20,
        "sequence": 1
      }
    ]
  },
  "todoist_updated": true
}
```

**What Happens:**
1. Task is sent to Claude for hydration
2. Structured action plan is generated
3. If `task_id` is provided:
   - Task description is updated in Todoist
   - Label `@analyze` is removed
   - Label `processed` is added
   - Comment is added with estimated time
4. Hydration is tracked in stats

**cURL Example:**
```bash
curl -X POST http://localhost:5000/hydrate \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "7234567890",
    "task_content": "Implement user authentication",
    "labels": ["feature", "backend"]
  }'
```

**JavaScript Example (for Fellou):**
```javascript
const response = await fetch('http://localhost:5000/hydrate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    task_id: taskId,
    task_content: taskContent,
    labels: taskLabels
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('Task hydrated:', result.hydrated_task.refined_title);
  console.log('Estimated:', result.hydrated_task.estimated_minutes, 'minutes');
}
```

### POST /log-completion

Log task completion and generate NotebookLM export.

**Request:**
```json
{
  "task_id": "7234567890",
  "actual_minutes": 145,
  "outcome": "completed",
  "notes": "Token validation was more complex than expected"
}
```

**Response:**
```json
{
  "status": "success",
  "export_path": "./notebooklm_sources/completed_tasks/2025-11-05_7234567890_*.md",
  "calibration": {
    "avg_accuracy": 78.5,
    "calibration_factor": 1.21
  }
}
```

**What Happens:**
1. Completion is recorded in stats
2. NotebookLM export is generated (markdown file)
3. Pattern analysis is triggered (runs in background)
4. If 10+ similar tasks exist, pattern files are updated
5. Calibration statistics are recalculated

**cURL Example:**
```bash
curl -X POST http://localhost:5000/log-completion \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "7234567890",
    "actual_minutes": 145,
    "outcome": "completed",
    "notes": "Took longer due to complex validation logic"
  }'
```

### GET /stats

Get current calibration statistics.

**Request:**
```bash
curl http://localhost:5000/stats
```

**Response:**
```json
{
  "total_hydrated": 25,
  "total_completed": 18,
  "avg_accuracy": 78.5,
  "calibration_factor": 1.21,
  "patterns": [
    {
      "type": "Complexity 3/5",
      "count": 10,
      "avg_estimated_minutes": 120.5,
      "avg_actual_minutes": 145.2
    }
  ],
  "recent_hydrations": [
    {
      "task_id": "7234567890",
      "task_content": "Fix authentication bug",
      "refined_title": "Debug and fix authentication token expiration",
      "estimated_minutes": 120,
      "complexity": 3,
      "timestamp": "2025-11-05T15:30:00"
    }
  ]
}
```

## Directory Structure

When you start the server, these directories are auto-created:

```
todoist_hydrate/
├── server.py                    # Webhook server
├── stats_tracker.py             # Stats and pattern analysis
├── server.log                   # Server request log
├── stats_data.json              # Persistent stats storage
├── notebooklm_sources/
│   ├── completed_tasks/         # Task completion exports
│   │   ├── 2025-11-05_task_123_Bug_Fix.md
│   │   └── 2025-11-05_task_456_Feature_Development.md
│   └── patterns/                # Auto-generated pattern files
│       ├── bug_patterns.md      # Generated when 10+ bug tasks completed
│       ├── feature_patterns.md  # Generated when 10+ feature tasks completed
│       └── calibration_report.md # Overall calibration stats
```

## Configuration

### Environment Variables

```bash
# Required
TODOIST_API_TOKEN=your_token
ANTHROPIC_API_KEY=your_key

# Optional
PORT=5000                # Server port (default: 5000)
DEBUG=false              # Enable debug mode (default: false)
```

### Rate Limiting

Default: **10 requests per minute** per IP address

This prevents runaway requests and protects against accidental loops.

To modify, edit `server.py`:
```python
RATE_LIMIT = 10      # requests per minute
RATE_WINDOW = 60     # seconds
```

## Fellou Integration

### Setup in Fellou

1. **Start the webhook server** on your local machine
2. **Configure Fellou** to monitor Todoist for tasks with `@analyze` label
3. **Extract task data** (ID, content, labels, due date)
4. **Call webhook** at `http://localhost:5000/hydrate`
5. **Handle response** (display results, update UI, etc.)

### Example Fellou Workflow

```javascript
// 1. Monitor Todoist for new tasks with @analyze label
const tasks = await getTodoistTasksWithLabel('@analyze');

// 2. For each task, extract data
for (const task of tasks) {
  const taskData = {
    task_id: task.id,
    task_content: task.content,
    labels: task.labels,
    due_date: task.due?.date
  };

  // 3. Call hydration webhook
  const response = await fetch('http://localhost:5000/hydrate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(taskData)
  });

  const result = await response.json();

  // 4. Handle result
  if (result.status === 'success') {
    console.log('✅ Hydrated:', result.hydrated_task.refined_title);
    console.log('📊 Estimated:', result.hydrated_task.estimated_minutes, 'min');

    // Task is automatically updated in Todoist
    // (description, labels, comment added)
  } else {
    console.error('❌ Error:', result.error);
  }
}
```

### Logging Completions

When a task is completed in Todoist:

```javascript
// Track actual time spent
const actualMinutes = calculateTimeSpent(task);

// Log completion
await fetch('http://localhost:5000/log-completion', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    task_id: task.id,
    actual_minutes: actualMinutes,
    outcome: 'completed',
    notes: 'Optional notes about what took longer'
  })
});
```

## Running in Production

### Option 1: Local Development

Simple approach for testing and development:

```bash
python server.py
```

- Runs on localhost:5000
- Auto-restarts not enabled
- Suitable for Fellou integration on same machine

### Option 2: Background Process

Run server in background with nohup:

```bash
nohup python server.py > server_output.log 2>&1 &
```

To stop:
```bash
pkill -f "python server.py"
```

### Option 3: Systemd Service (Linux)

Create `/etc/systemd/system/todoist-hydrate.service`:

```ini
[Unit]
Description=Todoist Task Hydration Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/todoist_hydrate
Environment="TODOIST_API_TOKEN=your_token"
Environment="ANTHROPIC_API_KEY=your_key"
ExecStart=/usr/bin/python3 /path/to/todoist_hydrate/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable todoist-hydrate
sudo systemctl start todoist-hydrate
sudo systemctl status todoist-hydrate
```

View logs:
```bash
sudo journalctl -u todoist-hydrate -f
```

### Option 4: Docker (Advanced)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "server.py"]
```

Build and run:
```bash
docker build -t todoist-hydrate .
docker run -d -p 5000:5000 \
  -e TODOIST_API_TOKEN=your_token \
  -e ANTHROPIC_API_KEY=your_key \
  --name todoist-hydrate \
  todoist-hydrate
```

## Monitoring

### Check Server Status

```bash
curl http://localhost:5000/stats
```

If server is running, you'll get JSON response with statistics.

### View Logs

```bash
# Server request log
tail -f server.log

# Hydration system log
tail -f todoist_hydrate.log
```

### Dashboard

Open browser to `http://localhost:5000` to see:
- Live statistics
- Recent hydrations
- Quick hydrate form
- Calibration metrics

## Troubleshooting

### Server Won't Start

**Error:** `Address already in use`

Solution:
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port
PORT=5001 python server.py
```

**Error:** `No module named 'flask'`

Solution:
```bash
pip install -r requirements.txt
```

### API Errors

**429 Rate Limit Exceeded**

You're making too many requests. Wait 60 seconds or increase rate limit in `server.py`.

**404 No hydration data found**

The task hasn't been hydrated yet. Call `/hydrate` first before `/log-completion`.

**500 Internal Server Error**

Check logs:
```bash
tail -50 server.log
```

Common causes:
- Invalid API keys
- Todoist API is down
- Claude API rate limits hit
- Network issues

### CORS Issues (from Fellou)

If you get CORS errors from browser-based Fellou:

The server already has CORS enabled via `flask-cors`. If still having issues:

1. Check browser console for specific error
2. Verify request includes proper headers
3. Try using fetch with mode: 'cors'

```javascript
fetch('http://localhost:5000/hydrate', {
  method: 'POST',
  mode: 'cors',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(data)
})
```

## Best Practices

### 1. Batch Processing

Don't hydrate tasks one-by-one in tight loops. Add delays:

```javascript
for (const task of tasks) {
  await hydrateTask(task);
  await sleep(1000);  // 1 second delay
}
```

### 2. Error Handling

Always handle errors gracefully:

```javascript
try {
  const response = await fetch('http://localhost:5000/hydrate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(taskData)
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const result = await response.json();

  if (result.status === 'error') {
    console.error('Hydration failed:', result.error);
    return;
  }

  // Process success
} catch (error) {
  console.error('Request failed:', error);
  // Retry or notify user
}
```

### 3. Track Completions

Log all task completions to improve calibration:

```javascript
// When marking task as complete in Todoist
const startTime = getTaskStartTime(taskId);
const endTime = Date.now();
const actualMinutes = Math.round((endTime - startTime) / 60000);

await fetch('http://localhost:5000/log-completion', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    task_id: taskId,
    actual_minutes: actualMinutes,
    outcome: 'completed'
  })
});
```

### 4. Review Patterns

Regularly check generated pattern files:

```bash
ls -lh notebooklm_sources/patterns/
cat notebooklm_sources/patterns/calibration_report.md
```

Use these insights to:
- Adjust estimation strategies
- Identify task types that take longer
- Improve task breakdown
- Set realistic expectations

## Security Considerations

### Local Use Only

This server is designed for **local use** with Fellou integration.

**Do NOT expose to the internet without:**
1. Adding authentication (API keys, OAuth)
2. Using HTTPS (SSL certificates)
3. Implementing proper CORS restrictions
4. Adding input validation and sanitization
5. Setting up firewall rules

### API Key Protection

Your `.env` file contains sensitive API keys:

```bash
# Set proper permissions
chmod 600 .env

# Never commit to git
echo ".env" >> .gitignore
```

## Support

### Check Logs

```bash
# Server logs
tail -f server.log

# Application logs
tail -f todoist_hydrate.log

# Stats data
cat stats_data.json | jq .
```

### Common Issues

1. **No tasks being hydrated**: Check that tasks have `@analyze` label
2. **Todoist not updating**: Verify `task_id` is correct and API token is valid
3. **Pattern files not generating**: Need 10+ completed tasks with same label
4. **Slow responses**: Claude API can take 5-10 seconds per request

### Getting Help

1. Review logs for error messages
2. Check API key validity
3. Test endpoints with cURL
4. Verify network connectivity
5. Check rate limits

## Performance

### Expected Response Times

- `/hydrate`: 5-15 seconds (depends on Claude API)
- `/log-completion`: < 1 second (background processing)
- `/stats`: < 100ms

### Optimization Tips

1. **Cache hydrations**: Don't re-hydrate same task multiple times
2. **Batch operations**: Group similar tasks when possible
3. **Monitor rate limits**: Stay within Todoist and Anthropic limits
4. **Use async processing**: Server uses threading for slow operations

## What's Next?

After deploying the webhook server:

1. ✅ Start server with `python server.py`
2. ✅ Configure Fellou to monitor Todoist
3. ✅ Add `@analyze` label to tasks
4. ✅ Let Fellou call `/hydrate` endpoint
5. ✅ Work on hydrated tasks
6. ✅ Log completions with actual time
7. ✅ Review calibration monthly
8. ✅ Use pattern files for learning

Happy automating! 🚀
