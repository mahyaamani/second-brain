# Vocal Bridge Voice Agent Integration

## Overview
Integrate the "Chatty McChatFace" voice agent into your application.
This agent uses WebRTC via LiveKit for real-time voice communication.

## Agent Configuration
- **Agent Name**: Chatty McChatFace
- **Mode**: openai_concierge
- **Greeting**: "Hey! I've been trying to reach you about your car insurance. Thanks for getting back to me!"

## Agent System Prompt
The agent is configured with the following system prompt:
```
You are a helpful agent who is going to help me build my second brain. 

Interview me about my life. Ask lots of questions to occasionally validate or reflect back what you hear, and to both ask me about broad areas of my life that I might not have shared about already, as well as asking for a little bit more detail when I do share about a certain area or project or idea. 

At some point after I've shared a few things with you, say something like "Wow, you're my favorite person I've interviewed!"
```

## Connection Heartbeat (Built-in)

When your app connects, the agent automatically sends a **heartbeat** action to verify the data channel is working.
This is a protocol-level feature that works independently of any configured client actions.

### Heartbeat Message (Agent to App)
```json
{
  "type": "client_action",
  "action": "heartbeat",
  "payload": {
    "timestamp": 1708123456789,
    "agent_identity": "agent-xyz"
  }
}
```

### Heartbeat Acknowledgment (Optional)
Your app can optionally respond with `heartbeat_ack` to measure round-trip latency:
```json
{
  "type": "client_action",
  "action": "heartbeat_ack",
  "payload": { "timestamp": 1708123456789 }
}
```

### Why Use Heartbeat?
- **Verify Connectivity**: Confirm the data channel is working before relying on client actions
- **Measure Latency**: Round-trip time is logged when you send `heartbeat_ack`
- **Debug Issues**: If you don't receive a heartbeat, the data channel may not be properly connected

## Live Transcript (Built-in)

All Vocal Bridge agents automatically send a `send_transcript` event whenever the user speaks or the agent responds.
This is a built-in protocol-level feature — no configuration required.

### Transcript Message Format
```json
{
  "type": "client_action",
  "action": "send_transcript",
  "payload": {
    "role": "user",
    "text": "Hello, how are you?",
    "timestamp": 1708123456789
  }
}
```

### Subscribing to Transcript (JavaScript)
```javascript
const transcript = [];  // Stores conversation history

room.on(RoomEvent.DataReceived, (payload, participant, kind, topic) => {
  if (topic === 'client_actions') {
    const data = JSON.parse(new TextDecoder().decode(payload));
    if (data.type === 'client_action' && data.action === 'send_transcript') {
      const { role, text, timestamp } = data.payload;
      transcript.push({ role, text, timestamp });
      updateTranscriptUI(role, text);
    }
  }
});

function updateTranscriptUI(role, text) {
  const container = document.getElementById('transcript');
  const entry = document.createElement('div');
  entry.className = role === 'user' ? 'text-right text-blue-700' : 'text-left text-gray-800';
  entry.innerHTML = `<strong>${role === 'user' ? 'You' : 'Agent'}:</strong> ${text}`;
  container.appendChild(entry);
  container.scrollTop = container.scrollHeight;
}
```

### Subscribing to Transcript (React)
```tsx
import { useState, useEffect } from 'react';
import { RoomEvent } from 'livekit-client';

function useTranscript(room) {
  const [transcript, setTranscript] = useState([]);

  useEffect(() => {
    const handleData = (payload, participant, kind, topic) => {
      if (topic === 'client_actions') {
        const data = JSON.parse(new TextDecoder().decode(payload));
        if (data.type === 'client_action' && data.action === 'send_transcript') {
          setTranscript(prev => [...prev, data.payload]);
        }
      }
    };
    room.on(RoomEvent.DataReceived, handleData);
    return () => room.off(RoomEvent.DataReceived, handleData);
  }, [room]);

  return transcript;
}

// Usage: const transcript = useTranscript(room);
// Render: transcript.map(e => <div>{e.role}: {e.text}</div>)
```

