<template>
  <div class="flex flex-col w-full h-full items-center justify-center p-5 gap-y-5">
    <img :src="Logo" alt="로고" class="w-52">

    <div class="w-full bg-gray-100 p-4 rounded mb-4">
      <p>연결 상태: {{ connectionStatus }}</p>
      <p>내 Peer ID: {{ peerId }}</p>
      <p v-if="!isHost">목표 방장 ID: {{ hostPeerId }}</p>
      <p>연결된 피어 수: {{ connectedPeers.length }}</p>
    </div>
    
    <!-- 참가자 그리드 -->
    <div class="w-full h-full grid grid-cols-3 gap-x-5">
      <div class="col-span-1 grid grid-cols-2 gap-4">
        <!-- 방장 표시 -->
        <div v-if="isHost" class="flex flex-col justify-end items-center">
          <div class="relative rounded-full border border-black w-24 h-24">
            <div class="w-full h-full rounded-full overflow-hidden">
              <img :src="Profile1" alt="방장 프로필" />
            </div>
            <span class="absolute -top-3 -left-3 text-4xl z-10">👑</span>
          </div>
          <div>나 (방장)</div>
        </div>

        <!-- 일반 참가자로 접속한 경우 -->
        <div v-else class="flex flex-col justify-end items-center">
          <div class="relative rounded-full border border-black w-24 h-24">
            <div class="w-full h-full rounded-full overflow-hidden">
              <img :src="Profile1" alt="내 프로필" />
            </div>
          </div>
          <div>나</div>
        </div>

        <!-- 연결된 참가자들 표시 -->
        <div v-for="peer in connectedPeers" :key="peer.id" class="flex flex-col justify-end items-center">
          <div class="relative rounded-full border border-black w-24 h-24">
            <div class="w-full h-full rounded-full overflow-hidden">
              <img :src="getProfileImage(peer.index)" alt="참가자 프로필" />
            </div>
          </div>
          <div>{{ peer.name }}</div>
          <div v-if="peer.message" class="absolute mt-2 bg-white p-2 rounded shadow">
            {{ peer.message }}
          </div>
        </div>

        <!-- 남은 슬롯 표시 -->
        <div v-for="n in remainingSlots" :key="n" class="flex flex-col justify-end items-center">
          <div class="rounded-full border border-black w-24 h-24 bg-gray-200"></div>
          <div class="text-gray-500">대기 중...</div>
        </div>
      </div>

      <!-- 채팅 및 정보 영역 -->
      <div class="col-span-2 flex flex-col gap-4">
        <div v-if="isHost" class="bg-blue-50 p-4 rounded">
          <h2 class="font-bold">초대 링크</h2>
          <div class="flex gap-2 items-center">
            <input readonly :value="roomLink" class="flex-1 p-2 rounded border" />
            <button @click="copyLink" class="bg-blue-500 text-white px-4 py-2 rounded">
              복사
            </button>
          </div>
        </div>

        <!-- 채팅 영역 -->
        <div class="flex-1 flex flex-col gap-2">
          <div class="flex-1 bg-gray-50 p-4 rounded overflow-y-auto">
            <div v-for="(msg, idx) in chatMessages" :key="idx" class="mb-2">
              <strong>{{ msg.sender }}:</strong> {{ msg.content }}
            </div>
          </div>
          
          <div class="flex gap-2">
            <input 
              v-model="messageInput"
              @keyup.enter="sendMessage"
              placeholder="메시지를 입력하세요"
              class="flex-1 p-2 rounded border"
            />
            <button 
              @click="sendMessage"
              class="bg-blue-500 text-white px-4 py-2 rounded"
            >
              전송
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import Peer from 'peerjs';
import { Logo, Profile1, Profile2, Profile3, Profile4, Profile5, Profile6 } from '@/assets';

// 상태 관리
const route = useRoute();
const peer = ref(null);
const peerId = ref('');
const hostPeerId = ref('');
const connectedPeers = ref([]);
const chatMessages = ref([]);
const messageInput = ref('');
const roomLink = ref('');
const connectionStatus = ref('초기화 중...');
const retryCount = ref(0);
const MAX_RETRIES = 5;

// 계산된 속성
const isHost = computed(() => !route.query.roomID);

