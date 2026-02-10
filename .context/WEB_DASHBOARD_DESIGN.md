# 🌐 A-Team Web Dashboard - Design Brief

## 📋 Project Overview

**Component**: Web Reflection Dashboard (`ateam web`)  
**Purpose**: Premium, glassmorphic web interface for real-time mission monitoring and project visualization  
**Target**: Dual-monitor power users who want visual observability alongside terminal workflow  
**Status**: New feature to be implemented  

---

## 🎯 Core Features (From README)

### 1. **Visual Timeline**
Watch mission progress with real-time message bubbles showing agent conversations

### 2. **Architectural Map**
View automatically indexed structure of the project side-by-side with chat

### 3. **Zero-Config**
Runs instantly via lightweight internal server (no setup required)

### 4. **Glassmorphic Design**
Premium aesthetic with frosted glass effects, subtle shadows, modern UI

---

## 🏗️ Technical Architecture

### Backend (Python FastAPI)

```python
# ateam/web/server.py
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
from pathlib import Path

class WebDashboard:
    """Lightweight web server for dashboard."""
    
    def __init__(self, room_manager, history_manager):
        self.app = FastAPI()
        self.room_manager = room_manager
        self.history_manager = history_manager
        self.active_connections = []
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Configure API endpoints and WebSocket."""
        
        @self.app.get("/")
        async def root():
            return HTMLResponse(content=self._get_dashboard_html())
        
        @self.app.get("/api/rooms")
        async def get_rooms():
            """List all active rooms with metadata."""
            return {
                "rooms": [
                    {
                        "name": room.name,
                        "message_count": room.message_count,
                        "last_active": room.last_active.isoformat(),
                        "lead_agent": room.lead_agent,
                        "tokens_used": room.total_tokens
                    }
                    for room in self.room_manager.list_rooms()
                ]
            }
        
        @self.app.get("/api/room/{room_name}/messages")
        async def get_room_messages(room_name: str):
            """Get message history for a room."""
            messages = self.history_manager.load_messages(room_name)
            return {
                "room": room_name,
                "messages": [
                    {
                        "id": msg.id,
                        "timestamp": msg.timestamp.isoformat(),
                        "role": msg.role,
                        "content": msg.content,
                        "agent_name": msg.agent_name,
                        "tokens": msg.tokens
                    }
                    for msg in messages
                ]
            }
        
        @self.app.get("/api/room/{room_name}/structure")
        async def get_project_structure(room_name: str):
            """Get auto-indexed project structure."""
            # Return the indexed file tree
            return {
                "structure": self._build_file_tree(room_name)
            }
        
        @self.app.websocket("/ws/{room_name}")
        async def websocket_endpoint(websocket: WebSocket, room_name: str):
            """Real-time updates via WebSocket."""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Send updates when new messages arrive
                    await websocket.send_json({
                        "type": "message",
                        "data": "..."
                    })
                    await asyncio.sleep(0.1)
            except:
                self.active_connections.remove(websocket)
    
    def run(self, host="127.0.0.1", port=8888):
        """Start the web server."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port, log_level="warning")
```

### Frontend (Single-Page App)

**Tech Stack**:
- Pure HTML/CSS/JavaScript (no build step - zero-config requirement)
- WebSocket for real-time updates
- CSS Grid for glassmorphic layout
- Fetch API for REST calls

---

## 🎨 Design System

### Color Palette (Dark Theme)

```css
:root {
  /* Glassmorphic Background */
  --bg-primary: rgba(10, 10, 15, 0.95);
  --bg-glass: rgba(255, 255, 255, 0.05);
  --bg-glass-hover: rgba(255, 255, 255, 0.08);
  
  /* Accents */
  --accent-primary: #00D9FF;      /* Cyan - for titles, highlights */
  --accent-secondary: #7B61FF;    /* Purple - for agent names */
  --accent-success: #00FF88;      /* Green - for success states */
  --accent-warning: #FFB800;      /* Amber - for warnings */
  --accent-error: #FF4757;        /* Red - for errors */
  
  /* Text */
  --text-primary: rgba(255, 255, 255, 0.95);
  --text-secondary: rgba(255, 255, 255, 0.65);
  --text-tertiary: rgba(255, 255, 255, 0.45);
  
  /* Borders */
  --border-glass: rgba(255, 255, 255, 0.1);
  --border-glow: rgba(0, 217, 255, 0.3);
  
  /* Shadows */
  --shadow-soft: 0 8px 32px rgba(0, 0, 0, 0.3);
  --shadow-glow: 0 0 20px rgba(0, 217, 255, 0.2);
}
```

