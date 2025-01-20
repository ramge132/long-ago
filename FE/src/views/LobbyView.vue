<template>
    <div>
        <div>
            <img :src="Logo" alt="로고">
        </div>
        <div>
            <h1>PeerJS Multi-Connection</h1>
            <p>현재 피어 ID: {{ peerId }}</p>
        
            <div>
              <label>새로운 상대방 ID:</label>
              <input v-model="newRemoteId" placeholder="상대방의 Peer ID" />
              <button @click="connectToPeer">연결</button>
            </div>
        
            <div>
              <h3>연결된 피어 목록:</h3>
              <ul>
                <li v-for="peer in connectedPeers" :key="peer.id">
                  {{ peer.id }}
                </li>
              </ul>
            </div>
        
            <div v-if="connectedPeers.length">
              <textarea v-model="message" placeholder="모든 피어에 보낼 메시지를 입력하세요"></textarea>
              <button @click="broadcastMessage">브로드캐스트 메시지</button>
            </div>
        
            <div>
              <h3>받은 메시지:</h3>
              <ul>
                <li v-for="(msg, index) in receivedMessages" :key="index">
                  <strong>{{ msg.peerId }}:</strong> {{ msg.message }}
                </li>
              </ul>
            </div>
        </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from "vue";
  import Peer from "peerjs";
  import { Logo } from "@/assets";
  
  const peer = ref(null);
  const peerId = ref("");
  const newRemoteId = ref("");
  const message = ref("");
  const connectedPeers = ref([]); // 연결된 피어 목록
  const receivedMessages = ref([]); // 받은 메시지 목록
  
  // Peer 초기화
  const initializePeer = () => {
    peer.value = new Peer();
  
    peer.value.on("open", (id) => {
      console.log("My Peer ID:", id);
      peerId.value = id;
    });
  
    peer.value.on("connection", (conn) => {
      setupConnection(conn);
    });
  };
  
  // 연결 설정
  const setupConnection = (conn) => {
    console.log("Connected with:", conn.peer);
  
    // 연결 정보 저장
    connectedPeers.value.push({
      id: conn.peer,
      connection: conn,
    });
  
    // 데이터 수신 이벤트
    conn.on("data", (data) => {
      console.log(`Message received from ${conn.peer}:`, data);
      receivedMessages.value.push({ peerId: conn.peer, message: data });
    });
  
    // 연결 종료 이벤트
    conn.on("close", () => {
      console.log(`Connection with ${conn.peer} closed.`);
      connectedPeers.value = connectedPeers.value.filter((peer) => peer.id !== conn.peer);
    });
  };
  
  // 새 피어 연결
  const connectToPeer = () => {
    if (!newRemoteId.value) {
      console.error("Remote ID is required.");
      return;
    }
  
    // 이미 연결된 피어인지 확인
    if (connectedPeers.value.some((peer) => peer.id === newRemoteId.value)) {
      console.warn("Already connected to this peer.");
      return;
    }
  
    const conn = peer.value.connect(newRemoteId.value);
  
    conn.on("open", () => {
      console.log("Connection opened with:", newRemoteId.value);
      setupConnection(conn);
    });
  
    conn.on("error", (err) => {
      console.error(`Error connecting to ${newRemoteId.value}:`, err);
    });
  
    newRemoteId.value = ""; // 입력란 초기화
  };
  
  // 메시지 브로드캐스트
  const broadcastMessage = () => {
    if (!message.value.trim()) {
      console.error("Message is empty.");
      return;
    }
  
    connectedPeers.value.forEach((peer) => {
      if (peer.connection.open) {
        peer.connection.send(message.value);
      }
    });
  
    console.log("Broadcast message:", message.value);
    message.value = ""; // 메시지 입력란 초기화
  };
  
  // 컴포넌트 마운트 시 Peer 초기화
  onMounted(() => {
    initializePeer();
  });
  </script>
  
  <style scoped>
  textarea {
    width: 100%;
    height: 50px;
  }
  </style>
  