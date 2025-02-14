<template>
  <div class="w-full h-full">
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" :configurable="configurable" :connectedPeers="connectedPeers"
          v-model:roomConfigs="roomConfigs" :participants="participants" :receivedMessages="receivedMessages"
          :InviteLink="InviteLink" :gameStarted="gameStarted" :inGameOrder="inGameOrder" :currTurn="currTurn"
          :myTurn="myTurn" :peerId="peerId" :inProgress="inProgress" :bookContents="bookContents"
          :storyCards="storyCards" :endingCard="endingCard" :prompt="prompt" :votings="votings" :percentage="percentage"
          :usedCard="usedCard" :isForceStopped="isForceStopped" @on-room-configuration="onRoomConfiguration"
          @broadcast-message="broadcastMessage" @game-start="gameStart" @game-exit="gameStarted = false" @next-turn="nextTurn"
          @card-reroll="cardReroll" @vote-end="voteEnd" />
      </Transition>
    </RouterView>
    <div
      class="overlay absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col justify-center items-center scale-0">
      <img :src="currTurnImage" alt="">
      <div class="rounded-md px-3 py-1 bg-blue-400 text-xl"></div>
    </div>
    <Transition name="fade">
      <div v-if="isLoading" class="absolute z-50 top-0 left-0 rounded-lg w-full h-full bg-[#ffffff30]">
        <img src="@/assets/loading.gif" alt="" class="w-full h-full">
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import Peer from "peerjs";
import { useUserStore } from "@/stores/auth";
import { useGameStore } from "@/stores/game";
import { myTurnImage, currTurnImage, startImage } from "@/assets";
import { createGame, enterGame, deleteGame, endingCardReroll, promptFiltering, createImage, voteResultSend } from "@/apis/game";
import toast from "@/functions/toast";
import testImage from "@/assets/test.png";

const userStore = useUserStore();
const gameStore = useGameStore();
const route = useRoute();
const router = useRouter();
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
  currTurnTime: 20,
  currMode: 1,
});
// 최대 참가자
const maxParticipants = 6;
// 초대 링크
const InviteLink = ref("");
// 게임 시작 여부
const gameStarted = ref(false);
// 게임 정상 종료 : "champ" 비정상 종료 : "fail" 디폴트 : null
const isForceStopped = ref(null);
// 로딩 애니메이션 보이는 여부
const isLoading = ref(false);
// 게임 방 ID
const gameID = ref("");
// 게임 진행 순서 참가자 인덱스 배열
const inGameOrder = ref([]);
// 현재 턴 인덱스
const currTurn = ref(0);
// 누적 턴
const totalTurn = ref(0);
// 나의 턴 순서
const myTurn = ref(null);
const inProgress = ref(false);
// 내가 가지고있는 스토리카드
const storyCards = ref([]);
// 내가 가지고있는 엔딩카드
const endingCard = ref({});
// 턴 오버레이 애니메이션 지연
const overlayTimeout = ref(null);
// 책 리스트
const bookContents = ref([
  { content: "", image: null }
]);
// 내 턴에 작성한 이야기
const prompt = ref("");
// 이번 턴에 사용된 카드
const usedCard = ref({
  id: 0,
  keyword: "",
  isEnding: false
});
// 투표 결과 표시
const votings = ref([]);

// 게임 종료 애니메이션
watch(isForceStopped, (newValue) => {
  if (newValue !== null) {
    setTimeout(() => {
      isForceStopped.value = null;
    }, 6000);
  }
});