### Typography

```css
/* Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
}

code, pre {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}

h1 { font-size: 28px; font-weight: 600; letter-spacing: -0.5px; }
h2 { font-size: 20px; font-weight: 600; letter-spacing: -0.3px; }
h3 { font-size: 16px; font-weight: 500; }
```

### Glassmorphic Components

```css
/* Glass Card */
.glass-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  box-shadow: var(--shadow-soft);
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
  background: var(--bg-glass-hover);
  border-color: var(--border-glow);
  box-shadow: var(--shadow-glow), var(--shadow-soft);
  transform: translateY(-2px);
}

/* Glowing Border */
.glow-border {
  position: relative;
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  overflow: hidden;
}

.glow-border::before {
  content: '';
  position: absolute;
  inset: -2px;
  background: linear-gradient(
    135deg,
    var(--accent-primary),
    var(--accent-secondary)
  );
  border-radius: 12px;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: -1;
}

.glow-border:hover::before {
  opacity: 0.2;
}
```

---

## 📐 Layout Structure

### Grid System (3-Column Layout)

```
┌─────────────────────────────────────────────────────────────┐
│                     TOP BAR (60px)                          │
│  A-Team Logo │ Room: mission-alpha │ 🔴 Live │ Settings    │
├──────────────┬────────────────────────────┬─────────────────┤
│              │                            │                 │
│   SIDEBAR    │     CHAT TIMELINE          │  PROJECT MAP    │
│   (280px)    │     (flex-grow)            │  (400px)        │
│              │                            │                 │
│ - Rooms List │  ┌─────────────────────┐  │  📁 src/        │
│ - Stats      │  │ @Architect:         │  │    📄 main.py   │
│ - Filters    │  │ Let's design...     │  │    📄 cli.py    │
│              │  └─────────────────────┘  │  📁 tests/      │
│              │                            │  📁 docs/       │
│              │  ┌─────────────────────┐  │                 │
│              │  │ @Coder:             │  │  Stats:         │
│              │  │ I'll implement...   │  │  - 24 files     │
│              │  └─────────────────────┘  │  - 1,240 lines  │
│              │                            │                 │
└──────────────┴────────────────────────────┴─────────────────┘
```

### Responsive Breakpoints

```css
/* Desktop (default) - 3 columns */
@media (min-width: 1440px) {
  .dashboard { grid-template-columns: 280px 1fr 400px; }
}

/* Laptop - 2 columns (hide project map) */
@media (max-width: 1439px) {
  .dashboard { grid-template-columns: 280px 1fr; }
  .project-map { display: none; }
}

/* Tablet - 1 column + collapsible sidebar */
@media (max-width: 1024px) {
  .dashboard { grid-template-columns: 1fr; }
  .sidebar { position: fixed; transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
}
```

---

## 🧩 Component Specifications

### 1. Sidebar (Room Navigator)

**Features**:
- List of all active rooms with live status indicators
- Filter by: Active, Archived, Starred
- Sort by: Recent, Alphabetical, Token Usage
- Quick stats per room

**Design**:
```html
<div class="sidebar glass-card">
  <div class="sidebar-header">
    <h2>Rooms</h2>
    <button class="icon-button">+</button>
  </div>
  
  <div class="room-filters">
    <button class="filter active">All</button>
    <button class="filter">Active</button>
    <button class="filter">Starred</button>
  </div>
  
  <div class="room-list">
    <div class="room-card active">
      <div class="room-info">
        <div class="room-name">mission-alpha</div>
        <div class="room-meta">
          <span class="lead-agent">@Architect</span>
          <span class="message-count">24 msgs</span>
        </div>
      </div>
      <div class="live-indicator">🔴 Live</div>
    </div>
    <!-- More rooms... -->
  </div>
  
  <div class="sidebar-stats">
    <div class="stat">
      <span class="stat-label">Total Tokens</span>
      <span class="stat-value">45.2K</span>
    </div>
    <div class="stat">
      <span class="stat-label">Active Agents</span>
      <span class="stat-value">3</span>
    </div>
  </div>
</div>
```

