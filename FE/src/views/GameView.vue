<template>
  <div class="w-full h-full">
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component
          :is="Component"
          :configurable="configurable"
          :connectedPeers="connectedPeers"
          v-model:roomConfigs="roomConfigs"
          :participants="participants"
          :receivedMessages="receivedMessages"
          :InviteLink="InviteLink"
          :gameStarted="gameStarted"
          :inGameOrder="inGameOrder"
          :currTurn="currTurn"
          :myTurn="myTurn"
          :peerId="peerId"
          :inProgress="inProgress"
          @on-room-configuration="onRoomConfiguration"
          @broadcast-message="broadcastMessage"
          @game-start="gameStart"
          @game-exit="gameStarted = false"
          @next-turn="nextTurn"
        />
      </Transition>
    </RouterView>
    <div class="overlay absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col justify-center items-center scale-0">
      <img :src="currTurns" alt="">
      <div class="rounded-md px-3 py-1 bg-blue-400 text-xl"></div>
    </div>
    <!-- <div class="absolute top-0 left-0 rounded-lg w-full h-full">
    </div> -->
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import Peer from "peerjs";
import { useUserStore } from "@/stores/auth";
import { useGameStore } from "@/stores/game";
import { myTurnImage , currTurnImage, startImage } from "@/assets";

const userStore = useUserStore();
const gameStore = useGameStore();
const route = useRoute();
// 내 피어 객체
const peer = ref(null);
const peerId = ref("");
// 인코딩 된 방장 고유 ID
const compressedId = ref("");
// 나 포함 연결된 피어 객체들
const connectedPeers = ref([]);
// 채팅 메세지
const receivedMessages = ref([]);
// 현재 연결 된 참가자
const participants = ref([]);
// 게임 설정
const configurable = ref(false);
const roomConfigs = ref({
  currTurnTime: 10,
  currCardCount: 4,
  currMode: "textToPicture",
  currStyle: "korean",
});
// 최대 참가자
const maxParticipants = 6;
// 초대 링크
const InviteLink = ref("");
// 게임 시작 여부
const gameStarted = ref(false);
// 게임 진행 순서 참가자 인덱스 배열
const inGameOrder = ref([]);
// 현재 턴 인덱스
const currTurn = ref(0);
// 나의 턴 순서
const myTurn = ref(null);
const inProgress = ref(false);

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
const broadcastMessage = (data) => {
  connectedPeers.value.forEach((peer) => {
    sendMessage(
      "message",
      {
        message: data.message,
        sender: data.sender,
        form: data.form,
      },
      peer.connection,
    );
  });

  // 자신의 메시지도 표시
  receivedMessages.value.push({
    message: data.message,
    sender: data.sender,
    form: data.form,
  });
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
            roomConfigs: roomConfigs.value,
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
          form: data.form,
        });
        break;

      case "system": 
        // participants 중 id가 data.id와 같은 값 삭제
        participants.value.forEach((p, i) => {
          if(p.id === data.id) {
            inGameOrder.value = inGameOrder.value.filter(
              (order) => order !== i,
            );
          }
        })
        participants.value = participants.value.filter(
          (participant) => participant.id !== data.id,
        );

        const newBossId = compressUUID(participants.value[0].id);

        gameStore.setBossId(newBossId);

        // 초대 링크 초기화
        InviteLink.value =
          import.meta.env.VITE_MAIN_API_SERVER_URL + "?roomID=" + newBossId;
        receivedMessages.value.push({
          sender: "시스템",
          message: `${data.nickname}님이 나가셨습니다.`,
        });

        // 내가 다음 방장인 경우
        if (participants.value[0].id == peerId.value) {
          configurable.value = true;
        }
        break;
      

      case "config":
        roomConfigs.value = {
          currTurnTime: data.turnTime,
          currCardCount: data.cardCount,
          currMode: data.mode,
          currStyle: data.style,
        };
        break;

      // 수정필요 게임 시작 트리거 내용 추가해야 함
      // 카드 요청 보내야함
      // gameID, userID
      case "gameStart":
        startReceived(data).then(async () => {
          await showOverlay('start')
          setTimeout(async () => {
            await showOverlay('whoTurn');
            inProgress.value = true;
          }, 1000);
        });
        break;

      case "newParticipantJoined": 
        const isExisting = participants.value.some(
          (existing) => existing.id === data.data.id,
        );

        // 존재하지 않는 참가자만 추가
        if (!isExisting) {
          participants.value.push(data.data);
        } else {
          console.log("이미 존재하는 참가자:", data.data);
        }
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
  // 참가자 목록 업데이트
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
      handleExistingParticipants(data.participants);
      roomConfigs.value = data.roomConfigs;
    } else if (data.type === "newParticipantJoined") {
      participants.value.push(data.data);
    }

    const newParticipant = {
      id: peerId.value,
      name: userStore.userData.userNickname,
      image: userStore.userData.userProfile,
    };

    // 중복 확인 후 추가
    if (!participants.value.some((p) => p.id === newParticipant.id)) {
      participants.value.push(newParticipant);
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
    if (gameStore.getBossId()) {
      connectToRoom(gameStore.getBossId());
      InviteLink.value = import.meta.env.VITE_MAIN_API_SERVER_URL + "?roomID=" + gameStore.getBossId();
    }
    // 방장인 경우
    else if (
      !gameStore.getBossId() ||
      decompressUUID(gameStore.getBossId()) == peerId.value
    ) {
      participants.value.push({
        id: peerId.value,
        name: userStore.userData.userNickname,
        image: userStore.userData.userProfile,
      });
      configurable.value = true;
      InviteLink.value =
        import.meta.env.VITE_MAIN_API_SERVER_URL +
        "?roomID=" +
        compressUUID(peerId.value);
    }
  } catch (error) {
    console.error("Peer initialization failed:", error);
  }
});

