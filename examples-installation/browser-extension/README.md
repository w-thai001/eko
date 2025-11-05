# Eko Browser Extension Installation Example

A complete, ready-to-use Chrome/Browser extension example demonstrating how to install and use Eko for browser automation.

## Features

- 🚀 Complete browser extension with Eko integration
- ⚙️ Settings page for API key configuration
- 📊 Real-time progress monitoring
- 🎯 Quick action buttons for common tasks
- 🔄 Workflow generation and execution
- 💾 Secure API key storage in Chrome sync

## Quick Start

### 1. Install Dependencies

```bash
npm install
# or
pnpm install
```

### 2. Build the Extension

```bash
npm run build
# or
pnpm run build
```

This creates a `dist/` directory with the compiled extension.

### 3. Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Select the `dist/` directory from this project

### 4. Configure API Key

1. Click the Eko extension icon in your browser
2. Click "Open Options" or right-click the icon → "Options"
3. Select your LLM provider (Anthropic, OpenAI, or Google)
4. Enter your API key
5. Click "Save Settings"

### 5. Start Automating!

Click the extension icon and:
- Enter a task description
- Or use one of the quick action buttons
- Click "Run Task" to execute

## Project Structure

```
browser-extension/
├── src/
│   ├── background/
│   │   └── index.ts          # Background script (Eko logic)
│   ├── popup/
│   │   ├── popup.html        # Extension popup UI
│   │   ├── popup.ts          # Popup logic
│   │   └── popup.css         # Popup styles
│   ├── options/
│   │   ├── options.html      # Options page UI
│   │   ├── options.ts        # Options logic
│   │   └── options.css       # Options styles
│   └── content/
│       └── index.ts          # Content script (page interaction)
├── icons/                    # Extension icons (add your own)
├── manifest.json             # Extension manifest
├── vite.config.ts            # Vite configuration
├── package.json              # Dependencies
└── README.md                 # This file
```

## How It Works

### Background Script (`src/background/index.ts`)

- Initializes Eko with user's API key
- Handles task execution requests
- Manages LLM provider configuration
- Communicates with popup and content scripts

### Popup (`src/popup/`)

- User interface for entering tasks
- Quick action buttons for common tasks
- Real-time progress display
- Result visualization

### Options Page (`src/options/`)

- API key and provider configuration
- Model selection
- Usage instructions

### Content Script (`src/content/index.ts`)

- Runs on every web page
- Can interact with page DOM
- Bridges between background script and web pages

## Example Tasks

Try these in the extension popup:

1. **Web Navigation**
   ```
   Go to github.com and search for "Eko"
   ```

2. **Form Filling**
   ```
   Fill the login form with email test@example.com
   ```

3. **Data Extraction**
   ```
   Extract all article titles from this page and copy to clipboard
   ```

4. **Page Interaction**
   ```
   Scroll down, click all checkboxes, then click submit
   ```

5. **Multi-step Workflow**
   ```
   Navigate to news site, find the top article, summarize it, and save to notes
   ```

## Development

### Watch Mode

For development with auto-rebuild:

```bash
npm run dev
# or
pnpm run dev
```

Then reload the extension in Chrome after changes.

### Type Checking

```bash
npm run type-check
# or
pnpm run type-check
```

## Customization

### Adding Icons

Place your icon files in an `icons/` directory:
- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)
- `icon128.png` (128x128 pixels)

### Adding Quick Actions

Edit `src/popup/popup.html` and add more quick action buttons:

```html
<button class="quick-action-btn" data-task="Your task description">
  Button Label
</button>
```

### Custom Agents

Modify `src/background/index.ts` to add custom agents:

```typescript
import { CustomAgent } from "./agents/custom-agent";

const agents: Agent[] = [
  new BrowserAgent(),
  new CustomAgent(), // Your custom agent
];
```

## API Keys

### Anthropic (Claude)
- Get your key at: [console.anthropic.com](https://console.anthropic.com)
- Recommended for most tasks

### OpenAI (GPT)
- Get your key at: [platform.openai.com](https://platform.openai.com)
- Good for general-purpose tasks

### Google (Gemini)
- Get your key at: [makersuite.google.com](https://makersuite.google.com/app/apikey)
- Fast and cost-effective

## Security

- API keys are stored securely in Chrome sync storage
- Keys are never exposed to web pages
- All execution happens in the extension context
- No data is sent to third parties (except LLM providers)

## Troubleshooting

### Extension Not Loading

```bash
# Rebuild the extension
rm -rf dist node_modules
npm install
npm run build
```

Then reload in Chrome.

### API Key Not Working

1. Check the API key is correct in Options
2. Verify the provider is correct (Anthropic/OpenAI/Google)
3. Check your API account has credits
4. Look for errors in Chrome DevTools (Console)

### No Progress Updates

- Ensure the popup stays open during task execution
- Check background script logs: Extensions → Eko → Background page → Inspect

### Tasks Not Executing

1. Open Chrome DevTools (F12)
2. Go to Extensions → Your Eko Extension
3. Click "background page" → Inspect
4. Check console for errors

### Permission Issues

Ensure `manifest.json` includes necessary permissions:

```json
{
  "permissions": ["activeTab", "storage", "scripting", "tabs"],
  "host_permissions": ["http://*/*", "https://*/*"]
}
```

## Publishing

To publish your extension:

1. **Build for production**
   ```bash
   npm run build
   ```

2. **Test thoroughly** in multiple scenarios

3. **Create a ZIP file** of the `dist/` directory

4. **Submit to Chrome Web Store**
   - Visit [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole)
   - Upload your ZIP file
   - Fill in store listing details
   - Submit for review

## Resources

- [Eko Documentation](https://eko.fellou.ai/docs)
- [Chrome Extension Documentation](https://developer.chrome.com/docs/extensions/)
- [Manifest V3 Guide](https://developer.chrome.com/docs/extensions/mv3/)
- [GitHub Repository](https://github.com/FellouAI/eko)

## Support

- [GitHub Issues](https://github.com/FellouAI/eko/issues)
- [Documentation](https://eko.fellou.ai/docs)

---

Happy automating with Eko! 🚀
