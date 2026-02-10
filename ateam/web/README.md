# A-Team Web Dashboard

This is the web-based reflection interface for the A-Team CLI.

## Features
- **Real-time Chat Timeline**: Watch agent conversations as they happen.
- **Glassmorphic UI**: Premium dark-mode aesthetic.
- **Project Map**: Visual exploration of your project structure.
- **Room Management**: Switch between active mission rooms.

## Running the Dashboard

The dashboard is integrated into the A-Team CLI, but can be run standalone for development:

```bash
# From the project root
python -m ateam.web.server
```

Then open `http://localhost:8080` in your browser.

## Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: Vanilla JS + CSS (No build step required)
- **Communication**: REST API + WebSockets
