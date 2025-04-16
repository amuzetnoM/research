# Context Protocols for Intelligent Model Interactions

## Overview

The Model Context Protocol (MCP) is a flexible, unified interface for interacting with various AI models while maintaining conversational context. It provides a stateful session-based approach to model interactions, enabling more sophisticated applications.

### Key Features

- **Unified API**: Single interface for multiple model types (chat, completion, embedding)
- **Stateful Sessions**: Maintain context across multiple interactions
- **Provider Agnostic**: Support for various AI providers (OpenAI, HuggingFace, etc.)
- **Context Management**: Smart handling of conversation history and user context
- **Performance Monitoring**: Built-in metrics and observability
- **Async and Sync Support**: Both asynchronous and synchronous client implementations

The synchronous client is a wrapper around the asynchronous one for use in non-async code environments.

## Documentation

- [Architecture Guide](./docs/architecture.md) - Detailed system architecture and design principles
- [Setup Guide](./docs/setup.md) - Instructions for setting up the MCP server
- [Usage Guide](./docs/usage.md) - Guide to using the MCP client in your applications
- [API Reference](./docs/api_reference.md) - Complete API reference documentation

## Quick Start

### Server Setup

```bash
# Install required packages
pip install aiohttp prometheus_client psutil

# Start the MCP server
python -m mcp.run_mcp_server
```

### Client Usage

```python
from mcp.mcp_client import MCPClient
import asyncio

async def main():
    async with MCPClient() as client:
        # Create a session
        session = await client.create_session()
        print(f"Session created: {session['session_id']}")
        
        # Chat with a model
        result = await client.chat(
            messages=[{"role": "user", "content": "What is the Model Context Protocol?"}]
        )
        print(f"Response: {result['message']['content']}")

if __name__ == "__main__":
    asyncio.run(main())
```

For synchronous code:

```python
from mcp.mcp_client import MCPSyncClient

with MCPSyncClient() as client:
    # Create a session
    session = client.create_session()
    
    # Get a completion
    result = client.complete(prompt="Explain MCP in one sentence:")
    print(f"Completion: {result['text']}")
```

## License

[MIT License](./LICENSE)
