# 🚀 QUICK START GUIDE - A-Team CLI Development

## 📦 What You Have

You now have a **complete, production-ready specification** for a security-hardened multi-agent AI orchestration CLI tool. All architectural decisions have been made, security requirements defined, and implementation roadmap created.

## 📁 Project Files (10 Documents)

### 1️⃣ Core Specifications (Read in Order)
```
.context/
├── START_HERE.md              ⭐ Master prompt for Claude Code
├── specs.md                   📋 Functional specifications
├── technical.md               🏗️ Technical architecture + security
├── tasks.md                   ✅ Implementation roadmap
└── SECURITY.md                🔒 Security policy & threat model
```

### 2️⃣ Development Guides
```
.context/
├── CLAUDE_CODE_INSTRUCTIONS.md  📚 How to work with AI IDE
├── PROMPT_REFERENCE.md          💡 Quick prompts for common tasks
└── FRICTION_ANALYSIS.md         🔍 Design decisions & rationale
```

### 3️⃣ User Documentation
```
.context/
├── README.md                   📖 User-facing documentation
└── config.yaml                 ⚙️ Example configuration
```

## 🎯 File Summary

| File | Purpose | When to Reference |
|------|---------|------------------|
| **START_HERE.md** | Master prompt to begin | Opening Claude Code |
| **specs.md** | What we're building | Understanding features |
| **technical.md** | How we're building it | Implementation details |
| **tasks.md** | What to build next | Every task |
| **SECURITY.md** | Security requirements | Handling sensitive data |
| **README.md** | User documentation | Understanding user experience |
| **config.yaml** | Configuration example | Setting up agents |
| **CLAUDE_CODE_INSTRUCTIONS.md** | AI IDE workflow | Development process |
| **PROMPT_REFERENCE.md** | Quick prompts | Common scenarios |
| **FRICTION_ANALYSIS.md** | Design rationale | Understanding decisions |

---

## 🏁 Getting Started (3 Steps)

### Step 1: Set Up Project Structure

```bash
# Create project directory
mkdir ateam-cli && cd ateam-cli

# Create context directory for specs
mkdir .context

# Move all 10 spec files into .context/
# (START_HERE.md, specs.md, technical.md, tasks.md, SECURITY.md,
#  CLAUDE_CODE_INSTRUCTIONS.md, PROMPT_REFERENCE.md, FRICTION_ANALYSIS.md,
#  README.md, config.yaml)

# Initialize git
git init
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".venv/" >> .gitignore
echo "dist/" >> .gitignore
echo "build/" >> .gitignore
echo "*.egg-info/" >> .gitignore

# Create initial commit
git add .
git commit -m "Initial commit: Project specifications"
```

Your structure should look like:
```
ateam-cli/
├── .git/
├── .gitignore
└── .context/
    ├── START_HERE.md
    ├── specs.md
    ├── technical.md
    ├── tasks.md
    ├── SECURITY.md
    ├── README.md
    ├── config.yaml
    ├── CLAUDE_CODE_INSTRUCTIONS.md
    ├── PROMPT_REFERENCE.md
    └── FRICTION_ANALYSIS.md
```

### Step 2: Open in Claude Code (or AI IDE)

```bash
# If using Claude Code
code .

# If using Cursor
cursor .

# If using Windsurf
windsurf .
```

### Step 3: Use the Master Prompt

**Copy this EXACT prompt into Claude Code:**

```
Hi! I'm building A-Team CLI - a production-grade, security-hardened multi-agent 
AI orchestration tool.

📁 Context Files
I have 10 complete specification files in .context/. Please read ALL of them in 
this order:

1. START_HERE.md - Project overview
2. specs.md - Functional specifications  
3. technical.md - Architecture & security
4. tasks.md - Implementation roadmap
5. SECURITY.md - Security requirements
6. CLAUDE_CODE_INSTRUCTIONS.md - Development workflow
7. FRICTION_ANALYSIS.md - Design decisions
8. README.md - User documentation
9. config.yaml - Example configuration
10. PROMPT_REFERENCE.md - Quick reference

🎯 After Reading
1. Confirm you've read all 10 files
2. Summarize key architectural decisions
3. List security controls in Phase 1
4. Explain why SQLite from start (not JSON)
5. Explain API key storage hierarchy

🔒 Critical Security Requirements
- API keys in system keyring (encrypted)
- Rate limiting on all endpoints
- Pydantic schemas for input validation
- Path traversal prevention
- Secure logging (keys auto-redacted)

🏁 Then Start
Begin with Phase 1, Task 1.1 from tasks.md: "Create pyproject.toml"

Technical Stack: Python 3.11+, uv, Typer, Rich, SQLite, Pydantic, keyring, pytest

Security Tools: pip-audit, bandit, safety, ruff

Ready? Read the specs and let's build!
```

---

## 📋 What Happens Next

### Phase 1: Claude Code Will

1. ✅ **Read all 10 specification files** (~5 minutes)
2. ✅ **Summarize understanding**:
   - Tech stack (Python 3.11+, Typer, SQLite, etc.)
   - File structure (ateam/, tests/, pyproject.toml)
   - Security approach (keyring, validation, rate limits)
   - Unique features (SQLite from start, smart permissions)
3. ✅ **Confirm security understanding**:
   - API keys stored in system keyring
   - Input validation with Pydantic
   - Rate limiting implementation
   - Path traversal prevention
