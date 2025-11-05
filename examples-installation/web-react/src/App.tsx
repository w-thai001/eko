/**
 * Eko Web/React Installation Example
 *
 * This example demonstrates how to use Eko in a React web application.
 *
 * ⚠️ SECURITY WARNING:
 * NEVER expose your API keys in frontend code!
 * This example uses a backend proxy approach for production use.
 */

import { useState } from "react";
import { Eko, LLMs } from "@eko-ai/eko";
import { BrowserAgent } from "@eko-ai/eko-web";
import "./App.css";

function App() {
  const [task, setTask] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  /**
   * Initialize Eko with backend proxy
   *
   * IMPORTANT: In production, NEVER put API keys in frontend code!
   * Instead, use a backend proxy that handles the API calls.
   */
  const initEko = () => {
    // Production configuration - use backend proxy
    const llms: LLMs = {
      default: {
        provider: "openai", // Your backend can route to any provider
        model: "gpt-4",
        config: {
          // Point to your backend API proxy
          baseURL: "/api/llm", // Your backend endpoint
          headers: {
            // Use session token or other auth method
            Authorization: "Bearer your-session-token",
          },
        },
      },
    };

    const agents = [new BrowserAgent()];

    const eko = new Eko({
      llms,
      agents,
      onStreamCallback: (message) => {
        console.log("Stream update:", message);
        setProgress((prev) => [
          ...prev,
          `[${message.type}] ${message.content || ""}`,
        ]);
      },
      onError: (err) => {
        console.error("Eko error:", err);
        setError(err.message);
      },
    });

    return eko;
  };

  /**
   * Run a task with Eko
   */
  const runTask = async () => {
    if (!task.trim()) {
      setError("Please enter a task description");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setProgress([]);

    try {
      const eko = initEko();
      const taskResult = await eko.run(task);
      setResult(taskResult);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Example: Automate form filling
   */
  const exampleFormFilling = async () => {
    setTask(
      "Fill the login form with email 'demo@example.com' and password 'demo123', then click the login button"
    );
    // Auto-run after setting task
    setTimeout(() => runTask(), 100);
  };

  /**
   * Example: Web scraping
   */
  const exampleWebScraping = async () => {
    setTask("Navigate to news.ycombinator.com and get the top 5 story titles");
    setTimeout(() => runTask(), 100);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚀 Eko Web Installation Example</h1>
        <p>Build agentic workflows in your React app</p>
      </header>

      <main className="app-main">
        {/* Security Warning */}
        <div className="warning-box">
          <h3>⚠️ Security Warning</h3>
          <p>
            <strong>NEVER expose API keys in frontend code!</strong>
          </p>
          <p>
            This example uses a backend proxy approach. Configure your backend
            to handle LLM API calls securely.
          </p>
          <details>
            <summary>Click to see backend proxy example</summary>
            <pre>{`// Backend API route (Node.js/Express example)
app.post('/api/llm', async (req, res) => {
  // Verify user session
  if (!req.session.user) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  // Forward to actual LLM API with your secret key
  const response = await fetch('https://api.anthropic.com/v1/...', {
    method: 'POST',
    headers: {
      'Authorization': \`Bearer \${process.env.ANTHROPIC_API_KEY}\`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req.body),
  });

  const data = await response.json();
  res.json(data);
});`}</pre>
          </details>
        </div>

        {/* Task Input */}
        <div className="task-input-section">
          <h2>Enter Your Task</h2>
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Describe what you want Eko to do..."
            rows={4}
            disabled={loading}
          />
          <div className="button-group">
            <button
              onClick={runTask}
              disabled={loading || !task.trim()}
              className="primary-button"
            >
              {loading ? "Running..." : "Run Task"}
            </button>
          </div>
        </div>

        {/* Example Tasks */}
        <div className="examples-section">
          <h3>Try These Examples:</h3>
          <div className="button-group">
            <button onClick={exampleFormFilling} disabled={loading}>
              Form Filling
            </button>
            <button onClick={exampleWebScraping} disabled={loading}>
              Web Scraping
            </button>
          </div>
        </div>

        {/* Progress */}
        {progress.length > 0 && (
          <div className="progress-section">
            <h3>📊 Progress</h3>
            <div className="progress-log">
              {progress.map((msg, idx) => (
                <div key={idx} className="progress-item">
                  {msg}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="error-box">
            <h3>❌ Error</h3>
            <p>{error}</p>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="result-section">
            <h3>✅ Result</h3>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}

        {/* Documentation */}
        <div className="docs-section">
          <h2>📚 Next Steps</h2>
          <ul>
            <li>
              <a
                href="https://eko.fellou.ai/docs"
                target="_blank"
                rel="noopener noreferrer"
              >
                Read the Documentation
              </a>
            </li>
            <li>
              <a
                href="https://github.com/FellouAI/eko"
                target="_blank"
                rel="noopener noreferrer"
              >
                View GitHub Repository
              </a>
            </li>
            <li>
              <a
                href="https://eko.fellou.ai/docs/getting-started/quickstart"
                target="_blank"
                rel="noopener noreferrer"
              >
                Quickstart Guide
              </a>
            </li>
          </ul>
        </div>
      </main>
    </div>
  );
}

export default App;
