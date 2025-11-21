import React, { useState, useEffect} from "react";
import {
  Room,
  RoomEvent,
  createLocalAudioTrack,
} from "livekit-client";

export default function Assistant() {
  const [room, setRoom] = useState(null);
  const [connected, setConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  // const audioRef = useRef(null);

  const FLASK_SERVER_URL = "http://localhost:5000";

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  const handleJoinRoom = async () => {
    try {
      setIsLoading(true);
      setError("");
      console.log("🚀 Joining room...");
    function generateRoomName() {
  return 'room-' + Math.random().toString(36).substring(2, 10);
}

      const roomName = generateRoomName();

      // 1️⃣ Get token from Flask backend
      const tokenUrl = `${FLASK_SERVER_URL}/getToken?identity=frontend-user-${Date.now()}&room=${encodeURIComponent(roomName)}`;
      console.log("Fetching token from:", tokenUrl);

      const resp = await fetch(tokenUrl);
      if (!resp.ok) {
        throw new Error(`Server error: ${resp.status} ${resp.statusText}`);
      }

      const { url, token } = await resp.json();
      if (!token || !url) {
        throw new Error("Invalid token response from backend");
      }

      console.log("✅ Token received, LiveKit URL:", url);

      // 2️⃣ Create Room
      const lkRoom = new Room({
        audioCaptureDefaults: {
          autoGainControl: true,
          echoCancellation: true,
          noiseSuppression: true,
        },
        adaptiveStream: true,
        dynacast: true,
      });

      // 3️⃣ Event listeners
      lkRoom.on(RoomEvent.Connected, () => {
        console.log("✅ Connected to LiveKit room");
        setConnected(true);
      });

      lkRoom.on(RoomEvent.Disconnected, () => {
        console.log("❌ Disconnected from room");
        setConnected(false);
      });

      lkRoom.on(RoomEvent.ParticipantConnected, (p) => {
        console.log("👤 Participant connected:", p.identity);
      });

      lkRoom.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        console.log("🔊 Subscribed to track from:", participant.identity);
        if (track.kind === "audio") {
          const audioEl = track.attach();
          audioEl.autoplay = true;
          audioEl.playsInline = true;
          document.body.appendChild(audioEl);
        }
      });

      // 4️⃣ Connect
      console.log("Connecting to LiveKit...");
      await lkRoom.connect(url, token);
      setRoom(lkRoom);
      console.log("✅ WebSocket connected successfully");

      // 5️⃣ Publish mic
      console.log("Requesting microphone access...");
      const micTrack = await createLocalAudioTrack({
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      });
      console.log("✅ Microphone access granted");

      await lkRoom.localParticipant.publishTrack(micTrack);
      console.log("✅ Microphone track published to room");
    } catch (err) {
      console.error("❌ Connection failed:", err);
      setError(`Connection failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisconnect = async () => {
    if (room) {
      await room.disconnect();
      setRoom(null);
      setConnected(false);
      console.log("✅ Disconnected from room");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 text-white font-sans p-4">
      <div className="bg-white/10 backdrop-blur-lg p-6 rounded-2xl shadow-2xl w-full max-w-lg">
        <h1 className="text-3xl font-bold text-center mb-4">
          🎤 AI Voice Assistant
        </h1>

        {/* Status */}
        <div className="text-center mb-4 p-3 rounded-lg bg-black/20">
          <p
            className={`text-sm ${
              connected ? "text-green-300" : "text-red-300"
            }`}
          >
            {connected ? "✅ Connected - Mic Active" : "❌ Not connected"}
          </p>
          {error && (
            <p className="text-red-300 text-xs mt-2 bg-red-900/30 p-2 rounded">
              {error}
            </p>
          )}
        </div>

        {/* Buttons */}
        <div className="text-center space-y-3">
          {!connected ? (
            <button
              onClick={handleJoinRoom}
              disabled={isLoading}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-bold py-3 px-6 rounded-lg w-full transition-colors"
            >
              {isLoading ? "Connecting..." : "Join Room & Start Mic"}
            </button>
          ) : (
            <button
              onClick={handleDisconnect}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-lg w-full transition-colors"
            >
              Disconnect
            </button>
          )}
        </div>

        {/* Mic indicator */}
        <div className="flex justify-center mt-6">
          <div
            className={`w-20 h-20 rounded-full flex items-center justify-center shadow-lg ${
              connected
                ? "bg-green-500 shadow-green-400 animate-pulse"
                : "bg-gray-500 shadow-gray-400"
            } transition-all duration-300`}
          >
            <span className="text-2xl">🎙️</span>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-6 text-center text-sm opacity-80 space-y-1">
          <p>• Click "Join Room" to start</p>
          <p>• Allow microphone permissions when prompted</p>
          <p>• Speak clearly to interact with AI</p>
          <p>• Watch console logs for debug info</p>
        </div>
      </div>
    </div>
  );
}