### 2. Chat Timeline (Main Panel)

**Features**:
- Real-time message stream with WebSocket
- Agent avatars with color coding
- Markdown rendering for messages
- Tool execution indicators
- Expandable code blocks with syntax highlighting

**Message Types**:
1. **User Message** - Light glass bubble, left-aligned
2. **Agent Message** - Darker glass bubble, agent-colored border
3. **System Message** - Subtle, centered, italic
4. **Tool Execution** - Special card with spinner/results

**Design**:
```html
<div class="chat-timeline">
  <div class="timeline-header">
    <h1>mission-alpha</h1>
    <div class="timeline-controls">
      <button>Export</button>
      <button>Refresh Index</button>
    </div>
  </div>
  
  <div class="messages-container">
    <!-- User Message -->
    <div class="message user">
      <div class="message-bubble glass-card">
        <div class="message-content">
          @Architect, design a REST API for user management
        </div>
        <div class="message-meta">
          <span class="timestamp">2:45 PM</span>
        </div>
      </div>
    </div>
    
    <!-- Agent Message -->
    <div class="message agent">
      <div class="agent-avatar" style="--agent-color: var(--accent-secondary)">
        A
      </div>
      <div class="message-bubble glass-card">
        <div class="message-header">
          <span class="agent-name">Architect</span>
          <span class="provider-badge">Gemini</span>
        </div>
        <div class="message-content markdown">
          I recommend a layered architecture with...
        </div>
        <div class="message-meta">
          <span class="timestamp">2:45 PM</span>
          <span class="token-count">1.2K tokens</span>
        </div>
      </div>
    </div>
    
    <!-- Tool Execution -->
    <div class="message tool-execution">
      <div class="tool-card glass-card">
        <div class="tool-header">
          <span class="tool-icon">🔧</span>
          <span class="tool-name">file_read</span>
          <span class="tool-status pending">Running...</span>
        </div>
        <div class="tool-details">
          <code>src/main.py</code>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Typing Indicator -->
  <div class="typing-indicator">
    <div class="agent-avatar">C</div>
    <div class="typing-dots">
      <span></span><span></span><span></span>
    </div>
  </div>
</div>
```

### 3. Project Map (Right Panel)

**Features**:
- Auto-indexed file tree (from workspace indexing)
- Collapsible directories
- File type icons
- Click to view file in modal
- Stats panel (file count, line count, language breakdown)

**Design**:
```html
<div class="project-map glass-card">
  <div class="map-header">
    <h2>Project Structure</h2>
    <button class="refresh-button">↻</button>
  </div>
  
  <div class="file-tree">
    <div class="tree-node directory expanded">
      <span class="node-icon">📁</span>
      <span class="node-name">src/</span>
      <div class="tree-children">
        <div class="tree-node file">
          <span class="node-icon">🐍</span>
          <span class="node-name">main.py</span>
          <span class="node-meta">240 lines</span>
        </div>
        <div class="tree-node file">
          <span class="node-icon">🐍</span>
          <span class="node-name">cli.py</span>
          <span class="node-meta">180 lines</span>
        </div>
      </div>
    </div>
  </div>
  
  <div class="project-stats">
    <div class="stat-grid">
      <div class="stat-item">
        <div class="stat-label">Files</div>
        <div class="stat-value">24</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">Lines</div>
        <div class="stat-value">1.2K</div>
      </div>
      <div class="stat-item">
        <div class="stat-label">Python</div>
        <div class="stat-value">85%</div>
      </div>
    </div>
  </div>
</div>
```

### 4. Top Bar (Global Navigation)

**Features**:
- A-Team logo (animated on hover)
- Current room name
- Live status indicator
- Global settings
- Keyboard shortcuts help

