# A-Team Technical Specifications

## Technology Stack

### Core Dependencies
- **Language**: Python 3.11+ (required for modern typing and performance)
- **CLI Framework**: `Typer 0.9+` (type-safe CLI with auto-completion)
- **Dependency Management**: `uv` (100x faster than pip)
- **MCP SDK**: `mcp` Python package for Model Context Protocol
- **HTTP Client**: `httpx` (async support for parallel API calls)
- **Configuration**: `pydantic-settings` (type-safe config validation)
- **Storage**: `aiosqlite` (async JSON-like document store with ACID guarantees)

### Development Dependencies
- `pytest` + `pytest-asyncio` for testing
- `ruff` for linting and formatting
- `mypy` for static type checking
- `rich` for beautiful terminal output

## System Architecture

### Component Diagram
```
┌─────────────────────────────────────────────────┐
│                  CLI Layer                      │
│            (Typer Commands)                     │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│              Core Engine                        │
│  ┌──────────────────────────────────────┐      │
│  │    RoomManager                       │      │
│  │  - create/load rooms                 │      │
│  │  - manage room lifecycle             │      │
│  └──────────────────────────────────────┘      │
│  ┌──────────────────────────────────────┐      │
│  │    MessageDispatcher                 │      │
│  │  - parse @tags                       │      │
│  │  - route to agents                   │      │
│  │  - handle multi-agent scenarios      │      │
│  └──────────────────────────────────────┘      │
│  ┌──────────────────────────────────────┐      │
│  │    HistoryManager                    │      │
│  │  - load/save messages                │      │
│  │  - context window management         │      │
│  │  - token counting                    │      │
│  └──────────────────────────────────────┘      │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│          Provider Adapters                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Gemini   │ │ Claude   │ │ OpenAI   │       │
│  │ Adapter  │ │ Adapter  │ │ Adapter  │       │
│  └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐                    │
│  │ Ollama   │ │ Custom   │                    │
│  │ Adapter  │ │ Provider │                    │
│  └──────────┘ └──────────┘                    │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│            MCP Tool Layer                       │
│  - Filesystem operations                        │
│  - Web search                                   │
│  - Code execution                               │
│  - Custom MCP servers                           │
└─────────────────────────────────────────────────┘
```

### Data Flow

#### Message Processing Pipeline
```
User Input
    ↓
[1] Parse & Validate
    ↓
[2] Extract @tags → Determine target agent(s)
    ↓
[3] Load room history → Apply context window limits
    ↓
[4] Build provider-specific payload
    │   ├─ Inject "A-Team System Prompt"
    │   ├─ Format history for provider
    │   └─ Add MCP tool definitions
    ↓
[5] Call provider API (with retry logic)
    ↓
[6] Process response
    │   ├─ Handle tool calls (MCP)
    │   ├─ Extract final text
    │   └─ Calculate token usage
    ↓
[7] Save to history with metadata
    ↓
[8] Display to user
```

## File System Structure

### Configuration Directory
```
~/.config/ateam/                    # Linux/macOS
%APPDATA%/ateam/                    # Windows

├── config.yaml                     # Global config
├── keyring.db                      # Encrypted API keys (via system keyring)
├── rooms/                          # All conversation rooms
│   ├── dev-project/
│   │   ├── history.db              # SQLite for ACID guarantees
│   │   ├── config.yaml             # Room-specific overrides
│   │   └── attachments/            # Files referenced in chat
│   └── ml-research/
│       └── history.db
├── cache/                          # Provider response cache
│   └── provider_cache.db
└── logs/
    └── ateam.log                   # Application logs
```

### Configuration Schema (`config.yaml`)
```yaml
version: "1.0"

# Global defaults
default_agent: "Architect"
context_window_size: 30  # messages to keep in context
auto_prune: true
confirm_file_operations: true

# Agent definitions
agents:
  Architect:
    provider: gemini
    model: gemini-2.0-flash
    api_key_env: GOOGLE_API_KEY  # or direct key (not recommended)
    system_prompt: |
      You are a senior software architect.
      Focus on scalability, maintainability, and best practices.
    temperature: 0.7
    max_tokens: 2048
    
  Coder:
    provider: ollama
    model: deepseek-r1:7b
    base_url: http://localhost:11434  # Ollama endpoint
    system_prompt: |
      You write clean, well-documented code.
      Always include error handling and type hints.
    
  Critic:
    provider: anthropic
    model: claude-sonnet-4
    api_key_env: ANTHROPIC_API_KEY
    system_prompt: |
      You provide constructive code reviews.
      Focus on edge cases, performance, and security.

# MCP tool configuration
mcp:
  filesystem:
    enabled: true
    allowed_paths:
      - "~/projects"
      - "~/Documents"
    dangerous_operations: ["delete", "chmod"]  # require confirmation
  
  web_search:
    enabled: true
    provider: brave  # or google, ddg
    
  code_execution:
    enabled: false  # disabled by default for security
    sandboxed: true
```

## Core Implementation Details

### 1. Context Injection ("Omniscience Prompt")
Every API call includes this system message:

