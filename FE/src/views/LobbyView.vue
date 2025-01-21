<template>
  <div class="flex flex-col w-full h-full items-center justify-center p-5 gap-y-5">
      <img :src="Logo" alt="로고" class=" w-52">
      <div class="w-full h-full grid grid-cols-3 gap-x-5">
        <div class="col-span-1 flex flex-col gap-y-1 h-full">
          <!-- 접속한 사용자들 표시 -->
          <div v-for="(user, index) in participants" :key="user.id"
            class="flex items-center gap-x-3 rounded-md p-1 border-2 border-[#00000050]"
          >
            <div
              class="relative flex rounded-full border border-black w-10 h-10"
            >
              <div class="w-full h-full rounded-full overflow-hidden">
                <img :src="user.image" alt="프로필" />
              </div>
              <span v-if="user.isBoss" class="absolute -top-4 -left-4 text-2xl z-10">👑</span>
            </div>
            <div>
              {{ user.name }}
            </div>
          </div>

          <!-- 대기 중 슬롯 표시 -->
          <div v-for="n in maxParticipants - participants.length" :key="'waiting-' + n"
            class="flex items-center gap-x-3 rounded-md p-1 border-2 border-[#00000050]"
          >
            <div class="rounded-full border border-black w-10 h-10 bg-gray-500"></div>
            <div>대기 중...</div>
          </div>
          <div
            class="rounded-md border-2 border-[#00000050] h-36 max-h-36 overflow-y-scroll"
            ref="chatBox"
          >
            <p v-for="(msg, index) in receivedMessages" :key="index"
                class="text-sm"
            >
            <strong>{{ msg.sender }}:</strong> {{ msg.message }}
            </p>
        </div>
        <div class="flex items-center relative h-12 border-2 border-[#00000050] rounded-lg overflow-hidden">
          <input 
            type="text"
            v-model="message" 
            @keyup.enter="broadcastMessage" 
            placeholder="메시지를 입력하세요" 
            class="w-full h-full pl-4 pr-16 text-sm bg-[#ffffff00] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-600"
          />
          <button 
            @click="broadcastMessage"
            class="absolute h-8 w-14 right-2 px-4 py-2 bg-[#E5E091] hover:bg-blue-600 text-sm text-black rounded-lg transition-colors"
          >
            전송
          </button>
        </div>
        </div>
        <div class="col-span-2 border-2 border-[#00000050] rounded-md">
          정표형 가보자잇~~
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from "vue";
import { useRoute } from "vue-router";
import Peer from "peerjs";
import { useUserStore } from "@/stores/auth";
import { Logo } from "@/assets";
import { Profile1, Profile2, Profile3, Profile4, Profile5, Profile6 } from "@/assets";

const userStore = useUserStore();
const route = useRoute();
const peer = ref(null);
const peerId = ref("");
const compressedId = ref("");
const message = ref("");
const connectedPeers = ref([]);
const receivedMessages = ref([]);
const participants = ref([]);
const maxParticipants = 6;
const chatBox = ref(null);


const scrollToBottom = async () => {
await nextTick();
if (chatBox.value) {
  chatBox.value.scrollTop = chatBox.value.scrollHeight;
}
};

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

// 메시지 송신 함수
const sendMessage = (type, payload, conn) => {
if (conn && conn.open) {
  conn.send({ type, ...payload });
}
};

// 브로드캐스트 메시지
const broadcastMessage = () => {
if (message.value.trim()) {
  connectedPeers.value.forEach(peer => {
    sendMessage("message", { 
      message: message.value,
      sender: userStore.userData.userNickname
    }, peer.connection);
  });
  
  // 자신의 메시지도 표시
  receivedMessages.value.push({
    sender: userStore.userData.userNickname,
    message: message.value
  });

  scrollToBottom();

  message.value = "";
}
};