**Design**:
```html
<header class="top-bar glass-card">
  <div class="logo">
    <span class="logo-icon">🚀</span>
    <span class="logo-text">A-Team</span>
  </div>
  
  <div class="room-indicator">
    <span class="room-label">Room:</span>
    <span class="room-name">mission-alpha</span>
  </div>
  
  <div class="status-indicator live">
    <span class="pulse"></span>
    <span class="status-text">Live</span>
  </div>
  
  <div class="top-bar-actions">
    <button class="icon-button" title="Keyboard Shortcuts">⌨️</button>
    <button class="icon-button" title="Settings">⚙️</button>
  </div>
</header>
```

---

## 🎬 Animations & Interactions

### Smooth Transitions

```css
/* All interactive elements */
* {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Message entrance animation */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message {
  animation: slideIn 0.4s ease-out;
}

/* Live indicator pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.live-indicator .pulse {
  animation: pulse 2s infinite;
}

/* Typing indicator */
@keyframes typing {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
}

.typing-dots span {
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
```

### Hover Effects

```css
/* Glass card hover */
.glass-card:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 0 20px rgba(0, 217, 255, 0.2),
    0 8px 32px rgba(0, 0, 0, 0.3);
}

/* Room card hover */
.room-card:hover {
  background: var(--bg-glass-hover);
  border-left: 3px solid var(--accent-primary);
  padding-left: 21px; /* 24px - 3px border */
}

/* Button hover */
.icon-button:hover {
  background: var(--bg-glass);
  transform: scale(1.1);
}
```

---

## 🔌 Real-Time Updates (WebSocket)

### Client-Side WebSocket Handler

```javascript
class DashboardClient {
  constructor(roomName) {
    this.roomName = roomName;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }
  
  connect() {
    this.ws = new WebSocket(`ws://localhost:8888/ws/${this.roomName}`);
    
    this.ws.onopen = () => {
      console.log('🔌 Connected to A-Team Dashboard');
      this.reconnectAttempts = 0;
      this.updateConnectionStatus('connected');
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.updateConnectionStatus('error');
    };
    
    this.ws.onclose = () => {
      console.log('🔌 Disconnected from A-Team Dashboard');
      this.updateConnectionStatus('disconnected');
      this.attemptReconnect();
    };
  }
  
  handleMessage(data) {
    switch (data.type) {
      case 'message':
        this.addMessageToTimeline(data.message);
        break;
      case 'tool_execution':
        this.updateToolExecution(data.tool);
        break;
      case 'agent_typing':
        this.showTypingIndicator(data.agent);
        break;
      case 'structure_update':
        this.updateProjectStructure(data.structure);
        break;
    }
  }
  
  addMessageToTimeline(message) {
    const messagesContainer = document.querySelector('.messages-container');
    const messageEl = this.createMessageElement(message);
    messagesContainer.appendChild(messageEl);
    messageEl.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }
  
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
      setTimeout(() => {
        this.reconnectAttempts++;
        console.log(`🔄 Reconnecting... (attempt ${this.reconnectAttempts})`);
        this.connect();
      }, delay);
    }
  }
}

