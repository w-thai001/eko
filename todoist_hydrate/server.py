#!/usr/bin/env python3
"""
Flask webhook server for Todoist task hydration.
Integrates with Fellou browser automation for seamless task processing.
"""
import os
import json
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from todoist_api import TodoistAPI, TodoistAPIError
from hydrator import TaskHydrator, TaskHydrationError, HydratedTask
from notebooklm_export import NotebookLMExporter
from stats_tracker import StatsTracker, PatternAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for Fellou integration

# Initialize services
try:
    todoist = TodoistAPI()
    hydrator = TaskHydrator()
    exporter = NotebookLMExporter(export_dir="./notebooklm_sources/completed_tasks")
    stats_tracker = StatsTracker()
    pattern_analyzer = PatternAnalyzer()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise

# Rate limiting setup
request_counts = defaultdict(list)
RATE_LIMIT = 10  # requests per minute
RATE_WINDOW = 60  # seconds


def check_rate_limit(client_ip: str) -> bool:
    """
    Check if client has exceeded rate limit.

    Args:
        client_ip: Client IP address

    Returns:
        True if within limit, False if exceeded
    """
    now = datetime.now()
    cutoff = now - timedelta(seconds=RATE_WINDOW)

    # Clean old requests
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if req_time > cutoff
    ]

    # Check limit
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        return False

    # Add current request
    request_counts[client_ip].append(now)
    return True


@app.before_request
def rate_limit_check():
    """Rate limit all requests."""
    client_ip = request.remote_addr

    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        return jsonify({
            "status": "error",
            "error": f"Rate limit exceeded. Max {RATE_LIMIT} requests per minute."
        }), 429


