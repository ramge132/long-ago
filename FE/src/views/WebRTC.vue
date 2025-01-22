<template>
  <div class="flex flex-col w-full h-full items-center justify-center p-5 gap-y-5">
    <img :src="Logo" alt="로고" class=" w-52">
    <div class="w-full h-full grid grid-cols-3 gap-x-5">
      <div class="col-span-1 grid grid-cols-2">
        <!-- 접속한 사용자들 표시 -->
        <div v-for="(user, index) in participants" :key="user.id" class="flex flex-col justify-end items-center">
          <div class="relative rounded-full border border-black w-24 h-24">
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
          class="flex flex-col justify-end items-center">
          <div class="rounded-full border border-black w-24 h-24 bg-gray-500"></div>
          <div>대기 중...</div>
        </div>
      </div>
      <div class="col-span-2">
        <div class="h-full w-full grid grid-rows-4">
          <div class="row-span-3 grid grid-cols-7 grid-rows-7 gap-x-8 gap-y-8 border drop-shadow-md rounded-xl bg-[#ffffffa3]">
            <div class="col-span-4 row-span-2 flex flex-col items-center">
              <label class="self-start">1턴 당 시간(초)</label>
              <div class="w-full flex justify-between">
                <p v-for="n in 6" :key="n">{{ n + 9 }}</p>
              </div>
              <div class="range-container drop-shadow-md">
                <input type="range" :min="minTimeValue" :max="maxTimeValue" :step="stepTimeValue" class="range-slider rounded-xl"
                v-model="selectedTimeValue">
                <div class="ticks flex justify-between items-center p-[2px]">
                  <div v-for="(tick, index) in ticks" :key="index"></div>
                </div>
              </div>
            </div>
            <div class="col-span-3 row-span-2 flex flex-col">
              <label>플레이어 카드 개수</label>
              <div class="flex justify-between items-center w-[50%] self-center">
                <label :for="count + 'cards'" v-for="count in cardCount" :key="card" class="cursor-pointer" :class="count == selectedCountValue ? 'checked' : ''">
                  {{ count }}
                  <input type="radio" class="hidden" :id="count + 'cards'" name="card" :value="count" v-model="selectedCountValue" v-if="count == cardCount[0]" checked>
                  <input type="radio" class="hidden" :id="count + 'cards'" name="card" :value="count" v-model="selectedCountValue" v-if="count != cardCount[0]">
                </label>
              </div>
            </div>
            <div class="col-span-4 row-span-5">
              <label>게임 모드</label>
              <div class="grid grid-cols-2 gap-x-3 h-2/3">
                <div class="border-2 border-black rounded-xl shadow-lg flex flex-col justify-between" v-for="(mode, index) in modes" :key="index">
                  <img :src="mode.icon" alt="모드 아이콘">
                  <p>{{ mode.text }}</p>
                  <input type="radio" name="mode" :value="mode.value" v-model="selectedMode" class="self-center appearance-none border border-black rounded-xl w-5 h-5 checked:bg-white checked:border-[#EB978B] checked:border-4" :checked="index === 0"/>
                </div>
              </div>
            </div>
            <div class="col-span-3 row-span-5">
              <label>작화</label>
              <select class="rounded-lg bg-slate-300 w-[70%] drop-shadow-md appearance-none">
                <option value="korean">한국 전통민화</option>
                <option value="occident">서양 회화</option>
                <option value="japan">일본 우키요에</option>
                <option value="egypt">이집트 벽화</option>
              </select>
            </div>
          </div>
        </div>


      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import Peer from "peerjs";
import { Logo } from "@/assets";
import { Profile1, Profile2, Profile3, Profile4, Profile5, Profile6, Mode1, Mode2 } from "@/assets";

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



// 레인지 슬라이더 커스텀
const minTimeValue = ref(10);
const maxTimeValue = ref(15);
const stepTimeValue = ref(1);
const selectedTimeValue = ref(10);

const ticks = computed(() => {
  const steps = (maxTimeValue.value - minTimeValue.value) / stepTimeValue.value;
  const positions = [];
  for (let i = 0; i <= steps; i++) {
    positions.push(((i / steps) * 100)); // 위치를 백분율로 계산
  }
  return positions;
});


// 플레이어 카드 개수
const cardCount = ref([
  4, 5, 6
]);

const selectedCountValue = ref(4);


// 게임 모드
const modes = ref([
  {
    icon: Mode1,
    text: `문장을 입력하여 그림을 그립니다.
    재밌는 이야기를 적어주세요!`,
    value: 'textToPicture'
  },
  {
    icon: Mode2,
    text: `그림을 그려 이야기를 만듭니다.
    그림 실력을 뽐내보세요!`,
    value: 'pictureToText'
  }
])
const selectedMode = ref("textToPicture");
</script>

<style scoped>
textarea {
  width: 100%;
  height: 50px;
}

.range-container {
  position: relative;
  width: 100%;
  height: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.range-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  background: #ffffff;
  outline: none;
  position: absolute;
}

.range-slider::-webkit-slider-thumb { 
  cursor: pointer;
  position: relative;
  z-index: 30;
}

.ticks {
  width: 100%;
  height: 20px;
  pointer-events: none;
}

.ticks div {  
  height: 8px;
  width: 8px;
  background-color: #6d6d6d;
  border-radius: 50%;
  position: relative;
  z-index: 20;
}

.checked {
  border: 2px solid black;
  border-radius: 30px;
  width: 20px;
  height: 20px;
  text-align: center;
  line-height: 100%;
}
</style>
  