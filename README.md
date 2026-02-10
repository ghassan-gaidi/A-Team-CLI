# 🚀 A-Team CLI: The Multi-Agent Orchestrator

A-Team is a powerful, secure, and extensible CLI designed for seamless multi-agent collaboration. It allows multiple AI specialists (Architects, Coders, Researchers) to work together in persistent chat rooms, hand off tasks to one another, and interact with your local system through a secure tool layer.


---

## 🧪 Vibecoding & The Experiment

> *"I am not really technical, I am vibecoding these projects, experimenting with AI IDEs limits."* — **GG**

This project is a living experiment in **AI-driven development**. It was built by pushing the boundaries of what modern AI coding assistants can do, focusing on "vibes" and high-level intent rather than getting bogged down in implementation details.

- **The `.context` folder**: This directory contains the actual prompts, friction logs, and design specs used to build this tool. It serves as an open-source learning resource for anyone interested in prompt engineering and AI-native development workflows.
- **The Goal**: To see how far we can take an AI-generated codebase while maintaining security, usability, and a premium "cinematic" user experience.

If you're curious about how this was built, dive into the `.context` folder—it's the DNA of the A-Team.

---


## ✨ Key Features

- **🧠 Multi-Agent Orchestration**: Spin up a squad of specialized agents. Use `@mention` tags to route queries to specific experts.
- **🤝 Intelligent Hand-offs**: Agents can automatically detect when a task is better suited for a teammate and suggest a hand-off (e.g., Architect -> Coder).
- **🛠️ Secure Tool System**: Built-in `shell`, `file`, and **`search`** tools allow agents to master your codebase—always with **Human-in-the-Loop** confirmation.
- **📊 Diff-First Mutations**: Proposed file changes are presented in a split-screen side-by-side diff, allowing you to review code before it's written.
- **🧠 Auto-Context Indexing**: The CLI automatically indexes your workspace's signatures and structures, injecting them into agent context so they always "know" your project's layout without manual prompting.
- **🕵️ Shadow Critic Audit**: A background agent (the Critic) silently monitors every action taken by the Coder. If it detects a security vulnerability or bug, it interrupts with an immediate alert.
- **🌐 Web Reflection**: A zero-config, glassmorphic web dashboard to visualize your project structure, chat history, and mission status in real-time.
- **📄 Mission Manifests**: Use `/export` to generate a beautiful Markdown report of your entire session—including stats, tool logs, and a chronological timeline of implementation decisions.
- **⚡ Flow State (Trust Modes)**: Use `/trust @agent` to grant temporary auto-execution permissions, removing friction during intense coding sessions.
- **🎬 Cinematic UX**: Experience a split-screen interactive layout during tool execution, keeping context visible while tools run in real-time.
- **🔌 MCP Plugin System**: Easily extend the A-Team by dropping Python scripts into the `ateam/mcp` directory—dynamic tool discovery included.
- **🏗️ Project Spawner**: Use `ateam spawn <template>` to instantly scaffold new projects with team-approved architectures.
- **📡 Mission Control**: A real-time, live-refreshing dashboard to monitor all active rooms, agent status, and system activity across your entire squad.
- **🔒 Security First**: 
  - **Keyring Integration**: Securely store API keys in your system's keyring (macOS Keychain, Windows Credential Vault, Linux Secret Service).
  - **Hardened Validation**: Protection against path traversal and malicious injection.
  - **Scoped Access**: Agents are restricted to allowed directories.
- **💬 Interactive UI**: A premium terminal experience with streaming Markdown, live progress indicators, and color-coded provider feedback.
- **♻️ Persistent History**: Shared SQLite-backed history management allows agents to stay in sync across sessions.
- **🎨 Cinematic UX**: Experience a split-screen interactive layout with live Markdown streaming and color-coded status indices.

---

## 🛰️ Mission Control & Reflection

The A-Team provides high-fidelity observability into your agent's thought process and actions:

### 📡 Terminal Dashboard (`ateam dash`)
Launch a full-screen, real-time observability hub in your terminal.
- **Live Squad Status**: Monitor room activity, lead agents, and message counts.
- **Resource Monitoring**: Track token usage and context window consumption per room.
- **Interactive Routing**: Navigate between rooms using keyboard shortcuts.

### 🌐 Web Reflection (`ateam web`)
Fire up a premium, glassmorphic web dashboard for a dual-monitor setup.
- **Visual Timeline**: Watch the mission progress with real-time message bubbles.
- **Architectural Map**: View the automatically indexed structure of your project side-by-side with the chat.
- **Zero-Config**: Runs instantly via a lightweight internal server.

### 🕵️ Shadow Auditing
The **Shadow Critic** works in the background of every session, auditing actions for security risks and architectural drift. If an issue is found, it injects a high-priority alert into your chat session immediately.

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
| `ateam dash` | Launch the Mission Control terminal dashboard |
| `ateam web` | Fire up the Web Reflection glassmorphic dashboard |
| `ateam spawn <template> <name>` | Scaffold a new project from a template |
| `ateam version` | Display version information |

### Internal Chat Commands
Once inside a room, use these slash commands:
- `/help`: Show available commands.
- `/agent <name>`: Switch the default agent for the session.
- `/agents`: List all configured agents (e.g., Architect, Coder, Critic).
- `/history`: Show recent message history.
- `/refresh`: Manually re-index the workspace for updated context.
- `/web`: Launch the Web Reflection terminal.
- `/export`: Generate a Markdown manifest of the current mission.
- `/trust [@agent] [min]`: Grant temporary auto-execution trust.
- `/untrust [@agent]`: Revoke trust immediately.
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

## 🤝 Contributing

This project is a vibe-first experiment, and I’d love for the community to jump in! Whether you're a seasoned developer or just experimenting with AI, contributions are welcome.

- **Check out `.context/`**: Learn how the project evolved.
- **Improved Prompts**: Found a better way to instruct the agents? Submit a PR!
- **New Features**: Want a new Agent personality? Add it to `config.yaml` and share it.
- **Bug Fixes**: Help solidify the vibecode into production-grade software.

If you have ideas, open an issue or start a discussion. Let's push the limits of AI-assisted coding together.

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

**Built By GG.** 🚀