```python
ATEAM_SYSTEM_PROMPT = """
You are {agent_name}, part of an A-Team multi-agent collaboration.

CONTEXT:
- Room: {room_name}
- Other agents in this room: {other_agents}
- You share conversation history with all agents
- When users mention @AgentName, they're addressing that specific agent

CAPABILITIES:
- You can see all previous messages from users and other agents
- You have access to MCP tools: {available_tools}
- You can reference previous responses by saying "As @AgentName mentioned..."

GUIDELINES:
- Stay in character based on your role: {agent_role}
- Build on what other agents have said
- If a task is better suited for another agent, suggest tagging them
- Be concise but thorough
"""
```

### 2. Provider Adapter Interface
All providers implement this abstract base class:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ProviderAdapter(ABC):
    """Base class for all AI provider integrations."""
    
    @abstractmethod
    async def send_message(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        tools: List[Dict[str, Any]] | None = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a message to the provider.
        
        Returns:
            {
                "content": str,
                "tool_calls": List[Dict] | None,
                "usage": {"prompt_tokens": int, "completion_tokens": int}
            }
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Return model capabilities (context length, supports tools, etc.)"""
        pass
```

### 3. History Storage with SQLite
Why SQLite over JSON:
- ACID guarantees (no corruption from crashes)
- Efficient querying (get last N messages without loading all)
- Concurrent access handling
- Full-text search for message content

Schema:
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    agent_name TEXT,
    model_used TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    metadata TEXT  -- JSON blob for extensibility
);

CREATE INDEX idx_timestamp ON messages(timestamp);
CREATE INDEX idx_agent ON messages(agent_name);
```

### 4. Token Management Strategy
```python
import tiktoken
from typing import List, Dict

class ContextWindowManager:
    """Manages message history to fit within token limits with intelligent pruning."""
    
    def __init__(self, max_tokens: int = 100_000):
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.reserve_tokens = 4096  # Reserve for response
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        return len(self.tokenizer.encode(text))
    
    def get_total_tokens(self, messages: List[Dict]) -> int:
        """Calculate total tokens across all messages."""
        total = 0
        for msg in messages:
            total += self.count_tokens(msg.get("content", ""))
        return total
    
    def prune_history(
        self,
        messages: List[Dict],
        system_prompt_tokens: int = 0
    ) -> tuple[List[Dict], int]:
        """
        Smart pruning to fit context window while preserving important context.
        
        Strategy:
        1. Always keep: first message (room context), last 5 messages
        2. Summarize middle messages when needed
        3. Return pruned messages and tokens removed
        
        Returns:
            (pruned_messages, tokens_removed)
        """
        total_tokens = self.get_total_tokens(messages) + system_prompt_tokens
        available_tokens = self.max_tokens - self.reserve_tokens
        
        if total_tokens <= available_tokens:
            return messages, 0
        
        # Identify messages to keep
        if len(messages) <= 6:
            # Can't prune if too few messages
            raise ContextOverflowError(
                f"Cannot fit {len(messages)} messages in context. "
                f"Total: {total_tokens:,} tokens, Available: {available_tokens:,} tokens"
            )
        
        first_msg = messages[0]
        last_msgs = messages[-5:]
        middle_msgs = messages[1:-5]
        
        # Calculate tokens for kept messages
        kept_tokens = (
            self.count_tokens(first_msg["content"]) +
            sum(self.count_tokens(m["content"]) for m in last_msgs) +
            system_prompt_tokens
        )
        
        # Summarize middle if we have space
        summary = self._create_summary(middle_msgs)
        summary_tokens = self.count_tokens(summary)
        
        if kept_tokens + summary_tokens <= available_tokens:
            # Insert summary between first and last messages
            summary_msg = {
                "role": "system",
                "content": summary,
                "agent_name": "System",
                "is_summary": True
            }
            pruned = [first_msg, summary_msg] + last_msgs
            tokens_removed = total_tokens - (kept_tokens + summary_tokens)
            return pruned, tokens_removed
        
        # If even summary doesn't fit, drop middle entirely
        pruned = [first_msg] + last_msgs
        tokens_removed = total_tokens - kept_tokens
        return pruned, tokens_removed
    
    def _create_summary(self, messages: List[Dict]) -> str:
        """Create a summary of middle messages."""
        if not messages:
            return ""
        
        # Group by agent
        by_agent = {}
        for msg in messages:
            agent = msg.get("agent_name", "User")
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append(msg)
        
        summary_parts = [
            "[Earlier conversation summary - not verbatim]",
            ""
        ]
        
        for agent, agent_msgs in by_agent.items():
            topics = self._extract_topics(agent_msgs)
            summary_parts.append(
                f"@{agent} discussed: {', '.join(topics)}"
            )
        
        return "\n".join(summary_parts)
    
    def _extract_topics(self, messages: List[Dict], max_topics: int = 3) -> List[str]:
        """Extract main topics from messages (simplified version)."""
        # In production, could use LLM to generate summary
        # For now, just take first few words from each message
        topics = []
        for msg in messages[:max_topics]:
            content = msg.get("content", "")
            # Get first sentence or 10 words
            first_part = content.split(".")[0][:50]
            if first_part and first_part not in topics:
                topics.append(first_part + "...")
        return topics or ["general discussion"]
    
    def should_warn_about_limit(self, current_tokens: int) -> bool:
        """Check if we should warn user about approaching context limit."""
        threshold = self.max_tokens * 0.85  # Warn at 85%
        return current_tokens >= threshold

class ContextOverflowError(Exception):
    """Raised when context cannot be pruned to fit."""
    pass
```

### 5. MCP Tool Integration
```python
from mcp import Server, Tool
from enum import Enum
from typing import List, Set

class PermissionMode(Enum):
    """Permission modes for file operations."""
    ALWAYS_ASK = "always_ask"
    SELECTIVE = "selective"  # Default - smart rules
    TRUSTED = "trusted"      # Auto-approve in allowed paths

class FileOperation(Enum):
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    CHMOD = "chmod"
    MOVE = "move"

class FileSystemTool(Tool):
    """MCP tool for file operations with smart permissions."""
    
    def __init__(self, config: dict):
        self.permission_mode = PermissionMode(
            config.get("permission_mode", "selective")
        )
        self.allowed_paths = config.get("allowed_paths", [])
        self.auto_approve_ops = set(config.get("auto_approve", {}).get("operations", []))
        self.dangerous_ops = set(config.get("dangerous_operations", ["delete", "chmod", "move"]))
        self.pending_batch = []
    
    async def execute(
        self,
        operation: str,
        path: str,
        content: str = None,
        batch_mode: bool = False
    ):
        """Execute file operation with permission checking."""
        
        # Validate path is in allowed directories
        if not self._is_path_allowed(path):
            return {
                "error": f"Access denied: {path} is outside allowed directories",
                "allowed_paths": self.allowed_paths
            }
        
        op_enum = FileOperation(operation.lower())
        
        # Batch mode - accumulate operations for bulk approval
        if batch_mode:
            self.pending_batch.append({
                "operation": op_enum,
                "path": path,
                "content": content
            })
            return {"status": "batched", "count": len(self.pending_batch)}
        
        # Check if approval needed
        if self._needs_approval(op_enum, path):
            if not await self._request_approval(op_enum, path, content):
                return {"error": "Operation denied by user"}
        
        # Execute operation
        try:
            result = await self._execute_operation(op_enum, path, content)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    def _needs_approval(self, operation: FileOperation, path: str) -> bool:
        """Determine if operation needs user approval."""
        
        if self.permission_mode == PermissionMode.ALWAYS_ASK:
            return True
        
        if self.permission_mode == PermissionMode.TRUSTED:
            # Still confirm dangerous operations
            return operation.value in self.dangerous_ops
        
        # SELECTIVE mode (smart rules)
        if operation.value in self.dangerous_ops:
            return True
        
        # Check auto-approve rules
        if operation == FileOperation.READ:
            return False  # Always allow reading
        
        if operation == FileOperation.CREATE:
            return False  # New files are safe
        
        if operation == FileOperation.WRITE:
            # Writing to existing files - check if sensitive
            return self._is_sensitive_file(path)
        
        return True
    
    def _is_sensitive_file(self, path: str) -> bool:
        """Check if file is sensitive (env, keys, etc.)."""
        sensitive_patterns = [
            ".env", ".key", ".pem", ".cert",
            "secret", "password", "credentials"
        ]
        path_lower = path.lower()
        return any(pattern in path_lower for pattern in sensitive_patterns)
    
    async def _request_approval(
        self,
        operation: FileOperation,
        path: str,
        content: str = None
    ) -> bool:
        """Request user approval for operation."""
        
        # Display friendly prompt
        op_description = {
            FileOperation.DELETE: "delete",
            FileOperation.CHMOD: "change permissions of",
            FileOperation.MOVE: "move",
            FileOperation.WRITE: "modify"
        }
        
        action = op_description.get(operation, operation.value)
        message = f"\n🔐 Permission required: {action} {path}"
        
        if content and operation == FileOperation.WRITE:
            preview = content[:100] + "..." if len(content) > 100 else content
            message += f"\nContent preview: {preview}"
        
        message += "\nAllow? [y/n]: "
        
        response = await self._get_user_input(message)
        return response.lower() in ['y', 'yes']
    
    async def approve_batch(self) -> dict:
        """Request approval for batched operations."""
        if not self.pending_batch:
            return {"error": "No pending operations"}
        
        # Group by operation type
        by_op = {}
        for item in self.pending_batch:
            op = item["operation"].value
            if op not in by_op:
                by_op[op] = []
            by_op[op].append(item["path"])
        
        # Display summary
        print("\n🔐 Batch operation approval requested:")
        for op, paths in by_op.items():
            print(f"\n{op.upper()}:")
            for path in paths[:5]:  # Show first 5
                print(f"  - {path}")
            if len(paths) > 5:
                print(f"  ... and {len(paths) - 5} more")
        
        print("\nOptions:")
        print("  [y] Approve all")
        print("  [n] Deny all")
        print("  [r] Review individually")
        
        response = await self._get_user_input("\nChoice: ")
        
        if response.lower() == 'y':
            results = await self._execute_batch(self.pending_batch)
            self.pending_batch = []
            return {"status": "approved", "results": results}
        
        elif response.lower() == 'r':
            results = await self._review_batch(self.pending_batch)
            self.pending_batch = []
            return {"status": "reviewed", "results": results}
        
        else:
            self.pending_batch = []
            return {"status": "denied"}
    
    def _is_path_allowed(self, path: str) -> bool:
        """Check if path is within allowed directories."""
        from pathlib import Path
        path_obj = Path(path).resolve()
        
        for allowed in self.allowed_paths:
            allowed_obj = Path(allowed).expanduser().resolve()
            try:
                path_obj.relative_to(allowed_obj)
                return True
            except ValueError:
                continue
        
        return False
    
    async def _execute_operation(
        self,
        operation: FileOperation,
        path: str,
        content: str = None
    ):
        """Execute the actual file operation."""
        from pathlib import Path
        
        path_obj = Path(path)
        
        if operation == FileOperation.READ:
            return path_obj.read_text()
        
        elif operation == FileOperation.WRITE:
            path_obj.write_text(content)
            return f"Wrote {len(content)} bytes"
        
        elif operation == FileOperation.CREATE:
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            path_obj.write_text(content or "")
            return f"Created {path}"
        
        elif operation == FileOperation.DELETE:
            path_obj.unlink()
            return f"Deleted {path}"
        
        elif operation == FileOperation.CHMOD:
            # content should be octal mode like "755"
            import os
            os.chmod(path, int(content, 8))
            return f"Changed permissions to {content}"
        
        elif operation == FileOperation.MOVE:
            # content should be destination path
            path_obj.rename(content)
            return f"Moved to {content}"
        
        raise ValueError(f"Unknown operation: {operation}")
```

## Cross-Platform Considerations

### Path Handling
```python
from pathlib import Path
import platformdirs

def get_config_dir() -> Path:
    """Get platform-specific config directory."""
    return Path(platformdirs.user_config_dir("ateam", "ateam-cli"))

def get_data_dir() -> Path:
    """Get platform-specific data directory."""
    return Path(platformdirs.user_data_dir("ateam", "ateam-cli"))
```

### Terminal Compatibility
- Use `rich` library for cross-platform colored output
- Fallback to plain text if terminal doesn't support colors
- Handle Ctrl+C gracefully on all platforms

### API Key Management
```python
import keyring  # cross-platform secure storage
from typing import Optional

class APIKeyManager:
    """Secure API key storage and retrieval."""
    
    SERVICE_NAME = "ateam-cli"
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Try multiple sources in order of preference:
        1. System keyring (most secure)
        2. Environment variable
        3. Config file (warn about security)
        """
        # 1. System keyring
        key = keyring.get_password(self.SERVICE_NAME, provider)
        if key:
            return key
        
        # 2. Environment variable
        env_var = f"{provider.upper()}_API_KEY"
        key = os.getenv(env_var)
        if key:
            return key
        
        # 3. Config file (with security warning)
        key = self._load_from_config(provider)
        if key:
            self._warn_insecure_storage()
            return key
        
        return None
    
    def set_api_key(self, provider: str, key: str, validate: bool = True) -> bool:
        """
        Store API key securely and optionally validate it.
        
        Returns:
            True if key was saved (and validated if requested)
        """
        if validate:
            if not self._validate_key(provider, key):
                raise ValueError(f"Invalid API key for {provider}")
        
        keyring.set_password(self.SERVICE_NAME, provider, key)
        return True
    
    def _validate_key(self, provider: str, key: str) -> bool:
        """Test API key with a minimal API call."""
        # Implementation varies by provider
        pass

class ErrorMessages:
    """Actionable error messages with fix instructions."""
    
    @staticmethod
    def invalid_api_key(provider: str, env_var: str, key_url: str) -> str:
        return f"""
⚠ {provider.title()} API Error: Invalid API key

This means: Your {env_var} is incorrect or expired

Fix it:
1. Get a new key: {key_url}
2. Run: ateam config set-key {provider}
   Or: export {env_var}="your-key"
3. Verify: ateam config test-keys

Need help? https://docs.ateam.dev/troubleshooting#api-keys
""".strip()
    
    @staticmethod
    def ollama_not_running() -> str:
        return """
⚠ Cannot connect to Ollama

This means: Ollama service is not running on localhost:11434

Fix it:
1. Install Ollama: https://ollama.com/download
2. Start service: ollama serve
3. Verify: ollama list

Alternative: Use cloud providers instead
  - Run: ateam config enable gemini
  - Or configure Claude/GPT in config.yaml

Need help? https://docs.ateam.dev/troubleshooting#ollama
""".strip()
    
    @staticmethod
    def context_limit_reached(current: int, max_tokens: int) -> str:
        return f"""
⚠ Context limit reached ({current:,} / {max_tokens:,} tokens)

This means: The conversation is too long for the model's context window

Options:
1. Auto-prune: Continue (oldest messages will be summarized)
2. Export and start fresh: ateam export <room> && ateam join <new-room>
3. Manual cleanup: ateam prune <room> --keep=20

Tip: Use shorter messages or switch to a model with larger context
""".strip()
    
    @staticmethod
    def model_not_found(model: str, provider: str) -> str:
        if provider == "ollama":
            return f"""
⚠ Model not found: {model}

This means: The model isn't pulled in Ollama

Fix it:
1. Pull the model: ollama pull {model}
2. Or list available: ollama list
3. Update config.yaml with an available model

Popular models: deepseek-r1:7b, qwen2.5-coder:7b, codellama:13b
""".strip()
        else:
            return f"""
⚠ Model not found: {model}

This means: The model doesn't exist or you don't have access

Fix it:
1. Check available models: https://docs.ateam.dev/models#{provider}
2. Update config.yaml with a valid model name
3. Verify your API tier has access to this model
""".strip()
```

## Performance Requirements

### Latency Targets
- **CLI startup**: <200ms (lazy-load heavy imports)
- **History loading**: <100ms for 1000 messages
- **First API call**: <2s (network dependent)
- **Message save**: <50ms (async write)

### Optimization Strategies
- Async I/O for all network calls
- Connection pooling for HTTP clients
- Lazy loading of provider adapters
- SQLite with WAL mode for concurrent reads
- Cache tokenizer instances

### Memory Management
- Stream large responses instead of loading fully
- Clear message cache after context window pruning
- Limit in-memory history to current room only

## Security Considerations

### Security Principles
A-Team handles sensitive data (API keys, user files, conversation history) and must follow security best practices:

1. **Defense in Depth**: Multiple layers of security controls
2. **Principle of Least Privilege**: Minimal permissions by default
3. **Fail Secure**: Errors default to denying access
4. **Security by Design**: Built-in from the start, not bolted on

### 1. Rate Limiting

**Why**: Prevent abuse, protect API quotas, avoid DoS attacks

**Implementation**:
```python
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class RateLimiter:
    """Rate limiter for API calls and user actions."""
    
    def __init__(self):
        # IP-based rate limits (for future web interface)
        self.ip_attempts = defaultdict(list)
        
        # User action rate limits (CLI)
        self.user_actions = defaultdict(list)
        
        # Provider-specific API rate limits
        self.provider_calls = defaultdict(list)
    
    async def check_api_limit(
        self,
        provider: str,
        limit: int = 100,  # calls per minute
        window: int = 60   # seconds
    ) -> bool:
        """
        Check if API call is within rate limit.
        
        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window)
        
        # Clean old entries
        self.provider_calls[provider] = [
            ts for ts in self.provider_calls[provider] if ts > cutoff
        ]
        
        # Check limit
        if len(self.provider_calls[provider]) >= limit:
            wait_time = (self.provider_calls[provider][0] - cutoff).total_seconds()
            raise RateLimitError(
                f"Rate limit exceeded for {provider}. "
                f"Try again in {wait_time:.0f} seconds."
            )
        
        # Record this call
        self.provider_calls[provider].append(now)
        return True
    
    async def check_user_action_limit(
        self,
        action: str,
        limit: int = 10,
        window: int = 60
    ) -> bool:
        """
        Prevent rapid-fire user actions (spam protection).
        
        Example: Limit room creation to 10/minute
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window)
        
        key = f"user:{action}"
        self.user_actions[key] = [
            ts for ts in self.user_actions[key] if ts > cutoff
        ]
        
        if len(self.user_actions[key]) >= limit:
            raise RateLimitError(
                f"Too many {action} attempts. Please wait a moment."
            )
        
        self.user_actions[key].append(now)
        return True

