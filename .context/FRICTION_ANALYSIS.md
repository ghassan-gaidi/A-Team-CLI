# A-Team: Friction Points & Improvement Recommendations

After analyzing the complete specification, here are the key friction points that could impede development or user adoption, along with actionable solutions.

---

## 🚨 CRITICAL FRICTION POINTS

### 1. **API Key Management Complexity**

**Problem:**
- Users need to manage multiple API keys (Google, Anthropic, OpenAI)
- Environment variables are fragile (not persistent across sessions)
- Config file storage is insecure
- System keyring adds platform-specific complexity
- No clear "best path" in the docs

**User Impact:**
- High barrier to entry for first-time users
- Security risks if keys go in config files
- Frustration when keys aren't found

**Recommended Solutions:**

**Option A: Interactive Setup Wizard (Best UX)**
```bash
$ ateam init

Welcome to A-Team! Let's set up your agents.

Which providers do you want to use?
[x] Google Gemini (free tier available)
[ ] Anthropic Claude
[ ] OpenAI GPT
[x] Ollama (local models)

→ Google Gemini selected
Enter your API key (or press Enter to set via environment): 
✓ Key validated and stored securely in system keyring

→ Ollama selected
Checking Ollama installation...
✓ Ollama found at http://localhost:11434
Available models: deepseek-r1:7b, qwen2.5-coder:7b

Configuration complete! Try: ateam join my-first-room
```

**Option B: Deferred Key Entry**
```bash
$ ateam join dev-room
You: @Architect, help me design an API

⚠ Missing API key for Gemini
Would you like to:
1. Enter it now (stored in system keyring)
2. Set GOOGLE_API_KEY environment variable
3. Use a different agent

Choose [1]: 1
Enter API key: ***************
✓ Saved. Retrying...
```

**Implementation Priority: HIGH**
- Add interactive setup in Phase 1
- Use `keyring` library for secure storage
- Validate keys immediately (test API call)
- Provide clear fallback instructions

---

### 2. **Context Window Management is Too Opaque**

**Problem:**
- Users don't know when/why messages are being pruned
- No visibility into token counts
- "Last 30 messages" is arbitrary and might not fit context
- Different models have different limits (Gemini: 1M tokens vs GPT-4: 128K)

**User Impact:**
- Confusion when agents "forget" earlier context
- Frustration when they exceed limits without warning
- No way to optimize usage

**Recommended Solutions:**

**A. Real-Time Token Tracking**
```bash
You: @Architect, design a microservices architecture for e-commerce

[Tokens: 1,240 / 100,000 | Context: 8 messages]
Architect: Here's a comprehensive design...

[Tokens: 4,850 / 100,000 | Context: 9 messages]
```

**B. Proactive Pruning Warnings**
```bash
⚠ Context approaching limit (85% full)
Oldest 5 messages will be pruned on next interaction.

Options:
- Continue (auto-prune)
- Export and start fresh room
- Manually summarize older context
```

**C. Smart Pruning Strategy**
Instead of simple "last N messages", implement intelligent pruning:
- Always keep: first message (room context), last 5 messages
- Summarize middle: "In earlier messages, @Architect proposed a REST API design, @Coder implemented it, and @Critic suggested security improvements."
- User control: Pin important messages to prevent pruning

**Implementation Priority: HIGH**
- Add token counter display in Phase 3
- Implement smart pruning in Phase 3.1
- Add `--show-tokens` flag for power users

---

### 3. **Multi-Agent Routing is Underspecified**

**Problem:**
Current spec says "Multiple tags → ask user to choose" but this creates bad UX:

```bash
You: @Architect @Coder, work together on this API design

Which agent should respond?
1. Architect
2. Coder
Choose [1-2]: _
```

This defeats the purpose of multi-agent collaboration!

**User Impact:**
- Users can't get agents to collaborate naturally
- Workflow is serial, not parallel
- No way to get multiple perspectives simultaneously

**Recommended Solutions:**

**A. Sequential Mode (Default)**
```bash
You: @Architect @Coder, design and implement a REST API

→ Routing to Architect first...
Architect: Here's the design... [saves to history]

→ Routing to Coder (can see Architect's response)...
Coder: Implementing the design... [saves to history]

Both responses complete!
```

**B. Parallel Mode (Advanced)**
```bash
You: @Architect @Critic, what are pros/cons of microservices?

⚡ Parallel mode: Both agents will respond independently

[Architect typing...]
[Critic typing...]

--- Architect (Gemini) ---
Pros: Scalability, independent deployment...

--- Critic (Claude) ---
Important considerations: Complexity overhead...
```

