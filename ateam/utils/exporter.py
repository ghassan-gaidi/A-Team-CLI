"""
Mission Manifest Exporter for A-Team CLI.
"""

from datetime import datetime
from pathlib import Path
from typing import List
from ateam.core.history import Message


class ManifestExporter:
    """
    Generates a structured Markdown report of a conversation mission.
    """

    @staticmethod
    def export(room_name: str, messages: List[Message]) -> str:
        """
        Creates a MISSION_MANIFEST.md file and returns the path.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"MISSION_MANIFEST_{room_name}_{timestamp}.md"
        filepath = Path.cwd() / filename

        # Analyze statistics
        total_msgs = len(messages)
        agents = set(m.agent_tag for m in messages if m.agent_tag and m.agent_tag != "system")
        tools_called = [m.content for m in messages if m.role == "system" and "Tool '" in m.content]
        
        manifest = f"""# 📝 Mission Manifest: {room_name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Mission Overview
- **Room:** `{room_name}`
- **Total Messages:** {total_msgs}
- **Agents Involved:** {', '.join(f'@{a}' for a in agents) if agents else 'None'}
- **Tools Executed:** {len(tools_called)}

## 📜 Conversation Timeline
"""
        for m in messages:
            role = f"@{m.agent_tag}" if m.agent_tag else m.role.upper()
            time_str = m.timestamp.strftime("%H:%M:%S")
            
            if m.role == "system":
                manifest += f"\n> **[{time_str}] SYSTEM**: {m.content.strip()}\n"
            else:
                manifest += f"\n### {role} ({time_str})\n{m.content.strip()}\n"

        manifest += f"\n---\n**End of Manifest** - Created by A-Team CLI 🚀\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(manifest)

        return str(filepath)