class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass

# Usage example:
rate_limiter = RateLimiter()

async def call_provider(provider: str, messages: list):
    """API call with rate limiting."""
    await rate_limiter.check_api_limit(provider, limit=100, window=60)
    # Make actual API call...
```

**Configuration** (add to config.yaml):
```yaml
rate_limits:
  api_calls:
    gemini: {limit: 100, window: 60}      # 100/minute (free tier)
    anthropic: {limit: 50, window: 60}    # 50/minute
    openai: {limit: 60, window: 60}       # 60/minute
  
  user_actions:
    room_creation: {limit: 10, window: 60}
    message_send: {limit: 100, window: 60}
    file_operations: {limit: 50, window: 60}

# Graceful degradation when limits hit
rate_limit_behavior:
  show_retry_after: true
  auto_retry_with_backoff: true
  max_retries: 3
```

### 2. Input Validation & Sanitization

**Why**: Prevent injection attacks, path traversal, malformed data

**Implementation**:
```python
from pydantic import BaseModel, Field, validator, constr
from pathlib import Path
import re

class InputValidator:
    """Centralized input validation with schema-based checks."""
    
    # Regex patterns for validation
    AGENT_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]{0,48}[a-zA-Z0-9]$')
    ROOM_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]{2,48}[a-zA-Z0-9]$')
    
    @staticmethod
    def validate_room_name(name: str) -> str:
        """
        Validate room name format.
        
        Rules:
        - 3-50 characters
        - Alphanumeric, hyphens, underscores
        - Must start and end with alphanumeric
        - No path separators, no spaces
        """
        if not name:
            raise ValueError("Room name cannot be empty")
        
        if len(name) < 3:
            raise ValueError("Room name must be at least 3 characters")
        
        if len(name) > 50:
            raise ValueError("Room name must be 50 characters or less")
        
        if not InputValidator.ROOM_NAME_PATTERN.match(name):
            raise ValueError(
                "Room name must contain only letters, numbers, hyphens, and underscores. "
                "Must start and end with a letter or number."
            )
        
        # Block reserved names
        reserved = ['config', 'system', 'admin', 'root', 'test', 'tmp']
        if name.lower() in reserved:
            raise ValueError(f"'{name}' is a reserved name")
        
        return name
    
    @staticmethod
    def validate_agent_name(name: str) -> str:
        """Validate agent name (similar rules to room name)."""
        if not InputValidator.AGENT_NAME_PATTERN.match(name):
            raise ValueError(
                "Agent name must be 2-50 characters, alphanumeric with hyphens/underscores"
            )
        return name
    
    @staticmethod
    def validate_file_path(path: str, allowed_dirs: list[str]) -> Path:
        """
        Validate file path and prevent path traversal attacks.
        
        Security checks:
        - Resolve to absolute path
        - Check for path traversal attempts (.., symlinks)
        - Verify path is within allowed directories
        - Block access to sensitive files
        """
        try:
            # Resolve to absolute path (handles .., ~, symlinks)
            path_obj = Path(path).expanduser().resolve()
        except (ValueError, RuntimeError) as e:
            raise ValueError(f"Invalid path: {e}")
        
        # Check for path traversal
        if '..' in path:
            raise ValueError("Path traversal attempts are not allowed")
        
        # Verify path is in allowed directories
        allowed = False
        for allowed_dir in allowed_dirs:
            allowed_dir_resolved = Path(allowed_dir).expanduser().resolve()
            try:
                path_obj.relative_to(allowed_dir_resolved)
                allowed = True
                break
            except ValueError:
                continue
        
        if not allowed:
            raise ValueError(
                f"Access denied: {path_obj} is outside allowed directories"
            )
        
        # Block sensitive files
        sensitive_patterns = [
            '/etc/passwd', '/etc/shadow', '/.ssh/', '/.aws/',
            '.env', '.key', '.pem', 'id_rsa', 'credentials'
        ]
        path_str = str(path_obj).lower()
        for pattern in sensitive_patterns:
            if pattern in path_str:
                raise ValueError(f"Access to sensitive file denied: {path}")
        
        return path_obj
    
    @staticmethod
    def sanitize_message(content: str, max_length: int = 50000) -> str:
        """
        Sanitize user message content.
        
        Checks:
        - Length limits (prevent DoS)
        - No null bytes
        - Normalize whitespace
        """
        if not content:
            raise ValueError("Message cannot be empty")
        
        # Remove null bytes (can cause issues in some systems)
        content = content.replace('\x00', '')
        
        # Check length
        if len(content) > max_length:
            raise ValueError(
                f"Message too long: {len(content)} chars (max: {max_length})"
            )
        
        # Normalize excessive whitespace (keep formatting, but prevent abuse)
        # Allow up to 3 consecutive newlines
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        
        return content.strip()

