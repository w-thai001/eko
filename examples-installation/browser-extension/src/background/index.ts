/**
 * Eko Browser Extension - Background Script
 *
 * This script runs in the background and handles:
 * - Eko initialization and task execution
 * - Communication with popup and content scripts
 * - API key management
 */

import { Eko, LLMs, Agent } from "@eko-ai/eko";
import { BrowserAgent } from "@eko-ai/eko-extension";

console.log("Eko Extension Background Script Loaded");

// Extension installation handler
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === "install") {
    console.log("Eko Extension installed!");
    // Open options page on first install
    chrome.runtime.openOptionsPage();
  } else if (details.reason === "update") {
    console.log("Eko Extension updated!");
  }
});

/**
 * Get API key from extension storage
 */
async function getApiKey(): Promise<string | null> {
  const result = await chrome.storage.sync.get(["apiKey", "provider"]);
  return result.apiKey || null;
}

/**
 * Get LLM provider configuration from storage
 */
async function getLLMConfig(): Promise<LLMs> {
  const result = await chrome.storage.sync.get([
    "apiKey",
    "provider",
    "model",
  ]);

  const provider = result.provider || "anthropic";
  const model =
    result.model ||
    (provider === "anthropic"
      ? "claude-sonnet-4-20250514"
      : provider === "openai"
        ? "gpt-4"
        : "gemini-2.0-flash-exp");

  return {
    default: {
      provider: provider,
      model: model,
      apiKey: result.apiKey || "",
    },
  };
}

/**
 * Initialize Eko instance
 */
async function createEko(
  onProgress?: (message: any) => void
): Promise<Eko | null> {
  const apiKey = await getApiKey();

  if (!apiKey) {
    console.error("No API key found. Please configure in options.");
    return null;
  }

  const llms = await getLLMConfig();
  const agents: Agent[] = [new BrowserAgent()];

  const eko = new Eko({
    llms,
    agents,
    onStreamCallback: (message) => {
      console.log("Eko progress:", message);
      if (onProgress) {
        onProgress(message);
      }
    },
    onError: (error) => {
      console.error("Eko error:", error);
    },
  });

  return eko;
}

/**
 * Run a task with Eko
 */
async function runTask(
  taskDescription: string,
  tabId?: number
): Promise<{ success: boolean; result?: any; error?: string }> {
  try {
    const eko = await createEko((progress) => {
      // Send progress updates to popup
      chrome.runtime.sendMessage({
        type: "progress",
        data: progress,
      });
    });

    if (!eko) {
      return {
        success: false,
        error: "Eko initialization failed. Please check your API key.",
      };
    }

    console.log("Running task:", taskDescription);

    const result = await eko.run(taskDescription);

    console.log("Task completed:", result);

    return {
      success: true,
      result,
    };
  } catch (error: any) {
    console.error("Task error:", error);
    return {
      success: false,
      error: error.message || "Unknown error occurred",
    };
  }
}

/**
 * Message handler from popup/content scripts
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Received message:", request);

  if (request.action === "runTask") {
    // Run task asynchronously
    runTask(request.task, request.tabId)
      .then(sendResponse)
      .catch((error) => {
        sendResponse({
          success: false,
          error: error.message,
        });
      });

    // Return true to indicate async response
    return true;
  }

  if (request.action === "checkApiKey") {
    getApiKey()
      .then((apiKey) => {
        sendResponse({ hasApiKey: !!apiKey });
      })
      .catch(() => {
        sendResponse({ hasApiKey: false });
      });

    return true;
  }

  if (request.action === "generateWorkflow") {
    // Generate workflow without executing
    createEko()
      .then(async (eko) => {
        if (!eko) {
          sendResponse({
            success: false,
            error: "Eko initialization failed",
          });
          return;
        }

        const workflow = await eko.generate(request.task);
        sendResponse({
          success: true,
          workflow,
        });
      })
      .catch((error) => {
        sendResponse({
          success: false,
          error: error.message,
        });
      });

    return true;
  }
});

/**
 * Context menu integration (optional)
 */
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "eko-automate",
    title: "Automate with Eko",
    contexts: ["page", "selection"],
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "eko-automate") {
    // Open popup or execute default action
    const selectedText = info.selectionText;
    if (selectedText) {
      // Run task with selected text
      runTask(`${selectedText}`, tab?.id);
    }
  }
});

export {};
