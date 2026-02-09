# Contributing to A-Team CLI 🚀

First off, thank you for considering contributing to A-Team! It's people like you that make A-Team such a great tool.

## 🌈 How Can I Contribute?

### Reporting Bugs
- Use the GitHub issue tracker.
- Check if the issue has already been reported.
- Use a clear and descriptive title.
- Describe the exact steps which reproduce the problem.

### Suggesting Enhancements
- Open a new issue with the "feature request" label.
- Explain why this enhancement would be useful.
- Provide examples of how it would work.

### Pull Requests
1. Fork the repo and create your branch from `main`.
2. Install development dependencies: `pip install -e ".[dev]"` (if defined) or `pip install pytest pytest-asyncio pydantic pyyaml rich typer`.
3. Ensure the test suite passes: `pytest tests/unit/`.
4. Add tests for any new functionality.
5. Follow the existing code style (PEP 8).
6. Update documentation if necessary.

## 🏗️ Technical Architecture

- **`ateam.cli`**: Typer commands and the Rich-based interactive interface.
- **`ateam.core`**: Orchestration logic (Router, Config, Context, History management).
- **`ateam.providers`**: Adapters for various AI providers (OpenAI, Gemini, Anthropic, Ollama).
- **`ateam.security`**: Secure API key management, rate limiting, and input validation.
- **`ateam.tools`**: MCP-inspired tool system for system interaction.

## 🛡️ Security Policy

If you discover a security vulnerability, please do NOT open a public issue. Instead, email the maintainers or follow the instructions in `SECURITY.md`.

## 📝 Commit Messages

- Use the present tense ("Add feature" not "Added feature").
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
- Limit the first line to 72 characters or less.

---

Happy coding! 🚀
