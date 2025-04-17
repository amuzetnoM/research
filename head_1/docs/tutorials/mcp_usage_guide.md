# Model Context Protocol (MCP) Usage Guide

This guide walks through the process of setting up and deploying the Model Context Protocol (MCP) server. 

## Prerequisites

Before installing MCP, ensure you have the following:

- Python 3.8 or higher
- pip (Python package manager)
- Access to at least one AI model provider (OpenAI, HuggingFace, etc.)
- API keys for your chosen model providers

## Installation Options

There are several ways to install and deploy MCP:

### Option 1: Direct Installation

```bash
# Clone the repository
git clone https://github.com/your-org/mcp.git
cd mcp

# Install dependencies
pip install -r requirements.txt

# Create configuration
python -m mcp.mcp_integrator --config-only
```

### Option 2: Using MCP Integrator

The MCP Integrator automates the process of integrating MCP with your existing systems:

```bash
# Install MCP and dependencies
pip install aiohttp prometheus_client psutil

# Run the integrator (safe mode first to see what would change)
python -m mcp.mcp_integrator --safe-mode

# Run the actual integration
python -m mcp.mcp_integrator
```

### Option 3: Docker Installation

```bash
# Clone the repository
git clone https://github.com/your-org/mcp.git
cd mcp

# Build the Docker image
docker build -t mcp-server .

# Run the container
docker run -p 8080:8080 -p 8081:8081 -v ./config:/app/config mcp-server
```

## Configuration

MCP is configured through a JSON configuration file located at `config/config.json`:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "metrics_port": 8081,
    "log_level": "INFO",
    "cors_origins": ["*"]
  },
  "session": {
    "default_ttl": 3600,
    "cleanup_interval": 300
  },
  "providers": {
    "default_completion": "openai_provider",
    "default_chat": "openai_provider",
    "default_embedding": "openai_provider",
    "enabled_providers": ["openai_provider", "huggingface_provider"]
  }
}
```

### Configuration Options

#### Server Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `host` | IP address to bind the server | `0.0.0.0` |
| `port` | Port for the main API server | `8080` |
| `metrics_port` | Port for Prometheus metrics | `8081` |
| `log_level` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `cors_origins` | List of allowed CORS origins | `["*"]` |

#### Session Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `default_ttl` | Default session time-to-live in seconds | `3600` |
| `cleanup_interval` | Interval for cleaning up expired sessions | `300` |

#### Provider Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `default_completion` | Default provider for completion requests | `openai_provider` |
| `default_chat` | Default provider for chat requests | `openai_provider` |
| `default_embedding` | Default provider for embedding requests | `openai_provider` |
| `enabled_providers` | List of enabled provider modules | `["openai_provider"]` |

## Setting Up Model Providers

### OpenAI Provider

To use the OpenAI provider, set your API key in the environment:

```bash
# Linux/macOS
export OPENAI_API_KEY="your-api-key"

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key

# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-api-key"
```

Or add it to the provider configuration in `providers/openai_provider.py`.

### HuggingFace Provider

To use the HuggingFace provider, set your API key in the environment:

```bash
# Linux/macOS
export HUGGINGFACE_API_KEY="your-api-key"

# Windows (Command Prompt)
set HUGGINGFACE_API_KEY=your-api-key

# Windows (PowerShell)
$env:HUGGINGFACE_API_KEY = "your-api-key"
```

### Custom Provider

To create a custom provider:

1. Create a new file in the `providers` directory (e.g., `my_provider.py`)
2. Implement the provider class following the provider interface
3. Add the provider to `enabled_providers` in your configuration

Example custom provider:

```python
import os
from typing import Dict, Any, List, Optional

