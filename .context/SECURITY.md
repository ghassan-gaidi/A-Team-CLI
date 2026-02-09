# Security Policy

## Overview

A-Team CLI handles sensitive data including API keys, conversation history, and file system access. This document outlines our security practices and how to report vulnerabilities.

## Security Principles

1. **Defense in Depth** - Multiple layers of security controls
2. **Principle of Least Privilege** - Minimal permissions by default
3. **Fail Secure** - Errors default to denying access
4. **Security by Design** - Built-in from the start, not bolted on
5. **Transparency** - Open source, auditable code

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

We provide security updates for the latest minor version only.

## Security Features

### 1. API Key Protection

**How we protect your API keys:**
- ✅ Stored in system keyring (OS-level encryption)
- ✅ Never logged, even in debug mode
- ✅ Filtered from error messages and stack traces
- ✅ Validated before storage
- ✅ Not stored in config files (warns if user does this)
- ✅ Support for key rotation

**Best practices:**
```bash
# GOOD - Use keyring
ateam config set-key gemini

# GOOD - Use environment variables
export GOOGLE_API_KEY="your-key"

# BAD - Don't put keys in config.yaml (will show warning)
```

### 2. Input Validation

**All user inputs are validated:**
- Room names: 3-50 chars, alphanumeric + hyphens/underscores
- Agent names: 2-50 chars, same rules
- Messages: Max 50,000 chars, sanitized
- File paths: Strict whitelist, path traversal blocked

**Protection against:**
- SQL injection (parameterized queries)
- Path traversal (`../`, symlinks)
- Command injection (validated arguments)
- Null byte injection
- Resource exhaustion (length limits)

### 3. File System Security

**Sandboxed file access:**
```yaml
# Only these directories are accessible
mcp:
  filesystem:
    allowed_paths:
      - "~/projects"
      - "~/Documents"
```

**Blocked by default:**
- `/etc/` (system files)
- `~/.ssh/` (SSH keys)
- `~/.aws/` (AWS credentials)
- Files matching: `.env`, `.key`, `.pem`, `id_rsa`, `credentials`
- Any path with `..` (traversal attempt)
- Symlinks pointing outside allowed directories

### 4. Rate Limiting

**Prevents abuse:**
- API calls: 100/minute (configurable per provider)
- Room creation: 10/minute
- File operations: 50/minute

**What happens when limit is hit:**
```
⚠ Rate limit exceeded for gemini. Try again in 23 seconds.
```

### 5. Secure Logging

**Never logged:**
- API keys (auto-redacted with regex filters)
- File contents from sensitive files
- Full file paths (only relative paths logged)

**Always logged:**
- Failed authentication attempts
- Permission denied events
- Rate limit violations
- Security-relevant errors

## Security Testing

We perform the following security testing before each release:

### Automated Testing
```bash
# Dependency vulnerability scanning
pip-audit

# Python security linting
bandit -r ateam/

# Dependency security checking
safety check

# Full test suite including security tests
pytest tests/security/ -v
```

### Manual Testing
- [ ] OWASP Top 10 review
- [ ] Path traversal attempts
- [ ] SQL injection attempts
- [ ] API key exposure checks
- [ ] Permission boundary testing
- [ ] Rate limit enforcement
- [ ] Error message information disclosure

## Threat Model

### In Scope
- Local file access exploitation
- API key exposure
- Path traversal attacks
- SQL injection
- Command injection
- Rate limit bypass
- Input validation bypass

### Out of Scope
- Physical access attacks
- Social engineering
- Attacks requiring MITM on user's network
- Browser-based attacks (CLI tool only)
- Attacks on third-party services (OpenAI, Anthropic, etc.)

## Known Limitations

1. **Local Storage**: Conversation history is stored unencrypted on disk. Users concerned about this should use full-disk encryption.

2. **Ollama Security**: When using local Ollama models, security depends on Ollama's implementation. We cannot guarantee security beyond our API calls.

3. **Terminal History**: User messages may appear in shell history. Use `HISTCONTROL=ignorespace` and prefix commands with space if concerned.

4. **Memory**: API keys and messages exist in memory during runtime. Memory dumps could expose sensitive data.

## Reporting a Vulnerability

### How to Report

**Please DO:**
- Email: security@ateam.dev
- Include detailed steps to reproduce
- Provide proof-of-concept if possible
- Allow reasonable time for fix before public disclosure

