<template>
  <div
    class="flex flex-col w-full h-full items-center justify-center p-5 gap-y-5"
  >
    <img :src="Logo" alt="로고" class="w-52" />
    <div class="w-full h-full grid grid-cols-3 gap-x-5">
      <div class="col-span-1 flex flex-col gap-y-1 h-full">
        <!-- 접속한 사용자들 표시 -->
        <div
          v-for="user in participants"
          :key="user.id"
          class="flex items-center gap-x-3 rounded-md p-1 border-2 border-[#00000050]"
        >
          <div class="relative flex rounded-full border border-black w-10 h-10">
            <div class="w-full h-full rounded-full overflow-hidden">
              <img :src="user.image" alt="프로필" />
            </div>
            <span
              v-if="user.isBoss"
              class="absolute -top-4 -left-4 text-2xl z-10"
              >👑</span
            >
          </div>
          <div>
            {{ user.name }}
          </div>
        </div>

        <!-- 대기 중 슬롯 표시 -->
        <div
          v-for="n in maxParticipants - participants.length"
          :key="'waiting-' + n"
          class="flex items-center gap-x-3 rounded-md p-1 border-2 border-[#00000050]"
        >
          <div
            class="rounded-full border border-black w-10 h-10 bg-gray-500"
          ></div>
          <div class="flex">
            <div class="animate-bounce" style="animation-delay: 0.1s">대</div>
            <div class="animate-bounce" style="animation-delay: 0.2s">기</div>
            <div class="animate-bounce" style="animation-delay: 0.3s">중</div>
            <div class="animate-bounce" style="animation-delay: 0.4s">.</div>
            <div class="animate-bounce" style="animation-delay: 0.5s">.</div>
            <div class="animate-bounce" style="animation-delay: 0.6s">.</div>
          </div>
        </div>
        <div
          class="rounded-md border-2 border-[#00000050] h-36 max-h-36 overflow-y-scroll"
          ref="chatBox"
        >
          <p
            v-for="(msg, index) in receivedMessages"
            :key="index"
            class="text-sm"
          >
            <strong>{{ msg.sender }}:</strong> {{ msg.message }}
          </p>
        </div>
        <div
          class="flex items-center relative h-12 border-2 border-[#00000050] rounded-lg overflow-hidden"
        >
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
      <div class="col-span-2">
        <!-- 방 설정 메뉴 표시 -->
        <form>
          <div class="h-full w-full grid grid-rows-4">
            <div
              class="row-span-3 grid grid-cols-7 grid-rows-7 gap-x-8 gap-y-8 border drop-shadow-md rounded-xl bg-[#ffffffa3] p-5"
              :class="configurable == false ? 'pointer-events-none' : ''"
            >
              <div class="col-span-4 row-span-2 flex flex-col items-center">
                <label class="self-start">1턴 당 시간(초)</label>
                <div class="w-full flex justify-between">
                  <p v-for="n in 6" :key="n">{{ n + 9 }}</p>
                </div>
                <div class="range-container drop-shadow-md relative w-full h-[20px] flex justify-center items-center">
                  <input
                    type="range"
                    :min="minTimeValue"
                    :max="maxTimeValue"
                    :step="stepTimeValue"
                    class="range-slider rounded-xl appearance-none w-full bg-white outline-none absolute"
                    v-model="roomConfigs.currTurnTime"
                  />
                  <div class="ticks w-full h-[20px] pointer-events-none flex justify-between items-center p-[2px]">
                    <div v-for="(tick, index) in ticks" :key="index" class="h-[8px] w-[8px] bg-[#6d6d6d] rounded-lg relative z-20"></div>
                  </div>
                </div>
              </div>
              <div class="col-span-3 row-span-2 flex flex-col">
                <label>플레이어 카드 개수</label>
                <div
                  class="flex justify-between items-center w-[50%] self-center"
                >
                  <label
                    :for="count + 'cards'"
                    v-for="(count, index) in cardCount"
                    :key="index"
                    class="cursor-pointer"
                    :class="count == roomConfigs.currCardCount ? 'border-2 border-black rounded-xl w-[20px] h-[20px] text-center leading-[100%]' : ''"
                  >
                    {{ count }}
                    <input
                      type="radio"
                      class="hidden"
                      :id="count + 'cards'"
                      name="card"
                      :value="count"
                      v-model="roomConfigs.currCardCount"
                      v-if="count == cardCount[0]"
                      checked
                    />
                    <input
                      type="radio"
                      class="hidden"
                      :id="count + 'cards'"
                      name="card"
                      :value="count"
                      v-model="roomConfigs.currCardCount"
                      v-if="count != cardCount[0]"
                    />
                  </label>
                </div>
              </div>
              <div class="col-span-4 row-span-5">
                <label class="mb-2 block">게임 모드</label>
                <div class="grid grid-cols-2 gap-x-3 h-2/3">
                  <label
                    class="border-2 border-black rounded-xl flex flex-col justify-between p-3"
                    v-for="(mode, index) in modes"
                    :key="index"
                    :for="'mode' + index"
                    :class="
                      roomConfigs.currMode === mode.value
                        ? 'shadow-lg scale-105'
                        : ''
                    "
                  >
                    <img :src="mode.icon" alt="모드 아이콘" />
                    <p class="text-xs" v-html="mode.text"></p>
                    <input
                      type="radio"
                      :id="'mode' + index"
                      name="mode"
                      :value="mode.value"
                      v-model="roomConfigs.currMode"
                      class="self-center appearance-none border border-black rounded-xl w-5 h-5 checked:bg-white checked:border-[#EB978B] checked:border-4"
                      :checked="index === 0"
                    />
                  </label>
                </div>
              </div>
              <div class="col-span-3 row-span-5">
                <label class="mr-3">작화</label>
                <select
                  class="rounded-lg bg-slate-300 w-[70%] shadow-md pl-3"
                  v-model="roomConfigs.currStyle"
                >
                  <option value="korean">한국 전통민화</option>
                  <option value="occident">서양 회화</option>
                  <option value="japan">일본 우키요에</option>
                  <option value="egypt">이집트 벽화</option>
                </select>
              </div>
            </div>
            <div class="grid grid-cols-2">
              <div
                class="flex justify-center items-center"
                :class="configurable == false ? 'col-span-2' : ''"
              >
                <button
                  type="button"
                  class="border-2 w-[50%] h-[30%] max-w-[150px] rounded-lg border-black bg-yellow-100 flex items-center hover:shadow-md hover:scale-105"
                  @click="toggleModal"
                >
                  <img
                    :src="InviteIcon"
                    alt="초대 아이콘"
                    class="w-1/3 h-1/2 mr-2"
                  />
                  초대하기
                </button>
              </div>
              <div class="flex justify-center items-center" v-if="configurable">
                <button
                  class="border-2 w-[50%] h-[30%] rounded-lg border-black bg-yellow-100 flex items-center hover:shadow-md hover:scale-105"
                >
                  <img
                    :src="PlayIcon"
                    alt="시작 아이콘"
                    class="w-1/3 h-1/2 mr-2"
                  />
                  <span> 시작하기 </span>
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
      <Transition name="fade">
        <div
          v-if="isOpen"
          @click="toggleModal"
          class="absolute bg-[#00000035] w-full h-full top-0 left-0 flex justify-center items-center"
        >
          <div
            @click.stop
            class="w-96 h-36 text-[#ffffff] font-makgeolli text-2xl rounded-md overflow-hidden flex flex-col"
          >
            <div
              class="flex-1 max-w-full bg-[#00000050] overflow-auto flex items-center justify-center"
            >
              <div class="w-11/12">
                <p>초대링크</p>
                <div class="w-full flex">
                  <input
                    type="text"
                    class="bg-white rounded-xl pl-3 grow text-black mr-3"
                    :value="InviteLink"
                    disabled
                  />
                  <img
                    :src="CopyIcon"
                    alt="복사 아이콘"
                    class="inlin cursor-pointer"
                    @click="copy"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from "vue";
