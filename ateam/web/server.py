"""
Zero-dependency Web Server for A-Team Reflection.
Uses FastAPI and WebSockets to provide a live dashboard.
"""

import json
import asyncio
from pathlib import Path
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ateam.core import RoomManager, WorkspaceIndexer

# Resolve static directory relative to this file
STATIC_DIR = Path(__file__).parent

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

def create_app() -> FastAPI:
    app = FastAPI(title="A-Team Reflection")

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Room Manager
    room_manager = RoomManager()
    
    # Workspace Indexer
    indexer = WorkspaceIndexer()

    @app.get("/")
    async def root():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/rooms")
    async def get_rooms():
        """List all active rooms with metadata."""
        rooms = room_manager.list_rooms()
        return [r.model_dump() for r in rooms]

    @app.get("/api/history")
    async def get_history(room: str):
        """Get message history for a room."""
        try:
            history_mgr = room_manager.get_history(room)
            # Get last 50 messages
            msgs = history_mgr.get_history(limit=50)
            return [
                {
                    "role": m.role,
                    "content": m.content,
                    "agent_tag": m.agent_tag,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in msgs
            ]
        except Exception as e:
            return {"error": str(e)}

    @app.get("/api/summary")
    async def get_summary():
        """Get workspace summary."""
        indexer.refresh()
        return indexer.get_summary()
        
    @app.get("/api/structure")
    async def get_structure():
        """Get project file structure."""
        # Simple file tree implementation
        # In a real scenario, this would come from indexer or a recursive scan
        # For now, we'll scan the current working directory (excluding .git, venv, etc.)
        
        root_path = Path.cwd()
        ignore_dirs = {'.git', '.venv', 'venv', '__pycache__', '.idea', '.vscode', 'node_modules'}
        
        def build_tree(path: Path):
            tree = {
                "name": path.name,
                "type": "directory" if path.is_dir() else "file",
                "path": str(path.relative_to(root_path)),
            }
            
            if path.is_dir():
                children = []
                try:
                    for item in path.iterdir():
                        if item.name in ignore_dirs:
                            continue
                        children.append(build_tree(item))
                except PermissionError:
                    pass
                
                # Sort: directories first, then files
                children.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
                tree["children"] = children
                
            return tree
            
        return build_tree(root_path)

    @app.websocket("/ws/{room_name}")
    async def websocket_endpoint(websocket: WebSocket, room_name: str):
        await manager.connect(websocket)
        try:
            while True:
                # Keep connection alive
                # In a real implementation, we would listen for events 
                # (like new messages in the DB) and broadcast them.
                # For now, simple echo or keep-alive
                data = await websocket.receive_text()
                # await manager.broadcast(f"Client says: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    # Mount static files - MUST be last to avoid overriding API routes
    app.mount("/", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return app

app = create_app()

def start_server(host="127.0.0.1", port=8080):
    """Start the web server."""
    print(f"🚀 A-Team Reflection Live at: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="warning")

if __name__ == "__main__":
    start_server()
