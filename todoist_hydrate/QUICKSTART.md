# Quick Start Guide

Get up and running with the Todoist Task Hydration System in 5 minutes.

## Step 1: Install Dependencies

```bash
cd todoist_hydrate
pip install -r requirements.txt
```

## Step 2: Set Up API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your favorite editor
nano .env  # or vim, code, etc.
```

Add your API keys:
```
TODOIST_API_TOKEN=your_actual_todoist_token
ANTHROPIC_API_KEY=your_actual_anthropic_key
```

**Where to get API keys:**
- **Todoist**: https://todoist.com/prefs/integrations (scroll to "API token")
- **Anthropic**: https://console.anthropic.com/ (click "Get API keys")

## Step 3: Verify Setup

```bash
python verify_setup.py
```

If all checks pass ✅, you're ready to go!

## Step 4: Try It Out

### Option A: Hydrate a Single Task

1. Get a task ID from Todoist (open a task, look at the URL: `todoist.com/app/task/1234567890`)
2. Run hydration:

```bash
python cli.py hydrate 1234567890
```

### Option B: Batch Process with Labels

1. In Todoist, add a label (e.g., `@analyze`) to tasks you want to hydrate
2. Run batch hydration:

```bash
python cli.py batch --label @analyze
```

## What Happens Next?

The system will:
1. ✅ Fetch your task from Todoist
2. 🧠 Send it to Claude for analysis
3. 📋 Generate a detailed action plan
4. 💾 Update the task in Todoist with the plan
5. 📄 Save a JSON file with the hydration data

## Example Output

```
🔍 Fetching task 1234567890...
📝 Task: Implement user authentication
   Labels: feature, backend

🧠 Hydrating with Claude...

✅ Hydration complete!

📋 Refined Title: Implement JWT-based user authentication system with email/password login
⏱️  Total Estimate: 180 minutes (3.0 hours)
🎯 Complexity: 4/5
📊 Confidence: medium

📍 Action Items (5):
  1. Set up authentication database schema (~30 min)
  2. Implement password hashing and validation (~40 min)
  3. Create JWT token generation and validation (~45 min)
  4. Build login/logout API endpoints (~40 min)
  5. Write tests for authentication flow (~25 min)

✓ Success Criteria:
  - Users can register with email/password
  - Users can log in and receive valid JWT token
  - Protected routes verify token correctly
  - All tests pass

💾 Updating Todoist task...
✅ Task updated in Todoist
```

## Common Commands

```bash
# Get help
python cli.py --help

# Hydrate without updating Todoist
python cli.py hydrate 1234567890 --no-update

# Export a completed task for analysis
python cli.py export 1234567890

# View calibration statistics
python cli.py analyze
```

## Troubleshooting

### "No API token provided"
- Make sure `.env` file exists
- Check that API keys don't have quotes or extra spaces
- Try exporting manually: `export TODOIST_API_TOKEN="your_token"`

### Rate limiting
- The system has automatic retry logic
- If you hit limits, wait a few minutes
- Consider upgrading your API tier for higher limits

### Task not found
- Double-check the task ID
- Make sure the task hasn't been deleted
- Verify your Todoist API token is correct

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out the API reference for programmatic usage
- Set up a regular workflow for hydrating and exporting tasks
- Review your estimation calibration monthly

## Tips

1. **Start small**: Hydrate 2-3 tasks to see how it works
2. **Use labels**: Create `@analyze` for tasks to hydrate, `@review` for tasks to export
3. **Track time**: Note actual time spent to improve calibration
4. **Review exports**: Use NotebookLM or similar tools to analyze patterns
5. **Iterate**: Refine your task descriptions based on what works

## Support

Having issues? Check:
1. `todoist_hydrate.log` for detailed error messages
2. The full [README.md](README.md) for troubleshooting
3. Your API keys are valid and have proper permissions

Happy task hydrating! 🚀
