<template>
  <div class="w-full h-full rounded-lg">
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component :is="Component" :configurable="configurable" :connectedPeers="connectedPeers"
          v-model:roomConfigs="roomConfigs" :participants="participants" :receivedMessages="receivedMessages"
          :InviteLink="InviteLink" :gameStarted="gameStarted" :inGameOrder="inGameOrder" :currTurn="currTurn" :ISBN="ISBN"
          :myTurn="myTurn" :peerId="peerId" :inProgress="inProgress" :bookContents="bookContents" :isElected="isElected"
          :storyCards="storyCards" :endingCard="endingCard" :prompt="prompt" :votings="votings" :percentage="percentage"
          :usedCard="usedCard" :isForceStopped="isForceStopped" :isVoted="isVoted" :bookCover="bookCover" :isPreview="isPreview" @on-room-configuration="onRoomConfiguration"
          @broadcast-message="broadcastMessage" @game-start="gameStart" @game-exit="gameStarted = false" @next-turn="nextTurn"
          @card-reroll="cardReroll" @vote-end="voteEnd" @go-lobby="goLobby" @winner-shown="onWinnerShown" @narration-complete="onNarrationComplete" @start-narration="onStartNarration" />
      </Transition>
    </RouterView>
    <div
      class="overlay absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col justify-center items-center scale-0">
      <img :src="currTurnImage" alt="">
      <div class="rounded-md px-3 py-1 bg-blue-400 text-xl"></div>
    </div>
    
    <!-- 부적절한 콘텐츠 경고 모달 -->
    <div
      v-if="showWarningModal"
      class="warning-modal fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50"
      @click="hideWarningModal">
      <div 
        class="warning-content bg-white rounded-lg p-8 max-w-md mx-4 text-center transform transition-all duration-300"
        @click.stop>
        <img :src="WarningIcon" alt="경고" class="w-20 h-20 mx-auto mb-4">
        <h3 class="text-xl font-bold text-red-600 mb-2">부적절한 콘텐츠 감지</h3>
        <p class="text-gray-700 mb-4">{{ warningModalMessage }}</p>
        <button 
          @click="hideWarningModal"
          class="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg font-medium transition-colors">
          확인
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { createGame, createImage, deleteGame, endingCardReroll, enterGame, promptFiltering, testGame, voteResultSend } from "@/apis/game";
import { currTurnImage, myTurnImage, startImage, MessageMusic, WarningIcon } from "@/assets";
import toast from "@/functions/toast";
import { useUserStore } from "@/stores/auth";
import { useGameStore } from "@/stores/game";
import { useAudioStore } from "@/stores/audio";
import Peer from "peerjs";
import { computed, nextTick, onMounted, ref, watch, onBeforeUnmount } from "vue";
import { useRoute, useRouter } from "vue-router";

const audioStore = useAudioStore();

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
// const participants = ref([{name: "홍석진_12345", image: "/src/assets/images/profiles/default.jpg", score: 15}, {name: "홍석진_67891", image: "/src/assets/images/profiles/default.jpg", score: 15}]);
const participants = ref([]);
// 게임 설정
const configurable = ref(false);
const roomConfigs = ref({
  currTurnTime: 30,
  currMode: 0,
});
// 최대 참가자
const maxParticipants = 6;
// 초대 링크
const InviteLink = ref("");
// 게임 시작 여부
const gameStarted = ref(false);
// 게임 정상 종료 : "champ" 비정상 종료 : "fail" 디폴트 : null
const isForceStopped = ref(null);
// 부적절한 콘텐츠 경고 모달 관련
const showWarningModal = ref(false);
const warningModalMessage = ref("");
// 투표 타이머 관리
let voteTimer = null;
// 게임 방 ID
const gameID = ref("");
// 게임 진행 순서 참가자 인덱스 배열
const inGameOrder = ref([]);
// 현재 턴 인덱스
const currTurn = ref(0);
// 누적 턴
const totalTurn = ref(1);
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
// 프롬프트 선출 여부
const isElected = ref(false);
// 책 표지, 제목
const bookCover = ref({
  title: "", imageUrl: ""
});
const ISBN = ref("");
// 시연 모드 on/off
const isPreview = ref(false);

watch(isElected, (newValue) => {
  if (newValue === true) {
    setTimeout(() => {
      isElected.value = false;
    }, 1000);
  }
})

// 로딩 표시
const emit = defineEmits(["startLoading"]);

