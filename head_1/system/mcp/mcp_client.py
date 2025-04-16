"""
MCP Client Library

This module provides a client library for interacting with MCP servers.
It enables applications to seamlessly integrate with MCP-enabled systems.
"""

import json
import logging
import aiohttp
import asyncio
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Configure logger
logger = logging.getLogger("mcp-client")

class MCPClient:
    """Client for interacting with MCP servers."""
    
    def __init__(
        self, 
        base_url: str = None,
        api_version: str = "v1",
        session_id: str = None,
        default_ttl: int = 3600
    ):
        """Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server
            api_version: API version to use
            session_id: Optional session ID to use (created if not provided)
            default_ttl: Default TTL for sessions in seconds
        """
        # Load configuration from environment or defaults
        self.base_url = base_url or os.environ.get("MCP_SERVER_URL", "http://localhost:8080")
        self.api_version = api_version
        self.api_base = f"{self.base_url}/api/{self.api_version}"
        self.session_id = session_id
        self.default_ttl = default_ttl
        self._aiohttp_session = None
        self._created_session = False
        
    async def __aenter__(self):
        """Enter async context manager."""
        self._aiohttp_session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self._aiohttp_session:
            await self._aiohttp_session.close()
            self._aiohttp_session = None
            
        if self._created_session and self.session_id:
            # Try to delete the session
            try:
                await self.delete_session()
            except Exception as e:
                logger.warning(f"Failed to delete session during cleanup: {e}")
                
    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session.
        
        Returns:
            aiohttp.ClientSession instance
        """
        if self._aiohttp_session is None:
            self._aiohttp_session = aiohttp.ClientSession()
        return self._aiohttp_session
        
    async def create_session(
        self,
        context: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
        ttl: int = None
    ) -> Dict[str, Any]:
        """Create a new MCP session.
        
        Args:
            context: Initial context to set
            metadata: Session metadata
            ttl: Session time-to-live in seconds
            
        Returns:
            Session information
        """
        ttl = ttl or self.default_ttl
        data = {"ttl": ttl}
        
        if context:
            data["context"] = context
            
        if metadata:
            data["metadata"] = metadata
            
        async with self._get_session().post(
            f"{self.api_base}/session",
            json=data
        ) as resp:
            if resp.status != 201:
                error_info = await resp.text()
                raise Exception(f"Failed to create session: {resp.status} - {error_info}")
                
            result = await resp.json()
            if result.get("status") != "success":
                error = result.get("error", {})
                raise Exception(f"API error: {error.get('message', 'Unknown error')}")
                
            session_data = result.get("session", {})
            self.session_id = session_data.get("session_id")
            self._created_session = True
            
            return session_data
            
    async def get_session(self, session_id: str = None) -> Dict[str, Any]:
        """Get information about a session.
        
        Args:
            session_id: Session ID (uses the stored session ID if not provided)
            
        Returns:
            Session information
        """
        session_id = session_id or self.session_id
        if not session_id:
            raise ValueError("No session ID provided or stored")
            
        async with self._get_session().get(
            f"{self.api_base}/session/{session_id}"
        ) as resp:
            if resp.status != 200:
                error_info = await resp.text()
                raise Exception(f"Failed to get session: {resp.status} - {error_info}")
                
            result = await resp.json()
            if result.get("status") != "success":
                error = result.get("error", {})
                raise Exception(f"API error: {error.get('message', 'Unknown error')}")
                
            return result.get("session", {})
            
    async def delete_session(self, session_id: str = None) -> bool:
        """Delete a session.
        
        Args:
            session_id: Session ID (uses the stored session ID if not provided)
            
        Returns:
            True if successful
        """
        session_id = session_id or self.session_id
        if not session_id:
            raise ValueError("No session ID provided or stored")
            
        async with self._get_session().delete(
            f"{self.api_base}/session/{session_id}"
        ) as resp:
            if resp.status != 200:
                error_info = await resp.text()
                raise Exception(f"Failed to delete session: {resp.status} - {error_info}")
                
            result = await resp.json()
            if result.get("status") != "success":
                error = result.get("error", {})
                raise Exception(f"API error: {error.get('message', 'Unknown error')}")
                
            if session_id == self.session_id:
                self.session_id = None
                self._created_session = False
                
            return True
            
    async def complete(
        self,
        prompt: str,
        model: str = "default",
        session_id: str = None,
        update_context: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Get a completion from the model.
        
        Args:
            prompt: The text prompt
            model: Model to use
            session_id: Session ID (uses the stored session ID if not provided)
            update_context: Whether to update the session context with results
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Completion result
        """
        session_id = session_id or self.session_id
        if not session_id:
            raise ValueError("No session ID provided or stored")
            
        data = {
            "prompt": prompt,
            "model": model,
            "update_context": update_context,
            **kwargs
        }
        
        async with self._get_session().post(
            f"{self.api_base}/session/{session_id}/complete",
            json=data
        ) as resp:
            if resp.status != 200:
                error_info = await resp.text()
                raise Exception(f"Completion failed: {resp.status} - {error_info}")
                
            result = await resp.json()
            if result.get("status") != "success":
                error = result.get("error", {})
                raise Exception(f"API error: {error.get('message', 'Unknown error')}")
                
            return result.get("result", {})
            
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "default",
        session_id: str = None,
        continue_conversation: bool = True,
        update_context: bool = True,
        max_history: int = 10,
        max_history_size: int = 50,
        **kwargs
    ) -> Dict[str, Any]:
        """Chat with the model.
        
        Args:
            messages: List of message objects with 'role' and 'content'
            model: Model to use
            session_id: Session ID (uses the stored session ID if not provided)
            continue_conversation: Whether to include previous messages from history
            update_context: Whether to update the session context with results
            max_history: Maximum number of history messages to include
            max_history_size: Maximum total history size to maintain
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Chat result
        """
        session_id = session_id or self.session_id
        if not session_id:
            raise ValueError("No session ID provided or stored")
            
        data = {
            "messages": messages,
            "model": model,
            "continue_conversation": continue_conversation,
            "update_context": update_context,
            "max_history": max_history,
            "max_history_size": max_history_size,
            **kwargs
        }
        
        async with self._get_session().post(
            f"{self.api_base}/session/{session_id}/chat",
            json=data
        ) as resp:
            if resp.status != 200:
                error_info = await resp.text()
                raise Exception(f"Chat failed: {resp.status} - {error_info}")
                
            result = await resp.json()
            if result.get("status") != "success":
                error = result.get("error", {})
                raise Exception(f"API error: {error.get('message', 'Unknown error')}")
                
            return result.get("result", {})
            
    async def embedding(
        self,
        input_text: Union[str, List[str]],
        model: str = "default",
        session_id: str = None,
        store_in_context: bool = False,
        context_key: str = "embeddings",
        **kwargs
    ) -> Dict[str, Any]:
        """Get embeddings from the model.
        
        Args:
            input_text: Text to embed (string or list of strings)
            model: Model to use
            session_id: Session ID (uses the stored session ID if not provided)
            store_in_context: Whether to store embeddings in the session context
            context_key: Key to use for storing embeddings in context
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Embedding result
        """
        session_id = session_id or self.session_id
        if not session_id:
            raise ValueError("No session ID provided or stored")
            
        data = {
            "input": input_text,
            "model": model,
            "store_in_context": store_in_context,
            "context_key": context_key,
            **kwargs
        }
        
        async with self._get_session().post(
            f"{self.api_base}/session/{session_id}/embedding",
            json=data
        ) as resp:
            if resp.status != 200:
                error_info = await resp.text()
                raise Exception(f"Embedding failed: {resp.status} - {error_info}")
                
            result = await resp.json()
            if result.get("status") != "success":
                error = result.get("error", {})
                raise Exception(f"API error: {error.get('message', 'Unknown error')}")
                
            return result.get("result", {})
            
    async def list_models(self) -> Dict[str, Any]:
        """List available models.
        
        Returns:
            Dictionary of available models
        """
        async with self._get_session().get(
            f"{self.api_base}/models"
        ) as resp:
            if resp.status != 200:
                error_info = await resp.text()
                raise Exception(f"Failed to list models: {resp.status} - {error_info}")
                
            result = await resp.json()
            if result.get("status") != "success":
                error = result.get("error", {})
                raise Exception(f"API error: {error.get('message', 'Unknown error')}")
                
            return {
                "models": result.get("models", {}),
                "provider_types": result.get("provider_types", [])
            }
            
    async def server_status(self) -> Dict[str, Any]:
        """Get server status.
        
        Returns:
            Server status information
        """
        async with self._get_session().get(
            f"{self.api_base}/status"
        ) as resp:
            if resp.status != 200:
                error_info = await resp.text()
                raise Exception(f"Failed to get status: {resp.status} - {error_info}")
                
            result = await resp.json()
            if result.get("status") != "success":
                error = result.get("error", {})
                raise Exception(f"API error: {error.get('message', 'Unknown error')}")
                
            return result.get("status", {})


