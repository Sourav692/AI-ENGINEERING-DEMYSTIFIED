let ws;

// --- Setup Function ---
function startInterview() {
    const role = document.getElementById('jobRole').value;
    if(!role) return alert("Please enter a job role");

    // UI Transition
    document.getElementById('setup-screen').style.display = 'none';
    document.getElementById('chat-screen').style.display = 'flex';
    document.getElementById('role-display').innerText = role + " Interview";

    // Establish WebSocket Connection
    // Uses window.location.host so it works on any port or server
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    ws = new WebSocket(`${protocol}://${window.location.host}/ws/interview?pos=${encodeURIComponent(role)}`);

    ws.onopen = function() {
        console.log("Connected to Interview Server");
    };

    ws.onmessage = function(event) {
        const data = event.data;
        
        // 1. Handle System Commands
        if (data.startsWith("SYSTEM_TURN:USER")) {
            enableInput(true);
            return;
        }
        if (data.startsWith("SYSTEM_INFO:")) {
            addSystemMessage(data.split(":")[1]);
            return;
        }
        if (data.startsWith("SYSTEM_END:")) {
            addSystemMessage("Interview Finished.");
            enableInput(false);
            document.getElementById('status').style.color = 'red';
            document.getElementById('status').innerText = '● Finished';
            ws.close();
            return;
        }

        // 2. Handle Chat Messages (Source:Content)
        const firstColon = data.indexOf(':');
        if(firstColon > -1) {
            const source = data.substring(0, firstColon);
            const content = data.substring(firstColon + 1);
            addMessage(source, content);
        }
    };
    
    ws.onclose = function() {
        document.getElementById('status').style.color = 'gray';
        document.getElementById('status').innerText = '● Disconnected';
    };
}

// --- Chat Functions ---

function addMessage(source, content) {
    // If source is 'Candidate', ignore it because we already rendered the user's message manually
    if(source === 'Candidate') return;

    const messagesDiv = document.getElementById('messages');
    const bubble = document.createElement('div');
    
    let type = 'interviewer';
    if(source === 'Evaluator') type = 'evaluator';

    bubble.className = `message ${type}`;
    
    const nameSpan = document.createElement('div');
    nameSpan.className = 'sender-name';
    nameSpan.innerText = source;

    const textSpan = document.createElement('div');
    textSpan.innerText = content;

    bubble.appendChild(nameSpan);
    bubble.appendChild(textSpan);
    messagesDiv.appendChild(bubble);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addSystemMessage(text) {
    const messagesDiv = document.getElementById('messages');
    const div = document.createElement('div');
    div.style.textAlign = 'center';
    div.style.color = '#9ca3af';
    div.style.fontSize = '0.8rem';
    div.style.margin = '10px 0';
    div.innerText = text;
    messagesDiv.appendChild(div);
}

function sendMsg() {
    const input = document.getElementById('msgInput');
    const text = input.value.trim();
    if(!text) return;

    // Render User Bubble
    const messagesDiv = document.getElementById('messages');
    const bubble = document.createElement('div');
    bubble.className = 'message user';
    bubble.innerText = text;
    messagesDiv.appendChild(bubble);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    // Send to backend
    ws.send(text);
    
    // Clear and lock input
    input.value = '';
    enableInput(false);
}

function enableInput(enabled) {
    const input = document.getElementById('msgInput');
    input.disabled = !enabled;
    if(enabled) input.focus();
}

// Handle 'Enter' key
document.getElementById('msgInput').addEventListener("keypress", function(event) {
    if (event.key === "Enter") sendMsg();
});