# Pydantic models for type-safe validation
class RoomCreate(BaseModel):
    """Schema for room creation."""
    name: constr(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9][a-zA-Z0-9_-]+[a-zA-Z0-9]$')
    
    @validator('name')
    def validate_name(cls, v):
        return InputValidator.validate_room_name(v)

class MessageInput(BaseModel):
    """Schema for message input."""
    content: constr(min_length=1, max_length=50000)
    agent_tags: list[str] = Field(default_factory=list)
    
    @validator('content')
    def sanitize_content(cls, v):
        return InputValidator.sanitize_message(v)
    
    @validator('agent_tags')
    def validate_agents(cls, v):
        return [InputValidator.validate_agent_name(name) for name in v]

class FileOperation(BaseModel):
    """Schema for file operations."""
    operation: str
    path: constr(min_length=1, max_length=1000)
    content: str | None = None
    
    @validator('operation')
    def validate_operation(cls, v):
        allowed = ['read', 'write', 'create', 'delete', 'chmod', 'move']
        if v not in allowed:
            raise ValueError(f"Invalid operation: {v}")
        return v
```

**Usage in CLI**:
```python
@app.command()
def join(room_name: str):
    """Join a room with validation."""
    try:
        # Validate before processing
        validated_name = InputValidator.validate_room_name(room_name)
        room = room_manager.create_or_load(validated_name)
        # ... continue
    except ValueError as e:
        console.print(f"[red]Invalid room name: {e}[/red]")
        raise typer.Exit(1)
