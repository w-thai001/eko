# Eko Installation Guide

Welcome to Eko! This guide will help you install and set up Eko in different environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Node.js](#nodejs)
  - [Web/Browser](#webbrowser)
  - [Browser Extension](#browser-extension)
- [Quick Start Examples](#quick-start-examples)
- [Environment-Specific Setup](#environment-specific-setup)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before installing Eko, make sure you have:

- **Node.js**: Version 18.0.0 or higher
- **Package Manager**: pnpm (recommended), npm, or yarn
- **API Keys**: At least one LLM provider API key (Anthropic, OpenAI, Google, etc.)

### Installing pnpm

If you don't have pnpm installed:

```bash
npm install -g pnpm
```

## Installation

### Node.js

For Node.js applications, install the core package and Node.js-specific agents:

```bash
pnpm install @eko-ai/eko @eko-ai/eko-nodejs
```

or with npm:

```bash
npm install @eko-ai/eko @eko-ai/eko-nodejs
```

### Web/Browser

For web applications (React, Vue, etc.), install the core and web packages:

```bash
pnpm install @eko-ai/eko @eko-ai/eko-web
```

### Browser Extension

For browser extension development:

```bash
pnpm install @eko-ai/eko @eko-ai/eko-extension
```

## Quick Start Examples

### 1. Node.js Automation

Create a file `index.ts`:

```typescript
import { BrowserAgent, FileAgent } from "@eko-ai/eko-nodejs";
import { Eko, Agent, LLMs } from "@eko-ai/eko";

// Configure LLM providers
const llms: LLMs = {
  default: {
    provider: "anthropic",
    model: "claude-sonnet-4-20250514",
    apiKey: process.env.ANTHROPIC_API_KEY || "",
  },
  openai: {
    provider: "openai",
    model: "gpt-4",
    apiKey: process.env.OPENAI_API_KEY || "",
  },
  gemini: {
    provider: "google",
    model: "gemini-2.0-flash-exp",
    apiKey: process.env.GOOGLE_API_KEY || "",
  },
};

// Initialize agents
const agents: Agent[] = [
  new BrowserAgent(),  // For browser automation
  new FileAgent(),     // For file operations
];

// Create Eko instance
const eko = new Eko({ llms, agents });

// Run a task
async function main() {
  const result = await eko.run(
    "Search for the latest news about AI, summarize and save to ./ai-news.md"
  );
  console.log("Task completed:", result);
}

main().catch(console.error);
```

Run the example:

```bash
# Install Playwright browsers (first time only)
pnpm exec playwright install

# Set your API keys and run
ANTHROPIC_API_KEY=your-key pnpm tsx index.ts
```

### 2. Web Application

Create a React component or vanilla JavaScript file:

```typescript
import { Eko, LLMs } from "@eko-ai/eko";
import { BrowserAgent } from "@eko-ai/eko-web";

// ⚠️ SECURITY WARNING: Never expose API keys in frontend code!
// Use a backend proxy instead. This is for demonstration only.
const llms: LLMs = {
  default: {
    provider: "openai",
    model: "gpt-4",
    // Use backend proxy
    config: {
      baseURL: "/api/llm", // Your backend endpoint
    },
  },
};

const agents = [new BrowserAgent()];
const eko = new Eko({ llms, agents });

// Example: Automate a login flow
async function automateLogin() {
  const result = await eko.run(
    "Navigate to the login page, enter username 'demo@example.com' and password 'demo123', then click login"
  );
  return result;
}

// Example with streaming callbacks
async function runWithFeedback(task: string) {
  const eko = new Eko({
    llms,
    agents,
    onStreamCallback: (message) => {
      console.log("Progress:", message);
      // Update UI with progress
    },
  });

  const result = await eko.run(task);
  return result;
}
```

### 3. Browser Extension

Create a background script `background.ts`:

```typescript
import { Eko, LLMs } from "@eko-ai/eko";
import { BrowserAgent } from "@eko-ai/eko-extension";

// Initialize Eko when extension loads
chrome.runtime.onInstalled.addListener(() => {
  console.log("Eko extension installed");
});

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "runTask") {
    runEkoTask(request.task).then(sendResponse);
    return true; // Keep channel open for async response
  }
});

async function runEkoTask(taskDescription: string) {
  // Get API key from extension storage
  const { apiKey } = await chrome.storage.sync.get("apiKey");

  const llms: LLMs = {
    default: {
      provider: "anthropic",
      model: "claude-sonnet-4-20250514",
      apiKey: apiKey,
    },
  };

  const agents = [new BrowserAgent()];
  const eko = new Eko({ llms, agents });

  try {
    const result = await eko.run(taskDescription);
    return { success: true, result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

Popup script `popup.ts`:

```typescript
document.getElementById("runBtn")?.addEventListener("click", async () => {
  const taskInput = document.getElementById("taskInput") as HTMLInputElement;
  const task = taskInput.value;

  const response = await chrome.runtime.sendMessage({
    action: "runTask",
    task: task,
  });

  console.log("Task result:", response);
});
```

## Environment-Specific Setup

### Development Setup

For contributing to Eko or running examples from the repository:

```bash
# Clone the repository
git clone https://github.com/FellouAI/eko.git
cd eko

# Install dependencies
pnpm install

# Build all packages
pnpm build

# Run tests (optional)
pnpm test
```

### Running Repository Examples

The repository includes three example projects:

#### 1. Node.js Example

```bash
cd example/nodejs
pnpm install
pnpm run playwright  # First time only
ANTHROPIC_API_KEY=your-key pnpm run start
```

#### 2. Web Example

```bash
cd example/web
pnpm install
pnpm run start
```

Visit `http://localhost:5173` (or the displayed port)

#### 3. Extension Example

```bash
cd example/extension
pnpm install
pnpm run build
```

Then:
1. Open Chrome and navigate to `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `example/extension/dist` directory

## Advanced Configuration

### Multiple LLM Providers

```typescript
const llms: LLMs = {
  default: {
    provider: "anthropic",
    model: "claude-sonnet-4-20250514",
    apiKey: process.env.ANTHROPIC_API_KEY,
  },
  // Fast, cheap model for simple tasks
  fast: {
    provider: "openai",
    model: "gpt-4o-mini",
    apiKey: process.env.OPENAI_API_KEY,
  },
  // Powerful model for complex reasoning
  powerful: {
    provider: "google",
    model: "gemini-2.0-flash-thinking-exp",
    apiKey: process.env.GOOGLE_API_KEY,
  },
  // OpenAI-compatible providers (Qwen, etc.)
  qwen: {
    provider: "openai",
    model: "qwen-plus",
    apiKey: process.env.QWEN_API_KEY,
    config: {
      baseURL: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    },
  },
};
```

### Custom Agents

```typescript
import { BaseAgent } from "@eko-ai/eko";

class CustomAgent extends BaseAgent {
  constructor() {
    super({
      name: "CustomAgent",
      description: "Performs custom operations",
    });
  }

  getTools() {
    return [
      {
        name: "custom_action",
        description: "Performs a custom action",
        execute: async (params) => {
          // Your custom logic
          return { success: true };
        },
      },
    ];
  }
}

const agents = [new CustomAgent(), new FileAgent()];
const eko = new Eko({ llms, agents });
```

### Callbacks and Monitoring

```typescript
const eko = new Eko({
  llms,
  agents,
  onStreamCallback: (message) => {
    console.log("Stream update:", message);
  },
  onTaskComplete: (result) => {
    console.log("Task completed:", result);
  },
  onError: (error) => {
    console.error("Error occurred:", error);
  },
});
```

### Workflow Management

```typescript
// Generate workflow without executing
const workflow = await eko.generate("Describe your task here");
console.log("Generated workflow:", workflow);

// Execute a generated workflow later
const result = await eko.execute(workflow.taskId);

// Modify an existing workflow
const modified = await eko.modify(
  workflow.taskId,
  "Change the output format to JSON"
);

// Pause and resume execution
const pausableEko = new Eko({
  llms,
  agents,
  onStreamCallback: async (message) => {
    if (message.type === "need_approval") {
      // Pause execution and ask user
      const approved = await askUser("Approve this action?");
      if (!approved) {
        throw new Error("User cancelled");
      }
    }
  },
});
```

## Troubleshooting

### Common Issues

#### 1. Module Not Found

**Error**: `Cannot find module '@eko-ai/eko'`

**Solution**: Make sure you've installed the package and built it (if using from repository):

```bash
pnpm install
pnpm build  # If using from repository
```

#### 2. Playwright Browsers Not Installed

**Error**: `browserType.launch: Executable doesn't exist`

**Solution**: Install Playwright browsers:

```bash
pnpm exec playwright install
# or
npx playwright install
```

#### 3. API Key Issues

**Error**: `API key not found` or `Unauthorized`

**Solution**: Ensure your API keys are set correctly:

```bash
# Check environment variables
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Set them if missing
export ANTHROPIC_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

#### 4. CORS Issues in Web Applications

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution**: Never call LLM APIs directly from the browser. Set up a backend proxy:

```typescript
// Good: Use backend proxy
const llms: LLMs = {
  default: {
    provider: "openai",
    model: "gpt-4",
    config: {
      baseURL: "/api/llm", // Your backend endpoint
      headers: {
        "Authorization": "Bearer your-session-token",
      },
    },
  },
};
```

#### 5. TypeScript Errors

**Error**: Type errors or `Cannot find type definition`

**Solution**: Install TypeScript and type definitions:

```bash
pnpm add -D typescript @types/node
```

Ensure your `tsconfig.json` includes:

```json
{
  "compilerOptions": {
    "moduleResolution": "node",
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

## Next Steps

- Read the [Quickstart Guide](https://eko.fellou.ai/docs/getting-started/quickstart/)
- Explore [API Documentation](https://eko.fellou.ai/docs)
- Check out [Example Projects](./example)
- Join the [Community](https://github.com/FellouAI/eko/issues)

## Security Best Practices

1. **Never expose API keys in frontend code**
2. **Use environment variables for sensitive data**
3. **Implement backend proxies for LLM API calls in web apps**
4. **Validate and sanitize user inputs**
5. **Use HTTPS for all API communications**
6. **Regularly update dependencies**

## Support

- **Issues**: [GitHub Issues](https://github.com/FellouAI/eko/issues)
- **Documentation**: [https://eko.fellou.ai/docs](https://eko.fellou.ai/docs)
- **Examples**: Check the `example/` directory in the repository

---

Happy building with Eko! 🚀
