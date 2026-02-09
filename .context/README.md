# A-Team CLI 🚀

> **The Multi-Agent Orchestrator for Your Terminal**

Stop switching between ChatGPT, Claude, and local models. Bring them all into one conversation where they can build on each other's ideas.

<div align="center">

```
┌─────────────────────────────────────────────────────────┐
│ You: @Architect, design a REST API for a blog          │
│                                                         │
│ Architect (Gemini): Here's a clean architecture...     │
│ [Detailed design response]                             │
│                                                         │
│ You: @Coder, implement the Architect's design          │
│                                                         │
│ Coder (DeepSeek): I'll create the FastAPI skeleton.    │
│ [Creates files via MCP]                                 │
│                                                         │
│ You: @Critic, review the code                          │
│                                                         │
│ Critic (Claude): Good start. Here are 3 improvements:  │
│ [Detailed code review]                                  │
└─────────────────────────────────────────────────────────┘
```

</div>

---

## ✨ Why A-Team?

### The Problem
You're building a project. You ask ChatGPT for architecture advice, copy-paste to Claude for code review, switch to a local model for privacy-sensitive parts. **Your context is fragmented. The AIs don't learn from each other.**

### The Solution
A-Team creates persistent "Rooms" where multiple AI agents collaborate with **shared memory**. Each agent sees the full conversation history. They build on each other's responses. You orchestrate expertise.

---

## 🎯 Features

<table>
<tr>
<td width="50%">

### 🧠 **Shared Context**
All agents see the same conversation history. No more copy-pasting between ChatGPT tabs.

</td>
<td width="50%">

### 🏠 **Persistent Rooms**
Conversations are saved locally. Return to any project anytime, context intact.

</td>
</tr>
<tr>
<td width="50%">

### 🎭 **Custom Agent Roles**
Name your agents: "Architect", "Coder", "Critic". Give each a specialized system prompt.

</td>
<td width="50%">

### 🔒 **Privacy First**
100% local storage. No telemetry. Works offline with local models via Ollama.

</td>
</tr>
<tr>
<td width="50%">

### 🛠️ **MCP Tool Access**
Agents can read/write files, search the web, execute code (with your permission).

</td>
<td width="50%">