// Peer 초기화
function initializePeer() {
  connectionStatus.value = 'Peer 초기화 중...';
  console.log('Peer 초기화 시작');

  peer.value = new Peer({
    debug: 3,
    config: {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        { urls: 'stun:stun2.l.google.com:19302' },
        { urls: 'stun:stun3.l.google.com:19302' },
        { urls: 'stun:stun4.l.google.com:19302' }
      ]
    }
  });

  peer.value.on('open', (id) => {
    console.log('Peer 열림, ID:', id);
    peerId.value = id;
    connectionStatus.value = 'Peer 준비됨';

    if (isHost.value) {
      const compressed = compressUUID(id);
      roomLink.value = `${window.location.origin}/webRTC?roomID=${compressed}`;
      console.log('방 링크 생성됨:', roomLink.value);
    }
  });

  peer.value.on('error', (error) => {
    console.error('Peer 에러:', error.type, error);
    connectionStatus.value = `에러 발생: ${error.type}`;
    
    if (error.type === 'peer-unavailable' && retryCount.value < MAX_RETRIES) {
      retryConnection();
    }
  });

  peer.value.on('connection', handleIncomingConnection);
}

// 들어오는 연결 처리
function handleIncomingConnection(conn) {
  console.log('들어오는 연결:', conn.peer);
  connectionStatus.value = '연결 요청 받음';

  setupConnection(conn);
}

// 나가는 연결 처리
function connectToHost(hostId) {
  if (!peer.value || !peer.value.id) {
    console.log('Peer 아직 준비 안됨, 재시도 예약');
    setTimeout(() => connectToHost(hostId), 1000);
    return;
  }

  console.log('방장에게 연결 시도:', hostId);
  connectionStatus.value = '방장에게 연결 시도 중...';

  const conn = peer.value.connect(hostId, {
    reliable: true
  });

  setupConnection(conn);
}

// 연결 설정
function setupConnection(conn) {
  conn.on('open', () => {
    console.log('연결 열림:', conn.peer);
    connectionStatus.value = '연결됨';
    
    // 이미 연결된 피어인지 확인
    if (!connectedPeers.value.some(p => p.id === conn.peer)) {
      connectedPeers.value.push({
        id: conn.peer,
        name: `참가자 ${connectedPeers.value.length + 1}`,
        connection: conn
      });
    }
  });

  conn.on('data', (data) => {
    console.log('데이터 받음:', conn.peer, data);
    chatMessages.value.push({
      sender: connectedPeers.value.find(p => p.id === conn.peer)?.name || '알 수 없음',
      content: data
    });
  });

  conn.on('close', () => {
    console.log('연결 닫힘:', conn.peer);
    connectedPeers.value = connectedPeers.value.filter(p => p.id !== conn.peer);
    connectionStatus.value = '연결 끊김';
  });

  conn.on('error', (err) => {
    console.error('연결 에러:', err);
    connectionStatus.value = '연결 에러 발생';
  });
}

// 재연결 시도
function retryConnection() {
  retryCount.value++;
  console.log(`재연결 시도 ${retryCount.value}/${MAX_RETRIES}`);
  connectionStatus.value = `재연결 시도 ${retryCount.value}/${MAX_RETRIES}`;

  if (hostPeerId.value) {
    setTimeout(() => {
      connectToHost(hostPeerId.value);
    }, 1000 * retryCount.value); // 점진적으로 딜레이 증가
  }
}

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

// 컴포넌트 마운트
onMounted(() => {
  console.log('컴포넌트 마운트');
  
  // Peer 초기화
  initializePeer();

  // 참가자 모드인 경우
  if (!isHost.value && route.query.roomID) {
    try {
      const decodedHostId = decompressUUID(route.query.roomID);
      hostPeerId.value = decodedHostId;
      console.log('방장 ID 디코딩됨:', decodedHostId);

      // peer 초기화 완료 확인 후 연결
      const initCheck = setInterval(() => {
        if (peer.value && peer.value.id) {
          clearInterval(initCheck);
          connectToHost(decodedHostId);
        }
      }, 500);

      // 30초 후 체크 중단
      setTimeout(() => {
        clearInterval(initCheck);
        if (!connectedPeers.value.length) {
          connectionStatus.value = '연결 실패 - 시간 초과';
        }
      }, 30000);

    } catch (err) {
      console.error('방장 ID 디코딩 실패:', err);
      connectionStatus.value = '방장 ID 디코딩 실패';
    }
  }
});

// peer 객체 정리
onBeforeUnmount(() => {
  if (peer.value) {
    peer.value.destroy();
  }
});
</script>