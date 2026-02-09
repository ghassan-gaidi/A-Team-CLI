# A-Team Implementation Roadmap

## How to Use This File
- Each task has a clear **acceptance criteria** (how to verify it's done)
- Tasks are ordered by dependency (don't skip ahead)
- Check off tasks as you complete them
- Estimated time is for an AI IDE with human guidance

---

## Phase 1: Foundation & Project Setup
**Goal**: Get a working CLI that can create and enter rooms with proper setup  
**Estimated Time**: 3-4 hours

### 1.1 Project Initialization
- [ ] **Task**: Create `pyproject.toml` with project metadata
  - **Acceptance**: File exists with name, version, Python requirement (3.11+)
  - **Dependencies**: `typer`, `rich`, `httpx`, `pydantic`, `pydantic-settings`, `keyring`, `tiktoken`, `aiosqlite`
  - **Script entry point**: `ateam = "ateam.cli:app"`
  - **Test**: Run `uv pip install -e .` without errors

- [ ] **Task**: Create basic project structure
  ```
  ateam/
  ├── pyproject.toml
  ├── README.md
  ├── ateam/
  │   ├── __init__.py
  │   ├── cli.py          # Typer app
  │   ├── core/
  │   │   ├── __init__.py
  │   │   ├── room.py     # RoomManager
  │   │   ├── history.py  # HistoryManager (SQLite)
  │   │   ├── config.py   # ConfigManager
  │   │   ├── context.py  # ContextWindowManager
  │   │   └── keys.py     # APIKeyManager
  │   ├── providers/
  │   │   ├── __init__.py
  │   │   └── base.py     # ProviderAdapter ABC
  │   └── utils/
  │       ├── __init__.py
  │       ├── paths.py    # Platform-specific paths
  │       └── errors.py   # ErrorMessages catalog
  └── tests/
      └── __init__.py
  ```
  - **Acceptance**: All files exist, imports work
  - **Test**: `python -c "import ateam"`

### 1.2 API Key Management & Configuration

- [ ] **Task**: Implement `SecureAPIKeyManager` class in `core/keys.py`
  - **Security features**:
    - Store keys in system keyring (encrypted)
    - Never log key values (implement log filter)
    - Validate key format before storing
    - Test key with minimal API call
    - Support key rotation
  - **Methods**:
    - `store_key(provider, key, validate=True) -> bool`
    - `get_key(provider) -> Optional[str]` (keyring → env → config)
    - `rotate_key(provider, new_key) -> bool`
    - `delete_key(provider) -> bool`
  - **Acceptance**: 
    - Can store key in system keyring securely
    - Keys never appear in logs or error messages
    - Validates key with actual API call
    - Warns if using insecure config file storage
  - **Test**: 
    - Store key, verify not in logs
    - Test invalid key rejection
    - Verify keyring → env → config fallback order

- [ ] **Task**: Implement `InputValidator` class in `utils/validation.py`
  - **Validates**:
    - Room names (3-50 chars, alphanumeric + hyphens/underscores)
    - Agent names (2-50 chars, same rules)
    - File paths (prevent path traversal, whitelist check)
    - Message content (length limits, sanitization)
  - **Security checks**:
    - Path traversal prevention (.., symlinks)
    - Null byte removal
    - Reserved name blocking
    - Sensitive file blocking
  - **Acceptance**:
    - Rejects path traversal attempts
    - Blocks access to /etc/passwd, ~/.ssh/, etc.
    - Validates all user inputs with Pydantic schemas
  - **Test**: 
    - Try '../../../etc/passwd' (should fail)
    - Try valid and invalid room names
    - Test all edge cases

- [ ] **Task**: Implement `RateLimiter` class in `core/rate_limit.py`
  - **Rate limits**:
    - API calls (100/min for Gemini, 50/min for Claude, etc.)
    - User actions (10 room creations/min, 100 messages/min)
    - File operations (50/min)
  - **Features**:
    - Sliding window algorithm
    - Configurable limits per provider
    - Graceful degradation (show retry-after time)
    - Auto-retry with exponential backoff
  - **Acceptance**:
    - Blocks requests exceeding limit
    - Shows clear error with retry time
    - Cleans up old entries automatically
  - **Test**:
    - Make 101 API calls in 1 minute (101st should fail)
    - Verify retry-after message
    - Test backoff behavior

- [ ] **Task**: Create `ErrorMessages` class in `utils/errors.py`
  - **Include messages for**:
    - Invalid API key (with fix steps)
    - Rate limit exceeded (with retry time)
    - Ollama not running
    - Model not found
    - Context limit reached
    - Path access denied
    - Invalid input format
  - **Format**: "What happened" + "Why" + "How to fix" + "Help link"
  - **Security**: Never include sensitive data in errors (API keys, file paths)
  - **Acceptance**: Each error includes actionable instructions
  - **Test**: Generate each error type, verify formatting and security

- [ ] **Task**: Create `ConfigManager` class in `core/config.py`
  - **Acceptance**: 
    - Loads `config.yaml` if exists
    - Returns default config if file missing
    - Validates schema with Pydantic
    - Supports permission_mode for MCP tools
  - **Schema**: Agent dict with provider, model, system_prompt, trust_level
  - **Test**: Load valid config, load invalid config (should error), load missing file

- [ ] **Task**: Implement `ateam init` command with interactive setup
  - **Flow**:
    1. Welcome message
    2. Detect internet connection
    3. Ask which providers to use (checkboxes)
    4. For each selected provider:
       - Prompt for API key
       - Validate immediately with test call
       - Store in keyring if valid
    5. Check for Ollama (optional)
    6. Create default config.yaml
    7. Display success + next steps
  - **Acceptance**:
    - Interactive multi-select for providers
    - API keys validated before saving
    - Ollama detection doesn't block setup
    - Config file has working agent definitions
  - **Test**: Run `ateam init`, go through flow, verify keys work

- [ ] **Task**: Add `ateam config` subcommands
  - `ateam config show` - Display current configuration
  - `ateam config set-key <provider>` - Add/update API key
  - `ateam config test-keys` - Validate all configured keys
  - `ateam config enable <provider>` - Add provider to config
  - **Acceptance**: Each command works and provides helpful output
  - **Test**: Run each command, verify behavior

### 1.3 Room Management
- [ ] **Task**: Implement `RoomManager` class in `core/room.py`
  - **Methods needed**:
    - `create_room(name: str) -> Room`
    - `load_room(name: str) -> Room | None`
    - `list_rooms() -> List[str]`
  - **Acceptance**:
    - Creates directory at `~/.config/ateam/rooms/<name>/`
    - Returns Room object with path and metadata
  - **Test**: Create room, verify directory exists, load same room

- [ ] **Task**: Implement `ateam join <room>` command
  - **Acceptance**:
    - Creates room if doesn't exist
    - Loads existing room and displays summary
    - Enters interactive mode (prints prompt: `You:`)
  - **Test**: `ateam join test-room`, verify directory created

- [ ] **Task**: Implement `ateam rooms` command
  - **Acceptance**: Lists all rooms with message counts
  - **Output format**: 
    ```
    Available rooms:
    - dev-project (24 messages)
    - ml-research (8 messages)
    ```
  - **Test**: Create 3 rooms, run `ateam rooms`

### 1.4 History Management (SQLite with ACID)
- [ ] **Task**: Implement `HistoryManager` class in `core/history.py`
  - **Storage**: SQLite database (not JSON - better concurrency, ACID guarantees)
  - **Schema**:
    ```sql
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
        content TEXT NOT NULL,
        agent_name TEXT,
        model_used TEXT,
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        is_summary BOOLEAN DEFAULT 0,
        metadata TEXT  -- JSON blob for extensibility
    );
    CREATE INDEX idx_timestamp ON messages(timestamp);
    CREATE INDEX idx_agent ON messages(agent_name);
    ```
  - **Methods**:
    - `load_messages() -> List[Message]`
    - `append_message(msg: Message) -> None`
    - `get_recent(n: int) -> List[Message]`
    - `get_total_tokens() -> int`
    - `delete_last(n: int) -> None` (for undo)
  - **Acceptance**: Can save and load messages, preserves order, handles concurrent access
  - **Test**: Save 5 messages, reload, verify all present, test token counting

- [ ] **Task**: Add graceful error handling for corrupted database
  - **Acceptance**:
    - Detects corrupted SQLite DB
    - Creates backup of corrupted file
    - Initializes fresh database with warning
  - **Test**: Manually corrupt DB file, load room, verify backup created

- [ ] **Task**: Implement `ContextWindowManager` in `core/context.py`
  - **Methods**:
    - `count_tokens(text: str) -> int`
    - `get_total_tokens(messages: List[Dict]) -> int`
    - `prune_history(messages, system_prompt_tokens) -> (pruned_msgs, tokens_removed)`
    - `should_warn_about_limit(current_tokens) -> bool`
  - **Smart pruning**:
    - Keep first message (room context)
    - Keep last 5 messages (recent context)
    - Summarize middle messages
  - **Acceptance**:
    - Accurate token counting with tiktoken
    - Pruned history fits in limits
    - Important messages preserved
  - **Test**: Create 50-message history, prune to fit 10K tokens, verify kept messages

---

## Phase 2: Agent Orchestration & Providers
**Goal**: Route messages to specific AI agents  
**Estimated Time**: 4-5 hours

### 2.1 Message Parsing & Routing
- [ ] **Task**: Implement tag parser in `MessageDispatcher` class
  - **Location**: `ateam/core/dispatcher.py`
  - **Method**: `parse_tags(message: str) -> ParseResult`
  - **ParseResult** should contain:
    - `target_agents: List[str]` (extracted from @tags)
    - `clean_message: str` (message with tags removed or preserved based on mode)
    - `mode: str` ("single", "sequential", "parallel")
  - **Acceptance**:
    - `"@Architect, help"` → `["Architect"]`, `"help"`, "single"
    - `"@A @B go"` → `["A", "B"]`, `"go"`, "sequential"
    - `"@A @B --parallel go"` → `["A", "B"]`, `"go"`, "parallel"
    - `"no tags here"` → `[]`, `"no tags here"`, "single"
  - **Test**: Unit test with 10+ edge cases

- [ ] **Task**: Implement sequential multi-agent routing logic
  - **Flow for `@A @B @C`**:
    1. Route to Agent A, get response
    2. Save A's response to history
    3. Route to Agent B (sees A's response in context)
    4. Save B's response to history
    5. Route to Agent C (sees A and B's responses)
    6. Display all responses to user
  - **UI Display**:
    ```
    → Routing to Architect first...
    Architect (Gemini): Here's the design...
    
    → Routing to Coder (can see Architect's response)...
    Coder (DeepSeek): Implementing the design...
    
    ✓ All agents responded
    ```
  - **Acceptance**: Multiple agents respond in sequence, each seeing previous responses
  - **Test**: Mock 3 agents, verify each sees previous context

- [ ] **Task**: Implement parallel mode routing (optional --parallel flag)
  - **Flow for `@A @B --parallel`**:
    1. Route to both agents simultaneously (async)
    2. Display both responses as they arrive
    3. Save both to history
  - **UI Display**:
    ```
    ⚡ Parallel mode: Both agents responding independently
    
    [Architect typing...]
    [Coder typing...]
    
    --- Architect (Gemini) ---
    Pros: scalability...
    
    --- Coder (DeepSeek) ---
    Implementation approach...
    ```
  - **Acceptance**: Agents respond independently in parallel
  - **Test**: Mock 2 agents with different response times

- [ ] **Task**: Implement default agent routing
  - **Rules**:
    - No tags → use default agent from config
    - Configurable default in config.yaml
  - **Acceptance**: Returns correct agent name given parsed tags
  - **Test**: Mock config with 3 agents, test all routing scenarios

### 2.2 Provider Adapter Architecture
- [ ] **Task**: Create `ProviderAdapter` ABC in `providers/base.py`
  - **Abstract methods**:
    - `async send_message(messages, system_prompt, tools) -> Response`
    - `get_model_info() -> ModelInfo`
  - **Response schema**:
    ```python
    {
      "content": str,
      "tool_calls": List[Dict] | None,
      "usage": {"prompt_tokens": int, "completion_tokens": int}
    }
    ```
  - **Acceptance**: Class cannot be instantiated (is abstract)
  - **Test**: Try instantiating, should raise TypeError

### 2.3 Gemini Provider (First Implementation)
- [ ] **Task**: Implement `GeminiAdapter` in `providers/gemini.py`
  - **Dependencies**: `google-generativeai` SDK
  - **Configuration**: Load API key from env (`GOOGLE_API_KEY`)
  - **Methods**:
    - Format A-Team system prompt
    - Convert message history to Gemini format
    - Call `model.generate_content_async()`
    - Extract response and token usage
  - **Acceptance**:
    - Can send a simple message and get response
    - Returns token usage
    - Handles API errors gracefully
  - **Test**: Mock API call, verify request format

- [ ] **Task**: Add retry logic with exponential backoff
  - **Acceptance**:
    - Retries 3 times on network errors
    - Waits 1s, 2s, 4s between retries
    - Raises clear error after exhausting retries
  - **Test**: Mock failing API, verify retry behavior

### 2.4 Ollama Provider (Local Models - Optional)
- [ ] **Task**: Implement `OllamaAdapter` in `providers/ollama.py`
  - **Endpoint**: `http://localhost:11434/api/chat` (configurable)
  - **Format**: OpenAI-compatible chat format
  - **Detection**: Check if Ollama is running before using
  - **Acceptance**:
    - Gracefully handles Ollama not being installed
    - Checks if Ollama is running (ping endpoint)
    - Sends message in correct format
    - Handles "model not found" error with helpful message
  - **Test**: Mock HTTP responses, verify error handling

- [ ] **Task**: Add model availability check
  - **Method**: `list_available_models() -> List[str]`
  - **Endpoint**: `/api/tags`
  - **Acceptance**: Returns list of pulled models
  - **Test**: Mock response with 3 models, verify parsing

- [ ] **Task**: Add Ollama detection utility
  - **Location**: `utils/ollama_detect.py`
  - **Method**: `is_ollama_available() -> tuple[bool, str]`
  - **Returns**: (is_available, message)
  - **Messages**:
    - Not installed: "Ollama not found. Install from https://ollama.com"
    - Not running: "Ollama installed but not running. Start with: ollama serve"
    - Running but no models: "Ollama running. Pull models with: ollama pull <model>"
    - Ready: "Ollama ready with N models available"
  - **Acceptance**: Provides actionable status message
  - **Test**: Mock each scenario, verify correct detection

### 2.5 Wire It All Together
- [ ] **Task**: Implement interactive chat loop in `ateam join`
  - **Flow**:
    1. User types message
    2. Parse tags → determine agent(s) and mode
    3. Load history → build context
    4. Display token counter
    5. Call provider(s) → get response(s)
    6. Save to history
    7. Display response with agent name and updated token count
  - **Display format**:
    ```
    [Context: 12.5K / 100K tokens | 15 messages]
    You: @Architect, design an API
    
    Architect (Gemini): Here's my design...
    
    [Context: 15.2K / 100K tokens | 16 messages]
    You: _
    ```
  - **Acceptance**: Full conversation works end-to-end with token tracking
  - **Test**: Manual test - have 3-turn conversation, verify tokens increase

- [ ] **Task**: Add context limit warning
  - **Trigger**: When context exceeds 85% of max tokens
  - **Display**:
    ```
    ⚠ Context approaching limit (87K / 100K tokens)
    Oldest messages will be summarized on next interaction.
    
    Options:
    - Continue (auto-prune)
    - Export and start fresh: ateam export <room>
    - Manual cleanup: ateam prune <room>
    ```
  - **Acceptance**: Warning appears at 85%, provides actionable options
  - **Test**: Fill context to 86%, verify warning appears

- [ ] **Task**: Add "exit" command to leave room
  - **Acceptance**: Typing `exit` or `quit` closes room gracefully
  - **Display**: "Saved conversation. Exited room: <name>"
  - **Test**: Join room, type `exit`, verify clean shutdown

---

## Phase 3: Shared Context & MCP Tools
**Goal**: Make agents aware of each other, add filesystem access  
**Estimated Time**: 5-6 hours

### 3.1 Context Window Management
- [ ] **Task**: Implement "Omniscience Prompt" injection
  - **Template**: See `technical.md` for full prompt
  - **Variables to inject**:
    - `{agent_name}`, `{room_name}`, `{other_agents}`, `{available_tools}`
  - **Acceptance**: System prompt includes room context
  - **Test**: Inspect actual API payload, verify prompt present

- [ ] **Task**: Add token counting utility
  - **Library**: `tiktoken` (OpenAI's tokenizer)
  - **Method**: `count_tokens(text: str, model: str) -> int`
  - **Acceptance**: Accurate within 5% for test strings
  - **Test**: Count tokens for known strings, compare to OpenAI's counter

- [ ] **Task**: Implement context window pruning
  - **Strategy**: Keep last N messages that fit in token budget
  - **Always preserve**:
    - First message (room intro)
    - Last 5 messages (recent context)
  - **Acceptance**:
    - Pruned history fits in max_tokens - reserve_tokens
    - Recent messages always included
  - **Test**: Create 100-message history, prune to 50, verify kept messages

### 3.2 MCP Integration - Filesystem Tool
- [ ] **Task**: Add `mcp` SDK to dependencies
  - **Package**: `mcp` (Model Context Protocol)
  - **Acceptance**: `pip install -e .` succeeds with mcp
  - **Test**: `python -c "import mcp"`

- [ ] **Task**: Implement `FileSystemTool` class with smart permissions
  - **Location**: `ateam/mcp/filesystem.py`
  - **Operations**: `read`, `write`, `create`, `delete`, `chmod`, `move`
  - **Permission modes**:
    - `always_ask`: Confirm every operation
    - `selective` (default): Smart rules (auto-approve safe ops)
    - `trusted`: Only confirm dangerous operations
  - **Smart rules**:
    - Read operations: Always auto-approve
    - Create new files: Auto-approve
    - Write to existing: Confirm if sensitive file (.env, .key, etc.)
    - Delete/chmod/move: Always confirm
  - **Safety**: Whitelist allowed directories from config
  - **Acceptance**:
    - Can read file in allowed directory
    - Blocks access outside allowed paths
    - Smart rules work correctly
    - Sensitive files require confirmation
  - **Test**: Try reading allowed file, try reading /etc/passwd (should fail), test each permission mode

- [ ] **Task**: Add batch operation support
  - **Feature**: When agent creates multiple files, batch approval
  - **UI**:
    ```
    🔐 Batch operation approval requested:
    
    CREATE:
      - main.py
      - utils.py
      - tests/test_utils.py
      ... and 2 more
    
    Options:
      [y] Approve all
      [n] Deny all
      [r] Review individually
    
    Choice: y
    ```
  - **Acceptance**: Multiple operations can be approved at once
  - **Test**: Create 5 files in batch, verify single approval

- [ ] **Task**: Integrate MCP tools into provider calls
  - **Changes needed**:
    - ProviderAdapter includes `tools` parameter
    - Convert MCP tool schema to provider format (OpenAI function calling)
    - Handle tool call responses (execute and return results)
  - **Acceptance**: Agent can call file tool and receive results
  - **Test**: Ask Gemini to "read README.md", verify it calls tool

- [ ] **Task**: Add permission configuration to config.yaml
  - **Settings**:
    ```yaml
    mcp:
      filesystem:
        permission_mode: selective  # always_ask, selective, trusted
        allowed_paths:
          - "~/projects"
        auto_approve:
          - read
          - create
        dangerous_operations:
          - delete
          - chmod
    ```
  - **Acceptance**: Config controls permission behavior
  - **Test**: Change mode, verify behavior changes

### 3.3 Agent Context Awareness
- [ ] **Task**: Add agent attribution to history display
  - **Format**: 
    ```
    You: @Architect, design a system
    
    Architect (Gemini): Here's my proposed architecture...
    
    You: @Coder, implement that
    
    Coder (DeepSeek): I'll start with the core module...
    ```
  - **Acceptance**: Each message shows which agent responded
  - **Test**: Multi-agent conversation, verify labels correct

- [ ] **Task**: Enable cross-agent references
  - **Feature**: Agent prompts include previous agent names
  - **Example system prompt addition**:
    ```
    Recent agents in this conversation:
    - @Architect (last spoke 2 messages ago)
    - @Critic (last spoke 5 messages ago)
    
    You can reference their ideas by mentioning their name.
    ```
  - **Acceptance**: Agents naturally reference each other
  - **Test**: Ask Coder to "implement Architect's suggestion", verify it works

---

## Phase 4: Polish & Distribution
**Goal**: Make it production-ready and shareable  
**Estimated Time**: 3-4 hours

### 4.1 CLI Enhancements
- [ ] **Task**: Add colorized output with `rich`
  - **Elements to colorize**:
    - User prompts (cyan)
    - Agent names (green)
    - Errors (red)
    - System messages (yellow)
    - Token counter (dim white/gray)
  - **Acceptance**: Terminal output is readable and attractive
  - **Test**: Run conversation, verify colors appear (or plain text on unsupported terminals)

- [ ] **Task**: Add progress indicators for API calls
  - **Display**: Spinner with text "Waiting for Architect..."
  - **Library**: `rich.spinner`
  - **Acceptance**: Shows while waiting, disappears on response
  - **Test**: Mock slow API, verify spinner displays

- [ ] **Task**: Implement `ateam export <room>` command with multiple formats
  - **Formats**:
    - `--format=md` (default): Markdown with formatting
    - `--format=html`: HTML with syntax highlighting
    - `--format=json`: JSON for programmatic access
    - `--format=pdf`: PDF for sharing (optional, requires reportlab)
  - **Filename**: `<room>_export_<timestamp>.<format>`
  - **Acceptance**: Creates readable transcript in each format
  - **Test**: Export room with 10 messages, verify formatting in each format

- [ ] **Task**: Add `ateam stats` command with detailed metrics
  - **Displays**:
    - Total tokens used per agent
    - Total API calls per agent
    - Cost estimate (if API pricing known)
    - Most active room
    - Tokens over time (simple chart with rich)
  - **Acceptance**: Shows accurate statistics
  - **Test**: Create data across multiple rooms, run stats, verify calculations

- [ ] **Task**: Implement `ateam undo [N]` command
  - **Functionality**:
    - `ateam undo` - Remove last message
    - `ateam undo 3` - Remove last 3 messages
  - **Safety**: 
    - Confirm before removing multiple messages
    - Don't allow undo of first message (room context)
  - **Display**:
    ```
    Removed last message from Architect
    Context: 15.2K → 12.8K tokens
    ```
  - **Acceptance**: Messages removed from history, tokens recalculated
  - **Test**: Add 5 messages, undo 2, verify history and tokens correct

- [ ] **Task**: Add keyboard shortcuts for interactive mode
  - **Shortcuts**:
    - `Ctrl+C`: Cancel current input (not exit)
    - `Ctrl+D`: Exit room
    - `Ctrl+L`: Clear screen
    - `↑/↓`: Navigate input history
  - **Library**: `prompt_toolkit` for advanced input
  - **Acceptance**: Shortcuts work as expected
  - **Test**: Try each shortcut in interactive mode

### 4.2 Error Handling & Validation
- [ ] **Task**: Add input validation for room names
  - **Rules**: Alphanumeric + hyphens, 3-50 chars, lowercase
  - **Acceptance**: Rejects invalid names with helpful error
  - **Test**: Try `ateam join "my room!"` (should fail)

- [ ] **Task**: Add helpful error messages for common issues
  - **Scenarios**:
    - Missing API key → "Add GOOGLE_API_KEY to environment"
    - Ollama not running → "Start Ollama with: ollama serve"
    - Unknown agent tag → "Did you mean: @Architect?"
  - **Acceptance**: Errors are actionable, not cryptic
  - **Test**: Trigger each scenario, verify message quality

- [ ] **Task**: Add API key validation on `ateam init`
  - **Check**: Attempt to call each configured provider
  - **Report**: Which agents are ready vs. which need setup
  - **Acceptance**: User knows immediately what needs fixing
  - **Test**: Run init with missing keys, verify report

### 4.3 Testing & Quality

- [ ] **Task**: Write unit tests for core components
  - **Coverage targets**:
    - `MessageDispatcher`: 100% (critical logic)
    - `HistoryManager`: 90%
    - `RoomManager`: 80%
    - `InputValidator`: 95% (security-critical)
    - `SecureAPIKeyManager`: 90% (security-critical)
    - `RateLimiter`: 85%
  - **Use**: `pytest` with `pytest-cov`
  - **Acceptance**: All tests pass, coverage meets targets
  - **Test**: `pytest --cov=ateam tests/`

- [ ] **Task**: Add integration tests
  - **Scenarios**:
    - Full message flow with mocked providers
    - Multi-agent conversation
    - History persistence across sessions
    - Rate limiting under load
    - API key validation flow
  - **Acceptance**: 5+ integration tests, all passing
  - **Test**: `pytest tests/integration/`

- [ ] **Task**: Add security tests
  - **Test suite**: `tests/security/test_security.py`
  - **Tests**:
    - Path traversal prevention
    - SQL injection prevention (parameterized queries)
    - API key logging prevention (keys never in logs)
    - Command injection prevention
    - Input validation edge cases
    - Rate limit enforcement
    - File permission checks
  - **Acceptance**: All security tests pass, no vulnerabilities
  - **Test**: `pytest tests/security/ -v`

- [ ] **Task**: Run security audit tools
  - **Tools**:
    - `pip-audit` - Check dependencies for vulnerabilities
    - `bandit` - Python security linter
    - `safety` - Check for known security issues
  - **Commands**:
    ```bash
    pip-audit
    bandit -r ateam/
    safety check
    ```
  - **Acceptance**: No HIGH or CRITICAL vulnerabilities
  - **Test**: Run all three tools, fix any issues found

- [ ] **Task**: Set up linting and formatting
  - **Tools**: `ruff` (all-in-one linter/formatter)
  - **Config**: Add `pyproject.toml` ruff section
  - **Security rules enabled**:
    - S (security warnings)
    - B (bandit checks)
    - E (error codes)
  - **Acceptance**: Code passes `ruff check` and `ruff format --check`
  - **Test**: Run linter on codebase

### 4.4 Documentation
- [ ] **Task**: Write comprehensive README.md
  - **Sections**:
    - Quick start (5-minute setup)
    - Features overview
    - Configuration guide
    - Troubleshooting
    - Contributing guidelines
  - **Acceptance**: New user can set up from README alone
  - **Test**: Have someone unfamiliar with project try installation

- [ ] **Task**: Add docstrings to all public APIs
  - **Format**: Google-style docstrings
  - **Include**: Args, Returns, Raises, Examples
  - **Acceptance**: `pydoc` generates useful docs
  - **Test**: Run `pydoc ateam.core.room`

- [ ] **Task**: Create example configuration files
  - **Files**:
    - `examples/config.yaml` (basic setup)
    - `examples/config-advanced.yaml` (all options)
    - `examples/config-ollama-only.yaml` (local-only)
  - **Acceptance**: Users can copy-paste and modify
  - **Test**: Use each example config, verify it works

### 4.5 Packaging & Distribution
- [ ] **Task**: Test installation methods
  - **Methods to verify**:
    1. `pip install -e .` (development)
    2. `pip install git+https://github.com/...`
    3. Build wheel and install: `uv build && uv pip install dist/*.whl`
  - **Acceptance**: All methods install working `ateam` command
  - **Test**: Fresh virtual env for each method

- [ ] **Task**: Create setup scripts
  - **Files**:
    - `setup.sh` (Linux/Mac)
    - `setup.bat` (Windows)
  - **Functionality**:
    - Install uv if needed
    - Clone repo
    - Install package
    - Run `ateam init`
  - **Acceptance**: One command sets up entire tool
  - **Test**: Run on clean VM for each OS

- [ ] **Task**: Publish to PyPI (optional)
  - **Prerequisites**: PyPI account, verified email
  - **Commands**: 
    ```bash
    uv build
    uv publish
    ```
  - **Acceptance**: `pip install ateam-cli` works globally
  - **Test**: Install in fresh environment

---

## Phase 5: Advanced Features (Future)
**Goal**: Nice-to-have enhancements (do after core is solid)

### Optional Enhancements
- [ ] Add voice input/output support
- [ ] Implement conversation branching (save snapshots)
- [ ] Add web search MCP tool
- [ ] Create web UI alternative to CLI
- [ ] Support streaming responses (real-time agent typing)
- [ ] Add conversation analytics dashboard
- [ ] Implement collaborative rooms (multi-user)
- [ ] Add plugin system for custom providers

---

## Success Checklist
Before considering the project "done", verify:

**Core Functionality:**
- [ ] Can install with single command
- [ ] Can create room and chat with at least 2 different agents
- [ ] Agents can use filesystem tool
- [ ] History persists across sessions
- [ ] Works on Windows, Mac, and Linux

**Code Quality:**
- [ ] Documentation is clear and complete
- [ ] Test coverage >70% overall, >90% for security-critical components
- [ ] No hardcoded paths or API keys
- [ ] Error messages are helpful and actionable
- [ ] CLI feels snappy (<500ms for local operations)

**Security Hardening (Critical):**
- [ ] **Rate limiting** implemented on all API calls and user actions
- [ ] **Input validation** on all user inputs (schema-based with Pydantic)
- [ ] **API keys** secured:
  - [ ] Stored in system keyring (not config files)
  - [ ] Never appear in logs, errors, or stack traces
  - [ ] Validated before storage
  - [ ] Support key rotation
- [ ] **File operations** secured:
  - [ ] Path traversal prevention (.., symlinks blocked)
  - [ ] Whitelist-based directory access
  - [ ] Sensitive files blocked (.env, .ssh, etc.)
  - [ ] Permission checks enforced
- [ ] **SQL injection** prevented (parameterized queries only)
- [ ] **Command injection** prevented (validated args, list form)
- [ ] **SSRF** prevented (if web search enabled)
- [ ] **Security tests** passing:
  - [ ] Path traversal tests
  - [ ] SQL injection tests
  - [ ] API key logging tests
  - [ ] Rate limit tests
  - [ ] Input validation tests
- [ ] **Security audit tools** passing:
  - [ ] `pip-audit` (no HIGH/CRITICAL vulnerabilities)
  - [ ] `bandit` (no security warnings)
  - [ ] `safety check` (dependencies secure)
- [ ] **Environment security**:
  - [ ] .env files have correct permissions (600)
  - [ ] Warning shown for insecure config storage
  - [ ] No secrets in version control (.gitignore configured)

**Pre-Release Security Review:**
- [ ] Review against OWASP Top 10
- [ ] All security recommendations from `technical.md` implemented
- [ ] Penetration testing performed (or plan in place)
- [ ] Security documentation complete
- [ ] Incident response plan drafted

---

## Notes for AI IDE
- **Start here**: Phase 1.1 - don't skip the foundation
- **Test incrementally**: After each task, verify it works before moving on
- **Ask for clarification**: If acceptance criteria is unclear, ask
- **Commit often**: Each completed task should be a git commit
- **Read specs first**: Reference `specs.md` and `technical.md` when implementing