```

### 3. API Key Security

**Why**: Leaked keys = unauthorized access, unexpected bills, data breaches

**Implementation**:
```python
import keyring
import os
from typing import Optional
import logging

class SecureAPIKeyManager:
    """Secure API key storage following OWASP best practices."""
    
    SERVICE_NAME = "ateam-cli"
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Never log key values
        self.logger.addFilter(self._filter_secrets)
    
    @staticmethod
    def _filter_secrets(record):
        """Filter API keys from logs."""
        # Redact patterns that look like API keys
        patterns = [
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI keys
            r'sk-ant-[a-zA-Z0-9-]{95}',  # Anthropic keys
            r'AIza[a-zA-Z0-9_-]{35}',  # Google API keys
        ]
        
        message = record.getMessage()
        for pattern in patterns:
            message = re.sub(pattern, '[REDACTED]', message)
        
        record.msg = message
        return True
    
    def store_key(self, provider: str, key: str, validate: bool = True) -> bool:
        """
        Securely store API key in system keyring.
        
        Security measures:
        1. Validate key format before storing
        2. Test key with API call if validate=True
        3. Use system keyring (encrypted storage)
        4. Never write to logs or config files
        """
        # Validate key format
        if not self._validate_key_format(provider, key):
            raise ValueError(f"Invalid key format for {provider}")
        
        # Optionally validate with API
        if validate:
            if not self._test_api_key(provider, key):
                raise ValueError(f"API key validation failed for {provider}")
        
        # Store in system keyring (encrypted)
        try:
            keyring.set_password(self.SERVICE_NAME, provider, key)
            self.logger.info(f"API key stored securely for {provider}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to store key: {e}")
            raise
    
    def get_key(self, provider: str) -> Optional[str]:
        """
        Retrieve API key with fallback chain.
        
        Order of precedence:
        1. System keyring (most secure)
        2. Environment variable
        3. Config file (with security warning)
        """
        # 1. Try keyring first
        key = keyring.get_password(self.SERVICE_NAME, provider)
        if key:
            return key
        
        # 2. Try environment variable
        env_var = f"{provider.upper()}_API_KEY"
        key = os.getenv(env_var)
        if key:
            self.logger.info(f"Using API key from environment: {env_var}")
            return key
        
        # 3. Config file (warn about insecurity)
        key = self._get_from_config(provider)
        if key:
            self.logger.warning(
                f"⚠️  API key for {provider} is stored in config file. "
                f"This is insecure! Use keyring or environment variables."
            )
            return key
        
        return None
    
    def rotate_key(self, provider: str, new_key: str) -> bool:
        """
        Rotate API key (best practice: rotate regularly).
        
        Steps:
        1. Validate new key
        2. Test new key with API
        3. Store new key
        4. Delete old key
        """
        # Validate and test new key
        if not self._test_api_key(provider, new_key):
            raise ValueError("New API key failed validation")
        
        # Store new key
        self.store_key(provider, new_key, validate=False)
        
        self.logger.info(f"API key rotated for {provider}")
        return True
    
    def delete_key(self, provider: str) -> bool:
        """Securely delete API key."""
        try:
            keyring.delete_password(self.SERVICE_NAME, provider)
            self.logger.info(f"API key deleted for {provider}")
            return True
        except keyring.errors.PasswordDeleteError:
            self.logger.warning(f"No key found to delete for {provider}")
            return False
    
    def _validate_key_format(self, provider: str, key: str) -> bool:
        """Validate API key format (basic check)."""
        patterns = {
            'openai': r'^sk-[a-zA-Z0-9]{48}$',
            'anthropic': r'^sk-ant-[a-zA-Z0-9-]{95}$',
            'google': r'^AIza[a-zA-Z0-9_-]{35}$',
        }
        
        pattern = patterns.get(provider.lower())
        if pattern:
            return bool(re.match(pattern, key))
        
        # For unknown providers, just check it's not empty
        return bool(key and len(key) > 10)
    
    def _test_api_key(self, provider: str, key: str) -> bool:
        """Test API key with minimal API call."""
        # Implementation varies by provider
        # Should make smallest possible API call to validate
        pass

