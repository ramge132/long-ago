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
          @card-reroll="cardReroll" @vote-end="voteEnd" @vote-selected="onVoteSelected" @go-lobby="goLobby" @winner-shown="onWinnerShown" @narration-complete="onNarrationComplete" @start-narration="onStartNarration" />
      </Transition>
    </RouterView>
    <div
      class="overlay absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col justify-center items-center scale-0">
      <img :src="currTurnImage" alt="">
      <div class="rounded-md px-3 py-1 bg-blue-400 text-xl"></div>
    </div>
    
    <!-- 부적절한 콘텐츠 경고 모달 - 게임 테마 맞춤 디자인 -->
    <div
      v-if="showWarningModal"
      class="warning-modal fixed inset-0 bg-[#00000050] backdrop-blur-sm flex items-center justify-center z-50"
      @click="hideWarningModal">
      <div 
        class="warning-content bg-[#ffffff85] backdrop-blur-[20px] border-[1px] border-[#ffffff60] rounded-2xl p-8 max-w-md mx-4 text-center transform transition-all duration-500 shadow-2xl"
        style="animation: gentleBounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)"
        @click.stop>
        
        <!-- Warning Icon with Glow Effect -->
        <div class="relative mb-6">
          <div class="absolute inset-0 bg-gradient-to-r from-orange-400 to-red-500 rounded-full blur-xl opacity-30 animate-pulse"></div>
          <div class="relative w-20 h-20 mx-auto bg-gradient-to-br from-orange-100 to-red-100 rounded-full p-4 shadow-lg">
            <img :src="WarningIcon" alt="경고" class="w-full h-full object-contain filter drop-shadow-md">
          </div>
        </div>

        <!-- Title with Game Font -->
        <h3 class="text-2xl font-katuri font-bold text-[#8B4513] mb-3 drop-shadow-sm">
          🚨 부적절한 이야기 감지
        </h3>
        
        <!-- Message -->
        <p class="text-[#5D4E37] font-katuri text-lg mb-6 leading-relaxed">
          {{ warningModalMessage }}
        </p>
        
        <!-- Decorative Line -->
        <div class="w-16 h-1 bg-gradient-to-r from-orange-300 to-red-400 rounded-full mx-auto mb-6"></div>
        
        <!-- Confirm Button -->
        <button 
          @click="hideWarningModal"
          class="bg-gradient-to-r from-orange-400 to-red-500 hover:from-orange-500 hover:to-red-600 text-white font-katuri px-8 py-3 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 hover:shadow-lg active:scale-95">
          알겠습니다 ✨
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
// 경고 후 상태 리셋 타이머 관리
let warningTimer = null;
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
const currentVoteSelection = ref("up"); // 현재 선택된 투표 값 추적
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
    // 중요한 메시지들은 로그 출력
    if (["showResultsWithCover", "bookCover", "gameEnd", "showResults"].includes(data.type)) {
      
    }
    
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
          messageMusic.volume = audioStore.audioVolume;  // 볼륨 적용
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
            myTurn.value = i; // participants 배열에서의 내 인덱스
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
          // 내 카드 받기와 라우터 이동을 동시에 처리
          const [response] = await Promise.all([
            enterGame({
              userId: peerId.value,
              gameId: gameID.value,
            }),
            router.push("/game/play")
          ]);

          storyCards.value = response.data.data.storyCards;
          endingCard.value = response.data.data.endingCard;

          // 로딩 즉시 비활성화
          emit("startLoading", {value: false});
          
          // 오버레이 표시
          await showOverlay('start');
          setTimeout(() => {
            showOverlay('whoTurn').then(() => {
              inProgress.value = true;
            });
          }, 500); // 딜레이 단축
        });
        break;

      case "nextTurn":
        // 먼저 모든 상태 업데이트를 완료한 후 오버레이 표시
        
        // 1. 책 내용 삭제 (투표 거부 시)
        if (data.imageDelete === true) {
          if (bookContents.value.length === 1) {
            bookContents.value = [{ content: "", image: null }];
          } else {
            bookContents.value = bookContents.value.slice(0, -1);
          }
        }
        
        // 2. 점수 처리
        if (data.isTimeout) {
          // 타임아웃 점수 -1
          const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
          currentPlayer.score -= 1;
        }
        if (data.isInappropriate) {
          // 부적절한 콘텐츠로 인한 점수 -1 처리 (다른 플레이어들에게도 동기화)
          const currentPlayer = participants.value[inGameOrder.value[data.currTurn === 0 ? participants.value.length - 1 : data.currTurn - 1]];
          currentPlayer.score -= 1;
        }
        
        // 3. 투표 결과에 따른 점수 변화 처리 (P2P 동기화)
        if (data.scoreChange) {
          const targetPlayer = participants.value[data.scoreChange.playerIndex];
          if (targetPlayer) {
            if (data.scoreChange.type === "increase") {
              targetPlayer.score += data.scoreChange.amount;
            } else if (data.scoreChange.type === "decrease") {
              targetPlayer.score -= data.scoreChange.amount;
            }
          }
        }
        
        // 4. 카드 삭제 처리 (P2P 동기화)
        if (data.cardRemoval) {
          storyCards.value = storyCards.value.filter(card => card.id !== data.cardRemoval.cardId);
        }
        
        // 5. 턴 정보 업데이트
        totalTurn.value = data.totalTurn;
        currTurn.value = data.currTurn;
        
        // 6. 상태 업데이트 후 오버레이 표시
        inProgress.value = false;
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
        console.log("🎯 [sendPrompt] 새로운 프롬프트 수신");
        console.log("  - 발신자:", data.prompt);
        console.log("  - 현재 isVoted 상태:", isVoted.value);
        console.log("  - 현재 votings 배열:", JSON.stringify(votings.value));
        console.log("  - 현재 타이머 상태:", { voteTimer: !!voteTimer, warningTimer: !!warningTimer });
        
        // 기존 타이머들 모두 정리
        if (voteTimer) {
          console.log("  🔄 기존 voteTimer 정리");
          clearTimeout(voteTimer);
          voteTimer = null;
        }
        if (warningTimer) {
          console.log("  🔄 기존 warningTimer 정리");
          clearTimeout(warningTimer);
          warningTimer = null;
        }
        
        // 완전한 상태 초기화
        console.log("  🔄 상태 초기화 시작");
        usedCard.value = data.usedCard;
        prompt.value = data.prompt;
        inProgress.value = false;
        isVoted.value = false; // 새로운 투표를 위해 초기화
        currentVoteSelection.value = "up"; // 투표 선택값을 찬성으로 초기화
        votings.value = []; // 투표 배열 완전 초기화
        isElected.value = false; // 선출 상태 초기화
        
        console.log("  ✅ 상태 초기화 완료");
        console.log("    - isVoted:", isVoted.value);
        console.log("    - currentVoteSelection:", currentVoteSelection.value);
        console.log("    - votings:", JSON.stringify(votings.value));
        console.log("    - isElected:", isElected.value);
        
        // 책 콘텐츠 추가
        addBookContent({ content: data.prompt, image: null });
        
        // 새로운 투표 타이머 설정
        console.log("  ⏰ 새로운 투표 타이머 설정 (10초)");
        voteTimer = setTimeout(async () => {
          console.log("  ⏰ [voteTimer] 타이머 만료");
          console.log("    - isVoted 상태:", isVoted.value);
          console.log("    - currentVoteSelection:", currentVoteSelection.value);
          if(!isVoted.value) {
            console.log("    → 자동 투표 실행");
            await voteEnd({
              sender: userStore.userData.userNickname,
              selected: currentVoteSelection.value,
            });
          } else {
            console.log("    → 이미 투표함");
          }
          isVoted.value = false;
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
        console.log("📊 [voteResult] 투표 결과 수신");
        console.log("  - 투표자:", data.sender);
        console.log("  - 선택:", data.selected);
        console.log("  - 현재 votings 배열:", JSON.stringify(votings.value));
        console.log("  - 현재 isElected 상태:", isElected.value);
        
        // 투표 배열에 추가 전 중복 체크
        const voteExists = votings.value.some(v => v.sender === data.sender);
        if (!voteExists) {
          votings.value = [...votings.value, {sender: data.sender, selected: data.selected}];
          console.log("  - 투표 추가 후 votings:", JSON.stringify(votings.value));
        }

        if (votings.value.length == participants.value.length) {
          console.log("📊 [voteResult] 모든 투표 완료");
          let upCount = 0;
          let downCount = 0;
          votings.value.forEach((vote) => {
            if (vote.selected == 'up') upCount++;
            else downCount++;
          });
          console.log(`  - 투표 집계: 찬성 ${upCount} vs 반대 ${downCount}`);
          
          // 모든 플레이어가 동일한 결과를 봐야 함
          const voteAccepted = upCount >= downCount;
          console.log("  - 투표 결과:", voteAccepted ? "승인" : "거부");
          console.log("  - 현재 턴:", currTurn.value, "나의 턴:", myTurn.value);
          
          if (currTurn.value === myTurn.value) {
            console.log("  📌 내 턴 - 투표 결과 처리");
            
            // 턴 업데이트 전에 현재 플레이어 인덱스를 저장 (승인/거부 모두에서 사용)
            const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
            const currentPlayerIndex = inGameOrder.value[currTurn.value];
            
            let accepted = voteAccepted;
            if (accepted) {
              // 찬성이 더 많거나 동수일 때 승인 (동수 포함)
              console.log("    → isElected를 true로 설정");
              isElected.value = true;
              // 투표 가결 시 점수 +2
              
              if (usedCard.value.isEnding) {
                currentPlayer.score += 5;
              } else {
                currentPlayer.score += 2;
              }

              // 턴 종료 트리거 송신하기
              currTurn.value = (currTurn.value + 1) % participants.value.length;
              // condition에서 다음 턴 or 게임 종료
              if (usedCard.value.isEnding) {
                
                // 1단계: 백그라운드로 책 표지 생성 요청 시작 (응답을 기다리지 않음)
                gameEnd(true); // await 제거 - 백그라운드 실행
                
                // 2단계: 즉시 점수 정산을 먼저 전송
                connectedPeers.value.forEach((p) => {
                  if (p.id !== peerId.value && p.connection.open) {
                    sendMessage("endingCardScoreUpdate", {
                      scoreChange: {
                        type: "increase",
                        amount: 5, // 결말카드는 항상 +5점
                        playerIndex: currentPlayerIndex // 저장된 현재 플레이어 인덱스 사용
                      }
                    }, p.connection);
                  }
                });
                
                // 3단계: 점수 정산 후 1초 뒤 결과창 표시
                setTimeout(() => {
                  
                  // 방장 결과창 표시
                  isForceStopped.value = "champ";
                  
                  // 게스트들에게도 결과창 표시
                  connectedPeers.value.forEach(async (p) => {
                    if (p.id !== peerId.value && p.connection.open) {
                      sendMessage("showResultsWithCover", {
                        bookCover: {
                          title: "아주 먼 옛날", // 기본값
                          imageUrl: "" // 기본값 (빈 문자열)
                        },
                        ISBN: "generating..." // 생성 중 표시
                      }, p.connection);
                    }
                  });
                }, 1000);
              } else {
                // 다른 플레이어들에게 점수 증가 정보와 함께 nextTurn 메시지 전송
                const scoreIncrease = usedCard.value.isEnding ? 5 : 2;
                
                connectedPeers.value.forEach(async (p) => {
                  if (p.id !== peerId.value && p.connection.open) {
                    sendMessage(
                      "nextTurn",
                      {
                        currTurn: currTurn.value,
                        imageDelete: false,
                        totalTurn: totalTurn.value,
                        scoreChange: {
                          type: "increase",
                          amount: scoreIncrease,
                          playerIndex: currentPlayerIndex // 저장된 현재 플레이어 인덱스 사용
                        },
                        cardRemoval: {
                          cardId: usedCard.value.id
                        }
                      },
                      p.connection
                    )
                  };
                });

                await showOverlay('whoTurn');
                inProgress.value = true;
              };
            } else {
              // 반대가 더 많거나 동수일 때 거부
              accepted = false;
              
              // 먼저 다른 플레이어들에게 삭제 메시지 전송 (오버레이 표시 전)
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
              
              // 자신의 이미지도 삭제
              if (bookContents.value.length === 1) {
                bookContents.value = [{ content: "", image: null }];
              } else {
                bookContents.value = bookContents.value.slice(0, -1);
              }
              
              // 투표 거부된 플레이어 점수 -1
              currentPlayer.score -= 1;
              
              // 상태 동기화 후 오버레이 표시
              await showOverlay('whoTurn');
              inProgress.value = true;
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
          // 투표 찬성 시 카드 제거
          if (accepted) {
            storyCards.value.forEach((card, index) => {
              if (card.id === usedCard.value.id) {
                storyCards.value.splice(index, 1);
              }
            });
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
            // 게스트도 동일한 투표 결과 처리
            console.log("  📌 게스트 - 투표 결과 동기화");
            console.log("    - voteAccepted:", voteAccepted);
            console.log("    - currTurn:", currTurn.value, "myTurn:", myTurn.value);
            console.log("    - usedCard.isEnding:", usedCard.value.isEnding);
            console.log("    - 방장 여부:", participants.value[0].id === peerId.value);
            
            // 게스트도 투표 결과에 따라 isElected 설정
            if (voteAccepted) {
              console.log("    → isElected를 true로 설정 (게스트)");
              isElected.value = true;
              
              // 방장이 게스트의 결말카드 투표를 처리하는 경우
              if (usedCard.value.isEnding && participants.value[0].id === peerId.value) {
                console.log("    → 방장이 게스트의 결말카드 게임 종료 처리");
                
                // 1단계: 백그라운드로 책 표지 생성 요청
                gameEnd(true);
                
                // 2단계: 1초 뒤 결과창 표시 (점수 정산은 이미 endingCardScoreUpdate로 처리됨)
                setTimeout(() => {
                  console.log("    → 방장 결과창 표시");
                  isForceStopped.value = "champ";
                  
                  // 게스트들에게도 결과창 표시
                  connectedPeers.value.forEach(async (p) => {
                    if (p.id !== peerId.value && p.connection.open) {
                      sendMessage("showResultsWithCover", {
                        bookCover: {
                          title: "아주 먼 옛날",
                          imageUrl: ""
                        },
                        ISBN: "generating..."
                      }, p.connection);
                    }
                  });
                }, 1000);
              } else {
                // 동기화를 위해 약간의 지연 후 상태 확인
                setTimeout(() => {
                  console.log("    → isElected 상태 재확인:", isElected.value);
                  console.log("    → bookContents 길이:", bookContents.value.length);
                  // InGameContent.vue에 전달되는 isElected 상태 확인
                  if (isElected.value && bookContents.value.length > 0) {
                    console.log("    → 책 페이지 넘김이 자동으로 트리거됨");
                  }
                }, 100);
              }
            } else {
              console.log("    → 투표 거부 - isElected는 false 유지");
            }
          }
        }
        break;

      case "gameEnd":
        break;

      case "showResults":
        isForceStopped.value = "champ";
        break;

      case "gameEndPrepare":
        // 게스트들은 showResultsWithCover 메시지를 기다리는 상태로 전환
        // 특별한 처리는 필요없고, 로그만 출력
        break;

      case "endingCardScoreUpdate":
        // 결말카드 점수 정산 (결과창 표시 전에 먼저 처리)
        console.log("📊 [endingCardScoreUpdate] 결말카드 점수 정산 처리");
        if (data.scoreChange) {
          const targetPlayer = participants.value[data.scoreChange.playerIndex];
          if (targetPlayer) {
            if (data.scoreChange.type === "increase") {
              targetPlayer.score += data.scoreChange.amount;
              console.log(`📊 결말카드 점수 증가: ${targetPlayer.name} +${data.scoreChange.amount}점 (${targetPlayer.score - data.scoreChange.amount} → ${targetPlayer.score})`);
            }
          }
        }
        break;

      case "showResultsWithCover":
        
        // 표지 정보 설정 (점수는 이미 endingCardScoreUpdate에서 처리됨)
        if (data.bookCover) {
          bookCover.value = data.bookCover;
        }
        if (data.ISBN) {
          ISBN.value = data.ISBN;
        }
        
        // 결과창 표시
        console.log("🏆 [showResultsWithCover] 결과창 표시 (점수 정산은 이미 완료됨)");
        isForceStopped.value = "champ";
        break;

      case "bookCoverUpdate":
        
        // 표지 정보 업데이트 (결과창은 이미 표시된 상태)
        if (data.bookCover) {
          bookCover.value = data.bookCover;
        }
        if (data.ISBN) {
          ISBN.value = data.ISBN;
        }
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
  
  // 경고 토스트 메시지 표시 (모든 플레이어에게 보임)
  const warningMessage = `${warningData.message}`;
  
  // warning.png와 함께 커스텀 토스트 표시  
  toast.setToast({
    msg: warningMessage,
    type: "error",  // error 타입이 더 눈에 띄고 적절함
    timeout: 6000,  // 6초간 표시하여 확실히 인지하도록
    closeButton: "button",
    position: "top-center",
    icon: true
  });
  
};

// 부적절한 콘텐츠 경고 모달 표시
const showInappropriateWarningModal = (warningData) => {
  
  warningModalMessage.value = `${warningData.message}`;
  showWarningModal.value = true;
  
  // 3초 후 자동으로 모달 닫기
  setTimeout(() => {
    hideWarningModal();
  }, 3000);
  
};

// 경고 모달 숨기기
const hideWarningModal = () => {
  showWarningModal.value = false;
  warningModalMessage.value = "";
};

// 투표 중단 및 경고 표시 (모든 플레이어용)
const stopVotingAndShowWarning = async (data) => {
  console.log("🚨 [stopVotingAndShowWarning] 함수 시작");
  console.log("  - 데이터:", JSON.stringify(data));
  console.log("  - 현재 isVoted 상태:", isVoted.value);
  console.log("  - 현재 타이머 상태:", { voteTimer: !!voteTimer, warningTimer: !!warningTimer });
  
  // 모든 타이머 즉시 정리
  if (voteTimer) {
    console.log("  🔄 voteTimer 정리");
    clearTimeout(voteTimer);
    voteTimer = null;
  }
  if (warningTimer) {
    console.log("  🔄 warningTimer 정리");
    clearTimeout(warningTimer);
    warningTimer = null;
  }
  
  // 1. 투표 즉시 중단 (InGameView에서 투표 UI 숨김)
  console.log("  📊 투표 UI 중단 처리");
  inProgress.value = false;
  
  // 버그 수정: isVoted를 true로 설정하지 않음
  // 대신 임시 플래그를 사용하여 투표 UI를 숨김
  const wasVotingActive = !isVoted.value; // 현재 투표가 활성화되어 있었는지 기록
  console.log("  - 투표가 활성화되어 있었는가?:", wasVotingActive);
  
  // 투표 UI를 숨기기 위해 prompt를 초기화 (isVoted는 건드리지 않음)
  prompt.value = "";     // 프롬프트 초기화하여 투표 UI 제거
  isElected.value = false; // 선출 상태도 초기화
  
  // 투표 관련 상태 완전 초기화
  votings.value = [];
  usedCard.value = {
    id: 0,
    keyword: "",
    isEnding: false
  };
  currentVoteSelection.value = "up"; // 투표 선택값 초기화
  
  console.log("  ✅ 투표 상태 초기화 완료");
  console.log("    - isVoted (변경 안함):", isVoted.value);
  console.log("    - prompt:", prompt.value);
  console.log("    - votings:", JSON.stringify(votings.value));
  
  
  // 2. 점수 동기화 (다른 플레이어들)
  console.log("  💯 점수 동기화 처리");
  if (data.isInappropriate && !data.skipScoreDeduction) {
    const affectedPlayerIndex = data.currTurn === 0 ? participants.value.length - 1 : data.currTurn - 1;
    const affectedPlayer = participants.value[inGameOrder.value[affectedPlayerIndex]];
    if (affectedPlayer) {
      console.log(`    - ${affectedPlayer.name}의 점수 -1 (${affectedPlayer.score} → ${affectedPlayer.score - 1})`);
      affectedPlayer.score -= 1;
    }
  } else if (data.skipScoreDeduction) {
    console.log("    - 점수 차감 건너뜀 (이미 처리됨)");
  }
  
  // 3. 책 내용 제거 (중복 제거 방지)
  console.log("  📖 책 내용 제거 처리");
  if (data.imageDelete === true && !data.skipBookContentRemoval) {
    const beforeLength = bookContents.value.length;
    if (bookContents.value.length === 1) {
      bookContents.value = [{ content: "", image: null }];
    } else {
      bookContents.value = bookContents.value.slice(0, -1);
    }
    console.log(`    - 책 페이지 제거 (${beforeLength} → ${bookContents.value.length})`);
  } else if (data.skipBookContentRemoval) {
    console.log("    - 책 내용 제거 건너뜀 (이미 처리됨)");
  }
  
  // 4. 경고 모달 표시
  console.log("  ⚠️ 경고 모달 표시");
  showInappropriateWarningModal(data.warningData);
  
  // 5. 턴 정보 업데이트
  console.log("  🔄 턴 정보 업데이트");
  console.log(`    - totalTurn: ${totalTurn.value} → ${data.totalTurn}`);
  console.log(`    - currTurn: ${currTurn.value} → ${data.currTurn}`);
  totalTurn.value = data.totalTurn;
  currTurn.value = data.currTurn;
  
  // 6. isVoted 상태를 즉시 false로 리셋 (버그 수정)
  console.log("  🔧 isVoted 상태 즉시 리셋");
  isVoted.value = false;  // 다음 투표를 위해 즉시 리셋
  console.log("    - isVoted를 false로 설정 완료");
  
  // 7. 3초 후 whoTurn 오버레이 표시 (경고 모달이 먼저 표시된 후)
  console.log("  ⏰ warningTimer 설정 (3초 후 whoTurn 오버레이)");
  warningTimer = setTimeout(async () => {
    console.log("  ⏰ [warningTimer] 타이머 실행");
    
    // 타이머 실행 시점에 새로운 투표가 시작되었는지 확인
    if (prompt.value !== "" || voteTimer !== null) {
      console.log("    → 새로운 투표가 이미 시작됨, whoTurn 오버레이 건너뜀");
      warningTimer = null;
      return;
    }
    
    console.log("    → whoTurn 오버레이 표시");
    await showOverlay('whoTurn');
    
    // 다음 턴을 위한 상태 확인 (이미 false로 설정되어 있어야 함)
    console.log("    - 현재 isVoted 상태:", isVoted.value);
    console.log("    - 현재 currentVoteSelection:", currentVoteSelection.value);
    
    currentVoteSelection.value = "up"; // 투표 선택값 초기화
    inProgress.value = true; // 다음 턴 대기 상태
    
    warningTimer = null; // 타이머 완료 후 null로 설정
    console.log("  ✅ [warningTimer] 완료");
  }, 3000);  // 경고 모달이 표시되는 시간과 동일
  
  console.log("🚨 [stopVotingAndShowWarning] 함수 종료");
  
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
  
  // myTurn을 inGameOrder에서의 위치로 설정 (무작위 순서)
  participants.value.forEach((p, i) => {
    if (p.id === peerId.value) {
      // i는 participants 배열에서의 인덱스
      // inGameOrder에서 i를 찾아서 그 위치를 myTurn으로 설정
      const turnIndex = inGameOrder.value.indexOf(i);
      myTurn.value = turnIndex; // inGameOrder에서의 내 위치 (무작위 턴 순서)
    }
  });
  // API 호출과 라우터 이동을 병렬로 처리하여 시간 단축
  Promise.all([
    // 게임 시작 API 호출들을 여기에 넣을 수 있습니다.
    router.push("/game/play")
  ]).then(() => {
    // 로딩 즉시 비활성화
    emit("startLoading", {value: false});

    // 오버레이 표시
    showOverlay('start').then(() => {
      setTimeout(() => {
        showOverlay('whoTurn').then(() => {
          inProgress.value = true;
        });
      }, 500); // 딜레이 단축
    });
  });
};

const startReceived = (data) => {
  return new Promise((resolve) => {
    gameStarted.value = data.gameStarted;
    inGameOrder.value = data.order;
    gameID.value = data.gameId;

    // 내 순서 몇번인지 저장 (무작위 순서)
    participants.value.forEach((p, i) => {
      if (p.id === peerId.value) {
        // i는 participants 배열에서의 인덱스
        // inGameOrder에서 i를 찾아서 그 위치를 myTurn으로 설정
        const turnIndex = inGameOrder.value.indexOf(i);
        myTurn.value = turnIndex; // inGameOrder에서의 내 위치 (무작위 턴 순서)
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
  console.log("🔍 [nextTurn] 함수 호출됨");
  console.log("  - data:", JSON.stringify(data));
  console.log("  - data.isEnding:", data?.isEnding);
  console.log("  - data.prompt:", data?.prompt);
  
  // ContentTimer에서 호출된 30초 타이머 만료인 경우 (본인의 턴일 때만)
  const isMyCurrentTurn = inGameOrder.value[currTurn.value] === myTurn.value;
  
  if ((!data || !data.prompt) && isMyCurrentTurn) {
    // 타임아웃 점수 -1
    const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
    currentPlayer.score -= 1;

    // 턴 종료 트리거 송신하기
    currTurn.value = (currTurn.value + 1) % participants.value.length;
    inProgress.value = false;
    
    // 먼저 자신의 오버레이 표시
    await showOverlay('whoTurn');
    
    // 오버레이 완료 후 다른 플레이어들에게 메시지 전송
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
    
    inProgress.value = true;
    return;
  }
  
  // 프롬프트 제출인 경우
  if (data?.prompt) {
    const isEnding = data.isEnding === true; // 명시적으로 true 확인
    console.log("🎯 [nextTurn] isEnding 지역 변수 설정:", isEnding);
    console.log("  - data.isEnding 원본 값:", data.isEnding);
    console.log("  - isEnding 지역 변수 값:", isEnding);
    
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
      // 결말카드 정보 설정
      usedCard.value.id = -1; // 결말카드는 특별한 ID로 구분
      usedCard.value.keyword = data.prompt;
      usedCard.value.isEnding = isEnding; // 지역 변수 isEnding을 사용
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
              isEnding: usedCard.value.isEnding,
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
              selected: currentVoteSelection.value,
            });
            isVoted.value = false;
          }
        }, 10000);  // 투표 시간 10초로 설정

    addBookContent({ content: data.prompt, image: null });

    // 투표 모달 띄우기
    inProgress.value = false;
    prompt.value = data.prompt;
    currentVoteSelection.value = "up"; // 투표 선택값을 찬성으로 초기화
    votings.value = [];
    // 해당 프롬프트로 이미지 생성 요청 (api)
    console.log("🚀 [nextTurn] createImage API 호출 전");
    console.log("  - gameId:", gameID.value);
    console.log("  - userId:", peerId.value);
    console.log("  - userPrompt:", data.prompt);
    console.log("  - turn:", totalTurn.value);
    console.log("  - isEnding (전달할 값):", isEnding);
    
    try {
      const responseImage = await createImage({
        gameId: gameID.value,
        userId: peerId.value,
        userPrompt: data.prompt,
        turn: totalTurn.value++,
        isEnding: isEnding, // usedCard.value.isEnding 대신 지역 변수 isEnding을 직접 사용
      });
      
      
      
      // 이미지가 들어왔다고 하면 이미지 사람들에게 전송하고, 책에 넣는 코드
      const imageBlob = URL.createObjectURL(responseImage.data);

      // webRTC의 데이터 채널은 Blob을 지원하지 않으므로 변환
      const arrayBuffer = await responseImage.data.arrayBuffer();
      
      // 사람들에게 이미지 전송
      
      connectedPeers.value.forEach((peer, index) => {
        if (peer.id !== peerId.value && peer.connection.open) {
          sendMessage(
            "sendImage",
            { imageBlob: arrayBuffer },
            peer.connection
          )
        } else {
        }
      });
      
      // 나의 책에 이미지 넣기
      bookContents.value[bookContents.value.length - 1].image = imageBlob;
      
    } catch (error) {
      
      // Blob 응답 데이터를 텍스트로 변환하여 실제 에러 메시지 확인
      let errorMessage = "";
      let isInappropriateContent = false;
      
      if (error?.response?.data instanceof Blob) {
        try {
          const errorText = await error.response.data.text();
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.message || "";
        } catch (parseError) {
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
      
      
      // 콘텐츠 필터링으로 인한 이미지 생성 실패 처리
      if (isInappropriateContent) {
        
        
        // 자신의 턴일 때만 처리 (투표 부결과 동일한 조건)
        if (currTurn.value === myTurn.value) {
          
          // 투표 탈락과 동일한 처리: 점수 감소
          const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
          currentPlayer.score -= 1;
          
          // 사용자 메시지가 이미 책에 추가된 상태이므로 제거 (투표 탈락과 동일)
          if (bookContents.value.length === 1) {
            bookContents.value = [{ content: "", image: null }];
          } else {
            bookContents.value = bookContents.value.slice(0, -1);
          }
          
          // 경고 메시지와 아이콘을 모든 플레이어에게 전송
          const warningMessage = {
            type: "inappropriateContent",
            playerName: currentPlayer.name,
            message: "부적절한 이미지가 생성되었습니다"
          };
          
          // 턴 넘기기
          currTurn.value = (currTurn.value + 1) % participants.value.length;
          
          // condition에서 다음 턴 or 게임 종료 (투표 거부와 동일한 로직)
          if (usedCard.value.isEnding) {
            // 즉시 승자 표시 (1초 후)
            setTimeout(() => {
              isForceStopped.value = "champ";
            }, 1000);
            
            await gameEnd(true).then(() => {
              connectedPeers.value.forEach(async (p) => {
                if (p.id !== peerId.value && p.connection.open) {
                  sendMessage("gameEnd", {}, p.connection);
                }
              });
            });
          } else {
            // 게임이 계속되는 경우에만 투표 중단 신호 전송
            const stopVotingMessage = {
              type: "stopVotingAndShowWarning",
              warningData: warningMessage,
              currTurn: currTurn.value,
              totalTurn: totalTurn.value,
              imageDelete: true,
              isInappropriate: true
            };
            
            // 모든 피어에게 투표 중단 및 경고 알림 전송
            connectedPeers.value.forEach((peer) => {
              if (peer.id !== peerId.value && peer.connection.open) {
                sendMessage("stopVotingAndShowWarning", stopVotingMessage, peer.connection);
              }
            });
            
            // 자신에게도 투표 중단 및 경고 표시 (하지만 점수와 책 내용은 이미 처리했으므로 중복 적용 방지)
            const selfStopVotingMessage = {...stopVotingMessage, skipScoreDeduction: true, skipBookContentRemoval: true};
            stopVotingAndShowWarning(selfStopVotingMessage);
          }
          
        } else {
        }
      } else {
        // 일반적인 이미지 생성 실패
        toast.errorToast("이미지 생성에 실패했습니다: " + (error?.message || "알 수 없는 오류"));
      }
    }
    // const imageBlob = testImage;
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

// 투표 선택 시 즉시 호출
const onVoteSelected = (voteType) => {
  currentVoteSelection.value = voteType;
};

// 투표 종료
const voteEnd = async (data) => {
  console.log("🗳️ [voteEnd] 투표 종료 함수 호출");
  console.log("  - 투표자:", data.sender);
  console.log("  - 선택:", data.selected);
  console.log("  - 현재 votings:", JSON.stringify(votings.value));
  
  currentVoteSelection.value = data.selected; // 현재 투표 선택값 저장
  prompt.value = "";
  isVoted.value = true;
  // 이미지 들어올 때까지 대기

  const sendVoteResult = async () => {
  console.log("  📤 다른 플레이어들에게 투표 결과 전송");
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
    console.log("🗳️ [voteEnd] 모든 투표 완료 - 집계 시작");
    let upCount = 0;
    let downCount = 0;
    votings.value.forEach((vote) => {
      if (vote.selected == 'up') upCount++;
      else downCount++;
    });
    console.log(`  - 투표 집계: 찬성 ${upCount} vs 반대 ${downCount}`);
    
    // 모든 플레이어가 동일한 결과를 봐야 함
    const voteAccepted = upCount >= downCount;
    console.log("  - 투표 결과:", voteAccepted ? "승인" : "거부");

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
        // 투표 거부된 플레이어 점수 -1
        const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
        const currentPlayerIndex = inGameOrder.value[currTurn.value]; // 턴 업데이트 전에 저장
        currentPlayer.score -= 1;
        // 턴 종료 트리거 송신하기
        currTurn.value = (currTurn.value + 1) % participants.value.length;
        
        // 먼저 자신의 오버레이 표시
        await showOverlay('whoTurn');
        
        // 오버레이 완료 후 다른 플레이어들에게 메시지 전송
        connectedPeers.value.forEach((peer) => {
          if (peer.id !== peerId.value && peer.connection.open) {
            sendMessage(
              "nextTurn",
              {
                currTurn: currTurn.value,
                imageDelete: true,
                totalTurn: totalTurn.value,
                scoreChange: {
                  type: "decrease",
                  amount: 1,
                  playerIndex: currentPlayerIndex // 저장된 현재 플레이어 인덱스 사용
                }
              },
              peer.connection
            )
          }
        });
        
        inProgress.value = true;
      }
      else {
        isElected.value = true;
        accepted = true;
        // 투표 가결 시 점수 +2
        const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
        const currentPlayerIndex = inGameOrder.value[currTurn.value]; // 턴 업데이트 전에 저장!
        
        if (usedCard.value.isEnding) {
          currentPlayer.score += 5;
        } else {
          currentPlayer.score += 2;
        }

        // 턴 종료 트리거 송신하기
        currTurn.value = (currTurn.value + 1) % participants.value.length;
        // condition에서 다음 턴 or 게임 종료
        if (usedCard.value.isEnding) {
          
          // 1단계: 백그라운드로 책 표지 생성 요청 시작 (응답을 기다리지 않음)
          gameEnd(true); // await 제거 - 백그라운드 실행
          
          // 2단계: 즉시 점수 정산을 먼저 전송
          connectedPeers.value.forEach((p) => {
            if (p.id !== peerId.value && p.connection.open) {
              sendMessage("endingCardScoreUpdate", {
                scoreChange: {
                  type: "increase",
                  amount: 5, // 결말카드는 항상 +5점
                  playerIndex: currentPlayerIndex // 저장된 현재 플레이어 인덱스 사용
                }
              }, p.connection);
            }
          });
          
          // 3단계: 점수 정산 후 1초 뒤 결과창 표시
          setTimeout(() => {
            
            // 방장 결과창 표시
            isForceStopped.value = "champ";
            
            // 게스트들에게도 결과창 표시
            connectedPeers.value.forEach(async (p) => {
              if (p.id !== peerId.value && p.connection.open) {
                sendMessage("showResultsWithCover", {
                  bookCover: {
                    title: "아주 먼 옛날", // 기본값
                    imageUrl: "" // 기본값 (빈 문자열)
                  },
                  ISBN: "generating..." // 생성 중 표시
                }, p.connection);
              }
            });
          }, 1000);
        } else {
          // 다른 플레이어들에게 점수 증가 정보와 함께 nextTurn 메시지 전송
          const scoreIncrease = usedCard.value.isEnding ? 5 : 2;
          
          // 먼저 자신의 오버레이 표시
          await showOverlay('whoTurn');
          
          // 오버레이 완료 후 다른 플레이어들에게 메시지 전송
          connectedPeers.value.forEach(async (p) => {
            if (p.id !== peerId.value && p.connection.open) {
              sendMessage(
                "nextTurn",
                {
                  currTurn: currTurn.value,
                  imageDelete: false,
                  totalTurn: totalTurn.value,
                  scoreChange: {
                    type: "increase",
                    amount: scoreIncrease,
                    playerIndex: currentPlayerIndex // 저장된 현재 플레이어 인덱스 사용
                  },
                  cardRemoval: {
                    cardId: usedCard.value.id
                  }
                },
                p.connection
              )
            };
          });

          inProgress.value = true;
        }
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
            // 투표 찬성 시 사용한 카드 제거
            if (accepted) {
              storyCards.value.forEach((card, index) => {
                if (card.id === usedCard.value.id) {
                  storyCards.value.splice(index, 1);
                }
              });
            }
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
        
        return await deleteGame({
          gameId: gameID.value,
          isForceStopped: false
        }).then((res) => {
          
          if (res.data && res.data.data) {
            
            // 각 필드의 타입 체크
            
            // null/undefined 체크
            
            ISBN.value = res.data.data.bookId;
            bookCover.value.title = res.data.data.title;
            bookCover.value.imageUrl = res.data.data.bookCover;
            
          } else {
          }
        }).then(() => {
          
          // 표지 생성 완료 후 실제 표지 정보로 업데이트
          
          // 방장의 표지 정보는 이미 gameEnd 함수에서 설정됨
          // 게스트들에게 실제 표지 정보로 업데이트 메시지 전송
          
          connectedPeers.value.forEach(async (p, index) => {
            
            if (p.id !== peerId.value && p.connection.open) {
              
              try {
                sendMessage("bookCoverUpdate", {
                  bookCover: bookCover.value,
                  ISBN: ISBN.value,
                }, p.connection);
              } catch (error) {
              }
            } else {
            }
          });
        });

      } catch (error) {
        if (error.response) {
        }
        
        // 에러 발생해도 모든 플레이어에게 결과창 표시 (기본값 사용)
        
        // 기본 표지 정보 설정
        bookCover.value.title = "아주 먼 옛날";
        bookCover.value.imageUrl = "";
        
        // 방장 결과창 표시는 voteEnd 함수에서 별도로 처리됨 (에러 상황에서도)
        
        // 다른 플레이어들에게도 기본값으로 결과창 표시 명령 (에러 상황에서도)
        
        connectedPeers.value.forEach(async (p) => {
          if (p.id !== peerId.value && p.connection.open) {
            
            try {
              sendMessage("showResultsWithCover", {
                bookCover: bookCover.value, // 기본값 포함
                ISBN: ISBN.value,
              }, p.connection);
            } catch (msgError) {
            }
          }
        });
      }
    } else {
    }
    // 우승자 쇼 오버레이
    // isForceStopped.value = "champ";
  }
  
};

// 승자 표시 완료 후 나레이션 시작 (각 플레이어 개별 진행)
const onWinnerShown = () => {
  
  // 각 플레이어가 개별적으로 TTS 시작
  gameStarted.value = false;
};

// 나레이션 완료 후 승자 화면 제거 및 표지 표시 (각 플레이어 개별 진행)
const onNarrationComplete = () => {
  
  // 결과창 제거하고 표지로 전환
  isForceStopped.value = null;
  
  // GameView 내에서 표지를 표시하기 위해 상태 변경 (별도 라우팅 없음)
  nextTick(() => {
    // 표지 표시 상태를 나타내는 변수가 필요할 수 있음
    // 현재는 isForceStopped.value = null 이면 표지가 표시되는 것으로 보임
  });
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
@keyframes gentleBounce {
  0% {
    opacity: 0;
    transform: scale(0.3) translateY(-100px);
  }
  50% {
    opacity: 1;
    transform: scale(1.05) translateY(-10px);
  }
  70% {
    transform: scale(0.95) translateY(5px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.overlay {
  transition: all 1s ease-in-out;
}
</style>