// 긴장감 퍼센트
const percentage = computed(() => {
  if (bookContents.value.length == 1 && bookContents.value[0].content == "") {
    return 0
  } else {
    return Math.round((bookContents.value.length / (participants.value.length * 3)) * 100)
  }
});

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
  // ICE 연결 상태 모니터링
  const peerConnection = conn.peerConnection;
  if (peerConnection) {
    peerConnection.oniceconnectionstatechange = () => {
      const state = peerConnection.iceConnectionState;
      console.log(`ICE 연결 상태: ${state}`);
      
      if (state === 'failed' || state === 'disconnected') {
        console.warn(`피어 ${conn.peer}와의 ICE 연결 실패`);
        handleReconnection(conn.peer);
      }
    };
  }

  // 하트비트 시작
  let heartbeatInterval = setInterval(() => {
    console.log(conn);
    if (conn.open) {
      console.log(conn.peer, "하트비트 송신")
      sendMessage("heartbeat", { timestamp: Date.now() }, conn);
    } else {
      clearInterval(heartbeatInterval);
    }
  }, 5000);

  
  if (participants.value.length >= maxParticipants) {
    conn.close();
    return;
  }

  conn.on("data", async (data) => {
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
        let removedOrder = -1;
        let removedIndex = -1;
        inGameOrder.value = inGameOrder.value.filter(
          (order, index) => {
            if (participants.value[order].id === data.id) {
              removedOrder = order;
              removedIndex = index;
            }
            return participants.value[order].id !== data.id;
          }
        );
        // participants 중 id가 data.id와 같은 값 삭제
        participants.value = participants.value.filter(
          (participant) => participant.id !== data.id,
        );

        inGameOrder.value.forEach((order, index) => {
          if (order > removedOrder) inGameOrder.value[index] -= 1;
        });
        participants.value.forEach((p, i) => {
          if (p.id === peerId.value) {
            myTurn.value = inGameOrder.value.indexOf(i);
          }
        });
        const currTurnExited = currTurn.value === removedIndex;
        currTurn.value %= participants.value.length;
        if (currTurnExited && gameStarted.value) {
          inProgress.value = false;
          await showOverlay('whoTurn');
          inProgress.value = true;
        }

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
        // 로딩 애니메이션 활성화
        isLoading.value = true;

        startReceived(data).then(async () => {
          // 내 카드 받기
          const response = await enterGame({
            userId: peerId.value,
            gameId: gameID.value,
          });

          storyCards.value = response.data.data.storyCards;
          endingCard.value = response.data.data.endingCard;

          setTimeout(async () => {
            await router.push("/game/play");
            // 로딩 애니메이션 비활성화
            isLoading.value = false;
            
            showOverlay('start').then(() => {
              setTimeout(() => {
                showOverlay('whoTurn').then(() => {
                  inProgress.value = true;
                });
              }, 1000);
            });
          }, 3000);
        });
        break;

      case "nextTurn":
        if (data.imageDelete === true) {
          if (bookContents.value.length === 1) {
            bookContents.value = [{ content: "", image: null }];
          } else {
            bookContents.value = bookContents.value.slice(0, -1);
          }
        }
        if (data.isTimeout) {
          // 타임아웃 점수 -1
          const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
          currentPlayer.score -= 1;
        }
        inProgress.value = false;
        currTurn.value = data.currTurn;
        await showOverlay('whoTurn');
        inProgress.value = true;
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

      case "sendPrompt":
        usedCard.value = data.usedCard;
        prompt.value = data.prompt;
        inProgress.value = false;
        addBookContent({ content: data.prompt, image: null });
        votings.value = [];
        break;

      case "sendImage":
        const receivedArrayBuffer = data.imageBlob;
        const receivedBlob = new Blob([receivedArrayBuffer]);
        const imageBlob = URL.createObjectURL(receivedBlob);
        bookContents.value[bookContents.value.length - 1].image = imageBlob;
        break;

      case "voteResult":
        votings.value.push({
          sender: data.sender,
          selected: data.selected
        });

        if (votings.value.length == participants.value.length) {
          let upCount = 0;
          let downCount = 0;
          votings.value.forEach((vote) => {
            if (vote.selected == 'up') upCount++;
            else downCount++;
          });

          if (currTurn.value === myTurn.value) {
            let isAccepted;
            if (upCount < downCount) {
              isAccepted = false;
              // 이미지 버리는 api
              // 내 이미지 버리기
              if (bookContents.value.length === 1) {
                bookContents.value = [{ content: "", image: null }];
              } else {
                bookContents.value = bookContents.value.slice(0, -1);
              }
              // 현재 턴 사람 점수 -1
              const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
              currentPlayer.score -= 1;
              // 턴 종료 트리거 송신하기
              currTurn.value = (currTurn.value + 1) % participants.value.length;
              totalTurn.value++;
              connectedPeers.value.forEach((peer) => {
                if (peer.id !== peerId.value && peer.connection.open) {
                  sendMessage(
                    "nextTurn",
                    {
                      currTurn: currTurn.value,
                      imageDelete: true,
                    },
                    peer.connection
                  )
                }
              });
              // inProgress.value = false;
              await showOverlay('whoTurn');
              inProgress.value = true;
            } else {
              isAccepted = true;
              // 투표 가결 시 점수 +2
              const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
              if (usedCard.value.isEnding) {
                currentPlayer.score += 5;
              } else {
                currentPlayer.score += 2;
              }

              // 턴 종료 트리거 송신하기
              currTurn.value = (currTurn.value + 1) % participants.value.length;
              // condition에서 다음 턴 or 게임 종료
              connectedPeers.value.forEach(async (peer) => {
                if (peer.id !== peerId.value && peer.connection.open) {
                  if (usedCard.value.isEnding) {
                    // 게임 종료 송신
                    gameStarted.value = false;
                    sendMessage("gameEnd", {}, peer.connection);
                    // 랭킹 페이지 이동
                    gameEnd(true);
                    // router.push('/game/rank');
                  } else {
                    sendMessage(
                      "nextTurn",
                      {
                        currTurn: currTurn.value,
                        imageDelete: false,
                      },
                      peer.connection
                    )
                    // inProgress.value = false;
                    await showOverlay('whoTurn');
                    inProgress.value = true;
                  }
                }
              });
            }
            // 투표 결과 전송 api
      try {
          const response = await voteResultSend({
            gameId: gameID.value,
            userId: peerId.value,
            isAccepted: isAccepted,
            cardId: usedCard.value.id,
          });
          if (response.status === 200) {
            // 이미지 쓰레기통에 넣기
          }
        } catch (error) {
          if (error.response.status === 409) {
            storyCards.value.forEach((card, index) => {
              if (card.id === usedCard.value.id) {
                storyCards.value.splice(index, 1);
              }
            });
          }
        }
          } else {
            if (upCount < downCount) {
              // 현재 턴 사람 점수 -1
              const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
              currentPlayer.score -= 1;
            } else {
              // 투표 가결 시 점수 +2
              const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
              if (usedCard.value.isEnding) {
                currentPlayer.score += 5;
              } else {
                currentPlayer.score += 2;
              }
            }
          }
        }
        break;

      case "gameEnd":
        gameStarted.value = false;
        gameEnd(true);
        // router.push("/game/rank");
        break;

      case "heartbeat":
        sendMessage("heartbeat_back", { timestamp: data.timestamp }, conn);
        break;

      case "heartbeat_back":
        console.log(conn.peer, "하트비트 응답 받음");
        conn.lastHeartbeat = Date.now();
        break;
    }
  });

  // 연결 종료 처리
  conn.on("close", () => {
    connectedPeers.value = connectedPeers.value.filter(
      (p) => p.id !== conn.peer,
    );
    participants.value = participants.value.filter((p) => p.id !== conn.peer);

    clearInterval(heartbeatInterval);

    
    console.warn(`⚠️ ${conn.peer} 연결 종료됨. 재연결 시도 중...`);
    setTimeout(() => {
      connectToRoom(conn.peer);
    }, 3000);

  });

  connectedPeers.value.push({
    id: conn.peer,
    connection: conn,
  });
};

