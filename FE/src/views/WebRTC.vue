<template>
  <div class="flex flex-col w-full h-full items-center justify-center p-5 gap-y-5">
      <img :src="Logo" alt="로고" class=" w-52">
      <div class="w-full h-full grid grid-cols-3 gap-x-5">
        <div class="col-span-1 grid grid-cols-2">
          <!-- 접속한 사용자들 표시 -->
          <div v-for="(user, index) in participants" :key="user.id"
            class="flex flex-col justify-end items-center"
          >
            <div
              class="relative rounded-full border border-black w-24 h-24"
            >
              <div class="w-full h-full rounded-full overflow-hidden">
                <img :src="user.image" alt="프로필" />
              </div>
              <span v-if="user.isBoss" class="absolute -top-3 -left-3 text-4xl z-10">👑</span>
            </div>
            <div>
              {{ user.name }}
            </div>
          </div>

          <!-- 대기 중 슬롯 표시 -->
          <div v-for="n in maxParticipants - participants.length" :key="'waiting-' + n"
            class="flex flex-col justify-end items-center"
          >
            <div class="rounded-full border border-black w-24 h-24 bg-gray-500"></div>
            <div>대기 중...</div>
          </div>
        </div>
        <div class="col-span-2">
          <h1>PeerJS Multi-Connection</h1>
          <p>현재 피어 ID: {{ peerId }}</p>
          <p>base62 압축 ID: {{ peerId }}</p>
      
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
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import Peer from "peerjs";
import { Logo } from "@/assets";
import { Profile1, Profile2, Profile3, Profile4, Profile5, Profile6 } from "@/assets";

const route = useRoute();
const peer = ref(null);
const peerId = ref("");
const newRemoteId = ref("");
const message = ref("");
const connectedPeers = ref([]); // 연결된 피어 목록
const receivedMessages = ref([]); // 받은 메시지 목록


const participants = ref([
    { id: 1, name: 'User A', image: Profile1, isBoss: true },
    { id: 2, name: 'User B', image: Profile2, isBoss: false },
    { id: 3, name: 'User C', image: Profile3, isBoss: false },
]);
const maxParticipants = 6;

// UUID 압축/해제 함수
function compressUUID(uuidStr) {
    const cleanUUID = uuidStr.replace(/-/g, '');
    const bytes = new Uint8Array(16);
    for (let i = 0; i < 16; i++) {
        bytes[i] = parseInt(cleanUUID.substr(i * 2, 2), 16);
    }
    const base64 = btoa(String.fromCharCode.apply(null, bytes));
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

function decompressUUID(compressedStr) {
    let base64 = compressedStr.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4) base64 += '=';
    const binary = atob(base64);
    const hex = Array.from(binary)
        .map(ch => ch.charCodeAt(0).toString(16).padStart(2, '0'))
        .join('');
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

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
  console.log(conn);
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
  console.log(route.query)
  if(route.query.roomID){
    console.log("test");
  }
});
</script>

<style scoped>
textarea {
  width: 100%;
  height: 50px;
}
</style>
  