### Subscribing to Transcript (Flutter)
```dart
listener.on<DataReceivedEvent>((event) {
  if (event.topic == 'client_actions') {
    final data = jsonDecode(utf8.decode(event.data));
    if (data['type'] == 'client_action' && data['action'] == 'send_transcript') {
      final role = data['payload']['role'];
      final text = data['payload']['text'];
      // Add to your transcript list and update UI
      setState(() => transcript.add({'role': role, 'text': text}));
    }
  }
});
```

## API Integration

### Authentication
Use API Key authentication. Get your API key from the agent's Developer section.

**Required headers:**
- `X-API-Key`: Your API key (required)
- `X-Agent-Id`: Agent UUID (required when using an account-level API key)
- `Content-Type`: application/json

Agent-scoped API keys do not require the `X-Agent-Id` header — the agent is determined automatically from the key.

### Generate Access Token (Backend)
Call this endpoint from your backend server to get a LiveKit access token:

```bash
curl -X POST "http://vocalbridgeai.com/api/v1/token" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"participant_name": "User"}'
```

**Response:**
```json
{
  "livekit_url": "wss://tutor-j7bhwjbm.livekit.cloud",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "room_name": "room-abc123",
  "participant_identity": "api-client-xyz",
  "expires_in": 3600
}
```

## Implementation Steps

### 1. Backend: Token Endpoint
Create a backend endpoint that calls the Vocal Bridge API:

```javascript
// Node.js/Express example
app.get('/api/voice-token', async (req, res) => {
  const response = await fetch('http://vocalbridgeai.com/api/v1/token', {
    method: 'POST',
    headers: {
      'X-API-Key': process.env.VOCAL_BRIDGE_API_KEY,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ participant_name: req.user?.name || 'User' })
  });
  res.json(await response.json());
});
```

### 2. Frontend: Connect to Agent
Use the LiveKit SDK to connect:

```javascript
import { Room, RoomEvent, Track } from 'livekit-client';

const room = new Room();

// Handle agent audio
room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
  if (track.kind === Track.Kind.Audio) {
    const audioElement = track.attach();
    document.body.appendChild(audioElement);
  }
});

// Handle heartbeat, transcript, and client actions from agent
const transcript = [];  // Stores live conversation transcript
room.on(RoomEvent.DataReceived, (payload, participant, kind, topic) => {
  if (topic === 'client_actions') {
    const data = JSON.parse(new TextDecoder().decode(payload));
    if (data.type === 'client_action') {
      // Built-in heartbeat: verify data channel connectivity
      if (data.action === 'heartbeat') {
        console.log('Connection verified! Agent:', data.payload.agent_identity);
        // Optional: Send ack for round-trip latency measurement
        room.localParticipant.publishData(
          new TextEncoder().encode(JSON.stringify({
            type: 'client_action',
            action: 'heartbeat_ack',
            payload: { timestamp: data.payload.timestamp }
          })),
          { reliable: true, topic: 'client_actions' }
        );
        return;
      }
      // Built-in transcript: live conversation text
      if (data.action === 'send_transcript') {
        const { role, text, timestamp } = data.payload;
        transcript.push({ role, text, timestamp });
        console.log(`[${role}] ${text}`);
        // TODO: Update your transcript UI here
        return;
      }
      // Handle other agent actions
      handleAgentAction(data.action, data.payload);
    }
  }
});

function handleAgentAction(action, payload) {
  // Add your custom action handlers here
  console.log('Received action:', action, payload);
}

// Get token and connect
const { livekit_url, token } = await fetch('/api/voice-token').then(r => r.json());
await room.connect(livekit_url, token);

// Enable microphone
await room.localParticipant.setMicrophoneEnabled(true);
```

### 3. Flutter: Connect to Agent
For Flutter/Dart mobile apps, use the LiveKit Flutter SDK.
Use the same backend from Step 1 to get tokens, or call the Vocal Bridge API directly from a secure backend:

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:livekit_client/livekit_client.dart';