# Environment variable handling
class SecureEnvironment:
    """Secure environment variable management."""
    
    @staticmethod
    def load_env_file(path: str = ".env"):
        """
        Load .env file securely.
        
        Security measures:
        1. Check file permissions (should be 600)
        2. Warn if world-readable
        3. Never log contents
        """
        env_path = Path(path)
        
        if not env_path.exists():
            return
        
        # Check permissions
        if os.name != 'nt':  # Unix-like systems
            mode = env_path.stat().st_mode
            if mode & 0o044:  # World or group readable
                logging.warning(
                    f"⚠️  .env file has insecure permissions: {oct(mode)}\n"
                    f"   Run: chmod 600 {path}"
                )
        
        # Load without logging
        with env_path.open() as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
```

**Best Practices Enforced**:

1. ✅ **Never hard-code keys** in source code
2. ✅ **Use system keyring** for encrypted storage
3. ✅ **Environment variables** as fallback
4. ✅ **Config files** discouraged (with warnings)
5. ✅ **API keys never logged** (filter in logging)
6. ✅ **Keys validated** before storage
7. ✅ **Key rotation** supported
8. ✅ **No client-side exposure** (CLI only, no web UI yet)

**Configuration** (add to config.yaml):
```yaml
security:
  api_keys:
    storage_preference: keyring  # keyring > env > config
    validate_on_store: true
    warn_on_config_file_keys: true
    auto_rotate_reminder_days: 90
    
  key_exposure_prevention:
    filter_from_logs: true
    filter_from_error_messages: true
    filter_from_stack_traces: true
