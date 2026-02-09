# 🚀 A-Team CLI: The Multi-Agent Orchestrator

A-Team is a powerful, secure, and extensible CLI designed for seamless multi-agent collaboration. It allows multiple AI specialists (Architects, Coders, Researchers) to work together in persistent chat rooms, hand off tasks to one another, and interact with your local system through a secure tool layer.

---

## ✨ Key Features

- **🧠 Multi-Agent Orchestration**: Spin up a squad of specialized agents. Use `@mention` tags to route queries to specific experts.
- **🤝 Intelligent Hand-offs**: Agents can automatically detect when a task is better suited for a teammate and suggest a hand-off (e.g., Architect -> Coder).
- **🛠️ Secure Tool System**: Built-in `shell` and `file` tools allow agents to read code, write implementation, and run tests—always with **Human-in-the-Loop** confirmation.
- **🔒 Security First**: 
  - **Keyring Integration**: Securely store API keys in your system's keyring (macOS Keychain, Windows Credential Vault, Linux Secret Service).
  - **Hardened Validation**: Protection against path traversal and malicious injection.
  - **Scoped Access**: Agents are restricted to allowed directories.
- **💬 Interactive UI**: A premium terminal experience with streaming Markdown, live progress indicators, and color-coded provider feedback.
- **♻️ Persistent History**: Shared SQLite-backed history management allows agents to stay in sync across sessions.

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install the package locally:

```bash
git clone https://github.com/ghassan-gaidi/A-Team-CLI.git
cd A-Team-CLI
pip install -e .
```

### 2. Initialization
Run the interactive setup wizard to configure your team and store your API keys securely:

```bash
ateam init
```

### 3. Join a Mission
Launch a chat room and start collaborating:

```bash
ateam join mission-alpha
```

---

## 📖 Command Reference

| Command | Description |
| :--- | :--- |
| `ateam init` | Interactive setup wizard for config and keys |
| `ateam join <room>` | Enter an interactive chat room |
| `ateam status` | Show current session info and active room |
| `ateam rooms` | List all active conversation rooms |
| `ateam version` | Display version information |

### Internal Chat Commands
Once inside a room, use these slash commands:
- `/help`: Show available commands.
- `/agent <name>`: Switch the default agent for the session.
- `/agents`: List all configured agents (e.g., Architect, Coder, Critic).
- `/history`: Show recent message history.
- `/switch <room>`: Jump to another room without leaving the CLI.
- `/exit`: Securely leave the room and end the session.

---

## 🛠️ Configuration

A-Team is configured via `~/.config/ateam/config.yaml`. Here you can define:
- **Agents**: Custom providers (Gemini, OpenAI, Anthropic, Ollama), models, and system prompts.
- **Security**: Rate limits, blocked file patterns, and keyring settings.
- **MCP Tools**: Enable/disable system tools and define allowed paths.

```yaml
default_agent: "Architect"
agents:
  Architect:
    provider: gemini
    model: gemini-2.0-flash
    api_key_env: GOOGLE_API_KEY
    system_prompt: "You are a senior software architect..."
```

---

## 🧪 Development & Testing

We use `pytest` for comprehensive testing of the orchestration logic, security layer, and provider adapters.

```bash
# Run all tests
pytest tests/unit/

# Run with coverage (optional)
pytest --cov=ateam tests/unit/
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ by the A-Team Team.** 🚀
