/**
 * Eko Node.js Installation Example
 *
 * This example demonstrates how to set up and use Eko in a Node.js environment.
 *
 * Installation:
 * 1. npm install (or pnpm install)
 * 2. npx playwright install (first time only)
 * 3. Set your API keys in environment variables
 * 4. npm start (or pnpm start)
 */

import { BrowserAgent, FileAgent } from "@eko-ai/eko-nodejs";
import { Eko, Agent, LLMs, EkoConfig } from "@eko-ai/eko";

// Configure LLM providers
// You can use multiple providers and switch between them based on your needs
const llms: LLMs = {
  // Default provider (required)
  default: {
    provider: "anthropic",
    model: "claude-sonnet-4-20250514",
    apiKey: process.env.ANTHROPIC_API_KEY || "",
  },

  // Optional: Additional providers for different tasks
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

  // OpenAI-compatible providers (Qwen, Doubao, etc.)
  qwen: {
    provider: "openai",
    model: "qwen-plus",
    apiKey: process.env.QWEN_API_KEY || "",
    config: {
      baseURL: "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    },
  },
};

// Initialize agents
// Agents provide different capabilities to Eko
const agents: Agent[] = [
  new BrowserAgent(),  // Enables browser automation with Playwright
  new FileAgent(),     // Enables file system operations
];

// Configure Eko with callbacks for monitoring
const config: EkoConfig = {
  llms,
  agents,

  // Optional: Monitor execution progress
  onStreamCallback: (message) => {
    console.log("📊 Progress:", message.type, message.content);
  },

  // Optional: Handle task completion
  onTaskComplete: (result) => {
    console.log("✅ Task completed:", result.status);
  },

  // Optional: Handle errors
  onError: (error) => {
    console.error("❌ Error occurred:", error.message);
  },
};

// Create Eko instance
const eko = new Eko(config);

/**
 * Example 1: Simple web search and save
 */
async function example1_WebSearchAndSave() {
  console.log("\n🚀 Example 1: Web search and save to file\n");

  const result = await eko.run(
    "Search for the latest news about AI, summarize the top 3 articles, and save to ./ai-news.md"
  );

  console.log("Result:", result);
}

/**
 * Example 2: File operations
 */
async function example2_FileOperations() {
  console.log("\n🚀 Example 2: File operations\n");

  const result = await eko.run(
    "Create a directory called 'reports', then create a file called 'summary.txt' with today's date and time"
  );

  console.log("Result:", result);
}

/**
 * Example 3: Multi-step workflow
 */
async function example3_MultiStepWorkflow() {
  console.log("\n🚀 Example 3: Multi-step workflow\n");

  const result = await eko.run(
    "Visit news.ycombinator.com, get the top 5 story titles, create a markdown file with these titles and their links"
  );

  console.log("Result:", result);
}

/**
 * Example 4: Generate workflow without executing
 */
async function example4_GenerateWorkflow() {
  console.log("\n🚀 Example 4: Generate workflow (without execution)\n");

  // Generate a workflow plan without executing it
  const workflow = await eko.generate(
    "Search for JavaScript tutorials, summarize them, and save to a file"
  );

  console.log("Generated workflow:", JSON.stringify(workflow, null, 2));

  // You can execute it later
  // const result = await eko.execute(workflow.taskId);
}

/**
 * Example 5: Modify existing workflow
 */
async function example5_ModifyWorkflow() {
  console.log("\n🚀 Example 5: Generate and modify workflow\n");

  // Generate initial workflow
  const workflow = await eko.generate(
    "Search for Python news and save to python-news.txt"
  );

  console.log("Original workflow generated");

  // Modify the workflow
  const modified = await eko.modify(
    workflow.taskId,
    "Change the output format to JSON and save as python-news.json instead"
  );

  console.log("Modified workflow:", modified);

  // Execute the modified workflow
  // const result = await eko.execute(workflow.taskId);
}

/**
 * Example 6: Using specific LLM provider
 */
async function example6_SpecificProvider() {
  console.log("\n🚀 Example 6: Using specific LLM provider\n");

  // You can configure Eko to use a specific LLM for certain tasks
  const ekoWithOpenAI = new Eko({
    llms: {
      default: {
        provider: "openai",
        model: "gpt-4",
        apiKey: process.env.OPENAI_API_KEY || "",
      },
    },
    agents,
  });

  const result = await ekoWithOpenAI.run(
    "What is the current weather? (This is a demo task)"
  );

  console.log("Result:", result);
}

/**
 * Main function - Run examples
 */
async function main() {
  console.log("🎉 Eko Node.js Installation Example\n");
  console.log("====================================\n");

  // Check if API keys are set
  if (!process.env.ANTHROPIC_API_KEY && !process.env.OPENAI_API_KEY && !process.env.GOOGLE_API_KEY) {
    console.error("❌ Error: No API keys found!");
    console.error("Please set at least one of the following environment variables:");
    console.error("  - ANTHROPIC_API_KEY");
    console.error("  - OPENAI_API_KEY");
    console.error("  - GOOGLE_API_KEY");
    console.error("\nExample:");
    console.error("  ANTHROPIC_API_KEY=your-key pnpm start");
    process.exit(1);
  }

  try {
    // Run examples (uncomment the ones you want to try)

    // await example1_WebSearchAndSave();
    // await example2_FileOperations();
    // await example3_MultiStepWorkflow();
    await example4_GenerateWorkflow();
    // await example5_ModifyWorkflow();
    // await example6_SpecificProvider();

    console.log("\n✅ All examples completed successfully!");
  } catch (error) {
    console.error("\n❌ Error running examples:", error);
    process.exit(1);
  }
}

// Run the examples
main().catch(console.error);
