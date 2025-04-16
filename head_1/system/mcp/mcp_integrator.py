"""
MCP Integration Utility for Research Infrastructure

This module provides utilities to integrate the Model Context Protocol (MCP)
with the existing research infrastructure, upgrading servers and clients 
to use MCP without disrupting the existing workflows.
"""

import asyncio
import logging
import os
import shutil
import sys
import importlib
import inspect
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, Callable, Awaitable, Tuple

from unified_mcp_server import UnifiedMCPServer, MCPSession, MCPModelProvider, MCPSessionManager

# Configure logger
logger = logging.getLogger("mcp-integrator")

# Define the project root and paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.absolute()
HEAD_PATH = PROJECT_ROOT / "head_1"
FRAMEWORK_PATH = HEAD_PATH / "frameworks"
SYSTEM_PATH = HEAD_PATH / "system"
CONTROLS_PATH = PROJECT_ROOT / "CONTROLS"
BACKUP_PATH = PROJECT_ROOT / "backups" / "pre_mcp_integration"


class MCPIntegrator:
    """Integrates MCP into the existing infrastructure."""
    
    def __init__(
        self, 
        backup: bool = True,
        safe_mode: bool = True,
        project_root: Path = PROJECT_ROOT
    ):
        """Initialize the MCP integrator.
        
        Args:
            backup: Whether to back up files before modifying them
            safe_mode: Run in safe mode, which will avoid destructive changes
            project_root: Path to the project root
        """
        self.backup = backup
        self.safe_mode = safe_mode
        self.project_root = project_root
        
        # Paths to key components
        self.head_path = project_root / "head_1"
        self.framework_path = self.head_path / "frameworks"
        self.system_path = self.head_path / "system"
        self.controls_path = project_root / "CONTROLS"
        self.server_paths = self._find_server_paths()
        
        # Back up paths
        self.backup_path = project_root / "backups" / "pre_mcp_integration"
        
        # Track modified files
        self.modified_files: Set[Path] = set()
        self.errors: List[str] = []
        
    def _find_server_paths(self) -> List[Path]:
        """Find all server implementation paths in the project.
        
        Returns:
            List of paths to server implementations
        """
        server_paths = []
        
        # Common suffixes for server files
        server_suffixes = [
            "*server*.py", 
            "*api*.py", 
            "*service*.py", 
            "*endpoint*.py",
            "*http*.py",
            "*web*.py"
        ]
        
        # Search in common directories
        search_dirs = [
            self.head_path,
            self.system_path,
            self.framework_path,
            self.controls_path,
            self.project_root / "inference_api"
        ]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            for suffix in server_suffixes:
                for path in search_dir.glob(f"**/{suffix}"):
                    # Skip the MCP implementation itself
                    if "mcp" in path.name.lower() and path.name != "unified_mcp_server.py":
                        continue
                        
                    # Only include Python files
                    if path.suffix.lower() == ".py":
                        server_paths.append(path)
        
        return server_paths
        
    def backup_files(self, paths: List[Path]) -> bool:
        """Back up files before modification.
        
        Args:
            paths: List of paths to back up
            
        Returns:
            True if the backup was successful, False otherwise
        """
        if not self.backup:
            logger.info("Backup disabled, skipping")
            return True
            
        try:
            # Create backup directory
            timestamp = self._get_timestamp()
            backup_dir = self.backup_path / timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Backing up files to {backup_dir}")
            
            for path in paths:
                if not path.exists():
                    continue
                    
                # Create the relative directory structure in the backup
                rel_path = path.relative_to(self.project_root)
                backup_file_path = backup_dir / rel_path
                backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                shutil.copy2(path, backup_file_path)
                logger.debug(f"Backed up: {path} -> {backup_file_path}")
                
            logger.info(f"Successfully backed up {len(paths)} files")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            self.errors.append(f"Backup failed: {e}")
            return False
            
    def _get_timestamp(self) -> str:
        """Get a timestamp string for backup directories.
        
        Returns:
            Timestamp string
        """
        import datetime
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def analyze_server_file(self, path: Path) -> Dict[str, Any]:
        """Analyze a server file for integration.
        
        Args:
            path: Path to the server file
            
        Returns:
            Analysis information
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Check if file already has MCP references
            has_mcp = "mcp" in content.lower()
            
            # Look for server setup patterns
            has_aiohttp = "aiohttp" in content
            has_flask = "flask" in content
            has_fastapi = "fastapi" in content
            
            # Look for route definitions
            route_matches = []
            if has_aiohttp:
                # Look for add_routes, route decorators
                if "add_routes" in content or "@routes." in content or ".add_get" in content:
                    route_matches.append("aiohttp")
            
            if has_flask:
                # Look for Flask route decorators
                if "@app.route" in content or "add_url_rule" in content:
                    route_matches.append("flask")
                    
            if has_fastapi:
                # Look for FastAPI route decorators
                if "@app." in content and any(m in content for m in ["get", "post", "put", "delete"]):
                    route_matches.append("fastapi")
                    
            # Import paths to check dependencies
            import_lines = [line.strip() for line in content.split("\n") if line.strip().startswith("import ") or line.strip().startswith("from ")]
            
            # Determine server type
            server_type = None
            if has_aiohttp:
                server_type = "aiohttp"
            elif has_flask:
                server_type = "flask"
            elif has_fastapi:
                server_type = "fastapi"
                
            return {
                "path": path,
                "has_mcp": has_mcp,
                "server_type": server_type,
                "has_routes": bool(route_matches),
                "route_frameworks": route_matches,
                "import_lines": import_lines,
                "needs_integration": bool(route_matches) and not has_mcp
            }
        
        except Exception as e:
            logger.error(f"Error analyzing file {path}: {e}")
            self.errors.append(f"Error analyzing file {path}: {e}")
            return {
                "path": path,
                "error": str(e),
                "needs_integration": False
            }
    
    def get_integration_plan(self) -> Dict[str, Any]:
        """Analyze all server files and create an integration plan.
        
        Returns:
            Integration plan
        """
        logger.info("Creating MCP integration plan...")
        
        server_analyses = []
        need_integration = []
        already_integrated = []
        
        # Analyze each server file
        for server_path in self.server_paths:
            analysis = self.analyze_server_file(server_path)
            server_analyses.append(analysis)
            
            if analysis.get("needs_integration", False):
                need_integration.append(server_path)
            elif analysis.get("has_mcp", False):
                already_integrated.append(server_path)
        
        logger.info(f"Found {len(need_integration)} servers needing MCP integration")
        logger.info(f"Found {len(already_integrated)} servers already using MCP")
        
        return {
            "server_analyses": server_analyses,
            "need_integration": need_integration,
            "already_integrated": already_integrated,
            "total_servers": len(self.server_paths)
        }
        
    def integrate_server_file(self, path: Path, analysis: Dict[str, Any]) -> bool:
        """Integrate MCP into a server file.
        
        Args:
            path: Path to the server file
            analysis: Analysis information for the file
            
        Returns:
            True if integration was successful, False otherwise
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Determine integration strategy based on server type
            server_type = analysis.get("server_type")
            if not server_type:
                logger.warning(f"Cannot determine server type for {path}")
                return False
                
            # Get integration template
            template = self._get_integration_template(server_type)
            if not template:
                logger.warning(f"No integration template for server type {server_type}")
                return False
                
            # Prepare the integration
            imports_to_add = template["imports"]
            code_to_add = template["code"]
            
            # Check if we need to add imports
            existing_imports = analysis.get("import_lines", [])
            imports_to_add_str = ""
            
            for imp in imports_to_add:
                if not any(imp in existing_imp for existing_imp in existing_imports):
                    imports_to_add_str += f"{imp}\n"
                    
            # Apply the integration
            if imports_to_add_str:
                # Find a good place to add imports
                import_section_end = 0
                in_import_section = False
                
                for i, line in enumerate(content.split("\n")):
                    line = line.strip()
                    
                    if line.startswith("import ") or line.startswith("from "):
                        in_import_section = True
                        import_section_end = i
                    elif in_import_section and line and not line.startswith("#") and not line.startswith("import ") and not line.startswith("from "):
                        in_import_section = False
                        break
                        
                # If no imports found, add after docstring or at the beginning
                if import_section_end == 0:
                    if '"""' in content:
                        # Find the end of the docstring
                        docstring_end = content.find('"""', content.find('"""') + 3)
                        if docstring_end != -1:
                            insert_pos = content.find("\n", docstring_end) + 1
                            content = content[:insert_pos] + imports_to_add_str + "\n" + content[insert_pos:]
                    else:
                        # Add at the beginning
                        content = imports_to_add_str + "\n" + content
                else:
                    # Add after the import section
                    lines = content.split("\n")
                    lines.insert(import_section_end + 1, imports_to_add_str)
                    content = "\n".join(lines)
                    
            # Add the MCP integration code
            # Find a good position to add the code - after the class or function definitions
            # but before the main execution block
            if "__name__" in content:
                # Add before the main execution block
                insert_pos = content.find("if __name__ ==")
                if insert_pos != -1:
                    content = content[:insert_pos] + code_to_add + "\n\n" + content[insert_pos:]
                else:
                    # Add at the end
                    content += "\n\n" + code_to_add
            else:
                # Add at the end
                content += "\n\n" + code_to_add
                
            # Only modify in non-safe mode
            if not self.safe_mode:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Successfully integrated MCP into {path}")
                self.modified_files.add(path)
                return True
            else:
                logger.info(f"[SAFE MODE] Would integrate MCP into {path}")
                return True
                
        except Exception as e:
            logger.error(f"Error integrating MCP into {path}: {e}")
            self.errors.append(f"Error integrating MCP into {path}: {e}")
            return False
            
    def _get_integration_template(self, server_type: str) -> Optional[Dict[str, Any]]:
        """Get the integration template for a server type.
        
        Args:
            server_type: Type of server (aiohttp, flask, fastapi)
            
        Returns:
            Integration template or None if not found
        """
        templates = {
            "aiohttp": {
                "imports": [
                    "import sys",
                    "from pathlib import Path",
                    "# MCP integration imports",
                    "mcp_path = Path(__file__).parent.parent.parent / 'system' / 'mcp'",
                    "if mcp_path.exists() and str(mcp_path) not in sys.path:",
                    "    sys.path.append(str(mcp_path))",
                    "from unified_mcp_server import MCPSession, MCPSessionManager, MCPModelProvider"
                ],
                "code": """
# MCP integration
class MCPIntegration:
    \"\"\"Integration with the Model Context Protocol.\"\"\"
    
    def __init__(self, app=None):
        \"\"\"Initialize the MCP integration.
        
        Args:
            app: The server application
        \"\"\"
        self.app = app
        self.session_manager = MCPSessionManager()
        self.enabled = True
        
        if app:
            self.init_app(app)
            
    def init_app(self, app):
        \"\"\"Initialize the integration with an application.
        
        Args:
            app: The server application
        \"\"\"
        self.app = app
        
        # Add MCP routes
        app.router.add_routes([
            web.post('/mcp/v1/session', self.create_session),
            web.get('/mcp/v1/session/{session_id}', self.get_session),
            web.delete('/mcp/v1/session/{session_id}', self.delete_session),
        ])
        
        # Start the session manager
        asyncio.create_task(self.session_manager.start())
        
    async def create_session(self, request):
        \"\"\"Create a new MCP session.\"\"\"
        try:
            data = await request.json()
        except:
            data = {}
            
        ttl = int(data.get('ttl', 3600))
        session = self.session_manager.create_session(ttl=ttl)
        
        return web.json_response({
            "status": "success",
            "session": {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "ttl": session.ttl
            }
        })
        
    async def get_session(self, request):
        \"\"\"Get session information.\"\"\"
        session_id = request.match_info['session_id']
        session = self.session_manager.get_session(session_id)
        
        if not session:
            return web.json_response({
                "status": "error",
                "message": f"Session {session_id} not found"
            }, status=404)
            
        return web.json_response({
            "status": "success",
            "session": {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "last_accessed": session.last_accessed.isoformat(),
                "ttl": session.ttl,
                "context_size": len(session.context)
            }
        })
        
    async def delete_session(self, request):
        \"\"\"Delete a session.\"\"\"
        session_id = request.match_info['session_id']
        result = self.session_manager.delete_session(session_id)
        
        if not result:
            return web.json_response({
                "status": "error",
                "message": f"Session {session_id} not found"
            }, status=404)
            
        return web.json_response({
            "status": "success",
            "message": f"Session {session_id} deleted"
        })

# Create an instance to be used by the application
mcp_integration = MCPIntegration()
"""
            },
            "flask": {
                "imports": [
                    "import sys",
                    "import asyncio",
                    "import threading",
                    "from pathlib import Path",
                    "# MCP integration imports",
                    "mcp_path = Path(__file__).parent.parent.parent / 'system' / 'mcp'",
                    "if mcp_path.exists() and str(mcp_path) not in sys.path:",
                    "    sys.path.append(str(mcp_path))",
                    "from unified_mcp_server import MCPSession, MCPSessionManager, MCPModelProvider"
                ],
                "code": """
# MCP integration for Flask
class MCPFlaskIntegration:
    \"\"\"Integration of MCP with Flask applications.\"\"\"
    
    def __init__(self, app=None):
        \"\"\"Initialize the MCP integration.
        
        Args:
            app: The Flask application
        \"\"\"
        self.app = app
        self.session_manager = MCPSessionManager()
        self.enabled = True
        self._async_thread = None
        self._loop = None
        self._loop_ready = threading.Event()
        
        if app:
            self.init_app(app)
            
    def init_app(self, app):
        \"\"\"Initialize the integration with a Flask application.
        
        Args:
            app: The Flask application
        \"\"\"
        self.app = app
        
        # Start the async loop in a separate thread
        self._start_async_thread()
        
        # Add MCP routes to Flask
        app.add_url_rule('/mcp/v1/session', 'mcp_create_session', 
                          self.create_session, methods=['POST'])
        app.add_url_rule('/mcp/v1/session/<session_id>', 'mcp_get_session',
                          self.get_session, methods=['GET'])
        app.add_url_rule('/mcp/v1/session/<session_id>', 'mcp_delete_session',
                          self.delete_session, methods=['DELETE'])
                          
        # Register shutdown function
        app.teardown_appcontext(self._teardown)
        
    def _start_async_thread(self):
        \"\"\"Start asyncio loop in a separate thread for the session manager.\"\"\"
        def run_async_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            # Start the session manager
            self._loop.run_until_complete(self.session_manager.start())
            
            # Signal that the loop is ready
            self._loop_ready.set()
            
            # Run the loop
            self._loop.run_forever()
            
        if not self._async_thread:
            self._async_thread = threading.Thread(target=run_async_loop, daemon=True)
            self._async_thread.start()
            
            # Wait for the loop to be ready
            self._loop_ready.wait()
            
    def _teardown(self, exception):
        \"\"\"Clean up resources when the application context ends.\"\"\"
        if self._loop and self._async_thread and self._async_thread.is_alive():
            # Stop the session manager and the loop
            asyncio.run_coroutine_threadsafe(
                self.session_manager.stop(), self._loop
            )
            self._loop.call_soon_threadsafe(self._loop.stop)
            
    def create_session(self):
        \"\"\"Create a new MCP session.\"\"\"
        from flask import request, jsonify
        
        try:
            data = request.get_json(silent=True) or {}
        except:
            data = {}
            
        ttl = int(data.get('ttl', 3600))
        
        # Create the session in the synchronous context
        session = self.session_manager.create_session(ttl=ttl)
        
        return jsonify({
            "status": "success",
            "session": {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "ttl": session.ttl
            }
        }), 201
        
    def get_session(self, session_id):
        \"\"\"Get session information.\"\"\"
        from flask import jsonify
        
        session = self.session_manager.get_session(session_id)
        
        if not session:
            return jsonify({
                "status": "error",
                "message": f"Session {session_id} not found"
            }), 404
            
        return jsonify({
            "status": "success",
            "session": {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "last_accessed": session.last_accessed.isoformat(),
                "ttl": session.ttl,
                "context_size": len(session.context)
            }
        })
        
    def delete_session(self, session_id):
        \"\"\"Delete a session.\"\"\"
        from flask import jsonify
        
        result = self.session_manager.delete_session(session_id)
        
        if not result:
            return jsonify({
                "status": "error",
                "message": f"Session {session_id} not found"
            }), 404
            
        return jsonify({
            "status": "success",
            "message": f"Session {session_id} deleted"
        })

# Create an instance to be used by the application
mcp_flask = MCPFlaskIntegration()
"""
            },
            "fastapi": {
                "imports": [
                    "import sys",
                    "from pathlib import Path",
                    "from typing import Dict, Optional, Any",
                    "# MCP integration imports",
                    "mcp_path = Path(__file__).parent.parent.parent / 'system' / 'mcp'",
                    "if mcp_path.exists() and str(mcp_path) not in sys.path:",
                    "    sys.path.append(str(mcp_path))",
                    "from unified_mcp_server import MCPSession, MCPSessionManager, MCPModelProvider",
                    "from pydantic import BaseModel"
                ],
                "code": """
# MCP integration for FastAPI
class MCPSessionRequest(BaseModel):
    \"\"\"Request model for session creation.\"\"\"
    ttl: Optional[int] = 3600
    context: Optional[Dict[str, Any]] = None

class MCPSessionResponse(BaseModel):
    \"\"\"Response model for session information.\"\"\"
    session_id: str
    created_at: str
    ttl: int
    
class MCPFastAPIIntegration:
    \"\"\"Integration of MCP with FastAPI applications.\"\"\"
    
    def __init__(self, app=None):
        \"\"\"Initialize the MCP integration.
        
        Args:
            app: The FastAPI application
        \"\"\"
        self.app = app
        self.session_manager = MCPSessionManager()
        self.enabled = True
        
        if app:
            self.init_app(app)
            
    def init_app(self, app):
        \"\"\"Initialize the integration with a FastAPI application.
        
        Args:
            app: The FastAPI application
        \"\"\"
        from fastapi import APIRouter, HTTPException, Depends
        
        self.app = app
        
        # Start the session manager
        @app.on_event("startup")
        async def startup_event():
            await self.session_manager.start()
            
        # Stop the session manager
        @app.on_event("shutdown")
        async def shutdown_event():
            await self.session_manager.stop()
            
        # Create a router for MCP endpoints
        mcp_router = APIRouter(prefix="/mcp/v1", tags=["mcp"])
        
        # Add routes
        @mcp_router.post("/session", response_model=dict)
        async def create_session(request: MCPSessionRequest):
            session = self.session_manager.create_session(ttl=request.ttl)
            
            # Apply initial context if provided
            if request.context:
                session.context.update(request.context)
                
            return {
                "status": "success",
                "session": {
                    "session_id": session.session_id,
                    "created_at": session.created_at.isoformat(),
                    "ttl": session.ttl
                }
            }
            
        @mcp_router.get("/session/{session_id}", response_model=dict)
        async def get_session(session_id: str):
            session = self.session_manager.get_session(session_id)
            
            if not session:
                raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
                
            return {
                "status": "success",
                "session": {
                    "session_id": session.session_id,
                    "created_at": session.created_at.isoformat(),
                    "last_accessed": session.last_accessed.isoformat(),
                    "ttl": session.ttl,
                    "context_size": len(session.context)
                }
            }
            
        @mcp_router.delete("/session/{session_id}", response_model=dict)
        async def delete_session(session_id: str):
            result = self.session_manager.delete_session(session_id)
            
            if not result:
                raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
                
            return {
                "status": "success",
                "message": f"Session {session_id} deleted"
            }
            
        # Add the router to the application
        app.include_router(mcp_router)
        
# Create an instance to be used by the application
mcp_fastapi = MCPFastAPIIntegration()
"""
            }
        }
        
        return templates.get(server_type)
    
    def execute_integration_plan(self) -> Dict[str, Any]:
        """Execute the MCP integration plan.
        
        Returns:
            Results of the integration
        """
        plan = self.get_integration_plan()
        
        # Check if we need to do any integration
        if not plan["need_integration"]:
            logger.info("No servers need MCP integration")
            return {
                "status": "success",
                "message": "No servers need MCP integration",
                "modified": [],
                "plan": plan
            }
        
        # Back up files if needed
        if self.backup:
            if not self.backup_files(plan["need_integration"]):
                logger.error("Failed to back up files, aborting integration")
                return {
                    "status": "error",
                    "message": "Failed to back up files",
                    "errors": self.errors,
                    "plan": plan
                }
        
        # Perform integration
        success_count = 0
        failures = []
        
        for server_path in plan["need_integration"]:
            # Find the analysis for this path
            analysis = next((a for a in plan["server_analyses"] if a["path"] == server_path), None)
            
            if not analysis:
                logger.warning(f"No analysis found for {server_path}, skipping")
                continue
                
            # Integrate MCP into the server
            success = self.integrate_server_file(server_path, analysis)
            
            if success:
                success_count += 1
            else:
                failures.append(str(server_path))
        
        # Build result
        result = {
            "status": "success" if not failures else "partial_success" if success_count > 0 else "error",
            "message": f"Successfully integrated MCP into {success_count} of {len(plan['need_integration'])} servers",
            "modified": list(map(str, self.modified_files)),
            "failures": failures,
            "errors": self.errors,
            "plan": plan,
            "safe_mode": self.safe_mode
        }
        
        logger.info(f"Integration complete: {result['status']}")
        return result
    
    def install_model_providers(self) -> Dict[str, Any]:
        """Install model providers for MCP.
        
        Returns:
            Results of the installation
        """
        # Path to providers directory
        providers_dir = SYSTEM_PATH / "mcp" / "providers"
        providers_dir.mkdir(parents=True, exist_ok=True)
        
        # Create provider files
        default_providers = {
            "openai_provider": """
import os
import json
import aiohttp
from typing import Dict, Any, List, Optional

class OpenAIProvider:
    """OpenAI API provider for MCP."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.chat_models = ["gpt-3.5-turbo", "gpt-4"]
        self.completion_models = ["text-davinci-003", "text-davinci-002"]
        self.embedding_models = ["text-embedding-ada-002"]
    
    async def __call__(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a model request.
        
        Args:
            request: Model request data
            
        Returns:
            Dictionary with model response
        """
        request_type = request.get("type", "chat")
        
        if request_type == "chat":
            return await self._handle_chat(request)
        elif request_type == "completion":
            return await self._handle_completion(request)
        elif request_type == "embedding":
            return await self._handle_embedding(request)
        else:
            raise ValueError(f"Unsupported request type: {request_type}")
    
    async def _handle_chat(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a chat request.
        
        Args:
            request: Chat request data
            
        Returns:
            Dictionary with chat response
        """
        model = request.get("model", "gpt-3.5-turbo")
        messages = request.get("messages", [])
        temperature = request.get("temperature", 0.7)
        max_tokens = request.get("max_tokens", None)
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            async with session.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                
                if response.status != 200:
                    raise Exception(f"OpenAI API error: {result.get('error', {}).get('message')}")
                
                message = result["choices"][0]["message"]
                usage = result.get("usage", {})
                
                return {
                    "message": message,
                    "model": model,
                    "usage": usage
                }
    
    async def _handle_completion(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a completion request.
        
        Args:
            request: Completion request data
            
        Returns:
            Dictionary with completion response
        """
        model = request.get("model", "text-davinci-003")
        prompt = request.get("prompt", "")
        temperature = request.get("temperature", 0.7)
        max_tokens = request.get("max_tokens", 100)
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            async with session.post(
                f"{self.api_base}/completions",
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                
                if response.status != 200:
                    raise Exception(f"OpenAI API error: {result.get('error', {}).get('message')}")
                
                text = result["choices"][0]["text"]
                usage = result.get("usage", {})
                
                return {
                    "text": text,
                    "model": model,
                    "usage": usage
                }
    
    async def _handle_embedding(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an embedding request.
        
        Args:
            request: Embedding request data
            
        Returns:
            Dictionary with embedding response
        """
        model = request.get("model", "text-embedding-ada-002")
        input_text = request.get("input", "")
        
        # Handle both string and list inputs
        if isinstance(input_text, str):
            inputs = [input_text]
        else:
            inputs = input_text
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "input": inputs
            }
            
            async with session.post(
                f"{self.api_base}/embeddings",
                headers=headers,
                json=payload
            ) as response:
                result = await response.json()
                
                if response.status != 200:
                    raise Exception(f"OpenAI API error: {result.get('error', {}).get('message')}")
                
                embeddings = [item["embedding"] for item in result["data"]]
                usage = result.get("usage", {})
                
                return {
                    "data": embeddings,
                    "model": model,
                    "usage": usage
                }
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models from this provider.
        
        Returns:
            Dictionary with model information
        """
        return {
            "chat": self.chat_models,
            "completion": self.completion_models,
            "embedding": self.embedding_models
        }

# Create an instance of the provider
provider = OpenAIProvider()
""",
            "huggingface_provider": """
import os
import json
import aiohttp
from typing import Dict, Any, List, Optional

class HuggingFaceProvider:
    """HuggingFace API provider for MCP."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the HuggingFace provider.
        
        Args:
            api_key: HuggingFace API key (defaults to HUGGINGFACE_API_KEY environment variable)
        """
        self.api_key = api_key or os.environ.get("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("HuggingFace API key is required")
        
        self.api_base = "https://api-inference.huggingface.co/models"
        
        # Default models - these can be expanded or configured
        self.chat_models = ["facebook/blenderbot-400M-distill"]
        self.completion_models = ["gpt2", "EleutherAI/gpt-neo-1.3B"]
        self.embedding_models = ["sentence-transformers/all-MiniLM-L6-v2"]
    
    async def __call__(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a model request.
        
        Args:
            request: Model request data
            
        Returns:
            Dictionary with model response
        """
        request_type = request.get("type", "completion")
        
        if request_type == "chat":
            return await self._handle_chat(request)
        elif request_type == "completion":
            return await self._handle_completion(request)
        elif request_type == "embedding":
            return await self._handle_embedding(request)
        else:
            raise ValueError(f"Unsupported request type: {request_type}")
    
    async def _handle_chat(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a chat request.
        
        Args:
            request: Chat request data
            
        Returns:
            Dictionary with chat response
        """
        model = request.get("model", self.chat_models[0])
        messages = request.get("messages", [])
        
        # Extract the last user message
        user_message = None
        for message in reversed(messages):
            if message.get("role") == "user":
                user_message = message.get("content", "")
                break
        
        if not user_message:
            user_message = "Hello"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with session.post(
                f"{self.api_base}/{model}",
                headers=headers,
                json={"inputs": user_message}
            ) as response:
                if response.status != 200:
                    result = await response.text()
                    raise Exception(f"HuggingFace API error: {result}")
                
                result = await response.json()
                
                # Format depends on the model, but most return a generated_text field
                if isinstance(result, list):
                    content = result[0].get("generated_text", "")
                else:
                    content = result.get("generated_text", "")
                
                message = {"role": "assistant", "content": content}
                
                # Approximate token count
                token_count = len(user_message.split()) + len(content.split())
                
                return {
                    "message": message,
                    "model": model,
                    "usage": {"total_tokens": token_count}
                }
    
    async def _handle_completion(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a completion request.
        
        Args:
            request: Completion request data
            
        Returns:
            Dictionary with completion response
        """
        model = request.get("model", self.completion_models[0])
        prompt = request.get("prompt", "")
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with session.post(
                f"{self.api_base}/{model}",
                headers=headers,
                json={"inputs": prompt}
            ) as response:
                if response.status != 200:
                    result = await response.text()
                    raise Exception(f"HuggingFace API error: {result}")
                
                result = await response.json()
                
                # Format depends on the model
                if isinstance(result, list):
                    text = result[0].get("generated_text", "")
                else:
                    text = result.get("generated_text", "")
                
                # Approximate token count
                token_count = len(prompt.split()) + len(text.split())
                
                return {
                    "text": text,
                    "model": model,
                    "usage": {"total_tokens": token_count}
                }
    
    async def _handle_embedding(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an embedding request.
        
        Args:
            request: Embedding request data
            
        Returns:
            Dictionary with embedding response
        """
        model = request.get("model", self.embedding_models[0])
        input_text = request.get("input", "")
        
        # Handle both string and list inputs
        if isinstance(input_text, str):
            inputs = [input_text]
        else:
            inputs = input_text
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            all_embeddings = []
            total_tokens = 0
            
            for text in inputs:
                async with session.post(
                    f"{self.api_base}/{model}",
                    headers=headers,
                    json={"inputs": text}
                ) as response:
                    if response.status != 200:
                        result = await response.text()
                        raise Exception(f"HuggingFace API error: {result}")
                    
                    result = await response.json()
                    
                    # Add the embedding
                    all_embeddings.append(result)
                    
                    # Approximate token count
                    total_tokens += len(text.split())
            
            return {
                "data": all_embeddings,
                "model": model,
                "usage": {"total_tokens": total_tokens}
            }
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models from this provider.
        
        Returns:
            Dictionary with model information
        """
        return {
            "chat": self.chat_models,
            "completion": self.completion_models,
            "embedding": self.embedding_models
        }

# Create an instance of the provider
provider = HuggingFaceProvider()
"""
        }
        
        # Create __init__.py to make it a proper package
        init_path = providers_dir / "__init__.py"
        
        if not init_path.exists() or not self.safe_mode:
            try:
                with open(init_path, "w") as f:
                    f.write("""
\"\"\"
MCP Model Providers

This package contains provider implementations for different model APIs.
\"\"\"

import os
import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional

# List of provider modules to automatically load
DEFAULT_PROVIDERS = [
    # Add provider module names here (without .py extension)
    # Example: "openai_provider"
]

# Dictionary of loaded provider instances
providers = {}

def load_provider(module_name: str):
    \"\"\"Load a provider module dynamically.
    
    Args:
        module_name: Name of the provider module to load
    
    Returns:
        The loaded provider instance or None if loading failed
    \"\"\"
    try:
        # Import the provider module
        provider_module = importlib.import_module(f".{module_name}", __name__)
        
        # Get the provider instance
        if hasattr(provider_module, "provider"):
            return provider_module.provider
        else:
            return None
    except Exception as e:
        print(f"Error loading provider {module_name}: {e}")
        return None

# Load default providers
for provider_name in DEFAULT_PROVIDERS:
    provider = load_provider(provider_name)
    if provider:
        providers[provider_name] = provider

# Function to get a provider by name
def get_provider(name: str):
    \"\"\"Get a provider instance by name.
    
    Args:
        name: Name of the provider to get
    
    Returns:
        The provider instance or None if not found
    \"\"\"
    return providers.get(name)

# Function to register a provider
def register_provider(name: str, provider):
    \"\"\"Register a provider instance.
    
    Args:
        name: Name to register the provider under
        provider: The provider instance to register
    \"\"\"
    providers[name] = provider
""")
                
                if not self.safe_mode:
                    logger.info(f"Created provider package __init__.py")
                    self.modified_files.add(init_path)
                else:
                    logger.info(f"[SAFE MODE] Would create provider package __init__.py")
            except Exception as e:
                logger.error(f"Error creating __init__.py: {e}")
                self.errors.append(f"Error creating __init__.py: {e}")
        
        # Create provider files
        results = []
        
        for name, content in default_providers.items():
            provider_path = providers_dir / f"{name}.py"
            
            if not provider_path.exists() or not self.safe_mode:
                try:
                    if not self.safe_mode:
                        with open(provider_path, "w") as f:
                            f.write(content)
                        
                        logger.info(f"Created provider: {name}")
                        self.modified_files.add(provider_path)
                        results.append(f"Created {name}.py")
                    else:
                        logger.info(f"[SAFE MODE] Would create provider: {name}")
                        results.append(f"Would create {name}.py")
                except Exception as e:
                    logger.error(f"Error creating provider {name}: {e}")
                    self.errors.append(f"Error creating provider {name}: {e}")
                    results.append(f"Error creating {name}.py: {e}")
        
        return {
            "status": "success" if not self.errors else "partial_success",
            "message": f"Provider installation {'would be completed' if self.safe_mode else 'completed'} with {len(results)} providers",
            "providers": results,
            "modified": list(map(str, self.modified_files)),
            "errors": self.errors,
            "safe_mode": self.safe_mode
        }
        
    def create_mcp_configuration(self) -> Dict[str, Any]:
        """Create MCP configuration files.
        
        Returns:
            Results of the configuration creation
        """
        config_dir = SYSTEM_PATH / "mcp" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        default_config = {
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
                "enabled_providers": ["openai_provider"]
            }
        }
        
        # Create config.json
        config_path = config_dir / "config.json"
        
        if not config_path.exists() or not self.safe_mode:
            try:
                if not self.safe_mode:
                    with open(config_path, "w") as f:
                        json.dump(default_config, f, indent=2)
                    
                    logger.info("Created MCP configuration file")
                    self.modified_files.add(config_path)
                else:
                    logger.info("[SAFE MODE] Would create MCP configuration file")
            except Exception as e:
                logger.error(f"Error creating configuration file: {e}")
                self.errors.append(f"Error creating configuration file: {e}")
                return {
                    "status": "error",
                    "message": f"Error creating configuration file: {e}",
                    "errors": self.errors
                }
        
        # Create run script
        run_script_path = SYSTEM_PATH / "mcp" / "run_mcp_server.py"
        
        if not run_script_path.exists() or not self.safe_mode:
            try:
                script_content = """#!/usr/bin/env python3
\"\"\"
MCP Server Runner

This script runs the MCP server using the configuration in config/config.json.
\"\"\"

import os
import sys
import json
import asyncio
import logging
import importlib
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

from mcp.unified_mcp_server import run_server, MCPModelProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-runner")

async def load_providers():
    \"\"\"Load model providers dynamically.
    
    Returns:
        Dictionary of loaded providers
    \"\"\"
    providers = {}
    
    # Load configuration
    config_path = Path(__file__).parent / "config" / "config.json"
    if not config_path.exists():
        logger.warning(f"Configuration file not found: {config_path}")
        return providers
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return providers
    
    # Get enabled providers
    enabled_providers = config.get("providers", {}).get("enabled_providers", [])
    
    # Provider directory
    provider_dir = Path(__file__).parent / "providers"
    sys.path.append(str(provider_dir.parent))
    
    # Try to load each provider
    for provider_name in enabled_providers:
        provider_path = provider_dir / f"{provider_name}.py"
        
        if not provider_path.exists():
            logger.warning(f"Provider not found: {provider_path}")
            continue
        
        try:
            # Import the provider module
            module_name = f"mcp.providers.{provider_name}"
            provider_module = importlib.import_module(module_name)
            
            # Get the provider instance
            if hasattr(provider_module, "provider"):
                provider_instance = provider_module.provider
                
                # Wrap the provider for each model type
                if hasattr(provider_instance, "__call__"):
                    # Create completion provider
                    async def completion_provider(request):
                        request["type"] = "completion"
                        return await provider_instance(request)
                    
                    # Create chat provider
                    async def chat_provider(request):
                        request["type"] = "chat"
                        return await provider_instance(request)
                    
                    # Create embedding provider
                    async def embedding_provider(request):
                        request["type"] = "embedding"
                        return await provider_instance(request)
                    
                    # Add list_models method to the providers if the original has it
                    if hasattr(provider_instance, "list_models"):
                        completion_provider.list_models = provider_instance.list_models
                        chat_provider.list_models = provider_instance.list_models
                        embedding_provider.list_models = provider_instance.list_models
                    
                    # Register the providers
                    providers["completion"] = completion_provider
                    providers["chat"] = chat_provider
                    providers["embedding"] = embedding_provider
                    
                    logger.info(f"Loaded provider: {provider_name}")
                else:
                    logger.warning(f"Provider {provider_name} has no __call__ method")
            else:
                logger.warning(f"Module {provider_name} has no 'provider' attribute")
        except Exception as e:
            logger.error(f"Error loading provider {provider_name}: {e}")
    
    return providers

async def main():
    \"\"\"Main entry point.\"\"\"
    # Load configuration
    config_path = Path(__file__).parent / "config" / "config.json"
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        config = {}
    
    # Get server configuration
    server_config = config.get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8080)
    metrics_port = server_config.get("metrics_port", 8081)
    log_level = server_config.get("log_level", "INFO")
    
    # Load providers
    providers = await load_providers()
    
    if not providers:
        logger.warning("No providers loaded, using dummy providers")
        # Add dummy providers
        async def dummy_completion_provider(request):
            await asyncio.sleep(0.5)  # Simulate processing
            return {
                "text": f"Dummy completion for: {request['prompt'][:30]}...",
                "usage": {"total_tokens": 20}
            }
            
        async def dummy_chat_provider(request):
            await asyncio.sleep(0.5)  # Simulate processing
            return {
                "message": {"role": "assistant", "content": "This is a dummy response"},
                "usage": {"total_tokens": 15}
            }
            
        providers = {
            "completion": dummy_completion_provider,
            "chat": dummy_chat_provider
        }
    
    # Run the server
    logger.info(f"Starting MCP server on {host}:{port}")
    await run_server(
        host=host,
        port=port,
        metrics_port=metrics_port,
        log_level=log_level,
        model_providers=providers
    )

if __name__ == "__main__":
    asyncio.run(main())
"""
                
                if not self.safe_mode:
                    with open(run_script_path, "w") as f:
                        f.write(script_content)
                    
                    # Make the script executable
                    os.chmod(run_script_path, 0o755)
                    
                    logger.info("Created MCP run script")
                    self.modified_files.add(run_script_path)
                else:
                    logger.info("[SAFE MODE] Would create MCP run script")
            except Exception as e:
                logger.error(f"Error creating run script: {e}")
                self.errors.append(f"Error creating run script: {e}")
                return {
                    "status": "error",
                    "message": f"Error creating run script: {e}",
                    "errors": self.errors
                }
        
        return {
            "status": "success",
            "message": f"MCP configuration {'would be created' if self.safe_mode else 'created'} successfully",
            "modified": list(map(str, self.modified_files)),
            "errors": self.errors,
            "safe_mode": self.safe_mode
        }

    def setup_mcp(self) -> Dict[str, Any]:
        """Set up the complete MCP environment.
        
        Returns:
            Results of the setup
        """
        logger.info("Starting MCP setup...")
        
        # 1. Check if MCP is already installed
        mcp_server_path = SYSTEM_PATH / "mcp" / "unified_mcp_server.py"
        if not mcp_server_path.exists():
            logger.error(f"MCP server not found at {mcp_server_path}")
            return {
                "status": "error",
                "message": f"MCP server not found. Run the initial setup first.",
                "errors": [f"MCP server not found at {mcp_server_path}"]
            }
            
        # 2. Install providers
        provider_result = self.install_model_providers()
        if provider_result["status"] == "error":
            logger.error("Failed to install model providers")
            return provider_result
            
        # 3. Create configuration
        config_result = self.create_mcp_configuration()
        if config_result["status"] == "error":
            logger.error("Failed to create MCP configuration")
            return config_result
            
        # 4. Integrate with existing servers
        integration_result = self.execute_integration_plan()
        
        # 5. Return results
        return {
            "status": "success",
            "message": "MCP setup completed successfully",
            "provider_setup": provider_result,
            "config_setup": config_result,
            "integration_setup": integration_result,
            "modified": list(map(str, self.modified_files)),
            "errors": self.errors,
            "safe_mode": self.safe_mode
        }


def setup_mcp_cli():
    """CLI entry point for MCP setup."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up MCP for the research infrastructure")
    parser.add_argument("--safe-mode", action="store_true", 
                      help="Run in safe mode (no file modifications)")
    parser.add_argument("--no-backup", action="store_true",
                      help="Skip backing up files before modification")
    parser.add_argument("--providers-only", action="store_true",
                      help="Only install model providers")
    parser.add_argument("--config-only", action="store_true",
                      help="Only create MCP configuration")
    parser.add_argument("--integration-only", action="store_true",
                      help="Only integrate MCP with existing servers")
    parser.add_argument("--verbose", "-v", action="store_true",
                      help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create integrator
    integrator = MCPIntegrator(
        backup=not args.no_backup,
        safe_mode=args.safe_mode
    )
    
    # Run requested actions
    if args.providers_only:
        result = integrator.install_model_providers()
    elif args.config_only:
        result = integrator.create_mcp_configuration()
    elif args.integration_only:
        result = integrator.execute_integration_plan()
    else:
        result = integrator.setup_mcp()
    
    # Print results
    if result["status"] == "success":
        print(f"\n✅ {result['message']}")
    elif result["status"] == "partial_success":
        print(f"\n⚠️ {result['message']}")
    else:
        print(f"\n❌ {result['message']}")
        
    if result.get("errors"):
        print("\nErrors encountered:")
        for error in result["errors"]:
            print(f"  - {error}")
            
    if args.safe_mode:
        print("\nSafe mode was enabled. No files were modified.")
        print("Run without --safe-mode to apply changes.")
    else:
        modified = result.get("modified", [])
        if modified:
            print("\nModified files:")
            for file in modified:
                print(f"  - {file}")
    
    return 0 if result["status"] != "error" else 1


if __name__ == "__main__":
    sys.exit(setup_mcp_cli())