class MCPSyncClient:
    """Synchronous client for interacting with MCP servers.
    
    This is a wrapper around the async client for use in synchronous code.
    """
    
    def __init__(
        self, 
        base_url: str = None,
        api_version: str = "v1",
        session_id: str = None,
        default_ttl: int = 3600
    ):
        """Initialize the synchronous MCP client.
        
        Args:
            base_url: Base URL of the MCP server
            api_version: API version to use
            session_id: Optional session ID to use (created if not provided)
            default_ttl: Default TTL for sessions in seconds
        """
        self.async_client = MCPClient(
            base_url=base_url,
            api_version=api_version,
            session_id=session_id,
            default_ttl=default_ttl
        )
        self._loop = None
        self._client_session = None
        
    def _get_event_loop(self):
        """Get or create an event loop.
        
        Returns:
            asyncio.AbstractEventLoop instance
        """
        if self._loop is None:
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                # No event loop in current thread, create a new one
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop
        
    def _run_coroutine(self, coroutine):
        """Run a coroutine in the event loop.
        
        Args:
            coroutine: Coroutine to run
            
        Returns:
            Result of the coroutine
        """
        loop = self._get_event_loop()
        if loop.is_running():
            # If we're already in an event loop, use asyncio.run_coroutine_threadsafe
            import concurrent.futures
            future = asyncio.run_coroutine_threadsafe(coroutine, loop)
            return future.result()
        else:
            # Otherwise, just run the coroutine
            return loop.run_until_complete(coroutine)
            
    def __enter__(self):
        """Enter context manager."""
        self._client_session = self._run_coroutine(self.async_client.__aenter__())
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self._run_coroutine(self.async_client.__aexit__(exc_type, exc_val, exc_tb))
        self._client_session = None
        
    def create_session(self, context: Dict[str, Any] = None, metadata: Dict[str, Any] = None, ttl: int = None) -> Dict[str, Any]:
        """Create a new MCP session."""
        return self._run_coroutine(self.async_client.create_session(context=context, metadata=metadata, ttl=ttl))
        
    def get_session(self, session_id: str = None) -> Dict[str, Any]:
        """Get information about a session."""
        return self._run_coroutine(self.async_client.get_session(session_id=session_id))
        
    def delete_session(self, session_id: str = None) -> bool:
        """Delete a session."""
        return self._run_coroutine(self.async_client.delete_session(session_id=session_id))
        
    def complete(self, prompt: str, model: str = "default", session_id: str = None, update_context: bool = False, **kwargs) -> Dict[str, Any]:
        """Get a completion from the model."""
        return self._run_coroutine(self.async_client.complete(
            prompt=prompt, 
            model=model, 
            session_id=session_id, 
            update_context=update_context, 
            **kwargs
        ))
        
    def chat(self, messages: List[Dict[str, str]], model: str = "default", session_id: str = None, 
            continue_conversation: bool = True, update_context: bool = True, 
            max_history: int = 10, max_history_size: int = 50, **kwargs) -> Dict[str, Any]:
        """Chat with the model."""
        return self._run_coroutine(self.async_client.chat(
            messages=messages, 
            model=model, 
            session_id=session_id, 
            continue_conversation=continue_conversation, 
            update_context=update_context, 
            max_history=max_history, 
            max_history_size=max_history_size, 
            **kwargs
        ))
        
    def embedding(self, input_text: Union[str, List[str]], model: str = "default", session_id: str = None, 
                store_in_context: bool = False, context_key: str = "embeddings", **kwargs) -> Dict[str, Any]:
        """Get embeddings from the model."""
        return self._run_coroutine(self.async_client.embedding(
            input_text=input_text, 
            model=model, 
            session_id=session_id, 
            store_in_context=store_in_context, 
            context_key=context_key, 
            **kwargs
        ))
        
    def list_models(self) -> Dict[str, Any]:
        """List available models."""
        return self._run_coroutine(self.async_client.list_models())
        
    def server_status(self) -> Dict[str, Any]:
        """Get server status."""
        return self._run_coroutine(self.async_client.server_status())


# Example usage
async def example_async_usage():
    """Example of async client usage."""
    async with MCPClient() as client:
        # Create a session
        session = await client.create_session()
        print(f"Created session: {session['session_id']}")
        
        # Chat with the model
        result = await client.chat([
            {"role": "user", "content": "Hello, world!"}
        ])
        print(f"Response: {result['message']['content']}")
        
        # Get embeddings
        embedding_result = await client.embedding("Hello, world!")
        print(f"Generated {len(embedding_result['data'])} embeddings")


def example_sync_usage():
    """Example of synchronous client usage."""
    with MCPSyncClient() as client:
        # Create a session
        session = client.create_session()
        print(f"Created session: {session['session_id']}")
        
        # Chat with the model
        result = client.chat([
            {"role": "user", "content": "Hello, world!"}
        ])
        print(f"Response: {result['message']['content']}")
        
        # Get embeddings
        embedding_result = client.embedding("Hello, world!")
        print(f"Generated {len(embedding_result['data'])} embeddings")


if __name__ == "__main__":
    # Run the async example
    asyncio.run(example_async_usage())
    
    # Run the sync example
    example_sync_usage()