@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler."""
    logger.error(f"Unhandled error: {error}", exc_info=True)

    if isinstance(error, HTTPException):
        return jsonify({
            "status": "error",
            "error": error.description
        }), error.code

    return jsonify({
        "status": "error",
        "error": "Internal server error"
    }), 500


@app.route('/')
def dashboard():
    """Simple dashboard showing recent activity and stats."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Todoist Task Hydration Server</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .header h1 {
                margin: 0 0 10px 0;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .stat-card h3 {
                margin: 0 0 10px 0;
                color: #666;
                font-size: 14px;
                text-transform: uppercase;
            }
            .stat-card .value {
                font-size: 32px;
                font-weight: bold;
                color: #333;
            }
            .stat-card .subvalue {
                color: #999;
                font-size: 14px;
                margin-top: 5px;
            }
            .section {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .section h2 {
                margin-top: 0;
                color: #333;
            }
            .hydrate-form {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .hydrate-form input, .hydrate-form textarea {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: inherit;
            }
            .hydrate-form button {
                padding: 12px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: bold;
            }
            .hydrate-form button:hover {
                background: #5568d3;
            }
            .recent-item {
                padding: 15px;
                border-bottom: 1px solid #eee;
            }
            .recent-item:last-child {
                border-bottom: none;
            }
            .recent-item h4 {
                margin: 0 0 5px 0;
                color: #333;
            }
            .recent-item .meta {
                color: #999;
                font-size: 14px;
            }
            .badge {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 12px;
                margin-left: 10px;
            }
            .badge-success {
                background: #d4edda;
                color: #155724;
            }
            .badge-info {
                background: #d1ecf1;
                color: #0c5460;
            }
            #result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 4px;
                display: none;
            }
            #result.success {
                background: #d4edda;
                color: #155724;
                display: block;
            }
            #result.error {
                background: #f8d7da;
                color: #721c24;
                display: block;
            }
            .loading {
                opacity: 0.6;
                pointer-events: none;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧠 Todoist Task Hydration Server</h1>
            <p>AI-powered task transformation for Fellou integration</p>
        </div>

        <div class="stats-grid" id="stats-grid">
            <div class="stat-card">
                <h3>Total Hydrated</h3>
                <div class="value" id="total-hydrated">-</div>
            </div>
            <div class="stat-card">
                <h3>Total Completed</h3>
                <div class="value" id="total-completed">-</div>
            </div>
            <div class="stat-card">
                <h3>Avg Accuracy</h3>
                <div class="value" id="avg-accuracy">-</div>
                <div class="subvalue">estimation accuracy</div>
            </div>
            <div class="stat-card">
                <h3>Calibration Factor</h3>
                <div class="value" id="calibration-factor">-</div>
                <div class="subvalue">actual vs estimated</div>
            </div>
        </div>

        <div class="section">
            <h2>Quick Hydrate</h2>
            <form class="hydrate-form" id="hydrate-form">
                <input type="text" id="task-id" placeholder="Task ID (optional)" />
                <textarea id="task-content" rows="3" placeholder="Task description" required></textarea>
                <input type="text" id="labels" placeholder="Labels (comma-separated, e.g., work,urgent)" />
                <input type="date" id="due-date" placeholder="Due date" />
                <button type="submit">Hydrate Task</button>
            </form>
            <div id="result"></div>
        </div>

        <div class="section">
            <h2>Recent Hydrations</h2>
            <div id="recent-hydrations">Loading...</div>
        </div>

        <div class="section">
            <h2>API Endpoints</h2>
            <ul>
                <li><code>POST /hydrate</code> - Hydrate a task</li>
                <li><code>POST /log-completion</code> - Log task completion</li>
                <li><code>GET /stats</code> - Get calibration statistics</li>
            </ul>
            <p>Rate limit: {{ rate_limit }} requests per minute</p>
        </div>

        <script>
            // Load stats
            function loadStats() {
                fetch('/stats')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('total-hydrated').textContent = data.total_hydrated;
                        document.getElementById('total-completed').textContent = data.total_completed;
                        document.getElementById('avg-accuracy').textContent =
                            data.avg_accuracy ? data.avg_accuracy.toFixed(1) + '%' : 'N/A';
                        document.getElementById('calibration-factor').textContent =
                            data.calibration_factor ? data.calibration_factor.toFixed(2) + 'x' : 'N/A';

                        // Load recent hydrations
                        const recentDiv = document.getElementById('recent-hydrations');
                        if (data.recent_hydrations && data.recent_hydrations.length > 0) {
                            recentDiv.innerHTML = data.recent_hydrations.map(h => `
                                <div class="recent-item">
                                    <h4>${h.refined_title || h.task_content}</h4>
                                    <div class="meta">
                                        ${new Date(h.timestamp).toLocaleString()}
                                        <span class="badge badge-info">${h.estimated_minutes} min</span>
                                        ${h.complexity ? '<span class="badge badge-info">Complexity: ' + h.complexity + '/5</span>' : ''}
                                    </div>
                                </div>
                            `).join('');
                        } else {
                            recentDiv.innerHTML = '<p>No recent hydrations</p>';
                        }
                    })
                    .catch(err => console.error('Failed to load stats:', err));
            }

            // Handle form submission
            document.getElementById('hydrate-form').addEventListener('submit', async (e) => {
                e.preventDefault();

                const form = e.target;
                const resultDiv = document.getElementById('result');
                const submitBtn = form.querySelector('button');

                // Show loading state
                submitBtn.textContent = 'Hydrating...';
                submitBtn.disabled = true;
                form.classList.add('loading');
                resultDiv.style.display = 'none';

                try {
                    const labels = document.getElementById('labels').value
                        .split(',')
                        .map(l => l.trim())
                        .filter(l => l);

                    const response = await fetch('/hydrate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            task_id: document.getElementById('task-id').value || undefined,
                            task_content: document.getElementById('task-content').value,
                            labels: labels.length > 0 ? labels : undefined,
                            due_date: document.getElementById('due-date').value || undefined
                        })
                    });

                    const data = await response.json();

                    if (data.status === 'success') {
                        resultDiv.className = 'success';
                        resultDiv.innerHTML = `
                            <strong>✅ Success!</strong><br>
                            <strong>Refined Title:</strong> ${data.hydrated_task.refined_title}<br>
                            <strong>Estimated Time:</strong> ${data.hydrated_task.estimated_minutes} minutes<br>
                            ${data.todoist_updated ? '<em>Task updated in Todoist</em>' : ''}
                        `;

                        // Reload stats
                        loadStats();

                        // Clear form
                        form.reset();
                    } else {
                        resultDiv.className = 'error';
                        resultDiv.innerHTML = `<strong>❌ Error:</strong> ${data.error}`;
                    }
                } catch (err) {
                    resultDiv.className = 'error';
                    resultDiv.innerHTML = `<strong>❌ Error:</strong> ${err.message}`;
                } finally {
                    submitBtn.textContent = 'Hydrate Task';
                    submitBtn.disabled = false;
                    form.classList.remove('loading');
                }
            });

            // Load initial stats
            loadStats();

            // Refresh stats every 30 seconds
            setInterval(loadStats, 30000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html, rate_limit=RATE_LIMIT)