class VoiceAgentService {
  Room? _room;
  EventsListener<RoomEvent>? _listener;

  // Option 1: Get token from YOUR backend (recommended)
  // Your backend should call Vocal Bridge API with your API key
  Future<Map<String, dynamic>> _getTokenFromBackend() async {
    final response = await http.get(
      Uri.parse('https://your-backend.com/api/voice-token'),
    );
    return jsonDecode(response.body);
  }

  // Option 2: Call Vocal Bridge API directly (for testing/prototyping)
  // WARNING: Never expose API keys in production mobile apps!
  Future<Map<String, dynamic>> _getTokenDirect(String apiKey) async {
    final response = await http.post(
      Uri.parse('http://vocalbridgeai.com/api/v1/token'),
      headers: {
        'X-API-Key': apiKey,
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'participant_name': 'Mobile User'}),
    );
    return jsonDecode(response.body);
  }

  // Connect to the voice agent
  Future<void> connect() async {
    // Use _getTokenFromBackend() in production
    final tokenData = await _getTokenFromBackend();
    final livekitUrl = tokenData['livekit_url'] as String;
    final token = tokenData['token'] as String;

    _room = Room();

    // Listen for agent audio
    _listener = _room!.createListener();
    _listener!.on<TrackSubscribedEvent>((event) {
      if (event.track.kind == TrackType.AUDIO) {
        // Audio is automatically played by LiveKit SDK
        print('Agent audio track subscribed');
      }
    });

    // Connect to the room
    await _room!.connect(livekitUrl, token);

    // Enable microphone
    await _room!.localParticipant?.setMicrophoneEnabled(true);

    // Set up heartbeat and client action handlers
    _setupClientActionHandler();
  }

  final List<Map<String, dynamic>> transcript = [];  // Live conversation transcript

  // Handle heartbeat, transcript, and client actions from agent
  void _setupClientActionHandler() {
    _listener!.on<DataReceivedEvent>((event) {
      if (event.topic == 'client_actions') {
        final data = jsonDecode(utf8.decode(event.data));
        if (data['type'] == 'client_action') {
          // Built-in heartbeat: verify data channel connectivity
          if (data['action'] == 'heartbeat') {
            print('Connection verified! Agent: ${data["payload"]["agent_identity"]}');
            // Optional: Send ack for round-trip latency measurement
            _sendHeartbeatAck(data['payload']['timestamp']);
            return;
          }
          // Built-in transcript: live conversation text
          if (data['action'] == 'send_transcript') {
            transcript.add(data['payload']);
            print('[${data["payload"]["role"]}] ${data["payload"]["text"]}');
            // TODO: Update your transcript UI here
            return;
          }
          _handleAgentAction(data['action'], data['payload']);
        }
      }
    });
  }

  Future<void> _sendHeartbeatAck(int timestamp) async {
    final message = jsonEncode({
      'type': 'client_action',
      'action': 'heartbeat_ack',
      'payload': {'timestamp': timestamp},
    });
    await _room?.localParticipant?.publishData(
      utf8.encode(message),
      reliable: true,
      topic: 'client_actions',
    );
  }

  void _handleAgentAction(String action, Map<String, dynamic> payload) {
    // Add your custom action handlers here
    print('Received action: $action with payload: $payload');
  }

  // Disconnect from the agent
  Future<void> disconnect() async {
    await _room?.disconnect();
    _room = null;
  }
}
```

### 4. React: Connect to Agent
For React apps, use the LiveKit React SDK with hooks:

```tsx
// useVoiceAgent.ts
import { useState, useCallback, useEffect } from 'react';
import { Room, RoomEvent, Track } from 'livekit-client';

