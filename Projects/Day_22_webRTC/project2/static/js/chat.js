// =============================================
// GLOBAL VARIABLES
// =============================================
let ws = null;
let token = null;
let currentUser = null;
let currentUserId = null;
let selectedUserId = null;
let selectedUsername = null;

// WebRTC variables
let localStream = null;
let remoteStream = null;
let peerConnection = null;
let currentCallId = null;
let isCallActive = false;
let callTimerInterval = null;
let callStartTime = null;

// Incoming call data (stored when call arrives)
let incomingCallData = null;

// STUN/ICE servers configuration
const rtcConfig = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
    ]
};

// =============================================
// INITIALIZATION
// =============================================
window.addEventListener('load', () => {
    console.log('🚀 Chat app initializing...');
    
    token = localStorage.getItem('chat_token');
    currentUser = localStorage.getItem('chat_username');
    currentUserId = localStorage.getItem('chat_user_id');
    
    console.log('User:', currentUser, 'ID:', currentUserId);
    
    if (!token) {
        console.log('❌ No token found, redirecting to login');
        window.location.href = '/login.html';
        return;
    }
    
    connectWebSocket();
    loadUsers();
});

// =============================================
// WEBSOCKET CONNECTION
// =============================================
function connectWebSocket() {
    console.log('🔌 Connecting to WebSocket...');
    
    ws = new WebSocket(`ws://localhost:8000/chat/ws?token=${token}`);
    
    ws.onopen = () => {
        console.log('✅ WebSocket connected');
        document.getElementById('connection-status').textContent = 'Connected';
    };
    
    ws.onmessage = (event) => {
        console.log('📥 Received:', event.data);
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
    
    ws.onclose = () => {
        console.log('❌ WebSocket disconnected');
        document.getElementById('connection-status').textContent = 'Disconnected';
        setTimeout(connectWebSocket, 3000);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// =============================================
// MESSAGE HANDLING
// =============================================
function handleMessage(data) {
    console.log('📨 Handling message type:', data.type);
    
    switch(data.type) {
        case 'connected':
            console.log('Connected to chat server');
            break;
            
        case 'private_message':
            handlePrivateMessage(data);
            break;
            
        case 'message_sent':
            handleMessageSent(data);
            break;
            
        case 'user_joined':
            console.log('👤 User joined:', data.username);
            loadUsers();
            break;
            
        case 'user_left':
            console.log('👤 User left:', data.username);
            loadUsers();
            break;
            
        case 'webrtc_signal':
            handleWebRTCSignal(data);
            break;
            
        case 'call_response':
            handleCallResponse(data);
            break;
            
        default:
            console.log('Unknown message type:', data.type);
    }
}

function handlePrivateMessage(data) {
    console.log('💬 Private message from:', data.from_user_id);
    
    if (data.from_user_id === selectedUserId) {
        addMessage('received', data.from_username, data.content, data.timestamp);
    } else {
        showNotification('New message from ' + data.from_username);
    }
}

function handleMessageSent(data) {
    console.log('✅ Message sent confirmation');
    
    if (selectedUserId && data.to_user_id === selectedUserId) {
        addMessage('sent', 'You', data.content, data.timestamp);
    }
}

// =============================================
// WEBRTC SIGNAL HANDLING
// =============================================
async function handleWebRTCSignal(signalData) {
    console.log('📞 WebRTC signal:', signalData.signal.action);
    
    const signal = signalData.signal;
    
    switch(signal.action) {
        case 'offer':
            await handleOffer(signal.sdp, signal.call_id, signalData.caller_id, signal.call_type);
            break;
            
        case 'answer':
            await handleAnswer(signal.sdp);
            break;
            
        case 'ice_candidate':
            await handleIceCandidate(signal.candidate);
            break;
            
        case 'call_ended':
            endCallUI();
            break;
            
        case 'call_accepted':
            console.log('✅ Call accepted by receiver');
            break;
    }
}

function handleCallResponse(data) {
    console.log('📞 Call response:', data.response.action);
    
    if (data.response.action === 'call_rejected') {
        alert('Call was rejected');
        endCallUI();
    } else if (data.response.action === 'call_accepted') {
        console.log('Call accepted');
    }
}

// =============================================
// INCOMING CALL NOTIFICATION
// =============================================
async function handleOffer(offer, callId, callerId, callType) {
    console.log('📞 Incoming call offer from user:', callerId, 'Type:', callType);
    
    // Store call data for when user accepts
    incomingCallData = {
        callId: callId,
        callType: callType,
        callerId: callerId,
        offer: offer
    };
    
    // Show incoming call modal
    showIncomingCallModal(callerId, callType, callId);
}

function showIncomingCallModal(callerId, callType, callId) {
    console.log('🔔 Showing incoming call modal');
    
    // Get caller username (you may need to fetch this)
    const callerName = 'User ' + callerId;
    
    // Update modal content
    document.getElementById('caller-name-display').textContent = callerName;
    document.getElementById('call-type-display').textContent = 
        callType === 'video' ? '📹 Video Call' : '📞 Audio Call';
    
    // Show modal
    const modal = document.getElementById('incoming-call-modal');
    modal.classList.remove('hidden');
    
    // Play ringtone (optional)
    playRingtone();
    
    console.log('✅ Incoming call modal displayed');
}

function playRingtone() {
    // Optional: Add ringtone audio
    // const audio = new Audio('/static/audio/ringtone.mp3');
    // audio.loop = true;
    // audio.play();
    // window.ringtoneAudio = audio;
}

function stopRingtone() {
    // if (window.ringtoneAudio) {
    //     window.ringtoneAudio.pause();
    //     window.ringtoneAudio.currentTime = 0;
    // }
}

// =============================================
// ACCEPT/REJECT CALL
// =============================================
async function acceptCall() {
    console.log('✅ Accepting call...');
    
    if (!incomingCallData) {
        console.error('❌ No incoming call data');
        return;
    }
    
    // Hide modal
    document.getElementById('incoming-call-modal').classList.add('hidden');
    stopRingtone();
    
    try {
        // Get local media
        console.log('🎤 Getting local media...');
        await getLocalMedia(incomingCallData.callType);
        
        // Create peer connection
        console.log('🔗 Creating peer connection...');
        createPeerConnection();
        
        // Set remote description (the offer)
        await peerConnection.setRemoteDescription(
            new RTCSessionDescription(incomingCallData.offer)
        );
        
        // Create answer
        console.log('📦 Creating answer...');
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);
        
        // Send answer to caller
        console.log('📤 Sending answer...');
        ws.send(JSON.stringify({
            type: 'webrtc_answer',
            receiver_id: incomingCallData.callerId,
            sdp: answer,
            call_id: incomingCallData.callId
        }));
        
        // Send accept signal
        ws.send(JSON.stringify({
            type: 'call_accept',
            call_id: incomingCallData.callId,
            receiver_id: incomingCallData.callerId
        }));
        
        // Show active call overlay
        console.log('📞 Showing active call overlay');
        showActiveCallOverlay(incomingCallData.callType, 'User ' + incomingCallData.callerId);
        
        // Clear incoming call data
        incomingCallData = null;
        
    } catch (error) {
        console.error('❌ Error accepting call:', error);
        alert('Could not accept call: ' + error.message);
        endCallUI();
    }
}

function rejectCall() {
    console.log('❌ Rejecting call...');
    
    if (!incomingCallData) {
        return;
    }
    
    // Send reject signal
    ws.send(JSON.stringify({
        type: 'call_reject',
        call_id: incomingCallData.callId,
        receiver_id: incomingCallData.callerId
    }));
    
    // Hide modal
    document.getElementById('incoming-call-modal').classList.add('hidden');
    stopRingtone();
    
    // Clear data
    incomingCallData = null;
    
    console.log('✅ Call rejected');
}

// =============================================
// OUTGOING CALL
// =============================================
async function startCall(callType) {
    console.log('📞 Starting outgoing call...');
    console.log('Type:', callType, 'To:', selectedUserId, selectedUsername);
    
    if (!selectedUserId) {
        alert('Please select a user first');
        return;
    }
    
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('Not connected to chat server');
        return;
    }
    
    try {
        // Get local media
        console.log('🎤 Getting local media...');
        await getLocalMedia(callType);
        
        // Create peer connection
        console.log('🔗 Creating peer connection...');
        createPeerConnection();
        
        // Create offer
        console.log('📦 Creating offer...');
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        
        currentCallId = Date.now();
        
        // Send offer
        console.log('📤 Sending offer...');
        ws.send(JSON.stringify({
            type: 'webrtc_offer',
            receiver_id: selectedUserId,
            sdp: offer,
            call_type: callType,
            call_id: currentCallId
        }));
        
        // Show caller overlay (ringing state)
        console.log('🔔 Showing caller overlay (ringing...)');
        showCallerOverlay(callType, selectedUsername);
        
    } catch (error) {
        console.error('❌ Error starting call:', error);
        alert('Could not access camera/microphone: ' + error.message);
        endCallUI();
    }
}

// =============================================
// CALL OVERLAY DISPLAY
// =============================================
function showCallerOverlay(callType, username) {
    const overlay = document.getElementById('call-overlay');
    overlay.classList.remove('hidden');
    
    document.getElementById('call-with-user').textContent = 
        callType === 'audio' ? '📞 Calling ' + username + '...' : '📹 Calling ' + username + '...';
    document.getElementById('call-status').textContent = 'Ringing...';
    document.getElementById('call-timer').textContent = '';
    
    // Hide video until connected
    document.getElementById('remote-video').style.display = 'none';
    document.getElementById('local-video').style.display = 'none';
    
    isCallActive = true;
}

function showActiveCallOverlay(callType, username) {
    const overlay = document.getElementById('call-overlay');
    overlay.classList.remove('hidden');
    
    document.getElementById('call-with-user').textContent = 
        callType === 'audio' ? '📞 ' + username : '📹 ' + username;
    document.getElementById('call-status').textContent = 'Connected';
    
    // Show video
    document.getElementById('remote-video').style.display = 'block';
    if (callType === 'video') {
        document.getElementById('local-video').style.display = 'block';
    }
    
    startCallTimer();
    isCallActive = true;
}

// =============================================
// CALL TIMER
// =============================================
function startCallTimer() {
    callStartTime = Date.now();
    callTimerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - callStartTime) / 1000);
        const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
        const seconds = (elapsed % 60).toString().padStart(2, '0');
        document.getElementById('call-timer').textContent = `${minutes}:${seconds}`;
    }, 1000);
}