// 퇴장 관련련
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

// 방 설정 관련 부분
const onRoomConfiguration = (data) => {
  roomConfigs.value = data;
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
};

///////////////////////
// 게임 진행 관련 부분 //
// 게임 진행 관련 부분 //
// 게임 진행 관련 부분 //
// 게임 진행 관련 부분 //
///////////////////////
const gameStart = async (data) => {
  gameStarted.value = data.gameStarted;
  inGameOrder.value = data.order;
  connectedPeers.value.forEach((peer) => {
    sendMessage(
      "gameStart",
      {
        gameStarted: gameStarted.value,
        order: inGameOrder.value,
      },
      peer.connection,
    );
  });
  participants.value.forEach((p, i) => {
      if(p.id === peerId.value) {
          myTurn.value = inGameOrder.value.indexOf(i);
      }
  });
  await showOverlay('start');
  setTimeout(async () => {
    await showOverlay('whoTurn');
    inProgress.value = true;
  }, 1000);
};

const startReceived = (data) => {
  return new Promise((resolve) => {
    gameStarted.value = data.gameStarted;
    inGameOrder.value = data.order;

    // 내 순서 몇번인지 저장
    participants.value.forEach((p, i) => {
      if(p.id === peerId.value) {
          myTurn.value = inGameOrder.value.indexOf(i);
      }
    });

    resolve();
  });
}

const showOverlay = (message) => {
  return new Promise((resolve) => {
    const overlay = document.querySelector(".overlay");
    if(message === 'start') {
      overlay.firstElementChild.src = startImage;
      overlay.lastElementChild.textContent = "당신의 차례는 " + (myTurn.value + 1) + "번 입니다."; 
      overlay.lastElementChild.style.background = "#FF9D00";
    } else {
      if(participants.value[inGameOrder.value[currTurn.value]].id === peerId.value) {
        overlay.firstElementChild.src = myTurnImage;
        overlay.lastElementChild.textContent = "멋진 이야기를 적어주세요!";
        overlay.lastElementChild.style.background = "#FF83BB";
      } else {
        overlay.firstElementChild.src = currTurnImage;
        overlay.lastElementChild.textContent = participants.value[inGameOrder.value[currTurn.value]].name + "님의 차례";
        overlay.lastElementChild.style.background = "#00B7FF";
      }
    }
    overlay.classList.remove('scale-0');
    setTimeout(() => {
      overlay.classList.add('scale-0');
      resolve();
    }, 2000);
  });
}

// 다음 순서 넘기기
const nextTurn = async (data) => {
  inProgress.value = false;
  if (data?.prompt) {
    // 프롬프트 제출 api 들어가야 함
    // 시간 멈춰야 함

    // 이미지가 들어왔다고 하면 이미지 사람들에게 전송하고, 책에 넣는 코드
    const imageBlob = 'test';
    
    // 사람들에게 이미지 전송
    connectedPeers.value.forEach((peer) => {
      if (peer.id !== peerId.value && peer.connection.open) {
        sendMessage(
          "sendImage",
          { imageBlob: imageBlob },
          peer.connection
        )
      }
    });

    // 나의 책에 프롬프트와 이미지 넣기
    console.log(data);
  }
  currTurn.value = (currTurn.value + 1) % participants.value.length;
  await showOverlay('whoTurn');
  inProgress.value = true;
};
</script>
<style>
/* Enter 애니메이션 (슬라이드 없이 나타남) */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease-in-out; /* opacity로 부드럽게 나타남 */
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0; /* 컴포넌트가 처음에는 안 보이게 설정 */
}

.overlay {
  transition: all 1s ease-in-out;
}
</style>