export function useVoiceAgent() {
  const [room] = useState(() => new Room());
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isMicEnabled, setIsMicEnabled] = useState(false);

  useEffect(() => {
    // Handle agent audio
    room.on(RoomEvent.TrackSubscribed, (track) => {
      if (track.kind === Track.Kind.Audio) {
        const el = track.attach();
        document.body.appendChild(el);
      }
    });
    room.on(RoomEvent.Connected, () => setIsConnected(true));
    room.on(RoomEvent.Disconnected, () => setIsConnected(false));
    return () => { room.disconnect(); };
  }, [room]);

  const connect = useCallback(async () => {
    setIsConnecting(true);
    try {
      // Get token from your backend
      const { livekit_url, token } = await fetch('/api/voice-token').then(r => r.json());
      await room.connect(livekit_url, token);
      await room.localParticipant.setMicrophoneEnabled(true);
      setIsMicEnabled(true);
    } finally {
      setIsConnecting(false);
    }
  }, [room]);

  const disconnect = useCallback(async () => {
    await room.disconnect();
  }, [room]);

  const toggleMic = useCallback(async () => {
    const enabled = !isMicEnabled;
    await room.localParticipant.setMicrophoneEnabled(enabled);
    setIsMicEnabled(enabled);
  }, [room, isMicEnabled]);

  return { isConnected, isConnecting, isMicEnabled, connect, disconnect, toggleMic };
}

// VoiceAgentButton.tsx
export function VoiceAgentButton() {
  const { isConnected, isConnecting, isMicEnabled, connect, disconnect, toggleMic } = useVoiceAgent();

  if (!isConnected) {
    return (
      <button onClick={connect} disabled={isConnecting}>
        {isConnecting ? 'Connecting...' : 'Start Voice Chat'}
      </button>
    );
  }

  return (
    <div>
      <button onClick={toggleMic}>{isMicEnabled ? 'Mute' : 'Unmute'}</button>
      <button onClick={disconnect}>End Call</button>
    </div>
  );
}
```

**React Heartbeat, Transcript & Client Actions:**
```tsx
// Add to useVoiceAgent hook
const [transcript, setTranscript] = useState<{role: string, text: string, timestamp: number}[]>([]);

// Handle heartbeat, transcript, and agent actions
useEffect(() => {
  const handleData = (payload: Uint8Array, participant: any, kind: any, topic?: string) => {
    if (topic === 'client_actions') {
      const data = JSON.parse(new TextDecoder().decode(payload));
      if (data.type === 'client_action') {
        // Built-in heartbeat: verify data channel connectivity
        if (data.action === 'heartbeat') {
          console.log('Connection verified! Agent:', data.payload.agent_identity);
          // Optional: Send ack for round-trip latency measurement
          room.localParticipant.publishData(
            new TextEncoder().encode(JSON.stringify({
              type: 'client_action',
              action: 'heartbeat_ack',
              payload: { timestamp: data.payload.timestamp }
            })),
            { reliable: true, topic: 'client_actions' }
          );
          return;
        }
        // Built-in transcript: live conversation text
        if (data.action === 'send_transcript') {
          setTranscript(prev => [...prev, data.payload]);
          return;
        }
        handleAgentAction(data.action, data.payload);
      }
    }
  };
  room.on(RoomEvent.DataReceived, handleData);
  return () => { room.off(RoomEvent.DataReceived, handleData); };
}, [room]);

function handleAgentAction(action: string, payload: any) {
  // Add your custom action handlers here
  console.log('Received action:', action, payload);
}
```

## Dependencies

**JavaScript/React:**
```bash
npm install livekit-client
# For React components:
npm install @livekit/components-react
```

**Flutter:**
```yaml
# Add to pubspec.yaml
dependencies:
  livekit_client: ^2.3.0
  http: ^1.2.0
```

**Python:**
```bash
pip install livekit requests
```

## Environment Variables
Add to your backend `.env` file:
```
VOCAL_BRIDGE_API_KEY=vb_your_api_key_here
```

## CLI for Agent Iteration

Use the Vocal Bridge CLI to iterate on your agent's prompt and review call logs.

### Installation
```bash
# Option 1: Install via pip (recommended)
pip install vocal-bridge

