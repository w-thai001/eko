/**
 * Eko Browser Extension - Options Page Script
 *
 * Handles saving and loading extension settings
 */

// DOM Elements
const providerSelect = document.getElementById("provider") as HTMLSelectElement;
const modelInput = document.getElementById("model") as HTMLInputElement;
const apiKeyInput = document.getElementById("apiKey") as HTMLInputElement;
const saveButton = document.getElementById("saveSettings") as HTMLButtonElement;
const saveStatus = document.getElementById("saveStatus") as HTMLDivElement;

// Default models for each provider
const defaultModels: Record<string, string> = {
  anthropic: "claude-sonnet-4-20250514",
  openai: "gpt-4",
  google: "gemini-2.0-flash-exp",
};

/**
 * Load saved settings
 */
async function loadSettings() {
  const settings = await chrome.storage.sync.get([
    "provider",
    "model",
    "apiKey",
  ]);

  if (settings.provider) {
    providerSelect.value = settings.provider;
  }

  if (settings.model) {
    modelInput.value = settings.model;
  } else {
    modelInput.placeholder = `e.g., ${defaultModels[providerSelect.value]}`;
  }

  if (settings.apiKey) {
    apiKeyInput.value = settings.apiKey;
  }
}

/**
 * Save settings
 */
async function saveSettings() {
  const provider = providerSelect.value;
  const model = modelInput.value.trim() || defaultModels[provider];
  const apiKey = apiKeyInput.value.trim();

  if (!apiKey) {
    showStatus("Please enter an API key", "error");
    return;
  }

  try {
    await chrome.storage.sync.set({
      provider,
      model,
      apiKey,
    });

    showStatus("Settings saved successfully!", "success");
  } catch (error: any) {
    showStatus(`Error saving settings: ${error.message}`, "error");
  }
}

/**
 * Show status message
 */
function showStatus(message: string, type: "success" | "error") {
  saveStatus.textContent = message;
  saveStatus.className = `status-message ${type}`;
  saveStatus.style.display = "block";

  setTimeout(() => {
    saveStatus.style.display = "none";
  }, 3000);
}

/**
 * Update model placeholder when provider changes
 */
function updateModelPlaceholder() {
  const provider = providerSelect.value;
  modelInput.placeholder = `e.g., ${defaultModels[provider]}`;
}

// Event listeners
saveButton.addEventListener("click", saveSettings);
providerSelect.addEventListener("change", updateModelPlaceholder);

// Load settings on page load
loadSettings();