import { useRoute } from "vue-router";
import Peer from "peerjs";
import { useUserStore } from "@/stores/auth";
import { Logo } from "@/assets";
import { Mode1, Mode2, InviteIcon, PlayIcon, CopyIcon } from "@/assets";
import useCilpboard from "vue-clipboard3";
import toast from "@/functions/toast";

const userStore = useUserStore();
const route = useRoute();
const peer = ref(null);
const peerId = ref("");
const compressedId = ref("");
const message = ref("");
const connectedPeers = ref([]);
const receivedMessages = ref([]);
const participants = ref([]);
const roomConfigs = ref({
  currTurnTime: 10,
  currCardCount: 4,
  currMode: "textToPicture",
  currStyle: "korean",
});
const maxParticipants = 6;
const chatBox = ref(null);
const { toClipboard } = useCilpboard();
const configurable = ref(false);

const scrollToBottom = async () => {
  await nextTick();
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight;
  }
};

// UUID 압축/해제 함수
function compressUUID(uuidStr) {
  const cleanUUID = uuidStr.replace(/-/g, "");
  const bytes = new Uint8Array(16);
  for (let i = 0; i < 16; i++) {
    bytes[i] = parseInt(cleanUUID.substr(i * 2, 2), 16);
  }
  const base64 = btoa(String.fromCharCode.apply(null, bytes));
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

function decompressUUID(compressedStr) {
  let base64 = compressedStr.replace(/-/g, "+").replace(/_/g, "/");
  while (base64.length % 4) base64 += "=";
  const binary = atob(base64);
  const hex = Array.from(binary)
    .map((ch) => ch.charCodeAt(0).toString(16).padStart(2, "0"))
    .join("");
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
    connectedPeers.value.forEach((peer) => {
      sendMessage(
        "message",
        {
          message: message.value,
          sender: userStore.userData.userNickname,
        },
        peer.connection,
      );
    });

    // 자신의 메시지도 표시
    receivedMessages.value.push({
      sender: userStore.userData.userNickname,
      message: message.value,
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
        sendMessage(
          "currentParticipants",
          {
            participants: participants.value,
          },
          conn,
        );

        // 새 참가자 정보를 다른 참가자들에게 전파
        broadcastNewParticipant(data.data);

        // 참가자 목록에 추가
        if (!participants.value.some((p) => p.id === data.data.id)) {
          participants.value.push(data.data);
        }
        break;

      case "message":
        receivedMessages.value.push({
          sender: data.sender,
          message: data.message,
        });
        scrollToBottom();
        break;

      case "system":
        // participants 중 id가 data.id와 같은 값 삭제
        participants.value = participants.value.filter(
          (participant) => participant.id !== data.id,
        );
        receivedMessages.value.push({
          sender: "시스템",
          message: `${data.nickname}님이 나가셨습니다.`,
        });
        scrollToBottom();
        break;

      case "config":
        roomConfigs.value = {
          currTurnTime: data.turnTime,
          currCardCount: data.cardCount,
          currMode: data.mode,
          currStyle: data.style,
        };
        break;
    }
  });

  // 연결 종료 처리
  conn.on("close", () => {
    connectedPeers.value = connectedPeers.value.filter(
      (p) => p.id !== conn.peer,
    );
    participants.value = participants.value.filter((p) => p.id !== conn.peer);
  });

  connectedPeers.value.push({
    id: conn.peer,
    connection: conn,
  });
};