### 🌐 **Hybrid Cloud + Local**
Mix GPT-4 for architecture with local DeepSeek for code. Your choice.

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (required)
- **API Keys** (at least one - choose based on your needs):
  - **For cloud AI** (recommended to start):
    - [Google AI Studio](https://aistudio.google.com/app/apikey) - **FREE tier available** (1500 requests/day)
    - [Anthropic API](https://console.anthropic.com/) - Claude models
    - [OpenAI API](https://platform.openai.com/api-keys) - GPT models
  - **For local AI** (optional, for privacy/offline):
    - [Ollama](https://ollama.ai) - Run models on your machine

**Note**: You can start with just Google Gemini (free) and add other providers later!

### Installation

```bash
# Option 1: Install from PyPI (when published)
pip install ateam-cli

# Option 2: Install from source
git clone https://github.com/yourusername/ateam.git
cd ateam
pip install .

# Option 3: Install with uv (fastest)
uv tool install ateam-cli
```

### First-Time Setup (Interactive)

```bash
# Run the interactive setup wizard
ateam init

# Follow the prompts:
# 1. Choose which providers to use (Gemini recommended for free tier)
# 2. Enter API key(s) - they'll be validated immediately
# 3. Optionally configure Ollama if you have it installed

# That's it! You're ready to go.
```

**What if I don't have Ollama?**
No problem! A-Team works great with just cloud providers. Ollama is completely optional and only needed if you want to run models locally on your machine.

### First-Time Setup (Manual)

If you prefer manual setup:

```bash
# Set your API key
export GOOGLE_API_KEY="your-key-here"
# Or for Claude:
export ANTHROPIC_API_KEY="your-key-here"

# Initialize config files
ateam init

# Optionally edit config
nano ~/.config/ateam/config.yaml
```

### Your First Multi-Agent Conversation

```bash
# Create or join a room
ateam join my-project

# Talk to specific agents with @mentions
You: @Architect, I need to build a URL shortener. What's the best tech stack?

Architect (Gemini): I recommend FastAPI + PostgreSQL + Redis...
[Detailed architecture response]

You: @Coder, scaffold the project based on that architecture

Coder (DeepSeek): I'll create the initial structure...
[Creates files: main.py, models.py, etc.]

You: @Critic, are there any security issues with this approach?

Critic (Claude): Yes, here are 3 concerns to address...
[Detailed security analysis]

You: exit
→ Exited room: my-project (7 messages saved)
```

---

## 📖 Core Concepts

### Rooms
Think of rooms as project folders for conversations. Each room has its own history that persists across sessions.

```bash
ateam join web-scraper      # Work on a scraping project
ateam join ml-experiment    # Switch to ML work
ateam rooms                 # List all your rooms
```

### Agents
Agents are AI models with custom names and roles. You define them in `~/.config/ateam/config.yaml`:

```yaml
agents:
  Architect:
    provider: gemini
    model: gemini-2.0-flash
    system_prompt: "You are a senior software architect..."
    
  Coder:
    provider: ollama
    model: deepseek-r1:7b
    system_prompt: "You write clean, production-ready code..."
    
  Critic:
    provider: anthropic
    model: claude-sonnet-4
    system_prompt: "You provide constructive code reviews..."
```

### Tagging
Use `@AgentName` to direct a message to a specific agent:

```bash
@Architect, design a caching layer
@Coder, implement what Architect suggested
@Critic, review the implementation
```

If you don't use a tag, the message goes to your default agent.

**Multi-agent collaboration:**
```bash
# Sequential mode (default) - agents build on each other
@Architect @Coder, design and implement a user auth system
→ Architect designs first, then Coder sees the design and implements

# Parallel mode - get multiple perspectives
@Architect @Critic --parallel, evaluate microservices vs monolith
→ Both respond independently
```

### Model Selection Guide

Choosing the right model for each agent role is important. Here's a comparison:

| Model | Provider | Speed | Cost | Tool Support | Best For |
|-------|----------|-------|------|--------------|----------|
| **gemini-2.0-flash** | Google | ⚡⚡⚡ | 🆓 Free tier (1500 req/day) | ✅ Yes | General tasks, rapid iteration, getting started |
| **gemini-2.5-pro** | Google | ⚡⚡ | 💰 Low ($1.25/M tokens) | ✅ Yes | Complex reasoning, architecture |
| **claude-sonnet-4** | Anthropic | ⚡⚡ | 💰 Medium ($3/M tokens) | ✅ Yes | Code review, analysis, writing |
| **claude-opus-4** | Anthropic | ⚡ | 💰💰 High ($15/M tokens) | ✅ Yes | Most complex tasks, research |
| **gpt-4o** | OpenAI | ⚡⚡ | 💰 Medium ($2.50/M tokens) | ✅ Yes | Versatile, good reasoning |
| **gpt-4o-mini** | OpenAI | ⚡⚡⚡ | 💰 Low ($0.15/M tokens) | ✅ Yes | Fast, cheap, simple tasks |
| **deepseek-r1:7b** | Ollama | ⚡⚡⚡ | 🆓 Free (local) | ❌ Limited | Code generation, privacy-focused |
| **qwen2.5-coder:7b** | Ollama | ⚡⚡⚡ | 🆓 Free (local) | ❌ Limited | Code-specific tasks |

**Recommended Starter Setup:**
- **Architect**: gemini-2.0-flash (free, fast, good for design)
- **Coder**: deepseek-r1:7b via Ollama (free, code-focused) OR gpt-4o-mini (cheap, reliable)
- **Critic**: claude-sonnet-4 (excellent at analysis and review)

**Budget-Conscious Setup:**
- All agents use gemini-2.0-flash (completely free within quota)

**Premium Setup:**
- **Architect**: gemini-2.5-pro (better reasoning)
- **Coder**: claude-sonnet-4 (excellent code quality)
- **Critic**: claude-opus-4 (most thorough reviews)

---

## 🎨 Advanced Usage

### MCP Tool Integration

Agents can interact with your computer via the Model Context Protocol:

```bash
You: @Coder, read the README.md file and suggest improvements

Coder: Let me read the file...
[Tool Call: read_file("README.md")]
Based on the content, I suggest...
```

Configure allowed operations in your `config.yaml`:

```yaml
mcp:
  filesystem:
    enabled: true
    allowed_paths:
      - "~/projects"
      - "~/Documents"
  web_search:
    enabled: true
```

### Export Conversations

Save your conversation as a shareable markdown file:

```bash
ateam export my-project
→ Exported to: my-project_2024-02-06.md
```

### View Statistics

See your usage across all agents:

```bash
ateam stats

Agent Statistics:
┌────────────┬───────────┬────────────────┐
│ Agent      │ Messages  │ Tokens Used    │
├────────────┼───────────┼────────────────┤
│ Architect  │ 24        │ 45,230         │
│ Coder      │ 31        │ 62,100         │
│ Critic     │ 18        │ 38,450         │
└────────────┴───────────┴────────────────┘
```

---

## 🛠️ Configuration

### Full Config Example

Located at `~/.config/ateam/config.yaml`:

```yaml
version: "1.0"

# Default agent when no @tag is used
default_agent: "Architect"

# Context settings
context_window_size: 30        # messages to keep in context
auto_prune: true               # automatically remove old messages
confirm_file_operations: true  # ask before agents modify files

# Agent definitions
agents:
  Architect:
    provider: gemini
    model: gemini-2.0-flash
    api_key_env: GOOGLE_API_KEY
    system_prompt: |
      You are a senior software architect with 15 years of experience.
      Focus on: scalability, maintainability, and production best practices.
      Always consider: performance, security, and developer experience.
    temperature: 0.7
    max_tokens: 4096
    
  Coder:
    provider: ollama
    model: deepseek-r1:7b
    base_url: http://localhost:11434
    system_prompt: |
      You write clean, well-documented code.
      Guidelines:
      - Use type hints in Python
      - Include docstrings for functions
      - Handle errors gracefully
      - Follow language-specific best practices
    
  Critic:
    provider: anthropic
    model: claude-sonnet-4
    api_key_env: ANTHROPIC_API_KEY
    system_prompt: |
      You provide constructive code reviews.
      Focus areas:
      - Edge cases and error handling
      - Performance bottlenecks
      - Security vulnerabilities
      - Code maintainability
      Be specific and suggest improvements.

# MCP Tools
mcp:
  filesystem:
    enabled: true
    allowed_paths:
      - "~/projects"
      - "~/Documents"
    dangerous_operations: ["delete", "chmod"]
    
  web_search:
    enabled: true
    provider: brave
    
  code_execution:
    enabled: false  # disabled by default for security
    sandboxed: true
```

---

## 📚 Command Reference

### Room Management
```bash
ateam init                  # Set up A-Team for first time
ateam join <room>           # Create or enter a room
ateam rooms                 # List all rooms
ateam export <room>         # Export room to markdown
ateam prune <room>          # Remove old messages from history
```

### Usage
```bash
# Inside a room
@AgentName your message     # Direct message to specific agent
your message                # Send to default agent
exit                        # Leave the room
quit                        # Leave the room
```

### Utilities
```bash
ateam stats                 # View token usage statistics
ateam config                # View current configuration
ateam version               # Show version info
```

---

## 🧪 Example Workflows

### Web Development Project
```bash
ateam join blog-api

You: @Architect, design a RESTful API for a blog with posts, comments, and users

Architect: Here's my proposed architecture...

You: @Coder, implement the Post model and CRUD endpoints

Coder: Creating models.py and routes.py...

You: @Critic, security review

Critic: I see 3 potential issues...
```

### Data Science Workflow
```bash
ateam join customer-churn

You: @Architect, what ML approach works best for customer churn prediction?

You: @Coder, write the data preprocessing pipeline

You: @Critic, review the feature engineering strategy
```

### Code Refactoring
```bash
ateam join refactor-legacy

You: @Critic, analyze this legacy codebase [attaches files]

You: @Architect, propose a refactoring strategy

You: @Coder, implement the first phase
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and write tests
4. **Run tests**: `pytest tests/`
5. **Lint your code**: `ruff check . && ruff format .`
6. **Commit**: `git commit -m "Add amazing feature"`
7. **Push**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Setup
```bash
git clone https://github.com/yourusername/ateam.git
cd ateam

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linter
ruff check .
```

---

## 🔒 Security & Privacy

A-Team takes security seriously. Your data, API keys, and files are protected through multiple layers of security:

### Data Privacy
- ✅ **100% Local Storage** - All conversations stored on your machine
- ✅ **Zero Telemetry** - No analytics, no tracking, no data sent to Anthropic servers
- ✅ **No Cloud Dependencies** - Works completely offline with local models (Ollama)
- ✅ **Encrypted API Keys** - Stored in system keyring, never in plain text

### Security Features
- ✅ **Rate Limiting** - Prevents API abuse and quota exhaustion
- ✅ **Input Validation** - All user inputs validated against strict schemas
- ✅ **Path Sandboxing** - File access restricted to whitelisted directories
- ✅ **Path Traversal Protection** - Blocks `../` attacks and symlink exploits
- ✅ **SQL Injection Prevention** - Parameterized queries throughout
- ✅ **Secure Logging** - API keys automatically redacted from logs

### Best Practices Enforced
1. **API Keys**: Use system keyring or environment variables (never config files)
2. **File Permissions**: Warns if `.env` file has insecure permissions
3. **Least Privilege**: Agents can only access explicitly allowed directories
4. **Fail Secure**: Permission denied by default, must be explicitly granted

### Security Audit
Before each release, A-Team is tested against:
- OWASP Top 10 vulnerabilities
- Dependency vulnerabilities (`pip-audit`, `safety`)
- Static analysis security testing (`bandit`)
- Penetration testing checklist

### Reporting Security Issues
Found a security vulnerability? Please report it responsibly:
- **Email**: security@ateam.dev (not public GitHub issues)
- **Response Time**: We aim to respond within 24 hours
- **Disclosure**: Coordinated disclosure after fix is released

**Do NOT** open public GitHub issues for security vulnerabilities.

---

## 🐛 Troubleshooting

### "No module named 'ateam'"
Make sure you've installed the package:
```bash
pip install -e .
```

### "Missing API key for provider: gemini"
Set your API key as an environment variable:
```bash
export GOOGLE_API_KEY="your-key-here"
```
Or add it to your `~/.config/ateam/config.yaml`

### "Ollama connection refused"
Start the Ollama server:
```bash
ollama serve
```

### Agent responses are repetitive/low quality
- Check your system prompts in `config.yaml`
- Adjust the `temperature` parameter (lower = more focused, higher = more creative)
- Try a different model

### History file corrupted
A-Team automatically creates backups. Check `~/.config/ateam/rooms/<room>/history.json.backup`

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🌟 Roadmap

- [x] Multi-agent conversation orchestration
- [x] MCP tool integration (filesystem)
- [ ] Voice input/output support
- [ ] Web UI alternative to CLI
- [ ] Streaming responses (real-time typing)
- [ ] Conversation branching/snapshots
- [ ] Web search MCP tool
- [ ] Collaborative rooms (multi-user)
- [ ] Plugin system for custom providers
- [ ] VSCode extension

---

## 💬 Community & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ateam/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ateam/discussions)
- **Email**: support@example.com

---

## 🙏 Acknowledgments

- [Typer](https://typer.tiangolo.com/) - Beautiful CLI framework
- [MCP](https://modelcontextprotocol.io/) - Tool integration protocol
- [Anthropic](https://anthropic.com), [Google](https://ai.google.dev/), [OpenAI](https://openai.com), [Ollama](https://ollama.ai) - AI providers

---

<div align="center">

**Built with ❤️ for developers who want AI collaboration, not AI silos.**

[⭐ Star this repo](https://github.com/yourusername/ateam) if you find it useful!

</div>
