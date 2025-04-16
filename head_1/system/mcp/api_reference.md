# Context Protocol API Reference

This document provides comprehensive API reference documentation for both the MCP server REST API and the Python client library.

## Table of Contents

- [Server REST API](#server-rest-api)
  - [Session Management](#session-management)
  - [Model Interaction](#model-interaction)
  - [System Information](#system-information)
- [Python Client API](#python-client-api)
  - [MCPClient (Async)](#mcpclient-async)
  - [MCPSyncClient (Sync)](#mcpsyncclient-sync)
- [Data Models](#data-models)
  - [Request Models](#request-models)
  - [Response Models](#response-models)

## Server REST API

All API endpoints use JSON for request and response bodies.

### Session Management

#### Create Session

Creates a new session for model interactions.

**Endpoint**: `POST /api/v1/session`

**Request Body**:
```json
{
  "ttl": 3600,                   // Optional, session time-to-live in seconds
  "session_id": "custom-id-123", // Optional, custom session ID
  "context": {                   // Optional, initial session context
    "key1": "value1",
    "key2": "value2"
  },
  "metadata": {                  // Optional, session metadata
    "source": "web-app",
    "user_id": "user123"
  }
}
```

**Response** (201 Created):
```json
{
  "status": "success",
  "session": {
    "session_id": "session-uuid-123",
    "created_at": "2023-10-15T12:34:56.789Z",
    "last_accessed": "2023-10-15T12:34:56.789Z",
    "ttl": 3600,
    "context": {},
    "metadata": { "source": "web-app", "user_id": "user123" },
    "history_length": 0
  },
  "timestamp": "2023-10-15T12:34:56.789Z"
}
```

#### Get Session

Retrieves information about an existing session.

**Endpoint**: `GET /api/v1/session/{session_id}`

**Response** (200 OK):
```json
{
  "status": "success",
  "session": {
    "session_id": "session-uuid-123",
    "created_at": "2023-10-15T12:34:56.789Z",
    "last_accessed": "2023-10-15T12:35:10.123Z",
    "ttl": 3600,
    "context": {
      "chat_history": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
      ]
    },
    "metadata": { "source": "web-app", "user_id": "user123" },
    "history_length": 1
  },
  "timestamp": "2023-10-15T12:35:15.456Z"
}
```

#### Delete Session

Deletes an existing session.

**Endpoint**: `DELETE /api/v1/session/{session_id}`

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Session session-uuid-123 deleted successfully",
  "timestamp": "2023-10-15T12:36:30.789Z"
}
```

### Model Interaction

#### Completion

Generates a text completion from a prompt.

**Endpoint**: `POST /api/v1/session/{session_id}/complete`

**Request Body**:
```json
{
  "prompt": "Write a poem about AI:",
  "model": "text-davinci-003",   // Optional, defaults to server config
  "temperature": 0.7,            // Optional, provider-specific parameters
  "max_tokens": 100,             // Optional
  "update_context": true         // Optional, whether to update session context
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "result": {
    "text": "In circuits deep where logic sleeps,\nA mind awakes and slowly creeps...",
    "model": "text-davinci-003",
    "usage": {
      "prompt_tokens": 5,
      "completion_tokens": 20,
      "total_tokens": 25
    }
  },
  "processing_time": 0.845,
  "timestamp": "2023-10-15T12:37:45.123Z"
}
```

#### Chat

Conducts a conversational interaction with a chat model.

**Endpoint**: `POST /api/v1/session/{session_id}/chat`

**Request Body**:
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is MCP?"}
  ],
  "model": "gpt-3.5-turbo",       // Optional, defaults to server config
  "temperature": 0.7,              // Optional, provider-specific parameters
  "continue_conversation": true,   // Optional, include previous messages
  "update_context": true,          // Optional, update session context
  "max_history": 10,               // Optional, max history messages to include
  "max_history_size": 50           // Optional, max history size to maintain
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "result": {
    "message": {
      "role": "assistant",
      "content": "MCP (Model Context Protocol) is a unified interface..."
    },
    "model": "gpt-3.5-turbo",
    "usage": {
      "prompt_tokens": 25,
      "completion_tokens": 40,
      "total_tokens": 65
    }
  },
  "processing_time": 1.234,
  "timestamp": "2023-10-15T12:38:30.456Z"
}
```

#### Embedding

Generates vector embeddings for text inputs.

**Endpoint**: `POST /api/v1/session/{session_id}/embedding`

**Request Body**:
```json
{
  "input": "This is a sample text for embedding",  // String or array of strings
  "model": "text-embedding-ada-002",               // Optional, defaults to server config
  "store_in_context": false,                       // Optional, store in session context
  "context_key": "embeddings"                      // Optional, key for context storage
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "result": {
    "data": [
      [0.001, 0.002, ..., 0.999]  // Vector of embeddings (may be multiple)
    ],
    "model": "text-embedding-ada-002",
    "usage": {
      "prompt_tokens": 7,
      "total_tokens": 7
    }
  },
  "processing_time": 0.567,
  "timestamp": "2023-10-15T12:39:15.789Z"
}
```

### System Information

#### List Models

Lists available models from all providers.

**Endpoint**: `GET /api/v1/models`

**Response** (200 OK):
```json
{
  "status": "success",
  "models": {
    "openai_provider": {
      "chat": ["gpt-3.5-turbo", "gpt-4"],
      "completion": ["text-davinci-003", "text-davinci-002"],
      "embedding": ["text-embedding-ada-002"]
    },
    "huggingface_provider": {
      "chat": ["facebook/blenderbot-400M-distill"],
      "completion": ["gpt2", "EleutherAI/gpt-neo-1.3B"],
      "embedding": ["sentence-transformers/all-MiniLM-L6-v2"]
    }
  },
  "provider_types": ["openai_provider", "huggingface_provider"],
  "timestamp": "2023-10-15T12:40:00.123Z"
}
```

#### Server Status

Gets server status information.

**Endpoint**: `GET /api/v1/status`

**Response** (200 OK):
```json
{
  "status": "success",
  "status": {
    "version": "1.0",
    "uptime": {
      "seconds": 3600,
      "formatted": "1:00:00"
    },
    "sessions": {
      "active": 5
    },
    "system": {
      "memory_usage": {
        "rss": 52428800,
        "rss_human": "50.0 MB"
      },
      "cpu_percent": 2.5,
      "platform": "Linux-5.15.0-1015-aws-x86_64-with-glibc2.35",
      "python_version": "3.9.12"
    },
    "providers": ["openai_provider", "huggingface_provider"]
  },
  "timestamp": "2023-10-15T12:41:30.456Z"
}
```

#### Health Check

Simple health check endpoint.

**Endpoint**: `GET /api/v1/health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2023-10-15T12:42:45.789Z"
}
```

#### Metrics

Prometheus metrics for monitoring.

**Endpoint**: `GET /metrics` (on the metrics port)

**Response** (200 OK):
```
# HELP mcp_active_sessions Number of active MCP sessions
# TYPE mcp_active_sessions gauge
mcp_active_sessions 5.0
# HELP mcp_memory_usage_bytes Memory usage of the MCP server
# TYPE mcp_memory_usage_bytes gauge
mcp_memory_usage_bytes 52428800.0
# HELP mcp_requests_total Total number of MCP requests
# TYPE mcp_requests_total counter
mcp_requests_total{endpoint="/api/v1/session",status="success"} 10.0
mcp_requests_total{endpoint="/api/v1/session/{session_id}/chat",status="success"} 25.0
...
```

## Python Client API

### MCPClient (Async)

Asynchronous client for interacting with the MCP server.

#### Constructor

```python
class MCPClient:
    def __init__(
        self, 
        base_url: str = None,       # Server base URL (default: environment or localhost)
        api_version: str = "v1",    # API version
        session_id: str = None,     # Existing session ID (optional)
        default_ttl: int = 3600     # Default session TTL in seconds
    ):
        # ...
```

#### Context Manager Methods

```python
async def __aenter__(self):
    """Enter async context manager."""
    # ...

async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Exit async context manager."""
    # ...
```

#### Session Management Methods

```python
async def create_session(
    self,
    context: Dict[str, Any] = None,    # Initial context
    metadata: Dict[str, Any] = None,   # Session metadata
    ttl: int = None                    # Session TTL (default from constructor)
) -> Dict[str, Any]:
    """Create a new MCP session."""
    # ...

async def get_session(self, session_id: str = None) -> Dict[str, Any]:
    """Get information about a session."""
    # ...

async def delete_session(self, session_id: str = None) -> bool:
    """Delete a session."""
    # ...
```

#### Model Interaction Methods

```python
async def complete(
    self,
    prompt: str,                      # The text prompt
    model: str = "default",           # Model to use
    session_id: str = None,           # Session ID (uses stored session ID if None)
    update_context: bool = False,     # Whether to update session context
    **kwargs                          # Additional provider-specific parameters
) -> Dict[str, Any]:
    """Get a completion from the model."""
    # ...

async def chat(
    self,
    messages: List[Dict[str, str]],    # List of message objects
    model: str = "default",            # Model to use
    session_id: str = None,            # Session ID (uses stored session ID if None)
    continue_conversation: bool = True, # Include previous messages from history
    update_context: bool = True,       # Update session context with results
    max_history: int = 10,             # Maximum history messages to include
    max_history_size: int = 50,        # Maximum total history size to maintain
    **kwargs                           # Additional provider-specific parameters
) -> Dict[str, Any]:
    """Chat with the model."""
    # ...

async def embedding(
    self,
    input_text: Union[str, List[str]], # Text to embed (string or list)
    model: str = "default",            # Model to use
    session_id: str = None,            # Session ID (uses stored session ID if None)
    store_in_context: bool = False,    # Store embeddings in session context
    context_key: str = "embeddings",   # Key for context storage
    **kwargs                           # Additional provider-specific parameters
) -> Dict[str, Any]:
    """Get embeddings from the model."""
    # ...
```

#### System Information Methods

```python
async def list_models(self) -> Dict[str, Any]:
    """List available models."""
    # ...

async def server_status(self) -> Dict[str, Any]:
    """Get server status."""
    # ...
```

### MCPSyncClient (Sync)

Synchronous wrapper around the async client for use in synchronous code.

#### Constructor

```python
class MCPSyncClient:
    def __init__(
        self, 
        base_url: str = None,       # Server base URL (default: environment or localhost)
        api_version: str = "v1",    # API version
        session_id: str = None,     # Existing session ID (optional)
        default_ttl: int = 3600     # Default session TTL in seconds
    ):
        # ...
```

#### Context Manager Methods

```python
def __enter__(self):
    """Enter context manager."""
    # ...

def __exit__(self, exc_type, exc_val, exc_tb):
    """Exit context manager."""
    # ...
```

#### Session Management Methods

```python
def create_session(
    self,
    context: Dict[str, Any] = None,   # Initial context
    metadata: Dict[str, Any] = None,  # Session metadata
    ttl: int = None                   # Session TTL (default from constructor)
) -> Dict[str, Any]:
    """Create a new MCP session."""
    # ...

def get_session(self, session_id: str = None) -> Dict[str, Any]:
    """Get information about a session."""
    # ...

def delete_session(self, session_id: str = None) -> bool:
    """Delete a session."""
    # ...
```

#### Model Interaction Methods

```python
def complete(
    self,
    prompt: str,                      # The text prompt
    model: str = "default",           # Model to use
    session_id: str = None,           # Session ID (uses stored session ID if None)
    update_context: bool = False,     # Whether to update session context
    **kwargs                          # Additional provider-specific parameters
) -> Dict[str, Any]:
    """Get a completion from the model."""
    # ...

def chat(
    self,
    messages: List[Dict[str, str]],    # List of message objects
    model: str = "default",            # Model to use
    session_id: str = None,            # Session ID (uses stored session ID if None)
    continue_conversation: bool = True, # Include previous messages from history
    update_context: bool = True,       # Update session context with results
    max_history: int = 10,             # Maximum history messages to include
    max_history_size: int = 50,        # Maximum total history size to maintain
    **kwargs                           # Additional provider-specific parameters
) -> Dict[str, Any]:
    """Chat with the model."""
    # ...

def embedding(
    self,
    input_text: Union[str, List[str]], # Text to embed (string or list)
    model: str = "default",            # Model to use
    session_id: str = None,            # Session ID (uses stored session ID if None)
    store_in_context: bool = False,    # Store embeddings in session context
    context_key: str = "embeddings",   # Key for context storage
    **kwargs                           # Additional provider-specific parameters
) -> Dict[str, Any]:
    """Get embeddings from the model."""
    # ...
```

#### System Information Methods

```python
def list_models(self) -> Dict[str, Any]:
    """List available models."""
    # ...

def server_status(self) -> Dict[str, Any]:
    """Get server status."""
    # ...
```

## Data Models

### Request Models

#### Session Creation Request

```json
{
  "ttl": 3600,                   // Time-to-live in seconds (optional)
  "session_id": "custom-id-123", // Custom session ID (optional)
  "context": {                   // Initial context (optional)
    "key1": "value1"
  },
  "metadata": {                  // Session metadata (optional)
    "source": "web-app"
  }
}
```

#### Completion Request

```json
{
  "prompt": "Write a poem about AI:",
  "model": "text-davinci-003",   // Model name (optional)
  "temperature": 0.7,            // Temperature parameter (optional)
  "max_tokens": 100,             // Maximum tokens to generate (optional)
  "update_context": true,        // Update session context (optional)
  "stop": ["\n\n", "END"],       // Stop sequences (optional)
  "logprobs": 0,                 // Log probabilities (optional)
  "top_p": 1.0,                  // Nucleus sampling parameter (optional)
  "frequency_penalty": 0.0,      // Frequency penalty (optional)
  "presence_penalty": 0.0        // Presence penalty (optional)
}
```

#### Chat Request

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is MCP?"}
  ],
  "model": "gpt-3.5-turbo",       // Model name (optional)
  "temperature": 0.7,              // Temperature parameter (optional)
  "max_tokens": 100,               // Maximum tokens to generate (optional)
  "continue_conversation": true,   // Include previous messages (optional)
  "update_context": true,          // Update session context (optional)
  "max_history": 10,               // Max history messages to include (optional)
  "max_history_size": 50,          // Max history size to maintain (optional)
  "top_p": 1.0,                    // Nucleus sampling parameter (optional)
  "frequency_penalty": 0.0,        // Frequency penalty (optional)
  "presence_penalty": 0.0          // Presence penalty (optional)
}
```

#### Embedding Request

```json
{
  "input": "This is a sample text", // Text to embed (string or array)
  "model": "text-embedding-ada-002", // Model name (optional)
  "store_in_context": false,        // Store in session context (optional)
  "context_key": "embeddings"       // Key for context storage (optional)
}
```

### Response Models

#### Session Information Response

```json
{
  "status": "success",
  "session": {
    "session_id": "session-uuid-123",
    "created_at": "2023-10-15T12:34:56.789Z",
    "last_accessed": "2023-10-15T12:35:10.123Z",
    "ttl": 3600,
    "context": {
      // Session context data
    },
    "metadata": {
      // Session metadata
    },
    "history_length": 5
  },
  "timestamp": "2023-10-15T12:35:15.456Z"
}
```

#### Completion Response

```json
{
  "status": "success",
  "result": {
    "text": "Generated completion text...",
    "model": "text-davinci-003",
    "usage": {
      "prompt_tokens": 5,
      "completion_tokens": 20,
      "total_tokens": 25
    },
    "context_updates": {           // Optional, if the model updated context
      "key1": "value1"
    }
  },
  "processing_time": 0.845,
  "timestamp": "2023-10-15T12:37:45.123Z"
}
```

#### Chat Response

```json
{
  "status": "success",
  "result": {
    "message": {
      "role": "assistant",
      "content": "Response content from the assistant..."
    },
    "model": "gpt-3.5-turbo",
    "usage": {
      "prompt_tokens": 25,
      "completion_tokens": 40,
      "total_tokens": 65
    }
  },
  "processing_time": 1.234,
  "timestamp": "2023-10-15T12:38:30.456Z"
}
```

#### Embedding Response

```json
{
  "status": "success",
  "result": {
    "data": [
      [0.001, 0.002, ...],  // First embedding vector
      [0.003, 0.004, ...]   // Second embedding vector (if multiple inputs)
    ],
    "model": "text-embedding-ada-002",
    "usage": {
      "prompt_tokens": 7,
      "total_tokens": 7
    }
  },
  "processing_time": 0.567,
  "timestamp": "2023-10-15T12:39:15.789Z"
}
```

#### Models List Response

```json
{
  "status": "success",
  "models": {
    "openai_provider": {
      "chat": ["gpt-3.5-turbo", "gpt-4"],
      "completion": ["text-davinci-003", "text-davinci-002"],
      "embedding": ["text-embedding-ada-002"]
    },
    "huggingface_provider": {
      "chat": ["facebook/blenderbot-400M-distill"],
      "completion": ["gpt2", "EleutherAI/gpt-neo-1.3B"],
      "embedding": ["sentence-transformers/all-MiniLM-L6-v2"]
    }
  },
  "provider_types": ["openai_provider", "huggingface_provider"],
  "timestamp": "2023-10-15T12:40:00.123Z"
}
```

#### Error Response

```json
{
  "status": "error",
  "error": {
    "type": "ValidationError",
    "message": "Missing required field: messages",
    "code": 400
  },
  "timestamp": "2023-10-15T12:45:30.789Z"
}
```

## Status Codes

| Code | Description |
|------|-------------|
| 200  | OK - Request successful |
| 201  | Created - Resource created successfully |
| 400  | Bad Request - Invalid request format or parameters |
| 401  | Unauthorized - Authentication required |
| 404  | Not Found - Resource not found |
| 500  | Internal Server Error - Server-side error |
| 501  | Not Implemented - Feature not available |
| 503  | Service Unavailable - Server temporarily unavailable |