// 투표 결과를 보냈는 지 여부
const isVoted = ref(false);
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
      
      if (state === 'failed' || state === 'disconnected') {
        handleReconnection(conn.peer);
      }
    };
  }

  // 하트비트 시작
  let heartbeatInterval = setInterval(() => {
    if (conn.open) {
      sendMessage("heartbeat", { timestamp: Date.now() }, conn);
    } else {
      clearInterval(heartbeatInterval);
    }
  }, 5000);

  
  if (participants.value.length > maxParticipants || gameStarted.value) {
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

      case "currentParticipants":
        // 현재 참가자 받기
        handleExistingParticipants(data.participants);
        roomConfigs.value = data.roomConfigs;
        break;

      case "message":
        receivedMessages.value.push({
          sender: data.sender,
          message: data.message,
          form: data.form,
        });
        if (audioStore.audioData) {
          const messageMusic = new Audio(MessageMusic);
          messageMusic.play();
        }
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

      case "gameStart":
        isPreview.value = data.isPreview;
        // 게임 관련 데이터 초기화
        participants.value = data.participants;
        receivedMessages.value = [];
        currTurn.value = 0;
        bookContents.value = [{ content: "", image: null }];
        bookCover.value = {title: "", imageUrl: ""};
        ISBN.value = "";
        votings.value = [];
        myTurn.value = null;
        inProgress.value = false;
        inGameOrder.value = [];
        isForceStopped.value = null;
        usedCard.value = {
          id: 0,
          keyword: "",
          isEnding: false
        };
        
        // 로딩 애니메이션 활성화
        emit("startLoading", {value: true});

        startReceived(data).then(async () => {
          // 내 카드 받기
          const response = await enterGame({
            userId: peerId.value,
            gameId: gameID.value,
          });

          // isPreview.value = response.data.data.isPreview;
          storyCards.value = response.data.data.storyCards;
          endingCard.value = response.data.data.endingCard;

          setTimeout(async () => {
            await router.push("/game/play");
            // 로딩 애니메이션 비활성화
            emit("startLoading", {value: false});
            
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
        if (data.isInappropriate) {
          // 부적절한 콘텐츠로 인한 점수 -1 처리 (다른 플레이어들에게도 동기화)
          const currentPlayer = participants.value[inGameOrder.value[data.currTurn === 0 ? participants.value.length - 1 : data.currTurn - 1]];
          currentPlayer.score -= 1;
          console.log("부적절한 콘텐츠로 인한 점수 감소 처리됨:", currentPlayer.name, currentPlayer.score);
        }
        totalTurn.value = data.totalTurn;
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
        }
        break;

      case "sendPrompt":
        usedCard.value = data.usedCard;
        prompt.value = data.prompt;
        inProgress.value = false;
        addBookContent({ content: data.prompt, image: null });
        votings.value = [];
        
        // 기존 투표 타이머가 있으면 취소
        if (voteTimer) {
          clearTimeout(voteTimer);
        }
        
        // 새로운 투표 타이머 설정
        voteTimer = setTimeout(async () => {
          if(isVoted.value) {
            isVoted.value = false;
          } else {
            await voteEnd({
              sender: userStore.userData.userNickname,
              selected: "up",
            });
            isVoted.value = false;
          }
        }, 10000);  // 투표 시간 10초로 설정
        break;

      case "sendImage":
        const receivedArrayBuffer = data.imageBlob;
        const receivedBlob = new Blob([receivedArrayBuffer]);
        const imageBlob = URL.createObjectURL(receivedBlob);
        bookContents.value[bookContents.value.length - 1].image = imageBlob;
        break;

      case "warningNotification":
        showInappropriateWarningModal(data);
        break;

      case "stopVotingAndShowWarning":
        stopVotingAndShowWarning(data);
        break;

      case "voteResult":
        votings.value = [...votings.value, {sender: data.sender, selected: data.selected}];

        if (votings.value.length == participants.value.length) {
          let upCount = 0;
          let downCount = 0;
          votings.value.forEach((vote) => {
            if (vote.selected == 'up') upCount++;
            else downCount++;
          });

          if (currTurn.value === myTurn.value) {
            let accepted;
            if (upCount < downCount) {
              accepted = false;
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
              connectedPeers.value.forEach((peer) => {
                if (peer.id !== peerId.value && peer.connection.open) {
                  sendMessage(
                    "nextTurn",
                    {
                      currTurn: currTurn.value,
                      imageDelete: true,
                      totalTurn: totalTurn.value,
                    },
                    peer.connection
                  )
                }
              });
              // inProgress.value = false;
              await showOverlay('whoTurn');
              inProgress.value = true;
            } else {
              isElected.value = true;
              accepted = true;
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
              if (usedCard.value.isEnding) {
                await gameEnd(true).then((res) => {
                  connectedPeers.value.forEach(async (p) => {
                    if (p.id !== peerId.value && p.connection.open) {
                      sendMessage("gameEnd",
                        {
                          bookCover: {
                            title: res.data.data.title,
                            imageUrl: res.data.data.bookCover
                          },
                          isbn: res.data.data.bookId,
                        },
                        p.connection
                      );
                    };
                  });
                  
                  // 먼저 승자를 표시
                  isForceStopped.value = "champ";
                  // gameStarted는 승자 표시 후 onWinnerShown에서 처리
                });
              } else {
                connectedPeers.value.forEach(async (p) => {
                  if (p.id !== peerId.value && p.connection.open) {
                    sendMessage(
                      "nextTurn",
                      {
                        currTurn: currTurn.value,
                        imageDelete: false,
                        totalTurn: totalTurn.value,
                      },
                      p.connection
                    )
                  };
                });

                await showOverlay('whoTurn');
                inProgress.value = true;
              };
            }
            //   connectedPeers.value.forEach(async (peer) => {
            //     if (peer.id !== peerId.value && peer.connection.open) {
            //       if (usedCard.value.isEnding) {
            //         // 게임 종료 송신
            //         gameStarted.value = false;
            //         sendMessage("gameEnd",
            //           {
            //             bookCover: bookCover.value,
            //             isbn: ISBN.value,
            //           },
            //           peer.connection
            //         );
            //         // 랭킹 페이지 이동
            //         // router.push('/game/rank');
            //         // 우승자 쇼 오버레이
            //         isForceStopped.value = "champ";
            //       } else {
            //         sendMessage(
            //           "nextTurn",
            //           {
            //             currTurn: currTurn.value,
            //             imageDelete: false,
            //           },
            //           peer.connection
            //         )
            //         // inProgress.value = false;
            //         await showOverlay('whoTurn');
            //         inProgress.value = true;
            //       }
            //     }
            //   });
            // }
            // 투표 결과 전송 api
      try {
          const response = await voteResultSend({
            gameId: gameID.value,
            userId: peerId.value,
            accepted: accepted,
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
              isElected.value = true;
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
        // 즉시 승자 표시 (1초 후)
        setTimeout(() => {
          isForceStopped.value = "champ";
        }, 1000);
        gameEnd(true);
        break;

      case "bookCover":
        bookCover.value = data.bookCover;
        ISBN.value = data.ISBN;
        break;

      case "heartbeat":
        sendMessage("heartbeat_back", { timestamp: data.timestamp }, conn);
        break;

      case "heartbeat_back":
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
const handleExistingParticipants = async (existingParticipants) => {
  const MAX_RETRIES = 5;
  const RETRY_DELAY = 2000;

  // Promise를 반환하는 연결 함수
  const connectToParticipant = (participant) => {
    return new Promise((resolve, reject) => {
      if (connectedPeers.value.some((p) => p.id === participant.id
      &&
      participant.id !== peerId.value)) {
        participants.value.push(participant);
        resolve();
      } else if (
        participant.id !== peerId.value &&
        !connectedPeers.value.some((p) => p.id === participant.id)
      ) {
        let retries = 0;

        const tryConnecting = () => {
          const conn = peer.value.connect(participant.id);

          conn.on("open", () => {
            setupConnection(conn);
            
            const isExisting = participants.value.some(
              (existing) => existing.id === participant.id
            );

            if (!isExisting) {
              participants.value.push(participant);
            }
            resolve();
          });

          conn.on("error", (error) => {
            if (retries < MAX_RETRIES) {
              retries++;
              setTimeout(() => {
                tryConnecting();
              }, RETRY_DELAY);
            } else {
              toast.errorToast(`${participant.id}와 연결에 실패했습니다. 최대 재시도 횟수 초과`);
              reject(new Error(`${participant.id}와 연결 실패`));
            }
          });
        };

        tryConnecting();
      } else {
        resolve();
      }
    });
  };

  try {
    // 모든 참가자 연결이 완료될 때까지 대기
    await Promise.all(
      existingParticipants.map(participant => connectToParticipant(participant))
    );

    // 모든 연결이 완료된 후 나 자신 추가
    const newParticipant = {
      id: peerId.value,
      name: userStore.userData.userNickname,
      image: userStore.userData.userProfile,
      score: 10,
    };
    
    if (!participants.value.some(
              (existing) => existing.id === newParticipant.id
            )) {
      participants.value.push(newParticipant);
    }
  } catch (error) {
    // 참가자 연결 중 오류 발생
  }
};

// 방 참가
const connectToRoom = async (roomID) => {
  const bossID = decompressUUID(roomID);
  const conn = peer.value.connect(bossID);

  const MAX_RETRIES = 5; // 최대 재시도 횟수
  const RETRY_DELAY = 2000; // 재시도 간격 (ms) 

  const attemptConnection = () => {
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

    // conn.on("data", (data) => {
    //   if (data.type != "heartbeat" && data.type != "heartbeat_back") {
    //     console.log("수신데이터", data);
    //   }
    //   if (data.type === "currentParticipants") {
    //     handleExistingParticipants(data.participants);
    //     roomConfigs.value = data.roomConfigs;
    //   } else if (data.type === "newParticipantJoined") {
    //     participants.value.push(data.data);
    //   }

    //   const newParticipant = {
    //     id: peerId.value,
    //     name: userStore.userData.userNickname,
    //     image: userStore.userData.userProfile,
    //     score: 10,
    //   };

    //   // 중복 확인 후 추가
    //   if (!participants.value.some((p) => p.id === newParticipant.id)) {
    //     participants.value.push(newParticipant);
    //   }
    // });

    // 재시도 횟수를 추적할 객체 생성
    let retries = 0;

    // 연결이 실패했을 때 재시도
    conn.on("error", (error) => {
      if (retries < MAX_RETRIES) {
        setTimeout(() => attemptConnection(retries + 1), RETRY_DELAY); // 일정 시간 후 재시도
      } else {
        toast.errorToast("최대 재시도 횟수를 초과했습니다. 연결에 실패했습니다.");
        throw error;
      }
    })
  };

  try {
    attemptConnection();
  } catch (error) {
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
            // { urls: "stun:stun.l.google.com:19302" }, // 예제 STUN 서버
            {
              urls: import.meta.env.VITE_TURN_SERVER_URL,
              username: import.meta.env.VITE_TURN_ID,
              credential: import.meta.env.VITE_TURN_PW,
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

      // 연결이 끊어졌을 때 다시 연결 유지 시도
      peer.value.on("disconnected", () => {
        peer.value.reconnect();
      });

      peer.value.on("error", (err) => {
        reject(err);
      });
    } catch (error) {
      reject(error);
    }
  });
};

// 부적절한 콘텐츠 경고 표시
const showInappropriateWarning = (warningData) => {
  console.log("=== 부적절한 콘텐츠 경고 표시 ===", warningData);
  
  // 경고 토스트 메시지 표시 (모든 플레이어에게 보임)
  const warningMessage = `${warningData.playerName}님의 ${warningData.message}`;
  
  // warning.png와 함께 커스텀 토스트 표시  
  toast.setToast({
    msg: warningMessage,
    type: "error",  // error 타입이 더 눈에 띄고 적절함
    timeout: 6000,  // 6초간 표시하여 확실히 인지하도록
    closeButton: "button",
    position: "top-center",
    icon: true
  });
  
  console.log("경고 알림 표시 완료:", warningMessage);
};

// 부적절한 콘텐츠 경고 모달 표시
const showInappropriateWarningModal = (warningData) => {
  console.log("=== 부적절한 콘텐츠 경고 모달 표시 ===", warningData);
  
  warningModalMessage.value = `${warningData.playerName}님이 ${warningData.message}`;
  showWarningModal.value = true;
  
  // 3초 후 자동으로 모달 닫기
  setTimeout(() => {
    hideWarningModal();
  }, 3000);
  
  console.log("경고 모달 표시 완료:", warningModalMessage.value);
};

// 경고 모달 숨기기
const hideWarningModal = () => {
  showWarningModal.value = false;
  warningModalMessage.value = "";
};

// 투표 중단 및 경고 표시 (모든 플레이어용)
const stopVotingAndShowWarning = async (data) => {
  console.log("=== 투표 중단 및 경고 표시 ===", data);
  
  // 1. 투표 즉시 중단 (InGameView에서 투표 UI 숨김)
  inProgress.value = false;
  isVoted.value = true;  // 투표 UI 즉시 숨김
  prompt.value = "";     // 프롬프트도 초기화하여 완전히 투표 UI 제거
  
  // 투표 타이머 취소
  if (voteTimer) {
    clearTimeout(voteTimer);
    voteTimer = null;
    console.log("투표 타이머 취소됨");
  }
  
  // 투표 관련 상태 초기화
  votings.value = [];
  usedCard.value = {};
  
  console.log("투표 진행 상태 비활성화 및 투표 UI 숨김");
  
  // 2. 점수 동기화 (다른 플레이어들)
  if (data.isInappropriate && !data.skipScoreDeduction) {
    const affectedPlayerIndex = data.currTurn === 0 ? participants.value.length - 1 : data.currTurn - 1;
    const affectedPlayer = participants.value[inGameOrder.value[affectedPlayerIndex]];
    if (affectedPlayer) {
      affectedPlayer.score -= 1;
      console.log("부적절한 콘텐츠로 인한 점수 감소 동기화:", affectedPlayer.name, affectedPlayer.score);
    }
  } else if (data.skipScoreDeduction) {
    console.log("점수 감소 중복 적용 방지: 이미 점수가 감소되었음");
  }
  
  // 3. 책 내용 제거
  if (data.imageDelete === true) {
    console.log("책 내용 제거 전:", bookContents.value.length, bookContents.value);
    if (bookContents.value.length === 1) {
      bookContents.value = [{ content: "", image: null }];
    } else {
      bookContents.value = bookContents.value.slice(0, -1);
    }
    console.log("책 내용 제거 후:", bookContents.value.length, bookContents.value);
  }
  
  // 4. 경고 모달 표시
  showInappropriateWarningModal(data.warningData);
  
  // 5. 턴 정보 업데이트
  totalTurn.value = data.totalTurn;
  currTurn.value = data.currTurn;
  
  // 6. 3초 후 whoTurn 오버레이 표시 (경고 모달이 먼저 표시된 후)
  setTimeout(async () => {
    console.log("whoTurn 오버레이 표시");
    await showOverlay('whoTurn');
    
    // 다음 턴을 위한 상태 리셋
    isVoted.value = false;
    inProgress.value = true;
    console.log("게임 진행 상태 재활성화 및 투표 상태 리셋");
  }, 3000);  // 경고 모달이 표시되는 시간과 동일
  
  console.log("투표 중단 및 경고 표시 완료");
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
        score: 10
      });
      configurable.value = true;
      InviteLink.value =
        import.meta.env.VITE_MAIN_API_SERVER_URL +
        "?roomID=" +
        compressUUID(peerId.value);
    }
  } catch (error) {
    // Peer initialization failed
  }
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

// 컴포넌트 언마운트 전에 peer 객체 정리
onBeforeUnmount(() => {
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
})

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
  // 게임 관련 데이터 초기화
  receivedMessages.value = [];
  currTurn.value = 0;
  bookContents.value = [{ content: "", image: null }];
  bookCover.value = {title: "", imageUrl: ""};
  ISBN.value = "";
  votings.value = [];
  myTurn.value = null;
  inProgress.value = false;
  inGameOrder.value = [];
  isForceStopped.value = null;
  participants.value.forEach((participant) => {
    participant.score = 10;
  })
  usedCard.value = {
    id: 0,
    keyword: "",
    isEnding: false
  };
  // 로딩 애니메이션 활성화
  emit("startLoading", {value: true});
  
  // 시연 모드 확인
  isPreview.value = data.isPreview;

  // 게임 방 생성
  if(isPreview.value) {
    try {
      const response = await testGame({
        bossId: peerId.value,
        player: participants.value.map((p) => p.id),
        drawingStyle: roomConfigs.value.currMode,
      });
      gameID.value = response.data.data.gameId;
      storyCards.value = response.data.data.status.storyCards;
      endingCard.value = response.data.data.status.endingCard;
    } catch (error) {
      // 에러 처리
    }
  } else {
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
      // 에러 처리
    }
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
        participants: participants.value,
        isPreview: isPreview.value,
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
    emit("startLoading", {value: false});
    
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
        toast.errorToast(error.response?.data?.message || "프롬프트 필터링 중 오류가 발생했습니다.");
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

    setTimeout(async () => {
          if(isVoted.value) {
            isVoted.value = false;
          } else {
            await voteEnd({
              sender: userStore.userData.userNickname,
              selected: "up",
            });
            isVoted.value = false;
          }
        }, 10000);  // 투표 시간 10초로 설정

    addBookContent({ content: data.prompt, image: null });

    // 투표 모달 띄우기
    inProgress.value = false;
    prompt.value = data.prompt;
    votings.value = [];
    // 해당 프롬프트로 이미지 생성 요청 (api)
    console.log("=== 이미지 생성 API 호출 시작 ===");
    console.log("게임ID:", gameID.value);
    console.log("사용자ID:", peerId.value);
    console.log("사용자 프롬프트:", data.prompt);
    console.log("턴:", totalTurn.value);
    console.log("현재 턴 번호 (totalTurn):", totalTurn.value);
    
    try {
      const responseImage = await createImage({
        gameId: gameID.value,
        userId: peerId.value,
        userPrompt: data.prompt,
        turn: totalTurn.value++,
      });
      
      console.log("=== 이미지 생성 API 응답 수신 ===");
      console.log("응답 상태:", responseImage?.status);
      console.log("응답 데이터 타입:", typeof responseImage?.data);
      console.log("응답 데이터 크기:", responseImage?.data?.size || "알 수 없음");
      
      // 이미지가 들어왔다고 하면 이미지 사람들에게 전송하고, 책에 넣는 코드
      const imageBlob = URL.createObjectURL(responseImage.data);
      console.log("이미지 Blob URL 생성 완료:", imageBlob);

      // webRTC의 데이터 채널은 Blob을 지원하지 않으므로 변환
      const arrayBuffer = await responseImage.data.arrayBuffer();
      console.log("ArrayBuffer 변환 완료. 크기:", arrayBuffer.byteLength, "bytes");
      
      // 사람들에게 이미지 전송
      console.log("=== WebRTC 이미지 전송 시작 ===");
      console.log("전송할 피어 수:", connectedPeers.value.length);
      
      connectedPeers.value.forEach((peer, index) => {
        if (peer.id !== peerId.value && peer.connection.open) {
          console.log(`피어 ${index + 1}(${peer.id})에게 이미지 전송 중...`);
          sendMessage(
            "sendImage",
            { imageBlob: arrayBuffer },
            peer.connection
          )
        } else {
          console.log(`피어 ${index + 1}(${peer.id}) 건너뜀 - 자신이거나 연결 닫힘`);
        }
      });
      
      // 나의 책에 이미지 넣기
      console.log("=== 자신의 책에 이미지 추가 ===");
      console.log("현재 책 페이지 수:", bookContents.value.length);
      bookContents.value[bookContents.value.length - 1].image = imageBlob;
      console.log("이미지 추가 완료. 최종 책 페이지 수:", bookContents.value.length);
      console.log("=== 이미지 생성 및 공유 완료 ===");
      
    } catch (error) {
      console.error("=== 이미지 생성 API 호출 실패 ===");
      console.error("에러 타입:", error?.constructor?.name);
      console.error("에러 메시지:", error?.message);
      console.error("HTTP 상태:", error?.response?.status);
      console.error("HTTP 상태 텍스트:", error?.response?.statusText);
      console.error("응답 데이터:", error?.response?.data);
      console.error("전체 에러 객체:", error);
      
      // Blob 응답 데이터를 텍스트로 변환하여 실제 에러 메시지 확인
      let errorMessage = "";
      let isInappropriateContent = false;
      
      if (error?.response?.data instanceof Blob) {
        try {
          const errorText = await error.response.data.text();
          console.error("Blob 에러 데이터 내용:", errorText);
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.message || "";
          console.error("파싱된 에러 메시지:", errorMessage);
        } catch (parseError) {
          console.error("Blob 데이터 파싱 실패:", parseError);
        }
      }
      
      // 콘텐츠 필터링 감지 로직 개선 (테스트를 위해 503 에러는 모두 부적절한 콘텐츠로 처리)
      isInappropriateContent = error?.response?.status === 503;
      
      // 더 구체적인 감지가 필요한 경우를 위한 키워드 체크 (향후 사용)
      const hasFilteringKeywords = (
        errorMessage.includes("필터링") || 
        errorMessage.includes("filter") ||
        errorMessage.includes("blocked") ||
        errorMessage.includes("safety") ||
        errorMessage.includes("콘텐츠") ||
        errorMessage.includes("부적절") ||
        errorMessage.includes("inappropriate") ||
        errorMessage.includes("content policy") ||
        errorMessage.includes("safety policy") ||
        error?.message?.includes("필터링") ||
        error?.message?.includes("filter")
      );
      
      console.log("부적절한 콘텐츠 감지 여부:", isInappropriateContent);
      
      // 콘텐츠 필터링으로 인한 이미지 생성 실패 처리
      if (isInappropriateContent) {
        
        console.log("=== 부적절한 콘텐츠로 인한 이미지 생성 거부 감지 ===");
        
        // 자신의 턴일 때만 처리 (투표 부결과 동일한 조건)
        console.log("현재 턴:", currTurn.value, "내 턴:", myTurn.value, "턴 비교:", currTurn.value === myTurn.value);
        if (currTurn.value === myTurn.value) {
          console.log("=== 자신의 턴이므로 부적절한 콘텐츠 처리 시작 ===");
          
          // 투표 탈락과 동일한 처리: 점수 감소
          const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
          console.log("현재 플레이어:", currentPlayer, "기존 점수:", currentPlayer.score);
          currentPlayer.score -= 1;
          console.log("점수 감소 후:", currentPlayer.score);
          
          // 사용자 메시지가 이미 책에 추가된 상태이므로 제거 (투표 탈락과 동일)
          console.log("책 내용 제거 전:", bookContents.value.length, bookContents.value);
          if (bookContents.value.length === 1) {
            bookContents.value = [{ content: "", image: null }];
          } else {
            bookContents.value = bookContents.value.slice(0, -1);
          }
          console.log("책 내용 제거 후:", bookContents.value.length, bookContents.value);
          
          // 경고 메시지와 아이콘을 모든 플레이어에게 전송
          const warningMessage = {
            type: "inappropriateContent",
            playerName: currentPlayer.name,
            message: "부적절한 이미지를 생성하려 했습니다"
          };
          console.log("경고 메시지 생성:", warningMessage);
          
          // 투표 중단 신호를 모든 플레이어에게 즉시 전송
          console.log("모든 플레이어에게 투표 중단 및 경고 알림 전송");
          const stopVotingMessage = {
            type: "stopVotingAndShowWarning",
            warningData: warningMessage,
            currTurn: (currTurn.value + 1) % participants.value.length,
            totalTurn: totalTurn.value,
            imageDelete: true,
            isInappropriate: true
          };
          
          // 모든 피어에게 투표 중단 및 경고 알림 전송
          connectedPeers.value.forEach((peer) => {
            if (peer.id !== peerId.value && peer.connection.open) {
              console.log("피어에게 투표 중단 및 경고 알림 전송:", peer.id);
              sendMessage("stopVotingAndShowWarning", stopVotingMessage, peer.connection);
            }
          });
          
          // 자신에게도 투표 중단 및 경고 표시 (하지만 점수는 이미 감소했으므로 중복 적용 방지)
          console.log("자신에게도 투표 중단 및 경고 모달 표시");
          const selfStopVotingMessage = {...stopVotingMessage, skipScoreDeduction: true};
          stopVotingAndShowWarning(selfStopVotingMessage);
          
          console.log("부적절한 콘텐츠 처리 완료. 플레이어 점수:", currentPlayer.score);
        } else {
          console.log("=== 자신의 턴이 아니므로 부적절한 콘텐츠 처리 건너뜀 ===");
        }
      } else {
        // 일반적인 이미지 생성 실패
        toast.errorToast("이미지 생성에 실패했습니다: " + (error?.message || "알 수 없는 오류"));
      }
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
    connectedPeers.value.forEach((peer) => {
      if (peer.id !== peerId.value && peer.connection.open) {
        sendMessage(
          "nextTurn",
          {
            currTurn: currTurn.value,
            isTimeout: true,
            totalTurn: totalTurn.value,
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
  isVoted.value = true;
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
      let accepted;
      if (upCount < downCount) {
        // 이미지 버리는 api
        accepted = false;

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
        connectedPeers.value.forEach((peer) => {
          if (peer.id !== peerId.value && peer.connection.open) {
            sendMessage(
              "nextTurn",
              {
                currTurn: currTurn.value,
                imageDelete: true,
                totalTurn: totalTurn.value,
              },
              peer.connection
            )
          }
        });
        await showOverlay('whoTurn');
        inProgress.value = true;
      }
      else {
        isElected.value = true;
        accepted = true;
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
        if (usedCard.value.isEnding) {
          // 즉시 승자 표시 (1초 후)
          setTimeout(() => {
            isForceStopped.value = "champ";
          }, 1000);
          
          await gameEnd(true).then(() => {
            connectedPeers.value.forEach(async (p) => {
              if (p.id !== peerId.value && p.connection.open) {
                sendMessage("gameEnd",
                  {},
                  p.connection
                );
              };
            });
          });
        } else {
          connectedPeers.value.forEach(async (p) => {
            if (p.id !== peerId.value && p.connection.open) {
              sendMessage(
                "nextTurn",
                {
                  currTurn: currTurn.value,
                  imageDelete: false,
                  totalTurn: totalTurn.value,
                },
                p.connection
              )
            };
          });

          await showOverlay('whoTurn');
          inProgress.value = true;
        };
      }
      // 투표 결과 전송 api
      try {
          const response = await voteResultSend({
            gameId: gameID.value,
            userId: peerId.value,
            accepted: accepted,
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
        isElected.value = true;
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
if (currTurn.value === myTurn.value) {
  let stopWatch;
  stopWatch = watch(
    () => [bookContents.value, votings.value],
    async ([newBookContents, newVotings]) => {
      await nextTick();
      const lastContent = newBookContents[newBookContents.length - 1];
      if (lastContent && lastContent.image !== null && newVotings.length === participants.value.length - 1) {
        votings.value = [...votings.value, {sender: data.sender, selected: data.selected}];
        sendVoteResult();
        if(stopWatch) {
          stopWatch();
        }
      }
    },
    { deep: true, immediate: true }
  );
} else {
  votings.value = [...votings.value, {sender: data.sender, selected: data.selected}];
  sendVoteResult();
}
};

const gameEnd = async (status) => {
  // 게임 시작 상태는 onWinnerShown에서 처리 (TTS 타이밍 제어를 위해)
  // gameStarted.value = false;  // 여기서 제거
  // 턴 초기화
  currTurn.value = -1;
  totalTurn.value = 1;
  
  // 비정상 종료인 경우 (긴장감 100 초과)
  if (!status) {
    // 책 비우기
    // 방장인 경우 게임실패 송신
    if (participants.value[0].id == peerId.value) {
      // 비정상 종료 api 들어가야함
      try {
        const response = await deleteGame({
          gameId: gameID.value,
          isForceStopped: true
        })
      } catch (error) {
        // 비정상 종료 처리 실패
      }
    }
    // 전체 실패 쇼 오버레이
    // isForceStopped.value = "fail";
  } else {
    // 정상 종료인 경우
    if (participants.value[0].id == peerId.value) {
      // 정상 종료 api 들어가야함
      try {
        const response = await deleteGame({
          gameId: gameID.value,
          isForceStopped: false
        }).then((res) => {
          ISBN.value = res.data.data.bookId;
          bookCover.value.title = res.data.data.title;
          bookCover.value.imageUrl = res.data.data.bookCover;
        }).then(() => {
          connectedPeers.value.forEach(async (p) => {
            if (p.id !== peerId.value && p.connection.open) {
              sendMessage("bookCover", {
                bookCover: bookCover.value,
                ISBN: ISBN.value,
              }, p.connection);
            }
          });
        });

      } catch (error) {
        // 정상 종료 처리 실패
      }
    }
    // 우승자 쇼 오버레이
    // isForceStopped.value = "champ";
  }
};

// 승자 표시 완료 후 나레이션 시작
const onWinnerShown = () => {
  // 승자 표시가 완료되었으므로 이제 나레이션 시작
  gameStarted.value = false;
};

// 나레이션 완료 후 승자 화면 제거 및 표지 표시
const onNarrationComplete = () => {
  // 승자 화면 제거
  isForceStopped.value = null;
  // 표지가 이미 표시되어 있으므로 추가 작업 없음
};

const goLobby = () => {
  // 게임 관련 데이터 초기화
  receivedMessages.value = [];
  currTurn.value = 0;
  bookContents.value = [{ content: "", image: null }];
  bookCover.value = {title: "", imageUrl: ""};
  ISBN.value = "";
  votings.value = [];
  myTurn.value = null;
  inProgress.value = false;
  inGameOrder.value = [];
  isForceStopped.value = null;
  participants.value.forEach((participant) => {
    participant.score = 10;
  });
  usedCard.value = {
    id: 0,
    keyword: "",
    isEnding: false
  };

  router.push("/game/lobby");
};

// 긴장감이 100 이상 진행 된 경우 전체 탈락
watch(
  () => [percentage.value, usedCard.value, isElected.value],
  ([newPercent, newUsedCard, newIsElected], [oldPercent, oldUsedCard, oldIsElected]) => {
    if (newPercent >= oldPercent && newPercent >= 100 && newUsedCard.isEnding == false && newIsElected) {
      gameEnd(false);
      // 전체 실패 쇼 오버레이
      isForceStopped.value = "fail";
    }
  },
  { deep: true }
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