// 기존 참가자들과 연결
const handleExistingParticipants = (existingParticipants) => { 
  const MAX_RETRIES = 5; // 최대 재시도 횟수
  const RETRY_DELAY = 2000; // 재시도 간격 (ms)

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
  existingParticipants.forEach((participant) => {
    if (
      participant.id !== peerId.value &&
      !connectedPeers.value.some((p) => p.id === participant.id)
    ) {
      // 재시도 횟수를 추적할 객체 생성
      let retries = 0;

      const tryConnecting = () => {
        const conn = peer.value.connect(participant.id);

        conn.on("open", () => {
          setupConnection(conn);
        });

        // 연결이 실패했을 때 재시도
        conn.on("error", (error) => {
          console.error(participant.id, "와 연결 오류:", error);

          if (retries < MAX_RETRIES) {
            retries++; // 재시도 횟수 증가
            console.log(`${participant.id} 연결 재시도 중... (${retries}/${MAX_RETRIES})`);

            // 일정 시간 후 재시도
            setTimeout(() => {
              console.log(`재시도 ${retries}번째: ${participant.id}`);
              tryConnecting(); // 재시도 호출
            }, RETRY_DELAY);
          } else {
            toast.errorToast(`${participant.id}와 연결에 실패했습니다. 최대 재시도 횟수 초과`);
            console.error(`${participant.id}와 연결에 실패했습니다. 최대 재시도 횟수를 초과하였습니다.`);
          }
        });
      };

      // 처음 연결 시도
      tryConnecting();
    }
  });
};

