# 🚀 A-TEAM PROJECT - MASTER PROMPT FOR CLAUDE CODE

Copy and paste this prompt into Claude Code to begin development.

================================================================================

Hi! I'm building **A-Team CLI** - a production-grade, security-hardened multi-agent AI orchestration tool that lets different AI models (Gemini, Claude, GPT, local models) collaborate in shared "Rooms" with unified context.

## 📁 Project Context

I have **complete, production-ready specification files**. Please read ALL of these files first to understand the full project:

### Core Specifications (READ FIRST - PRIORITY ORDER)
1. **START_HERE.md** - This file (overview)
2. **specs.md** - What we're building (features, user workflows, requirements)
3. **technical.md** - How we're building it (architecture, security, implementations)
4. **tasks.md** - Step-by-step implementation roadmap with acceptance criteria
5. **SECURITY.md** - Security policy, threat model, best practices
6. **FRICTION_ANALYSIS.md** - Design decisions and improvements made
7. **CLAUDE_CODE_INSTRUCTIONS.md** - Guide for working with these specs

### Supporting Documentation
8. **README.md** - User-facing documentation
9. **config.yaml** - Example configuration with security settings
10. **PROMPT_REFERENCE.md** - Quick reference for common prompts

## 🎯 Your Mission

After reading all the context files, we'll build this project **incrementally** following the task roadmap in `tasks.md`. 

**Critical Principles:**
- ✅ Complete ONE task at a time, in order (they have dependencies)
- ✅ **Security first** - Implement security features in Phase 1, not later
- ✅ Test each task before moving to the next
- ✅ Commit after each completed task
- ✅ Reference the specs when making implementation decisions
- ✅ Ask for clarification if acceptance criteria are unclear

## 🔒 Security Requirements (CRITICAL)

This project handles sensitive data (API keys, user files, conversations). Security is **non-negotiable**:

- ✅ **API keys** stored in system keyring (encrypted), never in config files
- ✅ **Rate limiting** on all API calls and user actions
- ✅ **Input validation** using Pydantic schemas (prevent injection attacks)
- ✅ **Path traversal prevention** (block `../`, symlinks, sensitive files)
- ✅ **Secure logging** (API keys auto-redacted from all logs/errors)
- ✅ **SQL injection prevention** (parameterized queries only)
- ✅ **Command injection prevention** (validated arguments)

**See SECURITY.md for full threat model and requirements.**

## 🏁 Starting Point

**First, please:**

1. **Confirm** you've read and understood all 10 specification files
2. **Summarize** the key architectural decisions:
   - What tech stack are we using?
   - What's the file structure?
   - What are the critical security requirements?
   - What makes our approach unique? (SQLite from start, smart permissions, etc.)
3. **List** the security controls that must be implemented in Phase 1
4. **Then begin** with **Phase 1, Task 1.1** from tasks.md: "Create `pyproject.toml` with project metadata"

## 📋 Development Flow

For each task, follow this pattern:

1. **Read** the task from tasks.md (with acceptance criteria)
2. **Check** technical.md for implementation details and security requirements
3. **Check** SECURITY.md if task involves sensitive data or user input
4. **Implement** the solution following security best practices
5. **Test** against acceptance criteria (including security tests)
6. **Verify** no security issues (API keys in logs, path traversal, etc.)
7. **Commit** with message: "Complete task X.X: [description]"
8. **Ask** if I want to proceed to next task or review

## ⚙️ Technical Stack

### Core Technologies
- **Python 3.11+** with modern type hints
- **uv** for dependency management (faster than pip)
- **Typer** for CLI commands
- **Rich** for terminal output
- **SQLite** from the start (not JSON - ACID guarantees)
- **Pydantic** for input validation (security-critical)
- **keyring** for secure API key storage
- **tiktoken** for token counting
- **pytest** for testing

### Security Tools (Must Use)
- **pip-audit** - Dependency vulnerability scanning
- **bandit** - Python security linting
- **safety** - Known security issue checking
- **ruff** with security rules (S, B, E)

## 🔐 Security Implementation Checklist

Before writing ANY code that handles:
- ✅ API keys → Use SecureAPIKeyManager (technical.md)
- ✅ User input → Use InputValidator with Pydantic (technical.md)
- ✅ File paths → Use validate_file_path with whitelist (technical.md)
- ✅ SQL queries → Use parameterized queries ONLY
- ✅ External commands → Use list form with validated args
- ✅ API calls → Use RateLimiter (technical.md)

## 🚦 Ready to Start?

Once you've read everything and summarized your understanding:

1. Confirm you understand the **security requirements**
2. List the **security controls** being implemented in Phase 1
3. Explain why we're using **SQLite from the start** (not JSON)
4. Explain the **API key storage hierarchy** (keyring > env > config)
5. Then let's begin with **Task 1.1**!

If anything in the specs is unclear or seems contradictory, please ask before implementing.

## 📊 Project Metadata

**Project Type:** Security-hardened CLI tool  
**Security Level:** OWASP Top 10 compliant  
**Test Coverage Target:** >70% overall, >90% for security-critical components  
**Coding Standards:** PEP 8, type hints required, security-first  

## ⚠️ Important Reminders

**DO:**
- ✅ Read SECURITY.md before implementing authentication/input handling
- ✅ Use the security implementations from technical.md (don't reinvent)
- ✅ Test security controls (path traversal, SQL injection, rate limits)
- ✅ Run security audit tools (pip-audit, bandit, safety)

**DON'T:**
- ❌ Store API keys in config files (use keyring)
- ❌ Use string interpolation for SQL (use parameterized queries)
- ❌ Skip input validation (use Pydantic schemas)
- ❌ Log sensitive data (keys are auto-redacted, but be careful)
- ❌ Allow path traversal (always validate with InputValidator)

================================================================================

**Note to Claude Code:** This is a **security-critical**, well-spec'd project. All architectural and security decisions have been made and documented. Your job is to implement them faithfully, with security as the top priority. When in doubt, check the specs - they contain the answers!

**Security is not optional. It's implemented in Phase 1, tested thoroughly, and audited before release.**