// 새로운 연결 설정
const setupConnection = (conn) => {
if (participants.value.length >= maxParticipants) {
  conn.close();
  return;
}

conn.on("data", (data) => {
  switch (data.type) {
    case "newParticipant":
      // 현재 참가자 목록 전송
      sendMessage("currentParticipants", { 
        participants: participants.value 
      }, conn);
      
      // 새 참가자 정보를 다른 참가자들에게 전파
      broadcastNewParticipant(data.data);
      
      // 참가자 목록에 추가
      if (!participants.value.some(p => p.id === data.data.id)) {
        participants.value.push(data.data);
      }
      break;
      
    case "message":
      console.log(data);
      receivedMessages.value.push({
        sender: data.sender,
        message: data.message
      });
      scrollToBottom();
      break;
  }
});

// 연결 종료 처리
conn.on("close", () => {
  connectedPeers.value = connectedPeers.value.filter(p => p.id !== conn.peer);
  participants.value = participants.value.filter(p => p.id !== conn.peer);
});

connectedPeers.value.push({
  id: conn.peer,
  connection: conn
});
};

// 기존 참가자들과 연결
const handleExistingParticipants = (existingParticipants) => {
console.log(existingParticipants);
// 참가자 목록 업데이트
// participants.value = existingParticipants;
existingParticipants.forEach(newParticipant => {
  // 이미 존재하는 참가자인지 확인
  const isExisting = participants.value.some(
    existing => existing.id === newParticipant.id
  );
  
  // 존재하지 않는 참가자만 추가
  if (!isExisting) {
    participants.value.push(newParticipant);
  } else {
    console.log('이미 존재하는 참가자:', newParticipant);
  }
});

// 각 참가자와 연결
existingParticipants.forEach(async (participant) => {
  if (participant.id !== peerId.value && 
      !connectedPeers.value.some(p => p.id === participant.id)) {
    
    const conn = peer.value.connect(participant.id);
    console.log(conn);

    conn.on("open", () => {
      setupConnection(conn);
    });
  }
});
};

// 방 참가
const connectToRoom = async (roomID) => {
const bossID = decompressUUID(roomID);

const conn = peer.value.connect(bossID);

conn.on("open", () => {
  setupConnection(conn);
  sendMessage("newParticipant", {
    data: {
      id: peerId.value,
      name: userStore.userData.userNickname,
      image: userStore.userData.userProfile,
    }
  }, conn);
});

conn.on("data", (data) => {
  if (data.type === "currentParticipants") {
    console.log("이전 참가자들 정보 도착", data);
    handleExistingParticipants(data.participants);
  } else if (data.type === "newParticipantJoined") {
    console.log("새로운 참가자 정보 도착", data.data);
    participants.value.push(data.data);
  }
});
};

// 새 참가자 정보 브로드캐스트
const broadcastNewParticipant = (newParticipant) => {
connectedPeers.value.forEach(peer => {
  if (peer.id !== newParticipant.id && peer.connection.open) {
    sendMessage("newParticipantJoined", { data: newParticipant }, peer.connection);
  }
});
};

// Peer 초기화
const initializePeer = () => {
return new Promise((resolve, reject) => {
  try {
    peer.value = new Peer();

    peer.value.on("open", (id) => {
      peerId.value = id;
      if (peerId.value === decompressUUID(compressUUID(peerId.value))) {
        compressedId.value = compressUUID(peerId.value);
      }
      resolve();
    });

    peer.value.on("connection", (conn) => {
      setupConnection(conn);
    });

    peer.value.on("error", (err) => {
      console.error("Peer error:", err);
      reject(err);
    });
  } catch (error) {
    reject(error);
  }
});
};

// 컴포넌트 마운트
onMounted(async () => {
try {
  await initializePeer();
  participants.value.push({
    id: peerId.value,
    name: userStore.userData.userNickname,
    image: userStore.userData.userProfile,
  });

  if (route.query.roomID) {
    connectToRoom(route.query.roomID);
  } else {
  }
} catch (error) {
  console.error("Peer initialization failed:", error);
}
});
</script>
  