**C. Conversation Mode (Future)**
```bash
You: @Architect @Coder @Critic, collaborate on this design

[Conversation mode: agents can respond to each other]

Architect: I propose using REST with...
→ Coder: Good idea. I'll implement with FastAPI...
→ Critic: Wait - have you considered GraphQL for...?
→ Architect: Valid point. Let me revise...

[Continues until all agents say "done" or user intervenes]
```

**Implementation Priority:**
- Sequential mode: HIGH (Phase 2, before MVP)
- Parallel mode: MEDIUM (Phase 4)
- Conversation mode: LOW (Phase 5 / future)

---

### 4. **Ollama Dependency is Poorly Communicated**

**Problem:**
- Specs mention Ollama but don't clarify it's optional
- No clear instructions on installing Ollama
- Users might think they NEED it to use A-Team
- No fallback if Ollama isn't running

**User Impact:**
- Installation confusion
- False perception that A-Team requires local setup
- Broken experience if Ollama fails

**Recommended Solutions:**

**A. Clearer Positioning**
```markdown
# README.md

## Installation

A-Team works with:
- ✅ Cloud AI (Gemini, Claude, GPT) - No local installation needed
- ✅ Local AI (via Ollama) - Optional, for privacy/offline use

### Quick Start (Cloud Only)
```bash
pip install ateam-cli
export GOOGLE_API_KEY="your-key"
ateam join first-room
```

### Advanced Setup (Add Local Models)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull deepseek-r1:7b
ollama pull qwen2.5-coder:7b

# A-Team will auto-detect Ollama
```

**B. Runtime Detection**
```bash
$ ateam init

Detecting available providers...
✓ Internet connection available
✓ Google Gemini configured (API key found)
⚠ Ollama not detected
  → Install from https://ollama.com to use local models

Continue without Ollama? [y/n]: y
```

**Implementation Priority: HIGH**
- Update README in Phase 1
- Add detection in Phase 2.4

---

### 5. **MCP Tool Permissions are Too Rigid**

**Problem:**
Current spec requires confirmation for EVERY file operation:
```bash
@Coder wants to write to main.py. Allow? (y/n)
@Coder wants to write to utils.py. Allow? (y/n)
@Coder wants to write to tests.py. Allow? (y/n)
```

This gets exhausting fast!

**User Impact:**
- Constant interruptions kill flow state
- Users will disable confirmations entirely (security risk)
- Frustration with legitimate bulk operations

**Recommended Solutions:**

**A. Permission Profiles**
```yaml
# config.yaml
mcp:
  filesystem:
    permission_mode: selective  # options: always_ask, selective, trusted
    
    # In 'selective' mode:
    auto_approve:
      - write_in: ["~/projects/current-project"]  # Project-specific
      - create_new_files: true
      - read_any_allowed_path: true
    
    always_confirm:
      - delete
      - chmod
      - write_to_existing: ["*.env", "*.key"]  # Sensitive files
```

**B. Batch Approval**
```bash
@Coder wants to create 5 files in ~/projects/api-server/

Files:
  - main.py (new)
  - models.py (new)
  - routes.py (new)
  - tests/test_api.py (new)
  - README.md (new)

Approve all? [y/n/review]: y
✓ All approved
```

**C. Trust Levels Per Agent**
```yaml
agents:
  Coder:
    trust_level: high  # Can create/modify in allowed paths
    
  Researcher:
    trust_level: read_only  # Can only read files
```

**Implementation Priority: MEDIUM**
- Basic "always confirm" in Phase 3.2
- Smart permissions in Phase 4
- Trust levels in Phase 5

---

## ⚠️ MODERATE FRICTION POINTS

### 6. **SQLite Migration is Delayed Too Long**

**Problem:**
Spec says "Use JSON for Phase 1, SQLite later" but this creates technical debt:
- Need to write migration code
- Risk of data loss during migration
- JSON doesn't handle concurrent access (corruption risk)

**Recommended Solution:**
**Use SQLite from the start.** It's not significantly more complex:

```python
# Barely more code than JSON:
class HistoryManager:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()
    
    def append_message(self, msg):
        self.conn.execute(
            "INSERT INTO messages (timestamp, role, content, agent_name) VALUES (?, ?, ?, ?)",
            (msg.timestamp, msg.role, msg.content, msg.agent_name)
        )
        self.conn.commit()
    
    def get_recent(self, n):
        return self.conn.execute(
            "SELECT * FROM messages ORDER BY timestamp DESC LIMIT ?", (n,)
        ).fetchall()
```