@app.route('/hydrate', methods=['POST'])
def hydrate_endpoint():
    """
    Hydrate a Todoist task.

    Request body:
        {
            "task_id": "optional string",
            "task_content": "string",
            "labels": ["optional", "array"],
            "due_date": "optional ISO string"
        }

    Response:
        {
            "status": "success|error",
            "hydrated_task": {...},
            "todoist_updated": bool,
            "error": "optional error message"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "error": "No JSON data provided"
            }), 400

        task_content = data.get('task_content')
        if not task_content:
            return jsonify({
                "status": "error",
                "error": "task_content is required"
            }), 400

        task_id = data.get('task_id')
        labels = data.get('labels', [])
        due_date = data.get('due_date')

        logger.info(f"Hydrating task: {task_content[:50]}...")

        # Hydrate the task
        try:
            hydrated = hydrator.hydrate_task(
                task_id=task_id or "manual",
                task_content=task_content,
                labels=labels,
                due_date=due_date
            )
        except TaskHydrationError as e:
            logger.error(f"Hydration failed: {e}")
            return jsonify({
                "status": "error",
                "error": f"Hydration failed: {str(e)}"
            }), 500

        # Format response
        response_data = {
            "status": "success",
            "hydrated_task": {
                "refined_title": hydrated.refined_title,
                "formatted_description": hydrator.format_for_todoist(hydrated),
                "suggested_labels": labels + ["processed"],
                "estimated_minutes": hydrated.total_estimate_minutes,
                "complexity": hydrated.complexity,
                "confidence": hydrated.confidence,
                "action_items": [
                    {
                        "item": action.item,
                        "estimated_minutes": action.estimated_minutes,
                        "sequence": action.sequence
                    }
                    for action in hydrated.action_items
                ]
            },
            "todoist_updated": False
        }

        # Update Todoist if task_id provided
        if task_id and task_id != "manual":
            def update_todoist_async():
                """Update Todoist in background thread."""
                try:
                    logger.info(f"Updating Todoist task {task_id}")

                    # Update description
                    todoist.update_task(
                        task_id=task_id,
                        description=hydrator.format_for_todoist(hydrated)
                    )

                    # Update labels
                    new_labels = [l for l in labels if l != "@analyze"]
                    if "processed" not in new_labels:
                        new_labels.append("processed")

                    todoist.update_task(
                        task_id=task_id,
                        labels=new_labels
                    )

                    # Add comment
                    todoist.add_comment(
                        task_id=task_id,
                        content=f"🧠 Hydrated by AI - estimated {hydrated.total_estimate_minutes} minutes"
                    )

                    logger.info(f"Successfully updated Todoist task {task_id}")
                except Exception as e:
                    logger.error(f"Failed to update Todoist: {e}")

            # Start background update
            threading.Thread(target=update_todoist_async, daemon=True).start()
            response_data["todoist_updated"] = True

        # Track hydration
        stats_tracker.track_hydration(
            task_id=task_id or "manual",
            task_content=task_content,
            hydrated=hydrated,
            labels=labels
        )

        logger.info(f"Successfully hydrated task")
        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Hydration endpoint error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/log-completion', methods=['POST'])
def log_completion_endpoint():
    """
    Log task completion and generate NotebookLM export.

    Request body:
        {
            "task_id": "string",
            "actual_minutes": int,
            "outcome": "completed|abandoned",
            "notes": "optional string"
        }

    Response:
        {
            "status": "success|error",
            "export_path": "string",
            "calibration": {...},
            "error": "optional error message"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "error": "No JSON data provided"
            }), 400

        task_id = data.get('task_id')
        actual_minutes = data.get('actual_minutes')
        outcome = data.get('outcome', 'completed')
        notes = data.get('notes', '')

        if not task_id:
            return jsonify({
                "status": "error",
                "error": "task_id is required"
            }), 400

        logger.info(f"Logging completion for task {task_id}")

        # Get task data
        try:
            task = todoist.get_task(task_id)
            task_content = task['content']
            labels = task.get('labels', [])
        except TodoistAPIError:
            # If task not found in Todoist, use stored data
            task_content = "Task content unavailable"
            labels = []

        # Get hydration data
        hydration_data = stats_tracker.get_hydration(task_id)

        if not hydration_data:
            return jsonify({
                "status": "error",
                "error": f"No hydration data found for task {task_id}"
            }), 404

        # Recreate HydratedTask object
        hydrated = HydratedTask(**hydration_data['hydrated'])

        # Prepare learnings
        learnings = None
        if notes:
            learnings = {
                'what_went_well': '',
                'what_took_longer': notes if actual_minutes and actual_minutes > hydrated.total_estimate_minutes else '',
                'blockers_encountered': notes if outcome == 'abandoned' else ''
            }

        # Export to NotebookLM format
        def export_async():
            """Export in background thread."""
            try:
                export_path = exporter.export_task(
                    task_id=task_id,
                    original_task=task_content,
                    hydrated=hydrated,
                    labels=labels,
                    actual_minutes=actual_minutes,
                    learnings=learnings,
                    completion_date=datetime.now()
                )
                logger.info(f"Exported to {export_path}")

                # Analyze patterns
                pattern_analyzer.analyze_and_update()

            except Exception as e:
                logger.error(f"Failed to export: {e}")

        threading.Thread(target=export_async, daemon=True).start()

        # Track completion
        stats_tracker.track_completion(
            task_id=task_id,
            actual_minutes=actual_minutes,
            outcome=outcome
        )

        # Get updated calibration stats
        stats = stats_tracker.get_stats()

        return jsonify({
            "status": "success",
            "export_path": f"./notebooklm_sources/completed_tasks/{datetime.now().strftime('%Y-%m-%d')}_{task_id}_*.md",
            "calibration": {
                "avg_accuracy": stats.get('avg_accuracy'),
                "calibration_factor": stats.get('calibration_factor')
            }
        }), 200

    except Exception as e:
        logger.error(f"Log completion endpoint error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/stats', methods=['GET'])
def stats_endpoint():
    """
    Get current calibration statistics.

    Response:
        {
            "total_hydrated": int,
            "total_completed": int,
            "avg_accuracy": float,
            "calibration_factor": float,
            "patterns": [...],
            "recent_hydrations": [...]
        }
    """
    try:
        stats = stats_tracker.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Stats endpoint error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


def ensure_directories():
    """Ensure required directories exist."""
    directories = [
        "./notebooklm_sources",
        "./notebooklm_sources/completed_tasks",
        "./notebooklm_sources/patterns"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")


if __name__ == '__main__':
    # Ensure directories exist
    ensure_directories()

    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))

    logger.info(f"Starting Todoist Task Hydration Server on port {port}")
    logger.info(f"Dashboard: http://localhost:{port}")
    logger.info(f"Rate limit: {RATE_LIMIT} requests per minute")

    # Run server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('DEBUG', 'false').lower() == 'true'
    )