class MyCustomProvider:
    """Custom model provider for MCP."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("CUSTOM_API_KEY")
        if not self.api_key:
            raise ValueError("Custom API key is required")
        
        # Initialize API client or other resources
        
    async def __call__(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a model request."""
        request_type = request.get("type", "completion")
        
        if request_type == "chat":
            # Handle chat request
            return {
                "message": {"role": "assistant", "content": "Your chat response"},
                "usage": {"total_tokens": 0}
            }
        elif request_type == "completion":
            # Handle completion request
            return {
                "text": "Your completion response",
                "usage": {"total_tokens": 0}
            }
        elif request_type == "embedding":
            # Handle embedding request
            return {
                "data": [[0.1, 0.2, 0.3]],  # Example embedding vector
                "usage": {"total_tokens": 0}
            }
        else:
            raise ValueError(f"Unsupported request type: {request_type}")
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models."""
        return {
            "chat": ["my-chat-model"],
            "completion": ["my-completion-model"],
            "embedding": ["my-embedding-model"]
        }

# Create an instance of the provider
provider = MyCustomProvider()
```

## Running the Server

### Manual Start

```bash
# Run the server with default configuration
python -m mcp.run_mcp_server

# Specify a custom configuration file
python -m mcp.run_mcp_server --config path/to/config.json
```

### Using a Service Manager (systemd)

Create a systemd service file:

```ini
[Unit]
Description=MCP Server
After=network.target

[Service]
User=mcp
WorkingDirectory=/path/to/mcp
ExecStart=/usr/bin/python -m mcp.run_mcp_server
Restart=on-failure
Environment=PYTHONPATH=/path/to/mcp

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable mcp.service
sudo systemctl start mcp.service
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3'

services:
  mcp:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
      - "8081:8081"
    volumes:
      - ./config:/app/config
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}
    restart: unless-stopped
```

Start the service:

```bash
docker-compose up -d
```

## Verifying Installation

Test that the server is running properly:

```bash
# Check the API server
curl http://localhost:8080/api/v1/health

# Check the metrics server
curl http://localhost:8081/metrics
```

You should see a valid JSON response from the health endpoint and Prometheus metrics from the metrics endpoint.

## Integrating with Existing Web Servers

The MCP Integrator can automatically add MCP routes to your existing web servers. Supported frameworks:

- aiohttp
- Flask
- FastAPI

Run the integrator to detect and modify your server files:

```bash
python -m mcp.mcp_integrator --integration-only
```

This will analyze your server files and add MCP integration code where appropriate.

## Securing Your MCP Installation

For production deployments, consider the following security measures:

1. **Use HTTPS**: Configure TLS certificates for your server
2. **Restrict CORS**: Set specific allowed origins in the configuration
3. **Add Authentication**: Implement an authentication middleware
4. **Secure API Keys**: Use environment variables or a secret management system
5. **Rate Limiting**: Add rate limiting middleware to prevent abuse

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check Python version (3.8+ required)
   - Verify all dependencies are installed
   - Ensure the port is not in use

2. **Provider errors**
   - Verify API keys are correctly set
   - Check network connectivity to provider APIs
   - Look for rate limiting or quota issues

3. **Performance issues**
   - Increase the number of worker processes
   - Optimize session cleanup interval
   - Consider using a load balancer for high-volume deployments

### Logging

MCP uses Python's logging system. To increase log verbosity:

```json
{
  "server": {
    "log_level": "DEBUG"
  }
}
```

Logs will be output to standard output and can be redirected to a file if needed.

## Next Steps

- [Usage Guide](./usage.md) - Learn how to use the MCP client
- [Architecture Guide](./architecture.md) - Understand the system architecture
- [API Reference](./api_reference.md) - Complete API reference documentation


# MCP Installation Guide

## Installation

```bash
# If you've installed MCP in your Python environment
pip install -e path/to/mcp

# Alternatively, make sure the MCP directory is in your Python path
export PYTHONPATH=$PYTHONPATH:/path/to/mcp
```

## Basic Concepts

Before diving into code examples, it's important to understand the core concepts of MCP:

1. **Sessions**: All interactions happen within a session context
2. **Context**: Sessions maintain state across requests, including history and embeddings
3. **Model Types**: MCP supports chat, completion, and embedding models
4. **Providers**: Different AI providers can be used interchangeably

## Importing the Client

```python
# For asynchronous code
from mcp.mcp_client import MCPClient

# For synchronous code
from mcp.mcp_client import MCPSyncClient
```

## Client Configuration

The client can be configured through constructor parameters or environment variables:

```python
# Using constructor parameters
client = MCPClient(
    base_url="http://localhost:8080",  # Server URL
    api_version="v1",                  # API version
    session_id=None,                   # Optional existing session ID
    default_ttl=3600                   # Default session TTL in seconds
)

# Using environment variables
os.environ["MCP_SERVER_URL"] = "http://localhost:8080"
client = MCPClient()  # Will use the environment variable
```

## Asynchronous Usage

### Context Manager Pattern (Recommended)

```python
import asyncio
from mcp.mcp_client import MCPClient

async def main():
    # The context manager handles session cleanup
    async with MCPClient() as client:
        # Create a session
        session = await client.create_session()
        print(f"Session created: {session['session_id']}")
        
        # Use the session for various operations
        chat_result = await client.chat(
            messages=[{"role": "user", "content": "Hello, world!"}]
        )
        print(f"Response: {chat_result['message']['content']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Manual Session Management

```python
import asyncio
from mcp.mcp_client import MCPClient

async def main():
    client = MCPClient()
    
    try:
        # Create a session manually
        session = await client.create_session(
            context={"user_info": {"name": "Alice"}},  # Initial context
            metadata={"source": "example"},            # Session metadata
            ttl=7200                                   # Custom TTL (2 hours)
        )
        session_id = session["session_id"]
        
        # Use the session for interactions
        result = await client.complete(
            prompt="Write a poem about AI:",
            session_id=session_id
        )
        print(f"Completion: {result['text']}")
        
        # Get session information
        session_info = await client.get_session(session_id)
        print(f"Session context: {session_info['context']}")
        
        # Clean up when done
        await client.delete_session(session_id)
    finally:
        # Clean up the client
        await client._aiohttp_session.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Synchronous Usage

### Context Manager Pattern (Recommended)

```python
from mcp.mcp_client import MCPSyncClient

def main():
    # The context manager handles event loop and cleanup
    with MCPSyncClient() as client:
        # Create a session
        session = client.create_session()
        print(f"Session created: {session['session_id']}")
        
        # Use the session for various operations
        chat_result = client.chat(
            messages=[{"role": "user", "content": "Hello, world!"}]
        )
        print(f"Response: {chat_result['message']['content']}")

if __name__ == "__main__":
    main()
```

### Manual Session Management

```python
from mcp.mcp_client import MCPSyncClient

def main():
    client = MCPSyncClient()
    
    try:
        # Create a session manually
        session = client.create_session()
        session_id = session["session_id"]
        
        # Use the session for interactions
        result = client.complete(
            prompt="Write a poem about AI:",
            session_id=session_id
        )
        print(f"Completion: {result['text']}")
        
        # Clean up when done
        client.delete_session(session_id)
    finally:
        # No explicit cleanup needed for the sync client
        pass

if __name__ == "__main__":
    main()
```

## Working with Chat Models

Chat models use a message-based interface:

```python
async with MCPClient() as client:
    session = await client.create_session()
    
    # Single message
    result = await client.chat(
        messages=[{"role": "user", "content": "What is MCP?"}]
    )
    print(f"Response: {result['message']['content']}")
    
    # Multi-turn conversation (the context is maintained automatically)
    result = await client.chat(
        messages=[{"role": "user", "content": "Can you give me an example?"}],
        continue_conversation=True  # Include previous messages from context
    )
    print(f"Response: {result['message']['content']}")
    
    # Advanced options
    result = await client.chat(
        messages=[{"role": "user", "content": "Summarize our conversation"}],
        model="gpt-4",              # Specify a different model
        temperature=0.7,            # Control randomness (provider-specific)
        max_tokens=500,             # Limit response length (provider-specific)
        continue_conversation=True, # Include conversation history
        update_context=True,        # Update session context with this exchange
        max_history=10,             # Maximum number of history messages to include
        max_history_size=50         # Maximum total history size to maintain
    )
```

## Working with Completion Models

Completion models use a prompt-based interface:

```python
async with MCPClient() as client:
    session = await client.create_session()
    
    # Basic completion
    result = await client.complete(
        prompt="Write a haiku about programming:"
    )
    print(f"Completion: {result['text']}")
    
    # Advanced options
    result = await client.complete(
        prompt="Explain quantum computing in simple terms:",
        model="text-davinci-003",   # Specify a different model
        temperature=0.5,            # Control randomness (provider-specific)
        max_tokens=200,             # Limit response length (provider-specific)
        update_context=True         # Update session context with this exchange
    )
```

## Working with Embedding Models

Embedding models convert text to vector representations:

```python
async with MCPClient() as client:
    session = await client.create_session()
    
    # Single text embedding
    result = await client.embedding(
        input_text="This is a sample text for embedding"
    )
    print(f"Embedding dimension: {len(result['data'][0])}")
    
    # Multiple text embeddings
    result = await client.embedding(
        input_text=[
            "First document to embed",
            "Second document to embed",
            "Third document to embed"
        ]
    )
    print(f"Number of embeddings: {len(result['data'])}")
    
    # Store embeddings in context for later use
    result = await client.embedding(
        input_text="Important information to remember",
        store_in_context=True,      # Save in session context
        context_key="knowledge_base" # Custom context key for storage
    )
    
    # Retrieve session to check stored embeddings
    session_info = await client.get_session()
    print(f"Stored embeddings: {session_info['context']['knowledge_base']}")
```

## Managing Server Information

### Listing Available Models

```python
async with MCPClient() as client:
    # Get information about available models
    models = await client.list_models()
    
    print("Available models:")
    for provider_type, provider_models in models["models"].items():
        print(f"  {provider_type}:")
        for model_type, model_list in provider_models.items():
            print(f"    {model_type}: {model_list}")
```

### Getting Server Status

```python
async with MCPClient() as client:
    # Get server status information
    status = await client.server_status()
    
    print(f"Server version: {status['version']}")
    print(f"Uptime: {status['uptime']['formatted']}")
    print(f"Active sessions: {status['sessions']['active']}")
    print(f"Available providers: {status['providers']}")
```

## Error Handling

The MCP client raises exceptions for various error conditions:

```python
from mcp.mcp_client import MCPClient

async def main():
    try:
        async with MCPClient() as client:
            # Handling connection errors
            try:
                session = await client.create_session()
            except Exception as e:
                print(f"Connection error: {e}")
                return
            
            # Handling API errors
            try:
                result = await client.chat(
                    messages=[{"invalid": "format"}]  # Invalid format
                )
            except Exception as e:
                print(f"API error: {e}")
            
            # Handling missing session
            try:
                await client.get_session("non-existent-session-id")
            except ValueError as e:
                print(f"Session error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Integration Patterns

### Web Application Integration

```python
# Flask example
from flask import Flask, request, jsonify
from mcp.mcp_client import MCPSyncClient

app = Flask(__name__)
mcp_client = MCPSyncClient()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id')
    
    # Create a session if needed
    if not session_id:
        session = mcp_client.create_session()
        session_id = session['session_id']
    
    # Process the chat request
    result = mcp_client.chat(
        messages=[{"role": "user", "content": user_message}],
        session_id=session_id
    )
    
    return jsonify({
        "response": result['message']['content'],
        "session_id": session_id
    })
```

### Async Web Application Integration

```python
# FastAPI example
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp.mcp_client import MCPClient

app = FastAPI()
client = None

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@app.on_event("startup")
async def startup():
    global client
    client = MCPClient()

@app.on_event("shutdown")
async def shutdown():
    if client and client._aiohttp_session:
        await client._aiohttp_session.close()

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Create a session if needed
        session_id = request.session_id
        if not session_id:
            session = await client.create_session()
            session_id = session['session_id']
        
        # Process the chat request
        result = await client.chat(
            messages=[{"role": "user", "content": request.message}],
            session_id=session_id
        )
        
        return ChatResponse(
            response=result['message']['content'],
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Batching Requests

For efficiency, you can batch multiple operations:

```python
async def process_batch(client, inputs):
    # Create a single session for the batch
    session = await client.create_session()
    session_id = session['session_id']
    
    results = []
    for input_text in inputs:
        result = await client.complete(
            prompt=input_text,
            session_id=session_id
        )
        results.append(result['text'])
    
    # Clean up the session when done
    await client.delete_session(session_id)
    return results

async def main():
    async with MCPClient() as client:
        inputs = [
            "Explain AI in one sentence:",
            "Write a haiku about programming:",
            "Give me a fun fact about space:"
        ]
        
        batch_results = await process_batch(client, inputs)
        for input_text, result in zip(inputs, batch_results):
            print(f"Input: {input_text}")
            print(f"Result: {result}\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Advanced Usage

### Custom Contexts

Sessions can store arbitrary context information:

```python
async with MCPClient() as client:
    # Create session with initial context
    session = await client.create_session(
        context={
            "user_profile": {
                "name": "Alice",
                "preferences": ["science", "technology"],
                "expertise_level": "intermediate"
            },
            "conversation_goal": "learning about quantum computing"
        }
    )
    
    # The context will influence how the model responds
    result = await client.chat(
        messages=[{"role": "user", "content": "Explain this topic to me"}]
    )
```

### Multiple Sessions for Different Contexts

You can maintain multiple sessions for different contexts:

```python
async with MCPClient() as client:
    # Technical session
    tech_session = await client.create_session(
        context={"domain": "technical", "style": "detailed"}
    )
    tech_id = tech_session['session_id']
    
    # Creative session
    creative_session = await client.create_session(
        context={"domain": "creative", "style": "imaginative"}
    )
    creative_id = creative_session['session_id']
    
    # Same prompt, different contexts
    prompt = "Tell me about the stars"
    
    tech_result = await client.complete(
        prompt=prompt,
        session_id=tech_id
    )
    
    creative_result = await client.complete(
        prompt=prompt,
        session_id=creative_id
    )
    
    print("Technical response:")
    print(tech_result['text'])
    print("\nCreative response:")
    print(creative_result['text'])
```

### Using Custom Model Providers

If you've configured custom model providers on the server:

```python
async with MCPClient() as client:
    # Specify a custom model from a specific provider
    result = await client.chat(
        messages=[{"role": "user", "content": "Hello"}],
        model="custom-provider/my-specialized-model"
    )
```

## Performance Considerations

1. **Reuse Sessions**: Creating new sessions for every request is inefficient
2. **Manage Context Size**: Large contexts consume more memory and tokens
3. **Use Async for Concurrency**: The async client can handle multiple simultaneous requests
4. **Connection Pooling**: The client automatically pools connections
5. **Clean Up Unused Sessions**: Delete sessions when they're no longer needed

## Best Practices

1. **Use Context Managers**: They handle proper cleanup of resources
2. **Handle Errors Gracefully**: Implement proper error handling
3. **Set Appropriate TTLs**: Match session lifetime to your use case
4. **Monitor Usage**: Keep track of token usage and response times
5. **Secure API Keys**: Never expose provider API keys in client-side code
6. **Version Your Sessions**: Consider adding version information to session metadata
7. **Document Context Structure**: Maintain documentation of your context structure
8. **Implement Fallbacks**: Have backup strategies for when the API is unavailable

## Next Steps

- [API Reference](./api_reference.md) - Detailed API documentation
- [Architecture Guide](./architecture.md) - Understand the system architecture
- [Setup Guide](./setup.md) - Server setup instructions