// 기존 참가자들과 연결
const handleExistingParticipants = (existingParticipants) => {
  // console.log(existingParticipants);
  // 참가자 목록 업데이트
  // participants.value = existingParticipants;
  existingParticipants.forEach((newParticipant) => {
    // 이미 존재하는 참가자인지 확인
    const isExisting = participants.value.some(
      (existing) => existing.id === newParticipant.id,
    );

    // 존재하지 않는 참가자만 추가
    if (!isExisting) {
      participants.value.push(newParticipant);
    } else {
      console.log("이미 존재하는 참가자:", newParticipant);
    }
  });

  // 각 참가자와 연결
  existingParticipants.forEach(async (participant) => {
    if (
      participant.id !== peerId.value &&
      !connectedPeers.value.some((p) => p.id === participant.id)
    ) {
      const conn = peer.value.connect(participant.id);

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
    sendMessage(
      "newParticipant",
      {
        data: {
          id: peerId.value,
          name: userStore.userData.userNickname,
          image: userStore.userData.userProfile,
        },
      },
      conn,
    );
  });

  conn.on("data", (data) => {
    if (data.type === "currentParticipants") {
      // console.log("이전 참가자들 정보 도착", data);
      handleExistingParticipants(data.participants);
    } else if (data.type === "newParticipantJoined") {
      // console.log("새로운 참가자 정보 도착", data.data);
      participants.value.push(data.data);
    }
  });
};

// 새 참가자 정보 브로드캐스트
const broadcastNewParticipant = (newParticipant) => {
  connectedPeers.value.forEach((peer) => {
    if (peer.id !== newParticipant.id && peer.connection.open) {
      sendMessage(
        "newParticipantJoined",
        { data: newParticipant },
        peer.connection,
      );
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

    // 일반 참여자인 경우
    if (route.query.roomID) {
      participants.value.push({
        id: peerId.value,
        name: userStore.userData.userNickname,
        image: userStore.userData.userProfile,
        isBoss: false,
      });
      connectToRoom(route.query.roomID);
      InviteLink.value = "http://localhost:5173/?roomID=" + route.query.roomID;
    }
    // 방장인 경우
    else {
      participants.value.push({
        id: peerId.value,
        name: userStore.userData.userNickname,
        image: userStore.userData.userProfile,
        isBoss: true,
      });
      configurable.value = true;
      console.log(
        "http://localhost:5173/?roomID=" + compressUUID(peerId.value),
      );
      InviteLink.value =
        "http://localhost:5173/?roomID=" + compressUUID(peerId.value);
    }
  } catch (error) {
    console.error("Peer initialization failed:", error);
  }
});

addEventListener("beforeunload", () => {
  // connectedPeers 중 내가 아닌 peer들에게 연결 종료를 알림
  connectedPeers.value.forEach((peer) => {
    sendMessage(
      "system",
      { id: peerId.value, nickname: userStore.userData.userNickname },
      peer.connection,
    );
  });
});

// 레인지 슬라이더 커스텀
const minTimeValue = ref(10);
const maxTimeValue = ref(15);
const stepTimeValue = ref(1);

const ticks = computed(() => {
  const steps = (maxTimeValue.value - minTimeValue.value) / stepTimeValue.value;
  const positions = [];
  for (let i = 0; i <= steps; i++) {
    positions.push((i / steps) * 100); // 위치를 백분율로 계산
  }
  return positions;
});

// 플레이어 카드 개수
const cardCount = ref([4, 5, 6]);

// 게임 모드
const modes = ref([
  {
    icon: Mode1,
    text: `문장을 입력하여 그림을 그립니다.
    <br>재밌는 이야기를 적어주세요!`,
    value: "textToPicture",
  },
  {
    icon: Mode2,
    text: `그림을 그려 이야기를 만듭니다.
    <br>그림 실력을 뽐내보세요!`,
    value: "pictureToText",
  },
]);

// 초대 링크 표시
const isOpen = ref(false);
const toggleModal = () => {
  isOpen.value = !isOpen.value;
};
const InviteLink = ref("");

// 초대링크 클립보드 복사
const copy = async () => {
  try {
    await toClipboard(InviteLink.value);
    console.log("Copied to clipboard");
    toast.successToast("클립보드에 복사되었습니다.");
  } catch (error) {
    console.error(error);
  }
};

watch(
  () => roomConfigs.value,
  () => {
    if (configurable.value) {
      connectedPeers.value.forEach((peer) => {
        sendMessage(
          "config",
          {
            turnTime: roomConfigs.value.currTurnTime,
            cardCount: roomConfigs.value.currCardCount,
            mode: roomConfigs.value.currMode,
            style: roomConfigs.value.currStyle,
          },
          peer.connection,
        );
      });
    }
  },
  { deep: true },
);
</script>
