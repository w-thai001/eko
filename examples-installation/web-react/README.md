# Eko Web/React Installation Example

This is a complete React application demonstrating how to install and use Eko in a web environment with proper security practices.

## 🚨 Security First

**NEVER expose API keys in frontend code!**

This example demonstrates the correct approach:
- API calls go through a backend proxy
- Your backend securely stores and uses API keys
- Frontend uses session authentication

## Quick Start

### 1. Install Dependencies

```bash
npm install
# or
pnpm install
```

### 2. Set Up Backend Proxy (Required for Production)

Create a backend server to proxy LLM API calls. Example using Node.js/Express:

```javascript
// backend/server.js
import express from 'express';
import fetch from 'node-fetch';

const app = express();
app.use(express.json());

// Proxy endpoint for LLM API
app.post('/api/llm', async (req, res) => {
  // Verify user session
  if (!req.session?.user) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    // Forward to actual LLM API with your secret key
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.ANTHROPIC_API_KEY}`,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify(req.body),
    });

    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(4000, () => {
  console.log('Backend proxy running on port 4000');
});
```

### 3. Run the Development Server

```bash
npm run dev
# or
pnpm run dev
```

Visit `http://localhost:3000`

## What This Example Demonstrates

1. **Secure API Configuration**: Using backend proxy instead of exposing API keys
2. **React Integration**: Full React component with Eko
3. **Real-time Progress**: Streaming updates via callbacks
4. **Error Handling**: Proper error display and handling
5. **Example Tasks**: Pre-configured example workflows
6. **User Interface**: Clean, modern UI for task execution

## Project Structure

```
web-react/
├── src/
│   ├── App.tsx           # Main application component
│   ├── App.css           # Application styles
│   ├── main.tsx          # React entry point
│   └── index.css         # Global styles
├── index.html            # HTML template
├── vite.config.ts        # Vite configuration with proxy
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
└── README.md            # This file
```

## Key Features

### Backend Proxy Configuration

The example includes a Vite proxy configuration in `vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:4000', // Your backend
        changeOrigin: true,
      },
    },
  },
});
```

### Eko Integration

```typescript
const llms: LLMs = {
  default: {
    provider: "openai",
    model: "gpt-4",
    config: {
      baseURL: "/api/llm", // Backend proxy endpoint
      headers: {
        Authorization: "Bearer your-session-token",
      },
    },
  },
};
```

### Real-time Callbacks

```typescript
const eko = new Eko({
  llms,
  agents,
  onStreamCallback: (message) => {
    // Update UI with progress
    setProgress(prev => [...prev, message]);
  },
  onError: (error) => {
    // Handle errors
    setError(error.message);
  },
});
```

## Example Tasks Included

1. **Form Filling**: Automate form input and submission
2. **Web Scraping**: Extract data from websites

You can add more examples or create your own tasks!

## Development Tips

### Adding New Features

1. **Custom Agents**: Import and configure additional agents
2. **Workflow Management**: Use `generate()` and `execute()` separately
3. **Error Recovery**: Implement retry logic for failed tasks
4. **Progress UI**: Enhance progress display with custom components

### Testing

```bash
npm run build  # Test production build
npm run preview  # Preview production build
```

## Deployment

### Build for Production

```bash
npm run build
```

The `dist/` directory contains the production build.

### Environment Variables

Set these on your backend server:

```bash
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key
GOOGLE_API_KEY=your-key
```

### Deploy Checklist

- [ ] Backend proxy is deployed and running
- [ ] API keys are stored securely on backend (not in code)
- [ ] CORS is configured correctly
- [ ] HTTPS is enabled
- [ ] Session authentication is implemented
- [ ] Rate limiting is in place
- [ ] Error logging is configured

## Troubleshooting

### CORS Errors

If you see CORS errors, ensure:
1. Your backend proxy is running
2. Vite proxy is configured correctly
3. Backend allows your frontend origin

### Module Not Found

```bash
rm -rf node_modules package-lock.json
npm install
```

### Type Errors

Make sure TypeScript is properly configured:

```bash
npm install -D typescript @types/react @types/react-dom
```

## Security Best Practices

✅ **DO**:
- Use backend proxy for all LLM API calls
- Store API keys in environment variables on backend
- Implement proper authentication
- Use HTTPS in production
- Validate and sanitize all inputs
- Implement rate limiting

❌ **DON'T**:
- Expose API keys in frontend code
- Commit API keys to version control
- Trust client-side validation alone
- Skip authentication checks
- Use HTTP in production

## Next Steps

- [ ] Implement your backend proxy
- [ ] Add authentication
- [ ] Create custom agents for your use case
- [ ] Add more example workflows
- [ ] Enhance the UI
- [ ] Add error recovery
- [ ] Implement workflow history

## Resources

- [Eko Documentation](https://eko.fellou.ai/docs)
- [Web Configuration Guide](https://eko.fellou.ai/docs/getting-started/configuration#web-environment)
- [GitHub Repository](https://github.com/FellouAI/eko)

## Support

- [GitHub Issues](https://github.com/FellouAI/eko/issues)
- [Documentation](https://eko.fellou.ai/docs)