**Benefits:**
- No migration needed
- Better concurrent access
- Corruption resistance
- Easier querying (for features like search)

**Implementation Priority: HIGH**
- Start with SQLite in Phase 1.4

---

### 7. **No Guidance on Model Selection**

**Problem:**
Users need to choose models for each agent but specs don't guide them:
- Which models are fast vs. smart?
- Which are free vs. paid?
- Which support tool calling?

**User Impact:**
- Poor model choices lead to bad experience
- Cost surprises (GPT-4 vs Gemini Flash)
- Feature confusion (not all models support tools)

**Recommended Solution:**

**Add Model Comparison Table to README**

| Model | Provider | Speed | Cost | Tool Support | Best For |
|-------|----------|-------|------|--------------|----------|
| gemini-2.0-flash | Google | ⚡⚡⚡ Fast | 🆓 Free tier | ✅ Yes | General tasks, rapid iteration |
| claude-sonnet-4 | Anthropic | ⚡⚡ Medium | 💰 $3/M tokens | ✅ Yes | Code review, analysis |
| gpt-4o | OpenAI | ⚡ Slower | 💰💰 $5/M tokens | ✅ Yes | Complex reasoning |
| deepseek-r1:7b | Ollama | ⚡⚡⚡ Fast | 🆓 Free (local) | ❌ No | Code generation, privacy |

**Add to config.yaml comments:**
```yaml
agents:
  Architect:
    # RECOMMENDED: gemini-2.0-flash
    # - Fast responses (1-2s)
    # - Free tier: 1500 requests/day
    # - Good for iterative design discussions
    provider: gemini
    model: gemini-2.0-flash
```

**Implementation Priority: MEDIUM**
- Add table to README in Phase 4.4

---

### 8. **Room Discovery is Limited**

**Problem:**
Only way to find rooms is `ateam rooms` which just lists names.
Users forget what each room was about.

**Recommended Solution:**

```bash
$ ateam rooms

Your Rooms:
┌─────────────────┬──────────┬─────────────┬────────────────────────┐
│ Name            │ Messages │ Last Active │ Summary                │
├─────────────────┼──────────┼─────────────┼────────────────────────┤
│ api-design      │ 24       │ 2 hours ago │ REST API architecture  │
│ ml-experiment   │ 8        │ 3 days ago  │ Customer churn model   │
│ debug-session   │ 15       │ 1 week ago  │ Memory leak debugging  │
└─────────────────┴──────────┴─────────────┴────────────────────────┘

$ ateam search "memory leak"
Found in rooms:
  - debug-session (3 messages mention "memory leak")

$ ateam recent
Recently active rooms:
  1. api-design (2 hours ago)
  2. ml-experiment (3 days ago)
```

**Implementation Priority: LOW**
- Basic listing in Phase 1
- Rich display in Phase 4
- Search in Phase 5

---

### 9. **Error Messages Could Be More Actionable**

**Problem:**
Spec says "provide clear errors" but doesn't give examples.
Generic errors are frustrating.

**Recommended Solution:**

**Error Message Template:**
```
[What went wrong] + [Why it matters] + [How to fix]
```

**Examples:**

❌ **Bad:**
```
Error: API call failed
```

✅ **Good:**
```
⚠ Gemini API Error: Invalid API key

This means: Your GOOGLE_API_KEY is incorrect or expired

Fix it:
1. Get a new key: https://aistudio.google.com/app/apikey
2. Set it: export GOOGLE_API_KEY="your-new-key"
3. Or run: ateam config set-key gemini

Need help? See: https://docs.ateam.dev/troubleshooting#api-keys
```

**Create Error Catalog:**
```python
# errors.py
class ErrorMessages:
    INVALID_API_KEY = """
    ⚠ {provider} API Error: Invalid API key
    
    This means: Your {env_var} is incorrect or expired
    
    Fix it:
    1. Get a new key: {key_url}
    2. Set it: export {env_var}="your-new-key"
    3. Or run: ateam config set-key {provider}
    """
    
    OLLAMA_NOT_RUNNING = """
    ⚠ Cannot connect to Ollama
    
    This means: Ollama service is not running
    
    Fix it:
    1. Install Ollama: https://ollama.com/download
    2. Start service: ollama serve
    3. Verify: ollama list
    
    Alternative: Use cloud providers (Gemini, Claude, GPT)
    """
```

**Implementation Priority: MEDIUM**
- Add error catalog in Phase 2
- Improve messages in Phase 4.2

---

### 10. **No "Undo" or Conversation Branching**