// =============================================
// END CALL
// =============================================
function endCall() {
    console.log('📞 Ending call...');
    
    if (currentCallId && selectedUserId) {
        ws.send(JSON.stringify({
            type: 'call_end',
            call_id: currentCallId,
            receiver_id: selectedUserId
        }));
    }
    
    endCallUI();
}

function endCallUI() {
    console.log('🧹 Cleaning up call...');
    
    // Stop timer
    if (callTimerInterval) {
        clearInterval(callTimerInterval);
        callTimerInterval = null;
    }
    
    // Stop all media tracks
    if (localStream) {
        localStream.getTracks().forEach(track => {
            console.log('Stopping track:', track.kind);
            track.stop();
        });
        localStream = null;
    }
    
    // Close peer connection
    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }
    
    // Clear video sources
    document.getElementById('local-video').srcObject = null;
    document.getElementById('remote-video').srcObject = null;
    
    // Hide overlays
    document.getElementById('call-overlay').classList.add('hidden');
    document.getElementById('incoming-call-modal').classList.add('hidden');
    
    // Reset UI
    document.getElementById('call-with-user').textContent = '';
    document.getElementById('call-status').textContent = '';
    document.getElementById('call-timer').textContent = '';
    
    currentCallId = null;
    isCallActive = false;
    incomingCallData = null;
    
    console.log('✅ Call cleanup complete');
}

