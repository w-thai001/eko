/**
 * Eko Browser Extension - Popup Script
 *
 * Handles the popup UI and communication with the background script
 */

// DOM Elements
const taskInput = document.getElementById("taskInput") as HTMLTextAreaElement;
const runTaskBtn = document.getElementById("runTask") as HTMLButtonElement;
const generateWorkflowBtn = document.getElementById(
  "generateWorkflow"
) as HTMLButtonElement;
const apiKeyWarning = document.getElementById("apiKeyWarning") as HTMLDivElement;
const openOptionsBtn = document.getElementById("openOptions") as HTMLButtonElement;
const progressSection = document.getElementById(
  "progressSection"
) as HTMLDivElement;
const progressLog = document.getElementById("progressLog") as HTMLDivElement;
const resultSection = document.getElementById("resultSection") as HTMLDivElement;
const resultTitle = document.getElementById("resultTitle") as HTMLHeadingElement;
const resultContent = document.getElementById("resultContent") as HTMLPreElement;
const quickActionButtons = document.querySelectorAll(".quick-action-btn");

// State
let isRunning = false;

/**
 * Check if API key is configured
 */
async function checkApiKey() {
  const response = await chrome.runtime.sendMessage({
    action: "checkApiKey",
  });

  if (!response.hasApiKey) {
    apiKeyWarning.style.display = "block";
    runTaskBtn.disabled = true;
    generateWorkflowBtn.disabled = true;
  }
}

/**
 * Run a task
 */
async function runTask() {
  const task = taskInput.value.trim();

  if (!task) {
    alert("Please enter a task description");
    return;
  }

  // Reset UI
  isRunning = true;
  updateButtonState();
  hideResult();
  showProgress();
  clearProgress();

  try {
    // Get current tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Send message to background script
    const response = await chrome.runtime.sendMessage({
      action: "runTask",
      task: task,
      tabId: tab.id,
    });

    if (response.success) {
      showResult("✅ Task Completed", response.result);
    } else {
      showResult("❌ Task Failed", { error: response.error });
    }
  } catch (error: any) {
    showResult("❌ Error", { error: error.message });
  } finally {
    isRunning = false;
    updateButtonState();
  }
}

/**
 * Generate workflow without executing
 */
async function generateWorkflow() {
  const task = taskInput.value.trim();

  if (!task) {
    alert("Please enter a task description");
    return;
  }

  isRunning = true;
  updateButtonState();
  hideResult();
  showProgress();
  clearProgress();

  try {
    const response = await chrome.runtime.sendMessage({
      action: "generateWorkflow",
      task: task,
    });

    if (response.success) {
      showResult("📋 Workflow Generated", response.workflow);
    } else {
      showResult("❌ Generation Failed", { error: response.error });
    }
  } catch (error: any) {
    showResult("❌ Error", { error: error.message });
  } finally {
    isRunning = false;
    updateButtonState();
  }
}

/**
 * Update button states
 */
function updateButtonState() {
  runTaskBtn.disabled = isRunning;
  generateWorkflowBtn.disabled = isRunning;
  runTaskBtn.textContent = isRunning ? "Running..." : "Run Task";
}

/**
 * Show progress section
 */
function showProgress() {
  progressSection.style.display = "block";
}

/**
 * Hide progress section
 */
function hideProgress() {
  progressSection.style.display = "none";
}

/**
 * Add progress message
 */
function addProgress(message: string) {
  const item = document.createElement("div");
  item.className = "progress-item";
  item.textContent = message;
  progressLog.appendChild(item);
  progressLog.scrollTop = progressLog.scrollHeight;
}

/**
 * Clear progress log
 */
function clearProgress() {
  progressLog.innerHTML = "";
}

/**
 * Show result
 */
function showResult(title: string, content: any) {
  resultTitle.textContent = title;
  resultContent.textContent = JSON.stringify(content, null, 2);
  resultSection.style.display = "block";
}

/**
 * Hide result
 */
function hideResult() {
  resultSection.style.display = "none";
}

/**
 * Listen for progress updates from background script
 */
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === "progress") {
    const progressText = `[${message.data.type}] ${message.data.content || ""}`;
    addProgress(progressText);
  }
});

// Event listeners
runTaskBtn.addEventListener("click", runTask);
generateWorkflowBtn.addEventListener("click", generateWorkflow);
openOptionsBtn.addEventListener("click", () => {
  chrome.runtime.openOptionsPage();
});

// Quick action buttons
quickActionButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    const task = btn.getAttribute("data-task");
    if (task) {
      taskInput.value = task;
      runTask();
    }
  });
});

// Allow Enter key to submit (with Shift+Enter for new line)
taskInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    runTask();
  }
});

// Initialize
checkApiKey();
