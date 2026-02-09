# A-Team Functional Specifications

## Project Vision
A-Team is a cross-platform CLI tool that orchestrates multiple AI agents (Gemini, Claude, Grok, DeepSeek, etc.) in collaborative "Rooms" with shared conversational context. Think of it as a persistent multi-agent workspace where each AI maintains awareness of the full discussion history.

## Core Capabilities

### 1. Room Management
- **Command**: `ateam join <room_name>`
- **Behavior**: 
  - Creates a new room if it doesn't exist
  - Enters an existing room and displays recent context summary
  - Each room is an isolated workspace with its own history
- **Room Structure**:
  ```
  ~/.config/ateam/rooms/<room_name>/
    ├── history.json
    ├── config.yaml (optional room-specific config)
    └── attachments/ (for file references)
  ```

### 2. Agent Configuration & Naming
- Users define agents in `~/.config/ateam/config.yaml`
- Each agent has:
  - **Display name** (e.g., "Architect", "Coder", "Critic")
  - **Provider** (gemini, claude, openai, ollama, etc.)
  - **Model** (e.g., "gemini-2.0-flash", "claude-sonnet-4")
  - **System prompt** (optional role definition)
- Example configuration:
  ```yaml
  agents:
    Architect:
      provider: gemini
      model: gemini-2.0-flash
      system_prompt: "You are a software architect specializing in scalable systems."
    Coder:
      provider: ollama
      model: deepseek-r1:7b
      system_prompt: "You write clean, production-ready code."
  ```

### 3. Unified Conversation History
- **Format**: JSON array of message objects
- **Schema**:
  ```json
  {
    "timestamp": "2024-02-06T14:30:00Z",
    "role": "user|assistant",
    "content": "message text",
    "agent_name": "Architect",
    "model_used": "gemini-2.0-flash",
    "tokens": {"prompt": 150, "completion": 200}
  }
  ```
- **Persistence**: Auto-saved after every interaction
- **Recovery**: Graceful handling of corrupted history files

### 4. Tagging & Routing System
- **Syntax**: `@AgentName` anywhere in the message
- **Behavior**:
  - **Single tag**: Routes to that specific agent
  - **Multiple tags (sequential mode)**: Agents respond in order, each seeing previous responses
  - **No tag**: Routes to the default agent (first in config or user-specified)
- **Examples**:
  ```
  @Architect, what's the best database for this?
  → Single agent response
  
  @Architect @Coder, design and implement a user authentication system
  → Architect designs first, then Coder implements (seeing the design)
  
  Hey team, any thoughts on this design? (→ goes to default agent)
  ```
- **Advanced Multi-Agent Modes**:
  - **Sequential (default)**: `@A @B @C` → A responds, then B sees A's response, then C sees both
  - **Parallel (opt-in)**: `@A @B --parallel` → Both respond independently, useful for comparing perspectives
  - **Conversation (future)**: Agents can naturally respond to each other until task completion

### 5. Privacy & Data Sovereignty
- **Zero telemetry**: No analytics, no external logging
- **Local-first**: All data stored on user's machine
- **No cloud dependencies** for core functionality
- **API keys**: Stored in system keyring or environment variables (never in history files)

### 6. MCP (Model Context Protocol) Integration
- **Tools available to agents**:
  - Filesystem operations (read/write with permission prompts)
  - Web search capabilities
  - Code execution sandbox
  - Custom MCP servers (user can add their own)
- **Safety**: All file operations require user confirmation unless auto-approved in config

## User Experience Flow

### First-Time Setup
```bash
$ ateam init

🚀 Welcome to A-Team! Let's set up your AI agents.

Detecting available providers...
✓ Internet connection available

Which AI providers do you want to use?
  [x] Google Gemini (free tier available - recommended for getting started)
  [ ] Anthropic Claude (requires API key)
  [ ] OpenAI GPT (requires API key)
  [x] Ollama (local models - optional, requires installation)

→ Google Gemini selected
  Enter API key (get one at https://aistudio.google.com/app/apikey): **********
  Testing API key... ✓ Valid!
  Saved securely to system keyring

→ Ollama selected
  Checking for Ollama installation...
  ⚠ Ollama not found. Install from https://ollama.com to use local models.
  Continue without Ollama? [Y/n]: y

✓ Configuration complete!
✓ Created default agent: Architect (using Gemini)

Try it now: ateam join my-first-project
```

