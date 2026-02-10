class DashboardClient {
    constructor() {
        this.currentRoom = null;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.projectStructure = null;
    }

    async init() {
        await this.refreshRooms();
        this.startPolling();
        
        // Event Listeners
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'r') this.refreshRooms();
        });
    }

    async fetchData(endpoint) {
        try {
            const response = await fetch(`/api/${endpoint}`);
            if (!response.ok) throw new Error(response.statusText);
            return await response.json();
        } catch (e) {
            console.error(`Error fetching ${endpoint}:`, e);
            return null;
        }
    }

    async refreshRooms() {
        const rooms = await this.fetchData('rooms');
        if (!rooms) return;

        const list = document.getElementById('room-list');
        list.innerHTML = '';
        
        // Sort rooms: active first, then by date
        rooms.sort((a, b) => new Date(b.last_active) - new Date(a.last_active));

        rooms.forEach((room, index) => {
            const div = document.createElement('div');
            div.className = `room-card ${this.currentRoom === room.name ? 'active' : ''}`;
            div.dataset.roomName = room.name;
            div.onclick = () => this.selectRoom(room.name);
            
            // Format time
            const lastActive = new Date(room.last_active).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            div.innerHTML = `
                <div class="room-info">
                    <span class="room-name">${room.name}</span>
                    <div class="room-meta">
                        ${room.message_count} msgs • ${lastActive}
                    </div>
                </div>
                <div class="live-indicator">🔴 Live</div>
            `;
            list.appendChild(div);
            
            // Auto-select first room if none selected
            if (!this.currentRoom && index === 0) {
                this.selectRoom(room.name);
            }
        });
    }

    async selectRoom(name) {
        if (this.currentRoom === name) return;
        
        // Disconnect previous WS
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        this.currentRoom = name;
        document.getElementById('current-room-name').innerText = name;
        document.getElementById('timeline-room-name').innerText = name;
        
        // Update UI selection using data attribute
        document.querySelectorAll('.room-card').forEach(el => {
            el.classList.toggle('active', el.dataset.roomName === name);
        });

        // Load History
        await this.refreshHistory();
        
        // Load Structure
        await this.refreshStructure();

        // Connect WebSocket
        this.connectWebSocket();
    }

    async refreshHistory() {
        const history = await this.fetchData(`history?room=${this.currentRoom}`);
        if (!history) return;

        const container = document.getElementById('chat-history');
        container.innerHTML = ''; // Clear existing

        history.forEach(msg => this.appendMessage(msg, container));
        
        this.scrollToBottom();
    }
    
    appendMessage(msg, container) {
        const div = document.createElement('div');
        const isUser = msg.role === 'user';
        div.className = `message ${isUser ? 'user' : 'assistant'}`;
        
        const roleName = isUser ? 'User' : (msg.agent_tag || 'System');
        const time = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        div.innerHTML = `
            <div class="message-bubble glass-card">
                <div class="message-header">
                    <span class="agent-name">${roleName}</span>
                    <span class="timestamp">${time}</span>
                </div>
                <div class="message-content">${this.formatContent(msg.content)}</div>
            </div>
        `;
        container.appendChild(div);
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.currentRoom}`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log(`🔌 Connected to ${this.currentRoom}`);
            document.querySelector('.status-indicator .status-text').innerText = 'Live';
            document.querySelector('.status-indicator .pulse').style.background = 'var(--accent-success)';
            this.reconnectAttempts = 0;
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            // Handle real-time updates
            if (data.type === 'message') {
                const container = document.getElementById('chat-history');
                this.appendMessage(data.message, container);
                this.scrollToBottom();
            }
        };
        
        this.ws.onclose = () => {
             console.log('🔌 Disconnected');
             document.querySelector('.status-indicator .status-text').innerText = 'Offline';
             document.querySelector('.status-indicator .pulse').style.background = 'var(--accent-error)';
             this.attemptReconnect();
        };
        
        this.ws.onerror = (err) => console.error('WS Error:', err);
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
            setTimeout(() => {
                this.reconnectAttempts++;
                console.log(`🔄 Reconnecting... (${this.reconnectAttempts})`);
                this.connectWebSocket();
            }, delay);
        }
    }

    async refreshStructure() {
        const structure = await this.fetchData('structure');
        if (!structure) return;
        
        const treeContainer = document.getElementById('file-tree');
        treeContainer.innerHTML = '';
        
        // Initial stats
        let fileCount = 0;
        
        const buildTree = (node, parent) => {
            const div = document.createElement('div');
            div.className = 'tree-node';
            div.style.paddingLeft = '15px';
            
            const icon = node.type === 'directory' ? '📁' : this.getFileIcon(node.name);
            
            div.innerHTML = `
                <div class="node-content">
                    <span class="node-icon">${icon}</span>
                    <span class="node-name">${node.name}</span>
                </div>
            `;
            
            parent.appendChild(div);
            
            if (node.children) {
                const childrenContainer = document.createElement('div');
                childrenContainer.style.marginLeft = '10px';
                childrenContainer.style.borderLeft = '1px solid rgba(255,255,255,0.1)';
                
                // Toggle expansion
                div.querySelector('.node-content').onclick = (e) => {
                    e.stopPropagation();
                    childrenContainer.style.display = childrenContainer.style.display === 'none' ? 'block' : 'none';
                };
                
                node.children.forEach(child => buildTree(child, childrenContainer));
                parent.appendChild(childrenContainer);
            } else {
                fileCount++;
            }
        };
        
        buildTree(structure, treeContainer);
        document.getElementById('stat-files').innerText = fileCount;
        document.getElementById('stat-lines').innerText = 'N/A'; // Need backend support
    }
    
    getFileIcon(filename) {
        if (filename.endsWith('.py')) return '🐍';
        if (filename.endsWith('.js')) return '📜';
        if (filename.endsWith('.html')) return '🌐';
        if (filename.endsWith('.css')) return '🎨';
        if (filename.endsWith('.json')) return '⚙️';
        if (filename.endsWith('.md')) return '📝';
        return '📄';
    }

    formatContent(text) {
        // Basic markdown formatting (bold, code blocks)
        // In production, use a proper library like marked.js
        return text
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    scrollToBottom() {
        const container = document.getElementById('chat-history');
        container.scrollTop = container.scrollHeight;
    }

    startPolling() {
        setInterval(() => this.refreshRooms(), 10000);
    }
}

// Initialize
const app = new DashboardClient();
app.init();