4. ✅ **Ask for approval** to start Task 1.1

### Phase 2: Incremental Development

Claude Code will follow tasks.md step by step:

**Phase 1 (3-4 hours)**: Foundation
- Task 1.1: Create pyproject.toml
- Task 1.2: Implement security (API keys, validation, rate limits)
- Task 1.3: Room management
- Task 1.4: History management (SQLite)

**Phase 2 (4-5 hours)**: Agent orchestration
- Task 2.1: Message parsing & routing
- Task 2.2: Provider adapters
- Task 2.3: Gemini provider
- Task 2.4: Ollama provider
- Task 2.5: Wire it together

**Phase 3 (5-6 hours)**: Shared context & MCP
- Task 3.1: Context window management
- Task 3.2: MCP filesystem tool (with smart permissions)
- Task 3.3: Agent awareness

**Phase 4 (3-4 hours)**: Polish & distribution
- Task 4.1: CLI enhancements
- Task 4.2: Error handling
- Task 4.3: Testing & security audit
- Task 4.4: Documentation

---

## 💬 Common Prompts During Development

### After Each Task
```
Task 1.1 complete. Please review against acceptance criteria, 
commit with message "Complete task 1.1: Create pyproject.toml", 
then move to Task 1.2.
```

### If Tests Fail
```
Tests for [component] are failing. Please:
1. Show actual vs expected output
2. Check implementation against technical.md
3. Fix and re-run tests
```

### Security Check
```
Before committing, verify:
1. No API keys in logs/errors
2. All inputs validated with Pydantic
3. File paths validated with InputValidator
4. SQL queries use parameterization
5. Security tests pass
```

### Moving to Next Phase
```
We've completed Phase 1. Before Phase 2:
1. Run full test suite
2. Run security audit (pip-audit, bandit, safety)
3. Review code against technical.md
4. Check security checklist in tasks.md
5. Then start Phase 2, Task 2.1
```

---

## 🔐 Security Reminders

### Before Writing ANY Code That Handles:

| Data Type | Must Use | Location |
|-----------|----------|----------|
| API keys | `SecureAPIKeyManager` | technical.md |
| User input | `InputValidator` + Pydantic | technical.md |
| File paths | `validate_file_path()` | technical.md |
| SQL queries | Parameterized queries ONLY | technical.md |
| External commands | List form + validation | technical.md |
| API calls | `RateLimiter` | technical.md |

### Security Audit Checklist (Run Before Each Commit)

```bash
# Check dependencies for vulnerabilities
pip-audit

# Run Python security linter
bandit -r ateam/

# Check for known security issues
safety check

# Run security test suite
pytest tests/security/ -v
```

---

## 📊 Progress Tracking

As you complete tasks, update tasks.md:

```markdown
## Phase 1: Foundation & Project Setup
- [x] Task 1.1: Create pyproject.toml
- [x] Task 1.2: Implement SecureAPIKeyManager
- [x] Task 1.3: Implement InputValidator
- [ ] Task 1.4: Implement RateLimiter  ← Currently here
```

---

## 🎓 Learning Resources

If you're new to any technology:

**Python Security:**
- Read: `SECURITY.md` for threat model
- Read: `technical.md` Security Considerations section
- Reference: OWASP Top 10 (linked in SECURITY.md)

**Project Architecture:**
- Read: `technical.md` System Architecture
- Read: `specs.md` Core Capabilities
- Reference: Component diagrams in technical.md

**Development Workflow:**
- Read: `CLAUDE_CODE_INSTRUCTIONS.md` (detailed guide)
- Read: `PROMPT_REFERENCE.md` (quick prompts)
- Reference: tasks.md for next steps

---

## ✅ Pre-Flight Checklist

Before you start coding, verify you have:

- [ ] All 10 spec files in `.context/` directory
- [ ] Git repository initialized
- [ ] `.gitignore` configured (no secrets in version control)
- [ ] Claude Code (or AI IDE) open in project directory
- [ ] Understanding of security requirements (read SECURITY.md)
- [ ] Master prompt ready to paste
- [ ] Python 3.11+ installed (check: `python --version`)
- [ ] uv installed (or plan to install: `pip install uv`)

---

## 🚀 You're Ready!

You now have everything needed to build a **production-grade, security-hardened CLI tool**:

✅ **Complete specifications** (10 files, 5000+ lines)  
✅ **Security hardened** (OWASP Top 10 compliant)  
✅ **Implementation roadmap** (50+ tasks with acceptance criteria)  
✅ **Code examples** (full implementations in technical.md)  
✅ **Testing strategy** (unit, integration, security)  
✅ **Development workflow** (AI IDE optimized)  

**Just paste the master prompt into Claude Code and start building!**

---

## 🆘 Need Help?

**Claude Code not following specs?**
→ "STOP. Read all files in .context/ first, then summarize understanding."

**Implementation doesn't match specs?**
→ "Check technical.md Section [X]. Spec says [Y], but you did [Z]. Fix to match spec."

**Security concern?**
→ "Check SECURITY.md. Does this implementation meet the security requirements?"

**Stuck on a task?**
→ "Read the acceptance criteria for Task [X.X] in tasks.md. What's unclear?"

---

**Good luck! You're about to build something amazing.** 🎉