// 방 참가
const connectToRoom = async (roomID) => {
  const bossID = decompressUUID(roomID);
  console.log("connectToRoom", peer.value);
  const conn = peer.value.connect(bossID);

  const MAX_RETRIES = 5; // 최대 재시도 횟수
  const RETRY_DELAY = 2000; // 재시도 간격 (ms) 

  const attemptConnection = () => {
    console.log("연결 시도", conn.peer);
    conn.on("open", () => {
      setupConnection(conn);
      sendMessage(
        "newParticipant",
        {
          data: {
            id: peerId.value,
            name: userStore.userData.userNickname,
            image: userStore.userData.userProfile,
            score: 10
          },
        },
        conn,
      );
    });

    conn.on("data", (data) => {
      console.log("수신데이터", data);
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
        score: 10,
      };

      // 중복 확인 후 추가
      if (!participants.value.some((p) => p.id === newParticipant.id)) {
        participants.value.push(newParticipant);
      }
    });

    // 재시도 횟수를 추적할 객체 생성
    let retries = 0;

    // 연결이 실패했을 때 재시도
    conn.on("error", (error) => {
      console.error("연결 오류:", error);

      if (retries < MAX_RETRIES) {
        console.log(`재시도 중... (${retries + 1}/${MAX_RETRIES})`);
        setTimeout(() => attemptConnection(retries + 1), RETRY_DELAY); // 일정 시간 후 재시도
      } else {
        toast.errorToast("최대 재시도 횟수를 초과했습니다. 연결에 실패했습니다.");
        console.error("최대 재시도 횟수를 초과하여 연결에 실패했습니다.");
        throw error;
      }
    })
  };

  try {
    attemptConnection();
  } catch (error) {
    console.error("연결 오류:", error);
    toast.errorToast("연결 오류가 발생했습니다. 다시 시도해주세요.");
    throw error;
  }
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
      peer.value = new Peer({
        config: {
          iceServers: [
            { urls: "stun:stun.l.google.com:19302" }, // 예제 STUN 서버
            {
              urls: "turn:i12b101.p.ssafy.io:3478",   // 턴서버 제작완료하면 바꿔야함
              username: import.meta.env.VITE_TURN_ID,              // docker 환경변수 참고
              credential: import.meta.env.VITE_TURN_PW          // docker 환경변수 참고
            }
          ]
        }
      });

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

// 피어들 연결상태 3초마다 확인
// const checkPeerConnections = () => {
//   console.log(connectedPeers.value);
//   connectedPeers.value = connectedPeers.value.filter((peer) => {
//     if (!peer.connection.open) {
//       console.warn(`⚠️ 연결 끊김: ${peer.id}. 제거합니다.`);
//       return false; // 연결이 끊어진 피어는 제거
//     }
//     return true;
//   });

//   setTimeout(checkPeerConnections, 3000); // 3초마다 체크
// };


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
        score: 10
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

  // checkPeerConnections();
});

// // 퇴장 관련
// addEventListener("beforeunload", () => {
//   // connectedPeers 중 내가 아닌 peer들에게 연결 종료를 알림
//   connectedPeers.value.forEach((peer) => {
//     sendMessage(
//       "system",
//       { id: peerId.value, nickname: userStore.userData.userNickname },
//       peer.connection,
//     );
//   });
// });