### Daily Workflow
```bash
$ ateam join ml-research
→ Entering room: ml-research (15 messages, 12.5K tokens in context)

[Context: 12.5K / 100K tokens | 15 messages]
You: @Architect, I need to build a recommendation system for 10M users

Architect (Gemini): I recommend a hybrid approach combining collaborative 
filtering with content-based methods. Here's the architecture...

[Context: 15.2K / 100K tokens | 16 messages]
You: @Coder, scaffold a Python project for this architecture

Coder (DeepSeek): I'll create a modular structure. Let me write the files...
[Requesting filesystem access: Create 5 files in ~/projects/recommender]
Approve all? [y/n/review]: y
✓ Created main.py, models.py, utils.py, tests/test_models.py, README.md

[Context: 18.9K / 100K tokens | 17 messages]
You: exit
→ Saved conversation. Exited room: ml-research
```

### Advanced Features
- **Room listing**: `ateam rooms` shows all available rooms with summaries
- **History export**: `ateam export <room_name> --format=[md|html|json|pdf]` → creates transcript
- **Context pruning**: `ateam prune <room_name>` → keeps last N messages or intelligently summarizes
- **Agent stats**: `ateam stats` → shows token usage per agent
- **Undo**: `ateam undo [N]` → removes last N messages from current room
- **Configuration testing**: `ateam config test-keys` → validates all API keys
- **Parallel mode**: Use `--parallel` flag for independent multi-agent responses

## Edge Cases & Error Handling

### Network Failures
- Retry logic with exponential backoff
- Cache last successful response
- Inform user which provider failed

### Context Overflow
- Monitor token counts per message and display to user
- Smart pruning strategy:
  - Always preserve: first message (room context), last 5 messages
  - Summarize middle messages when approaching limit
  - User can pin important messages to prevent pruning
- Warning at 85% capacity: "Context approaching limit (85K/100K tokens). Oldest messages will be summarized on next interaction."
- Users can export and start fresh, or manually prune with `ateam prune <room>`
- Token counter displayed in prompt: `[18.5K / 100K tokens]`

### Invalid Tags
- `@UnknownAgent` → Suggest closest match or list available agents
- Empty message → Prompt user for input

### Concurrent Access
- File locking mechanism for multi-terminal usage
- Display warning if room is active in another session

### API Key Issues
- Clear, actionable error messages with fix instructions:
  ```
  ⚠ Gemini API Error: Invalid API key
  
  This means: Your GOOGLE_API_KEY is incorrect or expired
  
  Fix it:
  1. Get a new key: https://aistudio.google.com/app/apikey
  2. Run: ateam config set-key gemini
     Or: export GOOGLE_API_KEY="your-key"
  3. Verify: ateam config test-keys
  
  Need help? https://docs.ateam.dev/troubleshooting
  ```
- Support deferred key entry (prompt when needed, not at init)
- Validate keys during setup with test API call

## Non-Functional Requirements

### Performance
- CLI response time: <100ms for local operations
- First API call: <2s (network dependent)
- History loading: <500ms for 1000+ messages

### Compatibility
- Python 3.11+ (for modern type hints)
- Cross-platform: Windows 10+, macOS 12+, Linux (Ubuntu 20.04+)

### Usability
- Autocomplete for room names and agent names
- Colored terminal output for readability
- Progress indicators for long-running API calls

## Success Metrics
- User can set up and run first multi-agent conversation in <5 minutes
- Zero data leaks to external services (verifiable via network monitoring)
- Supports 100+ message conversations without performance degradation
