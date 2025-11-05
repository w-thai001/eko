# Eko Node.js Installation Example

This is a complete, ready-to-run example demonstrating how to install and use Eko in a Node.js environment.

## Quick Start

### 1. Install Dependencies

```bash
npm install
# or
pnpm install
```

### 2. Install Playwright Browsers (First Time Only)

```bash
npm run playwright
# or
pnpm run playwright
```

### 3. Set Your API Keys

You need at least one LLM provider API key:

```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
# or
export OPENAI_API_KEY="your-openai-key"
# or
export GOOGLE_API_KEY="your-google-key"
```

### 4. Run the Example

```bash
npm start
# or
pnpm start
```

Or with API key inline:

```bash
ANTHROPIC_API_KEY=your-key npm start
```

## What This Example Demonstrates

This example shows:

1. **Basic Setup**: How to configure Eko with LLM providers and agents
2. **Web Search & Save**: Automating web searches and saving results
3. **File Operations**: Creating files and directories
4. **Multi-step Workflows**: Combining multiple actions
5. **Workflow Generation**: Creating workflows without executing them
6. **Workflow Modification**: Modifying generated workflows
7. **Provider Selection**: Using different LLM providers
8. **Callbacks**: Monitoring execution progress

## Available Examples

Edit `src/index.ts` and uncomment the examples you want to run:

- `example1_WebSearchAndSave()` - Search web and save results
- `example2_FileOperations()` - Create files and directories
- `example3_MultiStepWorkflow()` - Multi-step automation
- `example4_GenerateWorkflow()` - Generate workflow plan (currently active)
- `example5_ModifyWorkflow()` - Modify generated workflows
- `example6_SpecificProvider()` - Use specific LLM provider

## Project Structure

```
nodejs-basic/
├── src/
│   └── index.ts          # Main example code
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
└── README.md            # This file
```

## Troubleshooting

### Module Not Found

If you get "Cannot find module '@eko-ai/eko'":

```bash
rm -rf node_modules package-lock.json
npm install
```

### Playwright Browsers Missing

If you get "Executable doesn't exist":

```bash
npx playwright install
```

### API Key Not Found

Make sure you've set the environment variable:

```bash
echo $ANTHROPIC_API_KEY
```

If empty, set it:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

## Next Steps

- Modify the examples to try your own tasks
- Explore the [Eko Documentation](https://eko.fellou.ai/docs)
- Check out more [examples in the repository](../../example)
- Create custom agents for your specific needs

## Support

- [GitHub Issues](https://github.com/FellouAI/eko/issues)
- [Documentation](https://eko.fellou.ai/docs)