**Problem:**
Users can't undo bad agent responses or explore alternatives.

**User Impact:**
```bash
You: @Architect, design a REST API

Architect: [Gives a terrible design]

You: Uh... can we try that again with a different approach?
# Currently: No way to "rewind" except manually editing history.json
```

**Recommended Solution:**

**A. Simple Undo (Phase 4)**
```bash
$ ateam undo
Removed last message from Architect
Context restored to 8 messages ago

$ ateam undo 3
Removed last 3 messages
```

**B. Branching (Phase 5 / Future)**
```bash
You: @Architect, design a REST API

Architect: [Response A]

You: /branch try-graphql
Created branch: try-graphql

You: @Architect, what about GraphQL instead?

Architect: [Response B - different direction]

# Later:
$ ateam branches
  main (10 messages)
* try-graphql (12 messages)

$ ateam checkout main
Switched to branch: main
```

**Implementation Priority:**
- Basic undo: MEDIUM (Phase 4)
- Branching: LOW (Phase 5)

---

## 🔧 MINOR FRICTION POINTS

### 11. **No Conversation Export Templates**

Add export formats:
- Markdown (current)
- HTML (with syntax highlighting)
- JSON (for programmatic analysis)
- PDF (for sharing with non-technical stakeholders)

**Implementation Priority: LOW**

---

### 12. **Missing Keyboard Shortcuts**

Interactive mode should support:
- `Ctrl+C`: Cancel current input (not exit)
- `Ctrl+D`: Exit room
- `Ctrl+R`: Search history
- `↑/↓`: Navigate message history

**Implementation Priority: LOW**

---

### 13. **No Streaming Responses**

Current: Wait for full response, then display all at once
Better: Stream tokens as they arrive (feels faster)

```bash
You: @Architect, explain microservices

Architect: Microservices are an architectural pattern where...
[text appears in real-time as model generates it]
```

**Implementation Priority: LOW (Phase 5)**

---

## 📊 PRIORITY MATRIX

### Must Fix Before MVP (Phase 1-3):
1. ✅ API Key Management (interactive setup)
2. ✅ Context window visibility
3. ✅ Multi-agent sequential routing
4. ✅ SQLite from start
5. ✅ Ollama optional, not required

### Should Fix Before Public Release (Phase 4):
6. ✅ Smart MCP permissions
7. ✅ Model selection guidance
8. ✅ Better error messages
9. ✅ Basic undo functionality

### Nice to Have (Phase 5+):
10. Room search/discovery
11. Export templates
12. Keyboard shortcuts
13. Streaming responses
14. Conversation branching

---

## 🎯 IMPLEMENTATION RECOMMENDATIONS

### Update These Spec Files:

1. **specs.md**:
   - Add section on API key management UX
   - Clarify multi-agent routing behavior
   - Document context window visibility

2. **technical.md**:
   - Change Phase 1 to use SQLite (not JSON)
   - Add error message catalog architecture
   - Specify token counter implementation

3. **tasks.md**:
   - Add Task 1.2.2: "Interactive API key setup"
   - Add Task 2.1.1: "Sequential multi-agent routing"
   - Add Task 3.1.2: "Token counter display"
   - Move SQLite implementation to Phase 1.4 (not Phase 2)

4. **README.md**:
   - Clarify Ollama is optional
   - Add model comparison table
   - Add troubleshooting section with actionable errors

5. **config.yaml**:
   - Add permission profiles example
   - Add model selection comments
   - Show trust levels

---

## 🚀 QUICK WINS (Fix These First)

These changes have high impact with low effort:

1. **Add `ateam init --interactive`** (1 hour)
   - Walks through provider setup
   - Tests API keys immediately
   - Sets up first room

2. **Show token counts in prompt** (30 minutes)
   ```bash
   [1.2K tokens] You: _
   ```

3. **Detect Ollama, don't require it** (30 minutes)
   - Try connecting, continue if fails
   - Show helpful message if detected but no models

4. **Better default config.yaml** (1 hour)
   - Include all providers with comments
   - Show which need API keys
   - Provide model recommendations

These 4 changes would eliminate 80% of early user friction!

---

## 💡 CONCLUSION

The A-Team spec is solid, but these friction points could frustrate early users. Prioritize:

1. **Onboarding** (API keys, setup wizard)
2. **Transparency** (token counts, what's happening)
3. **Intelligence** (smart routing, smart pruning, smart permissions)
4. **Error handling** (actionable messages)

Fix the "Must Fix Before MVP" items and you'll have a delightful user experience!