// Initialize on page load
const dashboard = new DashboardClient('mission-alpha');
dashboard.connect();
```

---

## 📱 Responsive Behavior

### Mobile View (< 768px)

```css
@media (max-width: 768px) {
  /* Stack everything vertically */
  .dashboard {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
  
  /* Sidebar becomes bottom drawer */
  .sidebar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60vh;
    transform: translateY(100%);
    transition: transform 0.3s;
    z-index: 1000;
  }
  
  .sidebar.open {
    transform: translateY(0);
  }
  
  /* Hide project map */
  .project-map {
    display: none;
  }
  
  /* Floating action button to open sidebar */
  .fab {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
}
```

---

## 🔧 Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] FastAPI server with basic routes
- [ ] WebSocket connection for real-time updates
- [ ] Static HTML/CSS/JS serving
- [ ] Room listing endpoint
- [ ] Message history endpoint

### Phase 2: Chat Timeline (Week 2)
- [ ] Message rendering with Markdown support
- [ ] Real-time message streaming
- [ ] Typing indicators
- [ ] Tool execution cards
- [ ] Syntax highlighting for code blocks

### Phase 3: Glassmorphic UI (Week 3)
- [ ] Complete CSS design system
- [ ] All glassmorphic components
- [ ] Animations and transitions
- [ ] Dark theme polish
- [ ] Responsive breakpoints

### Phase 4: Project Map (Week 4)
- [ ] File tree rendering
- [ ] Auto-index integration
- [ ] Collapsible directories
- [ ] File preview modal
- [ ] Project statistics

### Phase 5: Polish & Optimization (Week 5)
- [ ] Performance optimization
- [ ] Error handling UI
- [ ] Keyboard shortcuts
- [ ] Settings panel
- [ ] Help documentation
- [ ] Connection status indicators

---

## 🎯 Success Metrics

### Performance
- [ ] Initial page load: <2 seconds
- [ ] WebSocket message latency: <100ms
- [ ] Smooth 60fps animations
- [ ] File tree render: <500ms for 1000+ files

### UX
- [ ] Zero-config setup (just run `ateam web`)
- [ ] Works on Chrome, Firefox, Safari, Edge
- [ ] Responsive on desktop, tablet, mobile
- [ ] Accessible (keyboard navigation, screen readers)

### Visual Quality
- [ ] Premium glassmorphic aesthetic
- [ ] Consistent with A-Team brand
- [ ] Professional, not overwhelming
- [ ] Delightful micro-interactions

---

## 📦 Dependencies

### Backend
```python
# pyproject.toml additions
[project.dependencies]
fastapi = ">=0.104.0"
uvicorn = {extras = ["standard"], version = ">=0.24.0"}
websockets = ">=12.0"
```

### Frontend
```html
<!-- Zero external dependencies! Pure HTML/CSS/JS -->
<!-- Optional: Marked.js for Markdown rendering (CDN) -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

<!-- Optional: Highlight.js for syntax highlighting (CDN) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11/styles/github-dark.css">
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11/highlight.min.js"></script>
```

---

## 🚀 Launch Command

```bash
# Terminal command to start the web dashboard
ateam web

# Expected output:
# 🌐 Web Reflection Dashboard starting...
# ✓ Server running at http://localhost:8888
# ✓ Connected to room: mission-alpha
# → Open in browser: http://localhost:8888
```

---

## 🎨 Visual Examples

### Message Bubble (Agent)
```
╔══════════════════════════════════════════╗
║  Architect  [Gemini]                     ║
║──────────────────────────────────────────║
║                                          ║
║  I recommend a layered architecture      ║
║  with clear separation of concerns:      ║
║                                          ║
║  1. **API Layer** - FastAPI endpoints    ║
║  2. **Service Layer** - Business logic   ║
║  3. **Data Layer** - Database access     ║
║                                          ║
║──────────────────────────────────────────║
║  2:45 PM                      1.2K tokens║
╚══════════════════════════════════════════╝
```

### File Tree
```
📁 src/
  ├─ 🐍 main.py              (240 lines)
  ├─ 🐍 cli.py               (180 lines)
  ├─ 📁 core/
  │  ├─ 🐍 room.py           (150 lines)
  │  └─ 🐍 history.py        (200 lines)
  └─ 📁 providers/
     ├─ 🐍 gemini.py         (120 lines)
     └─ 🐍 ollama.py         (110 lines)
```

---

## ✅ Acceptance Criteria

Before considering the web dashboard complete:

- [ ] Can view all active rooms in sidebar
- [ ] Can switch between rooms in real-time
- [ ] Messages appear instantly via WebSocket
- [ ] Markdown renders correctly in messages
- [ ] Code blocks have syntax highlighting
- [ ] Project structure displays automatically
- [ ] File tree is collapsible/expandable
- [ ] Glassmorphic design is polished
- [ ] Animations are smooth (60fps)
- [ ] Works on desktop, tablet, mobile
- [ ] Zero-config (runs with `ateam web`)
- [ ] Connection status is visible
- [ ] Graceful reconnection on disconnect
- [ ] Keyboard shortcuts work
- [ ] Settings panel functional
- [ ] Export function generates report
- [ ] Performance targets met

---

**Built for power users who want visual observability without leaving their workflow.** 🌐✨