// =============================================
// MEDIA CONTROLS
// =============================================
function toggleMute() {
    if (localStream) {
        const audioTrack = localStream.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            const btn = document.getElementById('mute-btn');
            btn.classList.toggle('muted', !audioTrack.enabled);
        }
    }
}

function toggleVideo() {
    if (localStream) {
        const videoTrack = localStream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = !videoTrack.enabled;
            const btn = document.getElementById('video-btn');
            btn.classList.toggle('off', !videoTrack.enabled);
        }
    }
}

// =============================================
// WEBRTC PEER CONNECTION
// =============================================
function createPeerConnection() {
    console.log('🔗 Creating RTCPeerConnection...');
    
    peerConnection = new RTCPeerConnection(rtcConfig);
    
    // Add local tracks
    if (localStream) {
        localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStream);
        });
    }
    
    // Handle remote stream
    peerConnection.ontrack = (event) => {
        console.log('🎥 Remote track received');
        remoteStream = event.streams[0];
        document.getElementById('remote-video').srcObject = remoteStream;
    };
    
    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            console.log('❄️ Sending ICE candidate');
            sendIceCandidate(event.candidate);
        }
    };
    
    peerConnection.onconnectionstatechange = () => {
        console.log('Connection state:', peerConnection.connectionState);
        
        if (peerConnection.connectionState === 'disconnected' || 
            peerConnection.connectionState === 'failed') {
            endCallUI();
        }
    };
}

async function getLocalMedia(callType) {
    console.log('🎤 Getting local media, type:', callType);
    
    const constraints = {
        audio: true,
        video: callType === 'video'
    };
    
    localStream = await navigator.mediaDevices.getUserMedia(constraints);
    
    if (callType === 'video') {
        document.getElementById('local-video').srcObject = localStream;
    }
    
    // Show/hide video button
    document.getElementById('video-btn').style.display = 
        callType === 'video' ? 'flex' : 'none';
    
    return localStream;
}

