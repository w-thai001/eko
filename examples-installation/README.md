# Eko Installation Examples

This directory contains complete, ready-to-use installation examples for Eko across different platforms. Each example is a fully functional project that you can use as a starting point for your own applications.

## 📁 Available Examples

### 1. [Node.js Basic](./nodejs-basic/)
Complete Node.js application with Eko integration for server-side automation.

**Use Cases:**
- Web scraping and data extraction
- File system operations
- Automated testing
- Server-side workflow automation

**Quick Start:**
```bash
cd nodejs-basic
pnpm install
pnpm run playwright  # First time only
ANTHROPIC_API_KEY=your-key pnpm start
```

**Features:**
- Multiple LLM provider support
- File and browser agents
- Comprehensive examples
- Progress monitoring
- Error handling

---

### 2. [Web/React](./web-react/)
Modern React application demonstrating secure Eko integration in web environments.

**Use Cases:**
- Browser-based automation
- Interactive web applications
- Form automation
- Client-side workflows

**Quick Start:**
```bash
cd web-react
pnpm install
pnpm run dev
```

**Features:**
- Backend proxy security pattern
- Real-time progress updates
- Modern React UI
- Example tasks included
- Production-ready architecture

**⚠️ Security Note:** Never expose API keys in frontend code! This example demonstrates the correct backend proxy approach.

---

### 3. [Browser Extension](./browser-extension/)
Full-featured Chrome extension for browser automation with Eko.

**Use Cases:**
- Browser automation
- Page interaction and scraping
- Automated form filling
- Workflow automation across tabs

**Quick Start:**
```bash
cd browser-extension
pnpm install
pnpm run build
# Load dist/ directory in chrome://extensions
```

**Features:**
- Complete extension with popup and options page
- Secure API key storage
- Quick action buttons
- Content script integration
- Real-time progress monitoring

---

## 🚀 Getting Started

### Prerequisites

All examples require:
- **Node.js** >= 18.0.0
- **pnpm** (recommended) or npm
- **API Key** from at least one LLM provider:
  - Anthropic (Claude): [console.anthropic.com](https://console.anthropic.com)
  - OpenAI (GPT): [platform.openai.com](https://platform.openai.com)
  - Google (Gemini): [makersuite.google.com](https://makersuite.google.com/app/apikey)

### Installation

1. **Install pnpm** (if not already installed):
   ```bash
   npm install -g pnpm
   ```

2. **Choose your example** and navigate to its directory:
   ```bash
   cd nodejs-basic    # or web-react, or browser-extension
   ```

3. **Install dependencies**:
   ```bash
   pnpm install
   ```

4. **Follow platform-specific instructions** in each example's README

---

## 📖 Comparison Guide

| Feature | Node.js | Web/React | Browser Extension |
|---------|---------|-----------|-------------------|
| **Environment** | Server | Browser | Browser |
| **Complexity** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Security** | ✅ Built-in | ⚠️ Needs proxy | ✅ Built-in |
| **UI** | Terminal | Web App | Extension Popup |
| **Best For** | Automation scripts | Web apps | Browser automation |
| **Distribution** | npm/standalone | Web hosting | Chrome Web Store |

---

## 🎯 Choose Your Platform

### Choose **Node.js** if you want to:
- ✅ Run automation scripts from the terminal
- ✅ Build server-side workflows
- ✅ Integrate with existing Node.js apps
- ✅ Use file system operations extensively
- ✅ Run headless browser automation

### Choose **Web/React** if you want to:
- ✅ Build interactive web applications
- ✅ Provide browser-based UI for users
- ✅ Integrate with existing React apps
- ✅ Deploy to web hosting
- ✅ Create client-side workflows

### Choose **Browser Extension** if you want to:
- ✅ Automate browser tasks across websites
- ✅ Provide always-available automation
- ✅ Interact with any web page
- ✅ Distribute via Chrome Web Store
- ✅ Run workflows on demand

---

## 🛠️ Common Setup Issues

### Issue: Module Not Found

```bash
rm -rf node_modules package-lock.json
pnpm install
```

### Issue: Playwright Not Installed (Node.js)

```bash
pnpm exec playwright install
```

### Issue: API Key Not Working

1. Verify your API key is correct
2. Check you have credits in your LLM provider account
3. Ensure you're using the correct provider name
4. Try generating a new API key

### Issue: TypeScript Errors

```bash
pnpm add -D typescript @types/node
```

---

## 📚 Documentation

### Main Documentation
- **Eko Docs**: [eko.fellou.ai/docs](https://eko.fellou.ai/docs)
- **Getting Started**: [eko.fellou.ai/docs/getting-started](https://eko.fellou.ai/docs/getting-started)
- **API Reference**: [eko.fellou.ai/docs/api](https://eko.fellou.ai/docs/api)

### Installation Guide
- See [INSTALLATION.md](../INSTALLATION.md) in the root directory for comprehensive installation instructions

### Example-Specific Docs
- [Node.js README](./nodejs-basic/README.md)
- [Web/React README](./web-react/README.md)
- [Browser Extension README](./browser-extension/README.md)

---

## 🔐 Security Best Practices

### ✅ DO:
- Store API keys in environment variables (Node.js)
- Use backend proxies for API calls (Web apps)
- Use secure storage (Browser extensions)
- Validate and sanitize user inputs
- Keep dependencies updated

### ❌ DON'T:
- Expose API keys in frontend code
- Commit API keys to version control
- Skip input validation
- Trust client-side data alone
- Use insecure HTTP connections

---

## 🎓 Learning Path

### 1. Start with Node.js Example
Learn the basics of Eko in a simple environment:
```bash
cd nodejs-basic
# Follow the README instructions
```

### 2. Explore Web Integration
See how to integrate Eko in web apps securely:
```bash
cd web-react
# Follow the README instructions
```

### 3. Build Browser Extensions
Create powerful browser automation tools:
```bash
cd browser-extension
# Follow the README instructions
```

---

## 🤝 Contributing

Found an issue or want to improve these examples?

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.

---

## 💬 Support

Need help?

- **Issues**: [GitHub Issues](https://github.com/FellouAI/eko/issues)
- **Discussions**: [GitHub Discussions](https://github.com/FellouAI/eko/discussions)
- **Documentation**: [eko.fellou.ai/docs](https://eko.fellou.ai/docs)

---

## 📄 License

All examples are MIT licensed. See [LICENSE](../LICENSE) for details.

---

## 🌟 Next Steps

1. **Choose your platform** from the examples above
2. **Follow the Quick Start** instructions
3. **Run the examples** to see Eko in action
4. **Customize** for your use case
5. **Build** something amazing!

Happy building with Eko! 🚀