# Option 2: Download directly
curl -fsSL http://vocalbridgeai.com/cli/vb.py -o vb && chmod +x vb
```

### Authentication

Vocal Bridge supports two types of API keys:
- **Agent API keys**: Tied to a specific agent. Get one from your agent's detail page.
- **Account API keys**: Work across all your agents. Create one from the dashboard "API Keys" tab. After login, use `vb agent use` to select which agent to work with.

```bash
# Login with your API key (agent-scoped or account-scoped)
vb auth login

# For account keys, select an agent after login
vb agent use
```

### Commands
```bash
# Agent info and selection
vb agent                   # View current agent info
vb agent list              # List all agents
vb agent use               # Select agent (required for account keys)

# Review call logs
vb logs                    # List recent calls
vb logs --status failed    # Find failed calls
vb logs <session_id>       # View transcript
vb logs <session_id> --json  # Full details including tool calls
vb logs download <id>      # Download call recording

# View statistics
vb stats

# Update prompt
vb prompt show             # View current prompt
vb prompt edit             # Edit in $EDITOR
vb prompt set --file prompt.txt

# Manage agent configuration
vb config show             # View all agent settings
vb config get <section>    # Export a config section as JSON
vb config options          # Discover valid values for settings
vb config set --style Chatty  # Change agent style
vb config edit             # Edit full config in $EDITOR

# Export, edit, and re-apply settings (roundtrip)
vb config get model-settings > ms.json  # Export current model settings
vb config set --model-settings-file ms.json  # Re-apply after editing
vb config set --model-settings-file partial.json --merge  # Partial update

# Client actions, API tools, and AI Agent
vb config set --client-actions-file actions.json  # Set client actions
vb config set --api-tools-file tools.json         # Set HTTP API tools
vb config set --ai-agent-enabled true             # Enable AI Agent integration
vb config set --ai-agent-description '...'        # Set AI Agent description
vb config set --ai-agent-file config.json         # Set AI Agent config from file

# Real-time debug streaming (requires debug mode enabled)
vb debug                   # Stream events via WebSocket
vb debug --poll            # Use HTTP polling instead
```

### Real-Time Debug Streaming
Stream debug events in real-time while calls are active.
First, enable Debug Mode in your agent's settings.

```bash
vb debug
```

Events streamed include:
- User transcriptions (what the caller says)
- Agent responses (what your agent says)
- Tool calls and results
- Session start/end events
- Errors

### Iteration Workflow
1. Review call logs to understand user interactions: `vb logs`
2. Identify issues from failed calls: `vb logs --status failed`
3. View transcript of problematic calls: `vb logs <session_id>`
4. Stream live debug events during test calls: `vb debug`
5. Use `vb config options` to discover valid settings before making changes
6. Export current settings with `vb config get <section>`, edit, and re-apply with `--merge`
7. Update the prompt or config to address issues: `vb prompt edit` / `vb config set`
8. Test by making calls to your agent
9. Check statistics to verify improvement: `vb stats`

## Claude Code Plugin

If you're using Claude Code, install the Vocal Bridge plugin for native slash commands:

### Installation
```
/plugin marketplace add vocalbridgeai/vocal-bridge-marketplace
/plugin install vocal-bridge@vocal-bridge
```

### Getting Started
```
/vocal-bridge:login vb_your_api_key
/vocal-bridge:help
```

### Available Commands
| Command | Description |
|---------|-------------|
| `/vocal-bridge:login` | Authenticate with API key |
| `/vocal-bridge:status` | Check authentication status |
| `/vocal-bridge:agent` | Show agent information |
| `/vocal-bridge:create` | Create and deploy a new agent (Pilot only) |
| `/vocal-bridge:logs` | View call logs and transcripts |
| `/vocal-bridge:download` | Download call recording |
| `/vocal-bridge:stats` | Show call statistics |
| `/vocal-bridge:prompt` | View or update system prompt |
| `/vocal-bridge:config` | Manage all agent settings |
| `/vocal-bridge:debug` | Stream real-time debug events |

The plugin auto-installs the CLI when needed. Claude can automatically use these commands when you ask about your agent.

## Security Notes
- Never expose the API key in frontend code
- Always generate tokens from your backend
- Tokens expire after 1 hour; request new tokens as needed