**Please DON'T:**
- Open public GitHub issues for security bugs
- Disclose publicly before we've issued a fix
- Exploit the vulnerability beyond proof-of-concept

### What to Expect

| Timeline | Action |
|----------|--------|
| 24 hours | Initial response acknowledging receipt |
| 48 hours | Vulnerability assessment and severity rating |
| 7 days   | Fix developed and tested (for HIGH/CRITICAL) |
| 14 days  | Fix developed and tested (for MEDIUM/LOW) |
| After fix | Coordinated disclosure, credit in release notes |

### Severity Ratings

**CRITICAL** - Immediate action required
- Remote code execution
- API key exposure to external parties
- Unrestricted file system access

**HIGH** - Fix within 7 days
- Path traversal allowing access to sensitive files
- SQL injection
- Rate limit bypass allowing DoS

**MEDIUM** - Fix within 14 days
- Information disclosure (non-sensitive)
- Input validation bypass
- Local privilege escalation

**LOW** - Fix in next release
- Weak default configuration
- Non-exploitable edge cases

## Security Best Practices for Users

### 1. API Key Management
```bash
# Use system keyring (most secure)
ateam config set-key gemini

# OR use environment variables (secure)
export GOOGLE_API_KEY="your-key"

# Rotate keys regularly
ateam config rotate-key gemini
```

### 2. File System Permissions
```bash
# Ensure config directory has correct permissions
chmod 700 ~/.config/ateam

# Ensure .env files are not world-readable
chmod 600 .env
```

### 3. Version Updates
```bash
# Always use the latest version
pip install --upgrade ateam-cli

# Check for security updates
ateam version --check-updates
```

### 4. Audit Your Configuration
```bash
# Review security settings
ateam config show --security

# Test your API keys are stored securely
ateam config test-keys --verbose
```

### 5. Monitor Usage
```bash
# Review your API usage
ateam stats

# Check for suspicious activity
ateam logs --level=warning
```

## Compliance

### OWASP Top 10 (2021)

| Risk | Status | Mitigation |
|------|--------|------------|
| A01: Broken Access Control | ✅ Mitigated | Whitelist-based file access, permission checks |
| A02: Cryptographic Failures | ✅ Mitigated | System keyring encryption, no custom crypto |
| A03: Injection | ✅ Mitigated | Parameterized queries, input validation |
| A04: Insecure Design | ✅ Mitigated | Security by design, threat modeling |
| A05: Security Misconfiguration | ✅ Mitigated | Secure defaults, configuration validation |
| A06: Vulnerable Components | ✅ Mitigated | Dependency scanning, regular updates |
| A07: Auth Failures | ⚠️ Partial | API key validation (no user auth yet) |
| A08: Data Integrity Failures | ✅ Mitigated | SQLite ACID, input validation |
| A09: Logging Failures | ✅ Mitigated | Security event logging, key redaction |
| A10: SSRF | ✅ Mitigated | URL validation, blocked private IPs |

### CWE Top 25 (Most Dangerous Software Weaknesses)

We have implemented mitigations for all applicable CWEs from the 2023 list:

- CWE-89: SQL Injection → Parameterized queries
- CWE-79: XSS → N/A (CLI tool, no HTML output)
- CWE-20: Input Validation → Comprehensive Pydantic schemas
- CWE-78: Command Injection → Argument validation, list form
- CWE-22: Path Traversal → Whitelist + sanitization
- CWE-352: CSRF → N/A (local CLI, no web interface)
- CWE-434: File Upload → Strict path validation, size limits
- CWE-862: Missing Authorization → Permission checks on all file ops

## Security Updates

We will publish security advisories for all vulnerabilities rated MEDIUM or higher.

**Stay informed:**
- Watch this repository for security advisories
- Subscribe to releases: https://github.com/yourusername/ateam/releases
- Follow security updates: https://twitter.com/ateam_security

## Hall of Fame

We acknowledge security researchers who responsibly disclose vulnerabilities:

<!-- Security researchers who help us will be listed here -->
- *Your name could be here!*

## Contact

- Security issues: security@ateam.dev
- General contact: support@ateam.dev
- Website: https://ateam.dev

---

**Last updated**: 2024-02-09
**Next review**: 2024-05-09 (quarterly review)
