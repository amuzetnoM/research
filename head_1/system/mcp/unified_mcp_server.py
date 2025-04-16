"""
Unified Model Context Protocol (MCP) Server Implementation

This module provides a comprehensive implementation of the Model Context Protocol,
integrating capabilities from various server implementations to provide:
- Context-aware model interactions
- Stateful sessions
- Protocol-based interchange formats
- Auto-configuration capabilities
- Built-in monitoring and diagnostics
"""

import asyncio
import base64
import datetime
import hashlib
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Awaitable

import aiohttp
from aiohttp import web
import aiohttp_cors
import psutil
import prometheus_client
from prometheus_client import Counter, Gauge, Histogram

# Configure logger
logger = logging.getLogger("mcp-server")

# Define MCP protocol constants
MCP_VERSION = "1.0"
MCP_STATUS_SUCCESS = "success"
MCP_STATUS_ERROR = "error"

# Define metrics
REQUEST_COUNT = Counter('mcp_requests_total', 'Total number of MCP requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('mcp_request_duration_seconds', 'Request latency in seconds', ['endpoint'])
MODEL_TOKENS_PROCESSED = Counter('mcp_tokens_processed_total', 'Total tokens processed', ['model', 'operation'])
ACTIVE_SESSIONS = Gauge('mcp_active_sessions', 'Number of active MCP sessions')
MEMORY_USAGE = Gauge('mcp_memory_usage_bytes', 'Memory usage of the MCP server')

class MCPSession:
    """Represents a stateful MCP session with context tracking."""
    
    def __init__(self, session_id: str = None, ttl: int = 3600):
        """Initialize a new MCP session.
        
        Args:
            session_id: Optional session ID (generated if not provided)
            ttl: Time-to-live in seconds for this session (default: 1 hour)
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.last_accessed = self.created_at
        self.ttl = ttl
        self.context: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        
    def update_last_accessed(self):
        """Update the last_accessed timestamp."""
        self.last_accessed = datetime.datetime.now()
        
    def is_expired(self) -> bool:
        """Check if this session has expired.
        
        Returns:
            True if the session has expired, False otherwise
        """
        elapsed = (datetime.datetime.now() - self.last_accessed).total_seconds()
        return elapsed > self.ttl
        
    def add_to_history(self, entry: Dict[str, Any]):
        """Add an entry to the session history.
        
        Args:
            entry: The history entry to add
        """
        self.history.append({
            **entry,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the session to a dictionary.
        
        Returns:
            Dictionary representation of the session
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "context": self.context,
            "history_length": len(self.history),
            "metadata": self.metadata
        }


class MCPSessionManager:
    """Manages MCP sessions and their lifecycle."""
    
    def __init__(self, cleanup_interval: int = 300):
        """Initialize the session manager.
        
        Args:
            cleanup_interval: Interval in seconds for cleanup of expired sessions
        """
        self.sessions: Dict[str, MCPSession] = {}
        self.cleanup_interval = cleanup_interval
        self.cleanup_task = None
        
    async def start(self):
        """Start the session manager and its cleanup task."""
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
    async def stop(self):
        """Stop the session manager and its cleanup task."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
                
    async def _cleanup_loop(self):
        """Background task to clean up expired sessions."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self._cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                
    def _cleanup_expired_sessions(self):
        """Remove expired sessions."""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired_sessions:
            logger.debug(f"Removing expired session: {session_id}")
            del self.sessions[session_id]
            
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            # Update metrics
            ACTIVE_SESSIONS.set(len(self.sessions))
            
    def create_session(self, session_id: Optional[str] = None, ttl: int = 3600) -> MCPSession:
        """Create a new session.
        
        Args:
            session_id: Optional custom session ID
            ttl: Time-to-live in seconds
            
        Returns:
            The newly created session
        """
        session = MCPSession(session_id=session_id, ttl=ttl)
        self.sessions[session.session_id] = session
        
        # Update metrics
        ACTIVE_SESSIONS.set(len(self.sessions))
        
        return session
        
    def get_session(self, session_id: str) -> Optional[MCPSession]:
        """Get a session by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            The session if found, None otherwise
        """
        session = self.sessions.get(session_id)
        if session:
            if session.is_expired():
                del self.sessions[session_id]
                return None
            session.update_last_accessed()
        return session
        
    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            True if the session was deleted, False if it didn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            # Update metrics
            ACTIVE_SESSIONS.set(len(self.sessions))
            return True
        return False


class UnifiedMCPServer:
    """Unified MCP server implementation integrating multiple capabilities."""
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        cors_origins: List[str] = None,
        metrics_port: int = 8081,
        log_level: str = "INFO",
        model_providers: Dict[str, Callable] = None
    ):
        """Initialize the unified MCP server.
        
        Args:
            host: Host IP to bind to
            port: Port to listen on
            cors_origins: List of allowed CORS origins
            metrics_port: Port for exposing Prometheus metrics
            log_level: Logging level
            model_providers: Dictionary mapping model types to provider functions
        """
        # Server configuration
        self.host = host
        self.port = port
        self.metrics_port = metrics_port
        self.cors_origins = cors_origins or ["*"]
        
        # Configure logging
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {log_level}")
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Application state
        self.app = web.Application()
        self.metrics_app = web.Application()
        self.session_manager = MCPSessionManager()
        self.model_providers = model_providers or {}
        self.start_time = datetime.datetime.now()
        
        # Setup server
        self._setup_routes()
        self._setup_cors()
        self._setup_metrics()
        
    def _setup_routes(self):
        """Configure the server routes."""
        # API routes
        self.app.add_routes([
            web.post('/api/v1/session', self.create_session),
            web.get('/api/v1/session/{session_id}', self.get_session),
            web.delete('/api/v1/session/{session_id}', self.delete_session),
            web.post('/api/v1/session/{session_id}/complete', self.complete),
            web.post('/api/v1/session/{session_id}/chat', self.chat),
            web.post('/api/v1/session/{session_id}/embedding', self.embedding),
            web.get('/api/v1/models', self.list_models),
            web.get('/api/v1/status', self.server_status),
            web.get('/api/v1/health', self.health_check),
        ])
        
        # Metrics routes
        self.metrics_app.add_routes([
            web.get('/metrics', self.metrics),
            web.get('/health', self.health_check),
        ])
        
    def _setup_cors(self):
        """Configure CORS for the API."""
        cors = aiohttp_cors.setup(self.app, defaults={
            origin: aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            ) for origin in self.cors_origins
        })
        
        # Apply CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
            
    def _setup_metrics(self):
        """Configure Prometheus metrics."""
        # Server metrics updates
        async def update_server_metrics():
            while True:
                try:
                    process = psutil.Process(os.getpid())
                    memory_info = process.memory_info()
                    MEMORY_USAGE.set(memory_info.rss)
                    await asyncio.sleep(15)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error updating metrics: {e}")
                    await asyncio.sleep(60)  # Retry after a longer interval
                    
        asyncio.create_task(update_server_metrics())
        
    async def start(self):
        """Start the MCP server."""
        # Start the session manager
        await self.session_manager.start()
        
        # Start the metrics server
        metrics_runner = web.AppRunner(self.metrics_app)
        await metrics_runner.setup()
        metrics_site = web.TCPSite(metrics_runner, self.host, self.metrics_port)
        await metrics_site.start()
        logger.info(f"Metrics server started on http://{self.host}:{self.metrics_port}")
        
        # Start the main API server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"MCP server started on http://{self.host}:{self.port}")
        
        return runner, metrics_runner
        
    async def stop(self):
        """Stop the MCP server."""
        await self.session_manager.stop()
        
    def register_model_provider(self, model_type: str, provider_func: Callable):
        """Register a model provider function.
        
        Args:
            model_type: The type of model (e.g., 'completion', 'chat', 'embedding')
            provider_func: Function that handles model requests
        """
        self.model_providers[model_type] = provider_func
        logger.info(f"Registered model provider for {model_type}")
        
    @web.middleware
    async def error_middleware(self, request, handler):
        """Middleware to handle exceptions and provide consistent error responses."""
        try:
            return await handler(request)
        except web.HTTPException as ex:
            return web.json_response({
                "status": MCP_STATUS_ERROR,
                "error": {
                    "type": ex.__class__.__name__,
                    "message": str(ex),
                    "code": ex.status
                }
            }, status=ex.status)
        except Exception as e:
            logger.exception("Unexpected error")
            return web.json_response({
                "status": MCP_STATUS_ERROR,
                "error": {
                    "type": "InternalServerError",
                    "message": str(e),
                    "code": 500
                }
            }, status=500)
            
    def _generate_response(self, data: Dict[str, Any], status_code: int = 200) -> web.Response:
        """Generate a consistent JSON response.
        
        Args:
            data: Response data
            status_code: HTTP status code
            
        Returns:
            JSON response
        """
        response_data = {
            "status": MCP_STATUS_SUCCESS,
            **data,
            "timestamp": datetime.datetime.now().isoformat()
        }
        return web.json_response(response_data, status=status_code)
        
    def _error_response(
        self, 
        message: str, 
        error_type: str = "BadRequest", 
        status_code: int = 400
    ) -> web.Response:
        """Generate a consistent error response.
        
        Args:
            message: Error message
            error_type: Type of error
            status_code: HTTP status code
            
        Returns:
            JSON error response
        """
        return web.json_response({
            "status": MCP_STATUS_ERROR,
            "error": {
                "type": error_type,
                "message": message,
                "code": status_code
            },
            "timestamp": datetime.datetime.now().isoformat()
        }, status=status_code)
        
    # API Route handlers
    async def create_session(self, request: web.Request) -> web.Response:
        """Create a new MCP session.
        
        Args:
            request: HTTP request
            
        Returns:
            JSON response with session information
        """
        with REQUEST_LATENCY.labels('/api/v1/session').time():
            try:
                data = await request.json()
            except json.JSONDecodeError:
                data = {}
                
            ttl = int(data.get('ttl', 3600))
            session_id = data.get('session_id')
            
            session = self.session_manager.create_session(session_id=session_id, ttl=ttl)
            
            # Apply initial context if provided
            if 'context' in data and isinstance(data['context'], dict):
                session.context.update(data['context'])
                
            # Apply metadata if provided
            if 'metadata' in data and isinstance(data['metadata'], dict):
                session.metadata.update(data['metadata'])
                
            REQUEST_COUNT.labels('/api/v1/session', 'success').inc()
            return self._generate_response({
                "session": session.to_dict()
            }, 201)
        
    async def get_session(self, request: web.Request) -> web.Response:
        """Get information about an existing session.
        
        Args:
            request: HTTP request
            
        Returns:
            JSON response with session information
        """
        with REQUEST_LATENCY.labels('/api/v1/session/{session_id}').time():
            session_id = request.match_info['session_id']
            session = self.session_manager.get_session(session_id)
            
            if not session:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}', 'error').inc()
                return self._error_response(
                    f"Session not found: {session_id}", 
                    "SessionNotFound", 
                    404
                )
                
            REQUEST_COUNT.labels('/api/v1/session/{session_id}', 'success').inc()
            return self._generate_response({
                "session": session.to_dict()
            })
        
    async def delete_session(self, request: web.Request) -> web.Response:
        """Delete an existing session.
        
        Args:
            request: HTTP request
            
        Returns:
            JSON response confirming deletion
        """
        with REQUEST_LATENCY.labels('/api/v1/session/{session_id}').time():
            session_id = request.match_info['session_id']
            success = self.session_manager.delete_session(session_id)
            
            if not success:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}', 'error').inc()
                return self._error_response(
                    f"Session not found: {session_id}", 
                    "SessionNotFound", 
                    404
                )
                
            REQUEST_COUNT.labels('/api/v1/session/{session_id}', 'success').inc()
            return self._generate_response({
                "message": f"Session {session_id} deleted successfully"
            })
            
    async def complete(self, request: web.Request) -> web.Response:
        """Handle a completion request.
        
        Args:
            request: HTTP request
            
        Returns:
            JSON response with completion result
        """
        with REQUEST_LATENCY.labels('/api/v1/session/{session_id}/complete').time():
            session_id = request.match_info['session_id']
            session = self.session_manager.get_session(session_id)
            
            if not session:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/complete', 'error').inc()
                return self._error_response(
                    f"Session not found: {session_id}", 
                    "SessionNotFound", 
                    404
                )
                
            try:
                data = await request.json()
            except json.JSONDecodeError:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/complete', 'error').inc()
                return self._error_response("Invalid JSON request body")
                
            # Validate request
            if 'prompt' not in data:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/complete', 'error').inc()
                return self._error_response("Missing required field: prompt")
                
            model = data.get('model', 'default')
            
            # Check if we have a provider for completions
            if 'completion' not in self.model_providers:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/complete', 'error').inc()
                return self._error_response(
                    "No completion model provider registered",
                    "ProviderNotAvailable",
                    501
                )
                
            # Enrich request with session context
            enriched_request = {
                **data,
                "session_context": session.context
            }
            
            # Process the completion
            try:
                start_time = time.time()
                completion_result = await self.model_providers['completion'](enriched_request)
                processing_time = time.time() - start_time
                
                # Update metrics
                MODEL_TOKENS_PROCESSED.labels(model, 'completion').inc(
                    completion_result.get('usage', {}).get('total_tokens', 0)
                )
                
                # Add to session history
                history_entry = {
                    "type": "completion",
                    "request": data,
                    "response": completion_result,
                    "processing_time": processing_time
                }
                session.add_to_history(history_entry)
                
                # Update context with completion result if requested
                if data.get('update_context', False):
                    context_updates = completion_result.get('context_updates', {})
                    if context_updates:
                        session.context.update(context_updates)
                        
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/complete', 'success').inc()
                return self._generate_response({
                    "result": completion_result,
                    "processing_time": processing_time
                })
                
            except Exception as e:
                logger.exception("Error processing completion")
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/complete', 'error').inc()
                return self._error_response(
                    f"Error processing completion: {str(e)}",
                    "CompletionError",
                    500
                )
                
    async def chat(self, request: web.Request) -> web.Response:
        """Handle a chat request.
        
        Args:
            request: HTTP request
            
        Returns:
            JSON response with chat result
        """
        with REQUEST_LATENCY.labels('/api/v1/session/{session_id}/chat').time():
            session_id = request.match_info['session_id']
            session = self.session_manager.get_session(session_id)
            
            if not session:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/chat', 'error').inc()
                return self._error_response(
                    f"Session not found: {session_id}", 
                    "SessionNotFound", 
                    404
                )
                
            try:
                data = await request.json()
            except json.JSONDecodeError:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/chat', 'error').inc()
                return self._error_response("Invalid JSON request body")
                
            # Validate request
            if 'messages' not in data or not isinstance(data['messages'], list):
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/chat', 'error').inc()
                return self._error_response("Missing or invalid required field: messages")
                
            model = data.get('model', 'default')
            
            # Check if we have a provider for chat
            if 'chat' not in self.model_providers:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/chat', 'error').inc()
                return self._error_response(
                    "No chat model provider registered",
                    "ProviderNotAvailable",
                    501
                )
                
            # Get previous messages from history if this is a continuing conversation
            if data.get('continue_conversation', False) and 'chat_history' in session.context:
                # Prepend previous messages from context, respecting max history if specified
                max_history = data.get('max_history', 10)
                history_messages = session.context.get('chat_history', [])[-max_history:]
                
                # Only add history if it's not empty
                if history_messages:
                    data['messages'] = history_messages + data['messages']
                    
            # Enrich request with session context
            enriched_request = {
                **data,
                "session_context": session.context
            }
            
            # Process the chat request
            try:
                start_time = time.time()
                chat_result = await self.model_providers['chat'](enriched_request)
                processing_time = time.time() - start_time
                
                # Update metrics
                MODEL_TOKENS_PROCESSED.labels(model, 'chat').inc(
                    chat_result.get('usage', {}).get('total_tokens', 0)
                )
                
                # Add to session history
                history_entry = {
                    "type": "chat",
                    "request": data,
                    "response": chat_result,
                    "processing_time": processing_time
                }
                session.add_to_history(history_entry)
                
                # Update context with chat history if requested
                if data.get('update_context', True):
                    # Initialize chat history if it doesn't exist
                    if 'chat_history' not in session.context:
                        session.context['chat_history'] = []
                        
                    # Add the new message exchanges to history
                    for message in data['messages']:
                        # Only add messages that aren't already in history
                        if message not in session.context['chat_history']:
                            session.context['chat_history'].append(message)
                            
                    # Add the response to history
                    if 'message' in chat_result:
                        session.context['chat_history'].append(chat_result['message'])
                        
                    # Trim history if it's too long
                    max_history_size = data.get('max_history_size', 50)
                    if len(session.context['chat_history']) > max_history_size:
                        session.context['chat_history'] = session.context['chat_history'][-max_history_size:]
                        
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/chat', 'success').inc()
                return self._generate_response({
                    "result": chat_result,
                    "processing_time": processing_time
                })
                
            except Exception as e:
                logger.exception("Error processing chat")
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/chat', 'error').inc()
                return self._error_response(
                    f"Error processing chat: {str(e)}",
                    "ChatError",
                    500
                )
                
    async def embedding(self, request: web.Request) -> web.Response:
        """Handle an embedding request.
        
        Args:
            request: HTTP request
            
        Returns:
            JSON response with embedding result
        """
        with REQUEST_LATENCY.labels('/api/v1/session/{session_id}/embedding').time():
            session_id = request.match_info['session_id']
            session = self.session_manager.get_session(session_id)
            
            if not session:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/embedding', 'error').inc()
                return self._error_response(
                    f"Session not found: {session_id}", 
                    "SessionNotFound", 
                    404
                )
                
            try:
                data = await request.json()
            except json.JSONDecodeError:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/embedding', 'error').inc()
                return self._error_response("Invalid JSON request body")
                
            # Validate request
            if 'input' not in data:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/embedding', 'error').inc()
                return self._error_response("Missing required field: input")
                
            model = data.get('model', 'default')
            
            # Check if we have a provider for embeddings
            if 'embedding' not in self.model_providers:
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/embedding', 'error').inc()
                return self._error_response(
                    "No embedding model provider registered",
                    "ProviderNotAvailable",
                    501
                )
                
            # Enrich request with session context
            enriched_request = {
                **data,
                "session_context": session.context
            }
            
            # Process the embedding request
            try:
                start_time = time.time()
                embedding_result = await self.model_providers['embedding'](enriched_request)
                processing_time = time.time() - start_time
                
                # Update metrics
                MODEL_TOKENS_PROCESSED.labels(model, 'embedding').inc(
                    embedding_result.get('usage', {}).get('total_tokens', 0)
                )
                
                # Add to session history
                history_entry = {
                    "type": "embedding",
                    "request": {**data, "input": f"{data['input'][:100]}..." if len(str(data['input'])) > 100 else data['input']},
                    "response": {
                        **embedding_result,
                        # Don't store full embeddings in history to save space
                        "data": f"{len(embedding_result.get('data', []))} embeddings generated"
                    },
                    "processing_time": processing_time
                }
                session.add_to_history(history_entry)
                
                # Store embeddings in context if requested
                if data.get('store_in_context', False) and 'data' in embedding_result:
                    context_key = data.get('context_key', 'embeddings')
                    
                    if context_key not in session.context:
                        session.context[context_key] = []
                        
                    # Store with metadata
                    session.context[context_key].append({
                        "input": data['input'],
                        "embeddings": embedding_result['data'],
                        "model": model,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                    
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/embedding', 'success').inc()
                return self._generate_response({
                    "result": embedding_result,
                    "processing_time": processing_time
                })
                
            except Exception as e:
                logger.exception("Error processing embedding")
                REQUEST_COUNT.labels('/api/v1/session/{session_id}/embedding', 'error').inc()
                return self._error_response(
                    f"Error processing embedding: {str(e)}",
                    "EmbeddingError",
                    500
                )
                
    async def list_models(self, request: web.Request) -> web.Response:
        """List available models.
        
        Args:
            request: HTTP request
            
        Returns:
            JSON response with available models
        """
        with REQUEST_LATENCY.labels('/api/v1/models').time():
            # Get models from providers
            models = {}
            
            for provider_type, provider_func in self.model_providers.items():
                if hasattr(provider_func, 'list_models'):
                    try:
                        provider_models = await provider_func.list_models()
                        models[provider_type] = provider_models
                    except Exception as e:
                        logger.error(f"Error listing models for {provider_type}: {e}")
                        models[provider_type] = {"error": str(e)}
                else:
                    models[provider_type] = {"available": True, "details": None}
                    
            REQUEST_COUNT.labels('/api/v1/models', 'success').inc()
            return self._generate_response({
                "models": models,
                "provider_types": list(self.model_providers.keys())
            })
            
    async def server_status(self, request: web.Request) -> web.Response:
        """Get server status information.
        
        Args:
            request: HTTP request
            
        Returns:
            JSON response with server status
        """
        with REQUEST_LATENCY.labels('/api/v1/status').time():
            # Get process info
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            # Calculate uptime
            uptime = datetime.datetime.now() - self.start_time
            uptime_seconds = uptime.total_seconds()
            
            status = {
                "version": MCP_VERSION,
                "uptime": {
                    "seconds": uptime_seconds,
                    "formatted": str(uptime)
                },
                "sessions": {
                    "active": len(self.session_manager.sessions)
                },
                "system": {
                    "memory_usage": {
                        "rss": memory_info.rss,
                        "rss_human": f"{memory_info.rss / (1024 * 1024):.2f} MB"
                    },
                    "cpu_percent": process.cpu_percent(),
                    "platform": platform.platform(),
                    "python_version": platform.python_version()
                },
                "providers": list(self.model_providers.keys())
            }
            
            REQUEST_COUNT.labels('/api/v1/status', 'success').inc()
            return self._generate_response({"status": status})
            
    async def health_check(self, request: web.Request) -> web.Response:
        """Simple health check endpoint.
        
        Args:
            request: HTTP request
            
        Returns:
            JSON response indicating server health
        """
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    async def metrics(self, request: web.Request) -> web.Response:
        """Expose Prometheus metrics.
        
        Args:
            request: HTTP request
            
        Returns:
            Response with Prometheus metrics
        """
        resp = web.Response(body=prometheus_client.generate_latest())
        resp.content_type = prometheus_client.CONTENT_TYPE_LATEST
        return resp


class MCPModelProvider:
    """Base class for MCP model providers."""
    
    @staticmethod
    async def list_models() -> Dict[str, Any]:
        """List available models from this provider.
        
        Returns:
            Dictionary with model information
        """
        return {"error": "Not implemented"}
        
    @staticmethod
    async def __call__(request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a model request.
        
        Args:
            request: Model request data
            
        Returns:
            Dictionary with model response
        """
        raise NotImplementedError("Model providers must implement __call__")


# Standalone function to run the server
async def run_server(
    host: str = "0.0.0.0",
    port: int = 8080,
    metrics_port: int = 8081,
    log_level: str = "INFO",
    model_providers: Dict[str, Callable] = None
):
    """Run the MCP server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
        metrics_port: Port for metrics server
        log_level: Logging level
        model_providers: Model provider functions
    """
    server = UnifiedMCPServer(
        host=host,
        port=port,
        metrics_port=metrics_port,
        log_level=log_level,
        model_providers=model_providers
    )
    
    runner, metrics_runner = await server.start()
    
    # Keep the server running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    finally:
        await runner.cleanup()
        await metrics_runner.cleanup()
        await server.stop()


if __name__ == "__main__":
    # Example model providers
    async def dummy_completion_provider(request):
        await asyncio.sleep(0.5)  # Simulate processing
        return {
            "text": f"Completion for: {request['prompt'][:30]}...",
            "usage": {"total_tokens": 20}
        }
        
    async def dummy_chat_provider(request):
        await asyncio.sleep(0.5)  # Simulate processing
        return {
            "message": {"role": "assistant", "content": "This is a dummy response"},
            "usage": {"total_tokens": 15}
        }
        
    # Define model providers
    providers = {
        "completion": dummy_completion_provider,
        "chat": dummy_chat_provider
    }
    
    # Run the server
    asyncio.run(run_server(model_providers=providers))