```

### 4. Additional Security Measures

**SQL Injection Prevention** (already handled by SQLite parameterization):
```python
# GOOD - Parameterized queries
cursor.execute(
    "INSERT INTO messages (content, agent) VALUES (?, ?)",
    (content, agent_name)
)

# BAD - String interpolation (never do this)
# cursor.execute(f"INSERT INTO messages VALUES ('{content}', '{agent}')")
```

**Command Injection Prevention**:
```python
# When executing external commands (like Ollama)
import subprocess
import shlex

def safe_command_execution(command: list[str]) -> str:
    """Execute external command safely."""
    # Use list form (not string) to prevent injection
    # Validate each argument
    validated_command = [shlex.quote(arg) for arg in command]
    
    try:
        result = subprocess.run(
            validated_command,
            capture_output=True,
            text=True,
            timeout=30,  # Prevent hanging
            check=True
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        raise SecurityError("Command execution timeout")
    except subprocess.CalledProcessError as e:
        raise SecurityError(f"Command failed: {e}")
```

**SSRF Prevention** (if adding web search):
```python
BLOCKED_IPS = [
    '127.0.0.0/8',      # Localhost
    '10.0.0.0/8',       # Private network
    '172.16.0.0/12',    # Private network
    '192.168.0.0/16',   # Private network
    '169.254.0.0/16',   # Link-local
]

def validate_url(url: str) -> bool:
    """Prevent SSRF attacks."""
    from urllib.parse import urlparse
    import ipaddress
    
    parsed = urlparse(url)
    
    # Block non-HTTP(S)
    if parsed.scheme not in ['http', 'https']:
        raise ValueError("Only HTTP(S) URLs allowed")
    
    # Block private IPs
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        for blocked_range in BLOCKED_IPS:
            if ip in ipaddress.ip_network(blocked_range):
                raise ValueError("Access to private IPs not allowed")
    except ValueError:
        pass  # Not an IP, probably a domain
    
    return True
```

### Security Checklist

Before each release, verify:

- [ ] **Rate limiting** implemented on all public endpoints
- [ ] **Input validation** on all user inputs (schema-based)
- [ ] **API keys** never in logs, errors, or stack traces
- [ ] **File paths** validated and sandboxed
- [ ] **SQL queries** use parameterization (no string interpolation)
- [ ] **External commands** use list form with argument validation
- [ ] **Sensitive files** (.env, .key, etc.) have correct permissions
- [ ] **Error messages** don't leak sensitive information
- [ ] **Dependencies** scanned for vulnerabilities (`pip-audit`)
- [ ] **Security tests** in test suite
- [ ] **OWASP Top 10** reviewed and mitigated

### Security Testing

```python
# tests/security/test_input_validation.py
def test_path_traversal_prevention():
    """Ensure path traversal attacks are blocked."""
    malicious_paths = [
        '../../../etc/passwd',
        '~/../../etc/passwd',
        '/etc/passwd',
        'allowed_dir/../../etc/passwd',
    ]
    
    for path in malicious_paths:
        with pytest.raises(ValueError, match="outside allowed"):
            InputValidator.validate_file_path(path, ['~/projects'])

def test_sql_injection_prevention():
    """Ensure SQL injection is not possible."""
    malicious_input = "'; DROP TABLE messages; --"
    
    # Should be safely escaped
    history_manager.append_message({
        'content': malicious_input,
        'role': 'user'
    })
    
    # Table should still exist
    assert history_manager.get_message_count() > 0

def test_api_key_logging_prevention():
    """Ensure API keys are never logged."""
    with patch('logging.Logger._log') as mock_log:
        api_key = "sk-test-key-1234567890abcdef"
        key_manager.store_key('test', api_key)
        
        # Check no log contains the actual key
        for call in mock_log.call_args_list:
            log_message = str(call)
            assert api_key not in log_message
            assert '[REDACTED]' in log_message or 'test' not in log_message
```

## Testing Strategy

### Unit Tests
```python
# Example test structure
def test_message_dispatcher_single_tag():
    dispatcher = MessageDispatcher(agents=mock_agents)
    result = dispatcher.parse_tags("@Architect, design a system")
    assert result.target_agent == "Architect"
    assert result.clean_message == "design a system"

async def test_gemini_adapter_retry_logic():
    adapter = GeminiAdapter(max_retries=3)
    # Simulate network failure
    # Verify exponential backoff
    # ...
```

### Integration Tests
- Test full message flow with mock APIs
- Verify history persistence across sessions
- Test concurrent room access

### End-to-End Tests
- Automated CLI interaction tests
- Real API calls (with test accounts)

## Deployment & Distribution

### Package Structure
```
pyproject.toml
├── [project]
├── name = "ateam-cli"
├── version = "0.1.0"
├── dependencies = [...]
├── [project.scripts]
└── ateam = "ateam.cli:app"
```

### Installation Methods
1. **PyPI**: `pip install ateam-cli`
2. **uv**: `uv tool install ateam-cli`
3. **Git**: `pip install git+https://github.com/user/ateam.git`
4. **Source**: `git clone ... && pip install .`

### Platform-Specific Installers
- **Windows**: `.msi` installer (optional)
- **macOS**: Homebrew formula (optional)
- **Linux**: `.deb` and `.rpm` packages (optional)
