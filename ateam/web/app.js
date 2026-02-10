let currentRoom = null;

async function fetchData(endpoint) {
    try {
        const response = await fetch(`/api/${endpoint}`);
        return await response.json();
    } catch (e) {
        console.error(`Error fetching ${endpoint}:`, e);
        return null;
    }
}

async function refreshRooms() {
    const rooms = await fetchData('rooms');
    if (!rooms) return;

    const list = document.getElementById('room-list');
    list.innerHTML = '';

    rooms.forEach(room => {
        const li = document.createElement('li');
        li.className = `room-item ${currentRoom === room.name ? 'active' : ''}`;
        li.onclick = () => selectRoom(room.name);
        
        li.innerHTML = `
            <span class="room-name">${room.name}</span>
            <div class="room-meta">
                ${room.message_count} msgs • ${room.last_active.substring(11, 16)}
            </div>
        `;
        list.appendChild(li);
    });

    if (!currentRoom && rooms.length > 0) {
        selectRoom(rooms[0].name);
    }
}

async function selectRoom(name) {
    currentRoom = name;
    document.getElementById('current-room-name').innerText = name;
    
    // Update active state in UI
    document.querySelectorAll('.room-item').forEach(el => {
        el.classList.toggle('active', el.querySelector('.room-name').innerText === name);
    });

    refreshHistory();
}

async function refreshHistory() {
    if (!currentRoom) return;
    
    const history = await fetchData(`history?room=${currentRoom}`);
    if (!history) return;

    const container = document.getElementById('chat-history');
    container.innerHTML = '';

    history.forEach(msg => {
        const div = document.createElement('div');
        div.className = `message ${msg.role}`;
        
        const roleText = msg.agent_tag ? `@${msg.agent_tag}` : msg.role.toUpperCase();
        
        div.innerHTML = `
            <div class="message-header">
                <span class="msg-role">${roleText}</span>
                <span class="msg-time">${msg.timestamp.substring(11, 19)}</span>
            </div>
            <div class="msg-content">${escapeHtml(msg.content)}</div>
        `;
        container.appendChild(div);
    });
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;

    // Update stats
    document.getElementById('msg-count').innerText = history.length;
    const lastAsst = history.filter(m => m.role === 'assistant').pop();
    if (lastAsst) {
        document.getElementById('lead-agent').innerText = `@${lastAsst.agent_tag || 'System'}`;
    }
}

async function refreshSummary() {
    const summary = await fetchData('summary');
    if (!summary) return;

    const container = document.getElementById('workspace-summary');
    container.innerHTML = `<pre style="white-space: pre-wrap; color: #a0a0a0;">${escapeHtml(summary)}</pre>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initial Load
refreshRooms();
refreshSummary();

// Update Polling
setInterval(refreshRooms, 5000);
setInterval(refreshHistory, 2000);
document.getElementById('connection-status').innerText = 'LIVE REFLECTION';
document.getElementById('connection-status').style.color = '#00f2ff';