function sendIceCandidate(candidate) {
    if (ws && selectedUserId) {
        ws.send(JSON.stringify({
            type: 'webrtc_ice_candidate',
            receiver_id: selectedUserId,
            candidate: candidate,
            call_id: currentCallId || (incomingCallData ? incomingCallData.callId : null)
        }));
    }
}

async function handleAnswer(answer) {
    console.log('📦 Received answer');
    
    if (peerConnection) {
        await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
        
        // Update caller overlay to show video
        document.getElementById('call-status').textContent = 'Connected';
        document.getElementById('remote-video').style.display = 'block';
        startCallTimer();
    }
}

async function handleIceCandidate(candidate) {
    if (peerConnection && candidate) {
        try {
            await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
        } catch (error) {
            console.error('Error adding ICE candidate:', error);
        }
    }
}

// =============================================
// CHAT FUNCTIONS
// =============================================
function displayUsers(users) {
    console.log('Displaying users:', users.length);
    
    const userList = document.getElementById('user-list');
    userList.innerHTML = '';
    
    if (users.length === 0) {
        userList.innerHTML = '<p class="no-users">No users found</p>';
        return;
    }
    
    users.forEach(user => {
        const userDiv = document.createElement('div');
        userDiv.className = 'user-item';
        userDiv.innerHTML = `
            <div class="user-info" onclick="selectUser(${user.id}, '${user.username}')">
                <strong>${user.username}</strong>
                <small>${user.email}</small>
            </div>
            <div class="user-actions">
                <button class="call-btn audio-call" 
                        onclick="event.stopPropagation(); selectUser(${user.id}, '${user.username}'); startCall('audio')"
                        title="Audio Call">📞</button>
                <button class="call-btn video-call" 
                        onclick="event.stopPropagation(); selectUser(${user.id}, '${user.username}'); startCall('video')"
                        title="Video Call">📹</button>
            </div>
        `;
        userList.appendChild(userDiv);
    });
}

function selectUser(userId, username) {
    console.log('Selected user:', userId, username);
    
    selectedUserId = userId;
    selectedUsername = username;
    
    document.getElementById('chat-with').textContent = 'Chat with ' + username;
    document.getElementById('message-input').disabled = false;
    document.getElementById('send-btn').disabled = false;
    
    loadChatHistory(userId);
}

async function loadChatHistory(otherUserId) {
    try {
        const response = await fetch('/chat/history/' + otherUserId + '?current_user_id=' + currentUserId);
        const messages = await response.json();
        
        const messagesDiv = document.getElementById('chat-messages');
        messagesDiv.innerHTML = '';
        
        messages.forEach(msg => {
            const type = msg.sender_id === currentUserId ? 'sent' : 'received';
            const from = type === 'sent' ? 'You' : msg.sender_username;
            addMessage(type, from, msg.content, msg.timestamp);
        });
    } catch (error) {
        console.error('Load history failed:', error);
    }
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    
    if (!content || !ws || !selectedUserId) return;
    
    console.log('Sending message to:', selectedUserId, content);
    
    ws.send(JSON.stringify({
        receiver_id: selectedUserId,
        content: content
    }));
    
    input.value = '';
}

function addMessage(type, from, text, timestamp) {
    const messagesDiv = document.getElementById('chat-messages');
    
    if (!messagesDiv) {
        console.error('Messages div not found!');
        return;
    }
    
    const placeholder = messagesDiv.querySelector('.placeholder');
    if (placeholder) placeholder.remove();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ' + type;
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="from">${from}</span>
            <span class="time">${timestamp}</span>
        </div>
        <div class="message-content">${text}</div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function searchUsers() {
    const query = document.getElementById('user-search').value.trim();
    if (!query) return;
    
    try {
        const response = await fetch('/chat/users/search?q=' + query + '&current_user_id=' + currentUserId);
        const users = await response.json();
        displayUsers(users);
    } catch (error) {
        console.error('Search failed:', error);
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/chat/users/search?q=&current_user_id=' + currentUserId);
        const users = await response.json();
        displayUsers(users);
    } catch (error) {
        console.error('Load users failed:', error);
    }
}

function showNotification(text) {
    document.title = '💬 ' + text;
    setTimeout(() => {
        document.title = 'Chat - Real-Time Chat';
    }, 3000);
}

// Enter key to send message
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('message-input');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
});