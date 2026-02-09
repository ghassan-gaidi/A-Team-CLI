# 🎯 Mission: The SQLite Notes Explorer

Objective: Build a simple Python CLI that manages snippets in a local SQLite database.

## 🛠️ Step-by-Step Guide

### 1. Launch the Squad
Open your terminal and join the mission:
```bash
ateam join mission-alpha
```

### 2. Tasking the Architect
Once inside, ask for the system design:
> **You**: "Hello team! @Architect, I need a design for a simple 'Notes' CLI. We want to store text snippets in a local SQLite database. What should the schema look like?"

### 3. Handle the Handoff
Architect will likely respond with a design and mention `@Coder`.
- **CLI**: "Detected hand-off to @Coder. Switch current agent? [y/N]:"
- **You**: Press `y`.

### 4. Implementation
Ask Coder to build it:
> **You**: "Excellent. @Coder, use the `shell` tool to create a directory `notes_app` and a file `setup.py` that initializes the SQLite database with that schema."

### 5. Review & Execute
Coder will suggest a tool call:
- **CLI**: "🛠️ Agent Action: Tool Call: shell | Args: {'command': 'mkdir notes_app && ...'}"
- **You**: Confirm with `y`.

---
### 🚀 Pro-Tips
- Use `@Critic` at any time to double-check the code's security.
- Use `/status` inside the chat to see which agent is currently leading.
- Use `/history` if you want to see the Architect's design again.