// 퇴장 관련
addEventListener("beforeunload", () => {
  // connectedPeers 중 내가 아닌 peer들에게 연결 종료를 알림
  connectedPeers.value.forEach((peer) => {
    sendMessage(
      "system",
      { id: peerId.value, nickname: userStore.userData.userNickname },
      peer.connection
    );

    // 연결 종료 신호 보내기
    if (peer.connection.open) {
      peer.connection.close();  // 연결 종료
    }
  });

  // 자신도 연결 종료
  if (peer.value) {
    peer.value.destroy();  // 자신의 Peer 객체 종료
  }
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
  // 로딩 애니메이션 활성화
  isLoading.value = true;
  // 게임 방 생성
  try {
    const response = await createGame({
      bossId: peerId.value,
      player: participants.value.map((p) => p.id),
      drawingStyle: roomConfigs.value.currMode,
    })
    gameID.value = response.data.data.gameId;
    storyCards.value = response.data.data.status.storyCards;
    endingCard.value = response.data.data.status.endingCard;
  } catch (error) {
    console.log(error);
    // return;
  }

  gameStarted.value = data.gameStarted;
  inGameOrder.value = data.order;

  
  connectedPeers.value.forEach((peer) => {
    sendMessage(
      "gameStart",
      {
        gameStarted: gameStarted.value,
        order: inGameOrder.value,
        gameId: gameID.value,
      },
      peer.connection,
    );
  });
  participants.value.forEach((p, i) => {
    if (p.id === peerId.value) {
      myTurn.value = inGameOrder.value.indexOf(i);
    }
  });
  setTimeout(async () => {
    await router.push("/game/play");
    // 로딩 애니메이션 비활성화
    isLoading.value = false;
    
    showOverlay('start').then(() => {
      setTimeout(() => {
        showOverlay('whoTurn').then(() => {
          inProgress.value = true;
        });
      }, 1000);
    });
  }, 3000);
};

const startReceived = (data) => {
  return new Promise((resolve) => {
    gameStarted.value = data.gameStarted;
    inGameOrder.value = data.order;
    gameID.value = data.gameId;

    // 내 순서 몇번인지 저장
    participants.value.forEach((p, i) => {
      if (p.id === peerId.value) {
        myTurn.value = inGameOrder.value.indexOf(i);
      }
    });

    resolve();
  });
}

const showOverlay = (message) => {
  return new Promise((resolve) => {
    const overlay = document.querySelector(".overlay");
    if (message === 'start') {
      overlay.firstElementChild.src = startImage;
      overlay.lastElementChild.textContent = "당신의 차례는 " + (myTurn.value + 1) + "번 입니다.";
      overlay.lastElementChild.style.background = "#FF9D00";
    } else {
      if (participants.value[inGameOrder.value[currTurn.value]].id === peerId.value) {
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
    if (overlayTimeout.value) clearTimeout(overlayTimeout.value);
    overlayTimeout.value = setTimeout(() => {
      overlay.classList.add('scale-0');
      resolve();
    }, 2000);
  });
}

// 책 데이터 추가
const addBookContent = (newContent) => {
  if (bookContents.value[0].content === "") {
    bookContents.value[0].content = newContent.content;
  } else {
    bookContents.value.push(newContent);
  }
};


// 다음 순서 넘기기
const nextTurn = async (data) => {
  // 프롬프트 제출인 경우
  if (data?.prompt) {
    const isEnding = data.isEnding ? true : false;
    // 스토리 카드 제출인 경우
    if (!isEnding) {
      try {
        const filteredPrompt = await promptFiltering({
          userId: peerId.value,
          gameId: gameID.value,
          userPrompt: data.prompt,
        })

        usedCard.value.id = filteredPrompt.data.data;
        storyCards.value.forEach((card) => {
          if (card.id == filteredPrompt.data.data) {
            usedCard.value.keyword = card.keyword;
          }
        })
      } catch (error) {
        console.log(error);
        toast.errorToast(error.response.data.message);
        return;
      }
    }
    // 결말 카드 제출인 경우
    else {
      if (percentage.value < 35) {
        toast.errorToast("긴장감이 충분히 오르지 않았습니다!");
        return;
      }
      usedCard.value.keyword = data.prompt;
      usedCard.value.isEnding = isEnding;
    }

    // 연결된 피어들에게 프롬프트 제출
    connectedPeers.value.forEach((peer) => {
      if (peer.id !== peerId.value && peer.connection.open) {
        sendMessage(
          "sendPrompt",
          {
            prompt: data.prompt,
            usedCard: {
              id: usedCard.value.id,
              keyword: usedCard.value.keyword,
              isEnding: isEnding,
            },
          },
          peer.connection
        )
      }
    });

    addBookContent({ content: data.prompt, image: null });

    // 투표 모달 띄우기
    inProgress.value = false;
    prompt.value = data.prompt;
    votings.value = [];
    // 해당 프롬프트로 이미지 생성 요청 (api)
    try {
      const responseImage = await createImage({
        gameId: gameID.value,
        userId: peerId.value,
        userPrompt: data.prompt,
        turn: totalTurn.value,
      });
      // 이미지가 들어왔다고 하면 이미지 사람들에게 전송하고, 책에 넣는 코드
      const imageBlob = URL.createObjectURL(responseImage.data);

      // webRTC의 데이터 채널은 Blob을 지원하지 않으므로 변환
      const arrayBuffer = await responseImage.data.arrayBuffer();
      
      // 사람들에게 이미지 전송
      connectedPeers.value.forEach((peer) => {
        if (peer.id !== peerId.value && peer.connection.open) {
          sendMessage(
            "sendImage",
            { imageBlob: arrayBuffer },
            peer.connection
          )
        }
      });
      
      // 나의 책에 이미지 넣기
      bookContents.value[bookContents.value.length - 1].image = imageBlob;
    } catch (error) {
      console.log(error);
    }
    // const imageBlob = testImage;
  }
  // 프롬프트 입력 시간초과로 턴 넘기는 경우
  else if (currTurn.value === myTurn.value) {
    // 타임아웃 점수 -1
    const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
    currentPlayer.score -= 1;

    // 턴 종료 트리거 송신하기
    currTurn.value = (currTurn.value + 1) % participants.value.length;
    totalTurn.value++;
    connectedPeers.value.forEach((peer) => {
      if (peer.id !== peerId.value && peer.connection.open) {
        sendMessage(
          "nextTurn",
          {
            currTurn: currTurn.value,
            isTimeout: true,
          },
          peer.connection
        )
      }
    });
    inProgress.value = false;
    await showOverlay('whoTurn');
    inProgress.value = true;
  }
};

// 결말카드 리롤 함수
const cardReroll = async () => {
  const response = await endingCardReroll({
    userId: peerId.value,
    gameId: gameID.value,
  });

  endingCard.value.content = response.data.data.content;
};

// 투표 종료
const voteEnd = async (data) => {
  prompt.value = "";
  votings.value.push({
    sender: data.sender,
    selected: data.selected,
  });
  // 이미지 들어올 때까지 대기

  const sendVoteResult = async () => {
  connectedPeers.value.forEach((peer) => {
    if (peer.id !== peerId.value && peer.connection.open) {
      sendMessage(
        "voteResult",
        {
          sender: data.sender,
          selected: data.selected,
        },
        peer.connection
      )
    }
  });

  if (votings.value.length == participants.value.length) {
    let upCount = 0;
    let downCount = 0;
    votings.value.forEach((vote) => {
      if (vote.selected == 'up') upCount++;
      else downCount++;
    });

    if (currTurn.value === myTurn.value) {
      let isAccepted;
      if (upCount < downCount) {
        // 이미지 버리는 api
        isAccepted = false;

        // 내 이미지 버리기
        if (bookContents.value.length === 1) {
          bookContents.value = [{ content: "", image: null }];
        } else {
          bookContents.value = bookContents.value.slice(0, -1);
        }
        // 현재 턴 사람 점수 -1
        const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
        currentPlayer.score -= 1;
        // 턴 종료 트리거 송신하기
        currTurn.value = (currTurn.value + 1) % participants.value.length;
        totalTurn.value++;
        connectedPeers.value.forEach((peer) => {
          if (peer.id !== peerId.value && peer.connection.open) {
            sendMessage(
              "nextTurn",
              {
                currTurn: currTurn.value,
                imageDelete: true,
              },
              peer.connection
            )
          }
        });
        // inProgress.value = false;
        await showOverlay('whoTurn');
        inProgress.value = true;
      }
      else {
        isAccepted = true;

        // 투표 가결 시 점수 +2
        const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
        if (usedCard.value.isEnding) {
          currentPlayer.score += 5;
        } else {
          currentPlayer.score += 2;
        }

        // 턴 종료 트리거 송신하기
        currTurn.value = (currTurn.value + 1) % participants.value.length;
        // condition에서 다음 턴 or 게임 종료
        connectedPeers.value.forEach((peer) => {
          if (peer.id !== peerId.value && peer.connection.open) {
            if (usedCard.value.isEnding) {
              // 게임 종료 송신
              gameStarted.value = false;
              sendMessage("gameEnd",{}, peer.connection);
              // 랭킹 페이지 이동
              gameEnd(true);
              // router.push('/game/rank');
            } else {
              sendMessage(
                "nextTurn",
                {
                  currTurn: currTurn.value,
                  imageDelete: false,
                },
                peer.connection
              )
            }
          }
        });
        // inProgress.value = false;
        await showOverlay('whoTurn');
        inProgress.value = true;
      }
      // 투표 결과 전송 api
      try {
          const response = await voteResultSend({
            gameId: gameID.value,
            userId: peerId.value,
            isAccepted: isAccepted,
            cardId: usedCard.value.id,
          });
          if (response.status === 200) {
            // 이미지 쓰레기통에 넣기
          }
        } catch (error) {
          if (error.response.status === 409) {
            storyCards.value.forEach((card, index) => {
              if (card.id === usedCard.value.id) {
                storyCards.value.splice(index, 1);
              }
            });
          }
        }
    } else {
      if (upCount < downCount) {
        // 현재 턴 사람 점수 -1
        const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
        currentPlayer.score -= 1;
      } else {
        // 투표 가결 시 점수 +2
        const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
        if (usedCard.value.isEnding) {
          currentPlayer.score += 5;
        } else {
          currentPlayer.score += 2;
        }
      }
    }
  }
}
// if (currTurn.value === myTurn.value) {
// const lastContent = bookContents.value[bookContents.value.length - 1];

// watch(
//   () => lastContent.image,
//   (newImage) => {
//     if (newImage !== null) {
//       sendVoteResult();
//     }
//   },
//   { immediate: true }
// );
// } else {
  sendVoteResult();
// }
};

const gameEnd = (status) => {
  // 게임 시작 상태 초기화
  gameStarted.value = false;
  // 메세지 초기화
  // receivedMessages.value = [];
  // 턴 초기화
  currTurn.value = 0;
  totalTurn.value = 0;
  
  // 비정상 종료인 경우 (긴장감 100 초과)
  if (!status) {
    // 책 비우기
    // 방장인 경우 게임실패 송신
    // if (participants.value[0].id == peerId.value) {
    //   // 비정상 종료 api 들어가야함
    // }
    // 전체 실패 쇼 오버레이
    isForceStopped.value = "fail";
  } else {
    // 정상 종료인 경우
    // 우승자 쇼 오버레이
    isForceStopped.value = "champ";
  }
};

// 긴장감이 100 이상 진행 된 경우 전체 탈락
watch(
  () => percentage.value,
  (percent) => {
    if (percent > 100) {
      gameEnd(false);
    }
  }
)
</script>
<style>
/* Enter 애니메이션 (슬라이드 없이 나타남) */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease-in-out;
  /* opacity로 부드럽게 나타남 */
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  /* 컴포넌트가 처음에는 안 보이게 설정 */
}

.overlay {
  transition: all 1s ease-in-out;
}
</style>
