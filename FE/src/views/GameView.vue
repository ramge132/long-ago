<template>
  <div class="w-full h-full rounded-lg">
    <RouterView v-slot="{ Component }">
      <Transition name="fade" mode="out-in">
        <component ref="currentViewRef" :is="Component" :configurable="configurable" :connectedPeers="connectedPeers"
          v-model:roomConfigs="roomConfigs" :participants="participants" :receivedMessages="receivedMessages"
          :InviteLink="InviteLink" :gameStarted="gameStarted" :isEndingMode="isEndingMode" :inGameOrder="inGameOrder" :currTurn="currTurn" :ISBN="ISBN"
          :myTurn="myTurn" :peerId="peerId" :inProgress="inProgress" :bookContents="bookContents" :isElected="isElected"
          :storyCards="storyCards" :endingCard="endingCard" :prompt="prompt" :votings="votings" :percentage="percentage"
          :usedCard="usedCard" :isForceStopped="isForceStopped" :isVoted="isVoted" :bookCover="bookCover" :isPreview="isPreview"
          :gameId="gameID" @on-room-configuration="onRoomConfiguration"
          @broadcast-message="broadcastMessage" @game-start="gameStart" @game-exit="gameStarted = false" @next-turn="nextTurn"
          @card-reroll="cardReroll" @vote-end="voteEnd" @vote-selected="onVoteSelected" @go-lobby="goLobby" @winner-shown="onWinnerShown" @narration-complete="onNarrationComplete" @start-narration="onStartNarration"
          @card-refreshed="handleCardRefreshed" @send-exchange-request="handleSendExchangeRequest" @card-exchanged="handleCardExchanged" @reject-exchange="handleRejectExchange" />
      </Transition>
    </RouterView>
    <div
      class="overlay absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col justify-center items-center scale-0 opacity-0 invisible">
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

    <!-- 작은 알람 모달 (35% 및 100% 도달용) -->
    <SmallAlert
      v-if="showSmallAlert"
      :message="smallAlertMessage"
      :type="isEndingMode ? '100' : '35'"
      :duration="isEndingMode ? 5000 : 3000"
      @close="showSmallAlert = false"
    />
  </div>
</template>

<script setup>
import { createGame, createImage, deleteGame, endingCardReroll, enterGame, promptFiltering, testGame, voteResultSend, exchangeStoryCard, refreshStoryCard } from "@/apis/game";
import { currTurnImage, myTurnImage, startImage, MessageMusic, WarningIcon } from "@/assets";
import CardImage from "@/assets/cards";
import toast from "@/functions/toast";
import { useUserStore } from "@/stores/auth";
import { useGameStore } from "@/stores/game";
import { useAudioStore } from "@/stores/audio";
import SmallAlert from "@/components/Presets/SmallAlert.vue";
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
// 현재 RouterView 컴포넌트 참조
const currentViewRef = ref(null);
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
// 결말 모드 여부 (긴장감 100% 도달 시)
const isEndingMode = ref(false);
// 게임 정상 종료 : "champ" 비정상 종료 : "fail" 디폴트 : null
const isForceStopped = ref(null);
// 부적절한 콘텐츠 경고 모달 관련
const showWarningModal = ref(false);
const warningModalMessage = ref("");
// 작은 알람 모달 관련 (35% 및 100% 도달용)
const showSmallAlert = ref(false);
const smallAlertMessage = ref("");
// 35% 도달 체크용 플래그
const hasReached35Percent = ref(false);
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
// 다른 플레이어들의 카드 정보 추적 (중복 방지용)
const otherPlayersCards = ref(new Map()); // Map<userId, cardIds[]>
// 교환 횟수 로컬 상태 관리
const exchangeCount = ref(3);
// 내가 가지고있는 엔딩카드
const endingCard = ref({ id: 0, content: "" });
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
  isEnding: false,
  isFreeEnding: false
});
// 투표 거절 시 복원용 카드 정보 저장
const usedCardBackup = ref(null);
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

// ✅ 투표 통과 후 이미지 생성 대기 상태 관리
const waitingForImage = ref(false);
const currentTurnVoteResult = ref(null);

// ✅ 투표 통과 및 이미지 준비 완료 시 최종 턴 진행 함수
const processVoteSuccess = () => {
  console.log("=== processVoteSuccess 함수 시작 ===");

  if (!currentTurnVoteResult.value) {
    console.error("❌ currentTurnVoteResult가 없음");
    return;
  }

  const { accepted, player, playerIndex, scoreIncrease, wasEndingCard, wasFreeEnding } = currentTurnVoteResult.value;

  console.log("투표 통과 최종 처리 - 점수 증가:", scoreIncrease);

  // 점수 증가
  player.score += scoreIncrease;

  // 상태 초기화
  waitingForImage.value = false;
  currentTurnVoteResult.value = null;

  // usedCard 상태 초기화 (결말카드가 아닌 경우에만)
  if (!wasEndingCard) {
    usedCard.value = {
      id: 0,
      keyword: "",
      isEnding: false,
      isFreeEnding: false
    };
  }

  // 턴 진행
  if (wasEndingCard) {
    console.log("=== 결말카드 최종 처리 - 게임 종료 ===");
    gameEnd(true);

    setTimeout(() => {
      isForceStopped.value = "champ";
      connectedPeers.value.forEach(async (p) => {
        if (p.id !== peerId.value && p.connection.open) {
          sendMessage("showResultsWithCover", {
            bookCover: { title: "아주 먼 옛날", imageUrl: "" },
            ISBN: "generating..."
          }, p.connection);
        }
      });
    }, 4000);
  } else {
    console.log("=== 일반 카드 최종 처리 - 다음 턴으로 ===");
    // 다음 턴으로
    currTurn.value = (currTurn.value + 1) % participants.value.length;

    connectedPeers.value.forEach((peer) => {
      if (peer.id !== peerId.value && peer.connection.open) {
        sendMessage("nextTurn", { nextTurn: currTurn.value }, peer.connection);
      }
    });
  }

  console.log("=== processVoteSuccess 함수 완료 ===");
};

watch(isElected, (newValue) => {
  if (newValue === true) {
    console.log("🔥 isElected watch 트리거");
    console.log("🔥 pendingImage 존재:", !!pendingImage.value);
    console.log("🔥 현재 bookContents:", bookContents.value);
    console.log("🔥 마지막 항목 인덱스:", bookContents.value.length - 1);

    // ✅ 수정: 투표 통과 시 임시 이미지를 책에 추가
    if (pendingImage.value) {
      const lastIndex = bookContents.value.length - 1;
      console.log("🔥 마지막 항목에 이미지 설정:", lastIndex);

      // ✅ 첫 번째 이미지 특별 처리: 중복된 첫 번째 이야기가 있으면 첫 번째 항목에 이미지 설정
      if (bookContents.value.length >= 2 &&
          bookContents.value[0].content === bookContents.value[1].content &&
          bookContents.value[0].image === null) {
        console.log("🔥 첫 번째 이미지 특별 처리 - 첫 번째 항목에 이미지 설정");
        bookContents.value[0].image = pendingImage.value;
      } else {
        bookContents.value[lastIndex].image = pendingImage.value;
      }

      console.log("✅ isElected watch: 임시 이미지를 책에 등록");
      console.log("🔥 업데이트 후 bookContents:", bookContents.value);
      pendingImage.value = null; // 임시 이미지 초기화
    } else {
      console.log("❌ pendingImage가 없음 - 이미지 도착 대기 중...");

      // ✅ 수정: pendingImage가 없을 때 최대 3초 대기
      let waitCount = 0;
      const maxWaitTime = 30; // 3초 (100ms * 30)

      const waitForImage = () => {
        if (pendingImage.value) {
          console.log("✅ 대기 중 이미지 도착 - 책에 추가");
          const lastIndex = bookContents.value.length - 1;

          // 첫 번째 이미지 특별 처리
          if (bookContents.value.length >= 2 &&
              bookContents.value[0].content === bookContents.value[1].content &&
              bookContents.value[0].image === null) {
            console.log("🔥 대기 후 첫 번째 이미지 특별 처리");
            bookContents.value[0].image = pendingImage.value;
          } else {
            bookContents.value[lastIndex].image = pendingImage.value;
          }

          pendingImage.value = null;
          return;
        }

        waitCount++;
        if (waitCount < maxWaitTime) {
          setTimeout(waitForImage, 100);
        } else {
          console.log("⏰ 이미지 대기 시간 초과 - 투표 부결 처리 시작");

          // ✅ 핵심 수정: 이미지 대기 시간 초과 시 투표 부결과 동일한 처리
          isElected.value = false; // isElected 상태 리셋

          if (currTurn.value === myTurn.value) {
            const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];

            // 1. 점수 차감 (투표 부결과 동일)
            currentPlayer.score -= 1;
            console.log(`이미지 대기 초과 - 점수 차감: ${currentPlayer.name} (${currentPlayer.score})`);

            // 2. 카드 복원 (투표 부결과 동일)
            if (usedCardBackup.value && !usedCard.value.isFreeEnding) {
              storyCards.value.push(usedCardBackup.value);
              console.log(`이미지 대기 초과 - 카드 복원: ID ${usedCardBackup.value.id}, keyword: ${usedCardBackup.value.keyword}`);

              // 복원된 카드 정보를 다른 플레이어들에게 전송
              const myCardIds = storyCards.value.map(card => card.id);
              connectedPeers.value.forEach((peer) => {
                if (peer.connection && peer.connection.open) {
                  sendMessage("playerCardsSync", {
                    userId: peerId.value,
                    cardIds: myCardIds
                  }, peer.connection);
                }
              });
            }

            // 3. 책 내용 제거 (투표 부결과 동일)
            if (bookContents.value.length === 1) {
              bookContents.value = [{ content: "", image: null }];
            } else {
              bookContents.value = bookContents.value.slice(0, -1);
            }

            // 4. 상태 초기화
            usedCardBackup.value = null;
            usedCard.value = {
              id: 0,
              keyword: "",
              isEnding: false,
              isFreeEnding: false
            };

            // 5. 다음 턴으로 진행
            currTurn.value = (currTurn.value + 1) % participants.value.length;

            // 6. 다른 플레이어들에게 알림
            connectedPeers.value.forEach((peer) => {
              if (peer.id !== peerId.value && peer.connection.open) {
                sendMessage("nextTurn", {
                  currTurn: currTurn.value,
                  imageDelete: true,
                  totalTurn: totalTurn.value,
                  scoreChange: {
                    type: "decrease",
                    amount: 1,
                    playerIndex: inGameOrder.value[currTurn.value === 0 ? participants.value.length - 1 : currTurn.value - 1]
                  },
                  reason: "이미지 대기 시간 초과"
                }, peer.connection);
              }
            });

            console.log("⏰ 이미지 대기 시간 초과 - 투표 부결 처리 완료");
          }
        }
      };

      setTimeout(waitForImage, 100);
    }

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
// 투표 대기 중인 임시 이미지 저장
const pendingImage = ref(null);
// 게임 종료 애니메이션
watch(isForceStopped, (newValue) => {
  if (newValue !== null) {
    setTimeout(() => {
      isForceStopped.value = null;
    }, 6000);
  }
});

// 긴장감 퍼센트 (결말카드는 제외)
const percentage = computed(() => {
  if (bookContents.value.length == 1 && bookContents.value[0].content == "") {
    return 0
  } else {
    // 결말카드는 긴장감 계산에서 제외
    const nonEndingContents = bookContents.value.filter((content, index) => {
      // 첫 번째는 빈 content이므로 제외, 마지막이 결말카드인 경우 제외
      if (index === 0 && content.content === "") return false;
      // 현재 마지막 콘텐츠가 결말카드인지 확인 (usedCard.isEnding으로 판단)
      if (index === bookContents.value.length - 1 && usedCard.value.isEnding) return false;
      return true;
    });
    return Math.round((nonEndingContents.length / (participants.value.length * 3)) * 100)
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
    // 모든 P2P 메시지 수신 로그
    if (data.type === "storyCardExchangeRequest" || data.type === "storyCardExchangeResponse") {
      console.log(`🔄 P2P 메시지 수신 [${data.type}]:`, data);
    }

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

      case "endingModeActivated":
        // 결말 모드로 전환
        isEndingMode.value = true;
        // 작은 알림 표시 (100% 타입)
        smallAlertMessage.value = "긴장감이 100%에 도달했습니다!\n이제 결말을 맺어야 할 때입니다!";
        showSmallAlert.value = true;
        break;

      case "endingCardAvailable":
        // 결말카드 사용 가능 알림 (35% 도달)
        smallAlertMessage.value = "긴장감이 35%에 도달했습니다";
        showSmallAlert.value = true;
        break;

      case "scoreUpdate":
        // 다른 플레이어의 점수 변화 처리
        const targetPlayer = participants.value.find(p => p.id === data.userId);
        if (targetPlayer) {
          targetPlayer.score += data.scoreChange;
          // 점수 변화 적용 완료
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

      case "startLoading":
        emit("startLoading", data);
        break;

      case "gameStart":
        isPreview.value = data.isPreview;
        // 게임 관련 데이터 초기화 (게스트용)
        participants.value = data.participants;
        receivedMessages.value = [];
        currTurn.value = 0;
        totalTurn.value = 1;
        bookContents.value = [{ content: "", image: null }];
        bookCover.value = {title: "", imageUrl: ""};
        ISBN.value = "";
        votings.value = [];
        myTurn.value = null;
        inProgress.value = false;
        inGameOrder.value = [];
        isForceStopped.value = null;
        isEndingMode.value = false;
        hasReached35Percent.value = false;
        usedCard.value = {
          id: 0,
          keyword: "",
          isEnding: false,
          isFreeEnding: false
        };

        // 투표 관련 초기화 (게스트용)
        isElected.value = false;
        isVoted.value = false;
        currentVoteSelection.value = "up";
        usedCardBackup.value = null;
        pendingImage.value = null;

        // 프롬프트 초기화 (게스트용)
        prompt.value = "";

        // 교환 시스템 초기화 (게스트용)
        otherPlayersCards.value = new Map();
        isExchangeProcessing.value = false;
        cardExchangeStatus.value = new Map();
        exchangeDebounceTimers.value = new Map();

        // 알림/모달 상태 초기화 (게스트용)
        showWarningModal.value = false;
        warningModalMessage.value = "";
        showSmallAlert.value = false;
        smallAlertMessage.value = "";

        // 로딩 애니메이션 활성화
        emit("startLoading", {value: true});

        startReceived(data).then(async () => {
          try {
            // 1. 내 카드 받기
            const response = await enterGame({
              userId: peerId.value,
              gameId: gameID.value,
            });

            storyCards.value = response.data.data.storyCards;
            endingCard.value = response.data.data.endingCard;

            // InGameControl의 refreshCount 초기화
            if (currentViewRef.value && currentViewRef.value.updateCounts) {
              const playerStatus = response.data.data;
              currentViewRef.value.updateCounts(playerStatus.refreshCount, playerStatus.exchangeCount);
            }

            // 2. 내 카드 정보 추출
            const storyCardIds = storyCards.value.map(card => card.id);
            const endingCardId = endingCard.value.id;

            console.log('🎯 게스트 카드 이미지 프리로딩 시작...', {
              storyCards: storyCardIds,
              endingCard: endingCardId
            });

            // 3. 모든 카드 이미지 프리로드 완료까지 대기
            await CardImage.preloadPlayerCards(storyCardIds, endingCardId);

            console.log('✅ 게스트 모든 카드 이미지 프리로딩 완료!');

            // 4. 게임 화면으로 전환
            await router.push("/game/play");

            // 5. 로딩 화면 종료
            emit("startLoading", {value: false});

            // 6. 오버레이 표시
            await showOverlay('start');
            setTimeout(() => {
              showOverlay('whoTurn').then(() => {
                inProgress.value = true;
              });
            }, 500);

          } catch (error) {
            console.error('❌ 게스트 카드 프리로딩 실패:', error);
            // 에러가 발생해도 게임은 계속 진행
            await router.push("/game/play");
            emit("startLoading", {value: false});
          }
        });
        break;

      case "nextTurn":
        // 먼저 모든 상태 업데이트를 완료한 후 오버레이 표시
        
        // 1. 책 내용 삭제 (투표 거부 시)
        if (data.imageDelete === true) {
          console.log("투표 거절로 인한 책 내용 삭제 처리");
          console.log("삭제 전 책 내용:", bookContents.value);

          // 투표 반대로 인한 삭제 시 임시 이미지도 함께 삭제
          if (pendingImage.value) {
            console.log("nextTurn: 투표 반대로 임시 이미지 삭제");
            pendingImage.value = null;
          }

          if (data.voteRejected && data.rejectedPrompt) {
            console.log("거절된 이야기:", data.rejectedPrompt);

            // 거절된 이야기와 일치하는 항목을 찾아서 제거
            const rejectedIndex = bookContents.value.findIndex(content =>
              content.content === data.rejectedPrompt
            );

            if (rejectedIndex !== -1) {
              console.log(`거절된 이야기 찾음 - 인덱스: ${rejectedIndex}`);
              bookContents.value.splice(rejectedIndex, 1);

              // 만약 모든 내용이 제거되었다면 빈 항목 추가
              if (bookContents.value.length === 0) {
                bookContents.value = [{ content: "", image: null }];
              }
            } else {
              console.log("거절된 이야기를 찾을 수 없음 - 기본 제거 로직 사용");
              // 기본 로직: 마지막 항목 제거
              if (bookContents.value.length === 1) {
                bookContents.value = [{ content: "", image: null }];
              } else {
                bookContents.value = bookContents.value.slice(0, -1);
              }
            }
          } else {
            // 기본 로직: 마지막 항목 제거
            if (bookContents.value.length === 1) {
              bookContents.value = [{ content: "", image: null }];
            } else {
              bookContents.value = bookContents.value.slice(0, -1);
            }
          }

          console.log("삭제 후 책 내용:", bookContents.value);
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

        // 4.5. 결말 상태 리셋 처리 (결말카드 투표 반대 시)
        if (data.resetEndingState) {
          isEndingMode.value = false;
          usedCard.value = {
            id: 0,
            keyword: "",
            isEnding: false,
            isFreeEnding: false
          };
          console.log("다른 플레이어로부터 결말상태 리셋 수신");
        }

        // 5. 턴 정보 업데이트
        totalTurn.value = data.totalTurn;
        currTurn.value = data.currTurn;
        
        // 6. 상태 업데이트 후 오버레이 표시
        inProgress.value = false;
        await showOverlay('whoTurn', {
          turnIndex: data.currTurn,
          participants: participants.value,
          inGameOrder: inGameOrder.value,
          peerId: peerId.value
        });
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
        // 기존 타이머들 모두 정리 (오버레이 타이머 포함)
        if (voteTimer) {
          clearTimeout(voteTimer);
          voteTimer = null;
        }
        if (warningTimer) {
          clearTimeout(warningTimer);
          warningTimer = null;
        }
        if (overlayTimeout.value) {
          clearTimeout(overlayTimeout.value);
          overlayTimeout.value = null;
          // 오버레이를 즉시 숨김
          const overlay = document.querySelector(".overlay");
          if (overlay) {
            overlay.classList.add('scale-0');
            overlay.style.opacity = '0';
            overlay.style.visibility = 'hidden';
          }
        }
        
        // 완전한 상태 초기화
        usedCard.value = data.usedCard;
        prompt.value = data.prompt;
        inProgress.value = false;
        isVoted.value = false; // 새로운 투표를 위해 초기화
        currentVoteSelection.value = "up"; // 투표 선택값을 찬성으로 초기화
        votings.value = []; // 투표 배열 완전 초기화
        isElected.value = false; // 선출 상태 초기화
        
        // 책 콘텐츠 추가
        addBookContent({ content: data.prompt, image: null });
        
        // 새로운 투표 타이머 설정
        voteTimer = setTimeout(async () => {
          if(!isVoted.value) {
            await voteEnd({
              sender: userStore.userData.userNickname,
              selected: currentVoteSelection.value,
            });
          }
          isVoted.value = false;
        }, 10000);  // 투표 시간 10초로 설정
        break;

      case "sendImage":
        const receivedArrayBuffer = data.imageBlob;
        const receivedBlob = new Blob([receivedArrayBuffer]);
        const imageBlob = URL.createObjectURL(receivedBlob);
        // 즉시 책에 추가하지 않고 투표 결과까지 임시 저장
        pendingImage.value = imageBlob;
        console.log("📷 다른 플레이어로부터 이미지 수신");
        console.log("📷 현재 투표 수:", votings.value.length, "/ 필요 수:", participants.value.length);

        // ✅ 수정: 이미지 수신 후 투표가 이미 완료되었다면 즉시 isElected 트리거
        if (votings.value.length === participants.value.length) {
          console.log("📷 투표 이미 완료됨 - 즉시 isElected 트리거");
          const upCount = votings.value.filter(v => v.selected === 'up').length;
          const downCount = votings.value.filter(v => v.selected === 'down').length;
          const voteAccepted = upCount >= downCount;

          if (voteAccepted) {
            console.log("📷 투표 통과 확인 - isElected 설정");
            isElected.value = true;
          }
        } else {
          console.log("📷 투표 결과 대기 중");
        }
        break;

      case "warningNotification":
        showInappropriateWarningModal(data);
        break;

      case "stopVotingAndShowWarning":
        stopVotingAndShowWarning(data);
        break;

      case "voteResult":
        console.log("=== voteResult 메시지 수신 ===");
        console.log("수신된 투표:", data);
        console.log("현재 votings:", votings.value);

        // 투표 배열에 추가 전 중복 체크
        const voteExists = votings.value.some(v => v.sender === data.sender);
        console.log("투표 중복 여부:", voteExists);

        if (!voteExists) {
          votings.value = [...votings.value, {sender: data.sender, selected: data.selected}];
          console.log("투표 추가 완료, 새로운 votings:", votings.value);
        }

        console.log("전체 투표 수:", votings.value.length, "/ 필요 수:", participants.value.length);

        if (votings.value.length == participants.value.length) {
          console.log("=== 모든 투표 수집 완료, 결과 처리 ===");

          let upCount = 0;
          let downCount = 0;
          votings.value.forEach((vote) => {
            if (vote.selected == 'up') upCount++;
            else downCount++;
          });

          console.log("찬성:", upCount, "반대:", downCount);

          const voteAccepted = upCount >= downCount;
          console.log("투표 결과:", voteAccepted ? "통과" : "거절");
          
          // 모든 플레이어가 동일한 투표 결과 처리
          const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
          const currentPlayerIndex = inGameOrder.value[currTurn.value];

          let accepted = voteAccepted;
          if (accepted) {
            // ✅ 수정: pendingImage가 있을 때만 isElected 설정
            if (pendingImage.value) {
              console.log("✅ pendingImage 존재 - isElected 설정");
              isElected.value = true;
            } else {
              console.log("⏳ pendingImage 대기 중 - isElected 설정 보류");
            }
          }

          // 현재 턴 플레이어만 점수 및 턴 전환 처리
          if (currTurn.value === myTurn.value) {
            if (accepted) {
              console.log("=== voteResult 케이스에서 투표 통과 처리 시작 ===");
              const wasEndingCard = usedCard.value.isEnding;
              const scoreIncrease = wasEndingCard ?
                (usedCard.value.isFreeEnding ? 3 : 5) : 2;
              const wasFreeEnding = usedCard.value.isFreeEnding;

              // ✅ 핵심 수정: voteResult 케이스에도 이미지 대기 로직 적용
              currentTurnVoteResult.value = {
                accepted: true,
                player: currentPlayer,
                playerIndex: currentPlayerIndex,
                scoreIncrease: scoreIncrease,
                wasEndingCard: wasEndingCard,
                wasFreeEnding: wasFreeEnding
              };

              console.log("voteResult - 투표 결과 저장:", currentTurnVoteResult.value);

              // 이미지가 이미 준비되어 있는지 확인
              if (pendingImage.value) {
                console.log("=== voteResult - 이미지 이미 준비됨 - 즉시 진행 ===");
                processVoteSuccess();
              } else {
                console.log("=== voteResult - 이미지 대기 상태로 전환 ===");
                waitingForImage.value = true;

                // 다른 플레이어들에게 대기 상태 알림
                connectedPeers.value.forEach((peer) => {
                  if (peer.id !== peerId.value && peer.connection.open) {
                    sendMessage("waitingForImage", {
                      message: "이미지 생성 중...",
                      playerName: currentPlayer.name
                    }, peer.connection);
                  }
                });
              }

              // 결말카드는 이미지 대기 없이 즉시 처리
              if (wasEndingCard) {
                console.log("=== voteResult - 결말카드 - 즉시 처리 ===");
                processVoteSuccess();
              }
              // ✅ voteResult 케이스의 투표 통과 처리는 processVoteSuccess()가 담당
            } else {
              accepted = false;
              console.log("=== 투표 거절 처리 시작 ===");

              // ✅ 수정: 투표 거절 시 pendingImage 정리
              if (pendingImage.value) {
                console.log("현재 턴 플레이어: 투표 거절 - pendingImage 정리");
                pendingImage.value = null;
              }

              // ✅ 수정: 투표 거절 시 사용된 카드를 패에 복원
              if (usedCardBackup.value && !usedCard.value.isFreeEnding) {
                storyCards.value.push(usedCardBackup.value);
                console.log(`투표 거절로 카드 복원: ID ${usedCardBackup.value.id}, keyword: ${usedCardBackup.value.keyword}`);
              } else {
                console.log("카드 복원 불가:", {
                  hasBackup: !!usedCardBackup.value,
                  isFreeEnding: usedCard.value.isFreeEnding
                });
              }

              // 백업 정보 및 usedCard 상태 초기화
              usedCardBackup.value = null;
              usedCard.value = {
                id: 0,
                keyword: "",
                isEnding: false,
                isFreeEnding: false
              };

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

              if (bookContents.value.length === 1) {
                bookContents.value = [{ content: "", image: null }];
              } else {
                bookContents.value = bookContents.value.slice(0, -1);
              }

              currentPlayer.score -= 1;

              await showOverlay('whoTurn');
              inProgress.value = true;
            }
      try {
          const response = await voteResultSend({
            gameId: gameID.value,
            userId: peerId.value,
            accepted: accepted,
            cardId: usedCard.value.id,
          });
          if (response.status === 200) {
          }
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
            // ✅ 수정: 게스트 플레이어 처리
            if (voteAccepted) {
              if (usedCard.value.isEnding && participants.value[0].id === peerId.value) {
                gameEnd(true);

                setTimeout(() => {
                  isForceStopped.value = "champ";
                  connectedPeers.value.forEach(async (p) => {
                    if (p.id !== peerId.value && p.connection.open) {
                      sendMessage("showResultsWithCover", {
                        bookCover: { title: "아주 먼 옛날", imageUrl: "" },
                        ISBN: "generating..."
                      }, p.connection);
                    }
                  });
                }, 4000); // 2초 → 4초로 변경하여 이미지 적용된 페이지를 충분히 보여줌
              } else {
                // ✅ 수정: 게스트 플레이어도 nextTurn 메시지 대기 (현재 턴 플레이어가 보낼 것임)
                console.log("게스트 플레이어 - nextTurn 메시지 대기 중");
              }
            } else {
              // ✅ 수정: 게스트 플레이어도 투표 거절 시 카드 복원
              console.log("게스트 플레이어 - 투표 거절 처리");

              // ✅ 수정: 투표 거절 시 pendingImage 정리
              if (pendingImage.value) {
                console.log("게스트 플레이어: 투표 거절 - pendingImage 정리");
                pendingImage.value = null;
              }

              // 투표 거절 시 사용된 카드를 패에 복원
              if (usedCardBackup.value && !usedCard.value.isFreeEnding) {
                storyCards.value.push(usedCardBackup.value);
                console.log(`게스트: 투표 거절로 카드 복원: ID ${usedCardBackup.value.id}, keyword: ${usedCardBackup.value.keyword}`);
              }

              // 백업 정보 및 usedCard 상태 초기화
              usedCardBackup.value = null;
              usedCard.value = {
                id: 0,
                keyword: "",
                isEnding: false,
                isFreeEnding: false
              };

              console.log("게스트 플레이어 - nextTurn 메시지 대기 중");
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
        // 결말카드 점수 정산 처리
        if (data.scoreChange) {
          const targetPlayer = participants.value[data.scoreChange.playerIndex];
          if (targetPlayer) {
            if (data.scoreChange.type === "increase") {
              targetPlayer.score += data.scoreChange.amount;
              // 결말카드 점수 증가 처리
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
        // 결과창 표시 (점수 정산은 이미 완료됨)
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

      case "playerCardsSync":
        // 다른 플레이어의 카드 정보 동기화
        if (data.userId !== peerId.value) {
          otherPlayersCards.value.set(data.userId, data.cardIds);
          console.log(`플레이어 ${data.userId}의 카드 정보 동기화:`, data.cardIds);
        }
        break;

      case "storyCardRefreshed":
        // 다른 플레이어의 카드 새로고침 동기화
        if (data.userId !== peerId.value) {
          // 다른 플레이어의 카드 목록 업데이트
          const playerCards = otherPlayersCards.value.get(data.userId);
          if (playerCards) {
            const cardIndex = playerCards.findIndex(cardId => cardId === data.oldCard.id);
            if (cardIndex !== -1) {
              playerCards[cardIndex] = data.newCard.id;
            }
          }

          // 다른 플레이어의 새로운 카드 이미지 프리로딩
          try {
            const newCardImageUrl = CardImage.getStoryCardImage(data.newCard.id);
            console.log(`🎯 다른 플레이어 새로고침 카드 이미지 프리로딩: ${data.newCard.keyword} (ID: ${data.newCard.id})`);

            const img = new Image();
            img.onload = () => {
              console.log(`✅ 다른 플레이어 새로고침 카드 이미지 로드 완료: ${data.newCard.keyword}`);
            };
            img.onerror = () => {
              console.warn(`❌ 다른 플레이어 새로고침 카드 이미지 로드 실패: ${data.newCard.keyword}`);
            };
            img.src = newCardImageUrl;
          } catch (error) {
            console.warn(`❌ 다른 플레이어 새로고침 카드 이미지 프리로딩 중 오류: ${data.newCard.keyword}`, error);
          }
        }
        break;

      case "storyCardExchangeRequest":
        console.log("=== 교환 신청 수신 처리 시작 ===");
        console.log("1. 수신한 data:", data);

        const exchangeRequestData = {
          senderName: data.fromUserName,
          senderCard: data.fromCard,
          fromUserId: data.fromUserId,
          toUserId: data.toUserId,
          fromCardId: data.fromCardId
        };
        console.log("2. 교환 요청 데이터:", exchangeRequestData);
        console.log("3. currentViewRef.value:", currentViewRef.value);

        // InGameView 컴포넌트의 showExchangeRequest 함수 직접 호출
        if (currentViewRef.value && currentViewRef.value.showExchangeRequest) {
          console.log("4. InGameView의 showExchangeRequest 함수 호출");
          currentViewRef.value.showExchangeRequest(exchangeRequestData);
        } else {
          console.log("4. ERROR: currentViewRef나 showExchangeRequest 함수를 찾을 수 없음");
          console.log("   - currentViewRef.value:", currentViewRef.value);
          console.log("   - showExchangeRequest 함수:", currentViewRef.value?.showExchangeRequest);

          // 대안: 전역 이벤트 발송
          console.log("   - 대안: 전역 이벤트 발송");
          window.dispatchEvent(new CustomEvent('showExchangeRequest', {
            detail: exchangeRequestData
          }));
        }
        console.log("=== 교환 신청 수신 처리 끝 ===");
        break;

      case "storyCardExchangeResponse":
        console.log("=== 교환 응답 수신 처리 시작 (신청자) ===");
        console.log("1. 받은 데이터:", data);
        console.log("2. 교환 전 내 카드 목록:", storyCards.value.map(c => ({id: c.id, keyword: c.keyword})));

        if (data.accepted) {
          // 교환 성공 - 신청자도 교환 횟수 차감 (로컬 상태 기반)
          console.log("2-1. 신청자 교환 성공 - exchangeCount 차감");
          if (currentViewRef.value && currentViewRef.value.updateCounts) {
            // 로컬 상태에서 1 차감
            exchangeCount.value = Math.max(0, exchangeCount.value - 1);
            console.log(`2-2. 신청자 exchangeCount 업데이트: ${exchangeCount.value + 1} → ${exchangeCount.value}`);
            currentViewRef.value.updateCounts(null, exchangeCount.value);
          }

          // 교환 성공 - 신청자 쪽에서 카드 교체
          const fromCardIndex = storyCards.value.findIndex(card => card.id === data.fromCardId);
          console.log("3. fromCardIndex (내가 보낸 카드):", fromCardIndex);
          console.log("4. 받을 카드 데이터:", data.toCard);

          if (fromCardIndex !== -1) {
            console.log("5. 교환 전 내 카드:", storyCards.value[fromCardIndex]);
            // 신청자의 카드를 수락자의 카드로 교체
            storyCards.value[fromCardIndex] = data.toCard;
            console.log("6. 교환 후 내 카드:", storyCards.value[fromCardIndex]);
          } else {
            console.log("5. ERROR: fromCardIndex를 찾을 수 없음");
          }

          console.log("7. 교환 후 내 카드 목록:", storyCards.value.map(c => ({id: c.id, keyword: c.keyword})));
          toast.successToast("카드 교환이 완료되었습니다!");

          // 교환받은 카드 이미지 프리로딩 (신청자)
          try {
            const receivedCardImageUrl = CardImage.getStoryCardImage(data.toCard.id);
            console.log(`🎯 교환받은 카드 이미지 프리로딩 (신청자): ${data.toCard.keyword} (ID: ${data.toCard.id})`);

            const img = new Image();
            img.onload = () => {
              console.log(`✅ 교환받은 카드 이미지 로드 완료 (신청자): ${data.toCard.keyword}`);
            };
            img.onerror = () => {
              console.warn(`❌ 교환받은 카드 이미지 로드 실패 (신청자): ${data.toCard.keyword}`);
            };
            img.src = receivedCardImageUrl;
          } catch (error) {
            console.warn(`❌ 교환받은 카드 이미지 프리로딩 중 오류 (신청자): ${data.toCard.keyword}`, error);
          }

          // 교환 완료 후 내 카드 정보 업데이트 (다른 플레이어들에게 전송)
          const myCardIds = storyCards.value.map(card => card.id);
          connectedPeers.value.forEach((peer) => {
            if (peer.connection && peer.connection.open) {
              sendMessage("playerCardsSync", {
                userId: peerId.value,
                cardIds: myCardIds
              }, peer.connection);
            }
          });

          // 교환 완료 시 pending 상태 해제
          if (currentViewRef.value && currentViewRef.value.clearPendingExchange) {
            currentViewRef.value.clearPendingExchange(data.fromCardId);
          }

          // 교환 성공 시 카드 상태 완전 초기화
          console.log("📋 교환 성공 - 카드 상태 완전 초기화");
          setCardExchangeStatus(data.fromCardId, EXCHANGE_STATUS.IDLE);
          setCardExchangeStatus(data.toCard.id, EXCHANGE_STATUS.IDLE);

          // 혹시 남아있을 수 있는 잘못된 상태들 정리
          cardExchangeStatus.value.forEach((status, cardId) => {
            if (status !== EXCHANGE_STATUS.IDLE &&
                (cardId === data.fromCardId || cardId === data.toCard.id)) {
              console.log(`📋 잔여 상태 정리: 카드 ${cardId} ${status} → idle`);
              cardExchangeStatus.value.set(cardId, EXCHANGE_STATUS.IDLE);
            }
          });
        } else {
          console.log("3. 교환 거절됨");

          // 교환 거절 시에도 신청자는 exchangeCount 차감 (시도 비용)
          console.log("3-1. 신청자 교환 거절 - exchangeCount 차감");
          if (currentViewRef.value && currentViewRef.value.updateCounts) {
            // 로컬 상태에서 1 차감
            exchangeCount.value = Math.max(0, exchangeCount.value - 1);
            console.log(`3-2. 신청자 교환 거절 시 exchangeCount 업데이트: ${exchangeCount.value + 1} → ${exchangeCount.value}`);
            currentViewRef.value.updateCounts(null, exchangeCount.value);
          }

          toast.errorToast("상대방이 교환을 거절했습니다.");

          // 교환 거절 시에도 pending 상태 해제
          if (currentViewRef.value && currentViewRef.value.clearPendingExchange) {
            currentViewRef.value.clearPendingExchange(data.fromCardId);
          }

          // 교환 거절 시 카드 상태 초기화
          setCardExchangeStatus(data.fromCardId, EXCHANGE_STATUS.IDLE);
        }
        console.log("=== 교환 응답 수신 처리 끝 (신청자) ===");
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
  // 투표 중단 및 경고 표시 함수 시작
  
  // 모든 타이머 즉시 정리 (오버레이 타이머 포함)
  if (voteTimer) {
    // voteTimer 정리
    clearTimeout(voteTimer);
    voteTimer = null;
  }
  if (warningTimer) {
    // warningTimer 정리
    clearTimeout(warningTimer);
    warningTimer = null;
  }
  if (overlayTimeout.value) {
    // 기존 overlayTimeout 정리 (애니메이션 중단)
    clearTimeout(overlayTimeout.value);
    overlayTimeout.value = null;
    // 오버레이를 즉시 숨김
    const overlay = document.querySelector(".overlay");
    if (overlay) {
      overlay.classList.add('scale-0');
      overlay.style.opacity = '0';
      overlay.style.visibility = 'hidden';
    }
  }
  
  // 1. 투표 즉시 중단 (InGameView에서 투표 UI 숨김)
  // 투표 UI 중단 처리
  inProgress.value = false;
  
  // 버그 수정: isVoted를 true로 설정하지 않음
  // 대신 임시 플래그를 사용하여 투표 UI를 숨김
  const wasVotingActive = !isVoted.value; // 현재 투표가 활성화되어 있었는지 기록
  // 투표가 활성화되어 있었는지 기록
  
  // 투표 UI를 숨기기 위해 prompt를 초기화 (isVoted는 건드리지 않음)
  prompt.value = "";     // 프롬프트 초기화하여 투표 UI 제거
  isElected.value = false; // 선출 상태도 초기화
  
  // 투표 관련 상태 완전 초기화
  votings.value = [];
  usedCard.value = {
    id: 0,
    keyword: "",
    isEnding: false,
    isFreeEnding: false
  };
  currentVoteSelection.value = "up"; // 투표 선택값 초기화
  
  // 투표 상태 초기화 완료
  // isVoted 상태 변경 안함
  // prompt 초기화
  // votings 초기화
  
  
  // 2. 점수 동기화 (다른 플레이어들)
  // 점수 동기화 처리
  if (data.isInappropriate && !data.skipScoreDeduction) {
    const affectedPlayerIndex = data.currTurn === 0 ? participants.value.length - 1 : data.currTurn - 1;
    const affectedPlayer = participants.value[inGameOrder.value[affectedPlayerIndex]];
    if (affectedPlayer) {
      // 점수 1점 차감
      affectedPlayer.score -= 1;
    }
  } else if (data.skipScoreDeduction) {
    // 점수 차감 건너뜀 (이미 처리됨)
  }
  
  // 3. 책 내용 제거 (중복 제거 방지)
  // 책 내용 제거 처리
  if (data.imageDelete === true && !data.skipBookContentRemoval) {
    const beforeLength = bookContents.value.length;
    if (bookContents.value.length === 1) {
      bookContents.value = [{ content: "", image: null }];
    } else {
      bookContents.value = bookContents.value.slice(0, -1);
    }
    // 책 페이지 제거
  } else if (data.skipBookContentRemoval) {
    // 책 내용 제거 건너뜀 (이미 처리됨)
  }
  
  // 4. 경고 모달 표시
  // 경고 모달 표시
  showInappropriateWarningModal(data.warningData);
  
  // 5. 턴 정보 업데이트
  // 턴 정보 업데이트
  // 총 턴 수 업데이트
  // 현재 턴 업데이트
  totalTurn.value = data.totalTurn;
  currTurn.value = data.currTurn;
  
  // 6. isVoted 상태를 즉시 false로 리셋 (버그 수정)
  // isVoted 상태 즉시 리셋
  isVoted.value = false;  // 다음 투표를 위해 즉시 리셋
  // isVoted를 false로 설정 완료
  
  // 7. 3초 후 whoTurn 오버레이 표시 (경고 모달이 먼저 표시된 후)
  // warningTimer 설정 (3초 후 whoTurn 오버레이)
  warningTimer = setTimeout(async () => {
    // warningTimer 타이머 실행
    
    // 타이머 실행 시점에 새로운 투표가 시작되었는지 확인
    if (prompt.value !== "" || voteTimer !== null) {
      // 새로운 투표가 이미 시작됨, whoTurn 오버레이 건너뜀
      warningTimer = null;
      return;
    }
    
    // whoTurn 오버레이 표시
    await showOverlay('whoTurn');
    
    // 다음 턴을 위한 상태 확인 (이미 false로 설정되어 있어야 함)
    // 현재 isVoted 상태 확인
    // 현재 투표 선택값 확인
    
    currentVoteSelection.value = "up"; // 투표 선택값 초기화
    inProgress.value = true; // 다음 턴 대기 상태
    
    warningTimer = null; // 타이머 완료 후 null로 설정
    // warningTimer 완료
  }, 3000);  // 경고 모달이 표시되는 시간과 동일
  
  // stopVotingAndShowWarning 함수 종료
  
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
  // 교환 관련 정리
  console.log("🧹 컴포넌트 정리 시작 - 교환 상태 및 타이머 정리");

  // 모든 교환 디바운스 타이머 정리
  exchangeDebounceTimers.value.forEach((timer, cardId) => {
    clearTimeout(timer);
    console.log(`⏰ 교환 타이머 정리: 카드 ${cardId}`);
  });
  exchangeDebounceTimers.value.clear();

  // 모든 카드 교환 상태 초기화
  cardExchangeStatus.value.clear();

  // 전역 교환 처리 플래그 초기화
  isExchangeProcessing.value = false;

  console.log("✅ 교환 관련 정리 완료");

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
  // 🚀 즉시 모든 플레이어에게 로딩 시작 신호 전송
  emit("startLoading", {value: true}); // 방장 로딩 시작

  // 게스트들에게도 즉시 로딩 시작 신호 전송
  connectedPeers.value.forEach((peer) => {
    if (peer.connection.open) {
      sendMessage("startLoading", {value: true}, peer.connection);
    }
  });

  // 게임 관련 데이터 초기화
  receivedMessages.value = [];
  currTurn.value = 0;
  totalTurn.value = 1;
  bookContents.value = [{ content: "", image: null }];
  bookCover.value = {title: "", imageUrl: ""};
  ISBN.value = "";
  votings.value = [];
  myTurn.value = null;
  inProgress.value = false;
  inGameOrder.value = [];
  isForceStopped.value = null;
  isEndingMode.value = false;
  hasReached35Percent.value = false;
  participants.value.forEach((participant) => {
    participant.score = 10;
  })
  usedCard.value = {
    id: 0,
    keyword: "",
    isEnding: false,
    isFreeEnding: false
  };

  // 투표 관련 초기화
  isElected.value = false;
  isVoted.value = false;
  currentVoteSelection.value = "up";
  usedCardBackup.value = null;
  pendingImage.value = null;

  // 프롬프트 초기화
  prompt.value = "";

  // 교환 시스템 초기화
  otherPlayersCards.value = new Map();
  isExchangeProcessing.value = false;
  cardExchangeStatus.value = new Map();
  exchangeDebounceTimers.value = new Map();

  // 알림/모달 상태 초기화
  showWarningModal.value = false;
  warningModalMessage.value = "";
  showSmallAlert.value = false;
  smallAlertMessage.value = "";

  // 시연 모드 확인
  isPreview.value = data.isPreview;

  // 엔딩카드 이미지 프리로딩 시작 (백그라운드에서)
  CardImage.preloadAllEndingCards().then(() => {
    // 모든 엔딩카드 이미지 프리로드 성공
  }).catch((error) => {
    // 일부 엔딩카드 이미지 프리로드 실패
  });

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

      // InGameControl의 refreshCount 초기화 (방장용)
      if (currentViewRef.value && currentViewRef.value.updateCounts) {
        const playerStatus = response.data.data.status;
        currentViewRef.value.updateCounts(playerStatus.refreshCount, playerStatus.exchangeCount);
      }
    } catch (error) {
      // 에러 처리
    }
  }

  gameStarted.value = data.gameStarted;
  inGameOrder.value = data.order;

  // 게임 시작 시 교환 횟수 초기화
  exchangeCount.value = 3;
  
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

  // 게임 시작 후 내 카드 정보를 다른 플레이어들에게 공유
  setTimeout(() => {
    const myCardIds = storyCards.value.map(card => card.id);
    connectedPeers.value.forEach((peer) => {
      if (peer.connection && peer.connection.open) {
        sendMessage("playerCardsSync", {
          userId: peerId.value,
          cardIds: myCardIds
        }, peer.connection);
      }
    });
  }, 1000); // 게임 시작 1초 후 카드 정보 동기화
  
  // myTurn을 inGameOrder에서의 위치로 설정 (무작위 순서)
  participants.value.forEach((p, i) => {
    if (p.id === peerId.value) {
      // i는 participants 배열에서의 인덱스
      // inGameOrder에서 i를 찾아서 그 위치를 myTurn으로 설정
      const turnIndex = inGameOrder.value.indexOf(i);
      myTurn.value = turnIndex; // inGameOrder에서의 내 위치 (무작위 턴 순서)
    }
  });
  // 카드 이미지 프리로딩 후 게임 화면으로 전환
  try {
    // 1. 내 카드 정보 추출
    const storyCardIds = storyCards.value.map(card => card.id);
    const endingCardId = endingCard.value.id;

    console.log('🎯 카드 이미지 프리로딩 시작...', {
      storyCards: storyCardIds,
      endingCard: endingCardId
    });

    // 2. 모든 카드 이미지 프리로드 완료까지 대기
    await CardImage.preloadPlayerCards(storyCardIds, endingCardId);

    console.log('✅ 모든 카드 이미지 프리로딩 완료!');

    // 3. 게임 화면으로 전환
    await router.push("/game/play");

    // 4. 로딩 화면 종료
    emit("startLoading", {value: false});

    // 5. 오버레이 표시
    showOverlay('start').then(() => {
      setTimeout(() => {
        showOverlay('whoTurn').then(() => {
          inProgress.value = true;
        });
      }, 500);
    });

  } catch (error) {
    console.error('❌ 카드 프리로딩 실패:', error);
    // 에러가 발생해도 게임은 계속 진행
    await router.push("/game/play");
    emit("startLoading", {value: false});
  }
};

const startReceived = (data) => {
  return new Promise((resolve) => {
    gameStarted.value = data.gameStarted;
    inGameOrder.value = data.order;
    gameID.value = data.gameId;

    // 게임 시작 시 교환 횟수 초기화 (게스트용)
    exchangeCount.value = 3;

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

const showOverlay = (message, options = {}) => {
  return new Promise((resolve) => {
    const overlay = document.querySelector(".overlay");

    if (message === 'start') {
      overlay.firstElementChild.src = startImage;
      overlay.lastElementChild.textContent = "당신의 차례는 " + (myTurn.value + 1) + "번 입니다.";
      overlay.lastElementChild.style.background = "linear-gradient(60deg, rgba(232,193,147,0.8) 0%, rgba(193,164,204,0.8) 20%, rgba(221,124,175,0.8) 60%, rgba(191,176,209,0.8) 90%, rgba(159,186,204,0.8) 100%)";
      // 텍스트 스타일 향상
      overlay.lastElementChild.style.color = "#2d3748";
      overlay.lastElementChild.style.fontWeight = "800";
      overlay.lastElementChild.style.letterSpacing = "0.025em";
      overlay.lastElementChild.style.textShadow = "-2px -2px 0 #ffffff, 2px -2px 0 #ffffff, -2px 2px 0 #ffffff, 2px 2px 0 #ffffff, 0 0 8px rgba(0,0,0,0.3)";
    } else {
      // 파라미터로 전달받은 정보 사용, 없으면 현재 상태 사용
      const currentTurnIndex = options.turnIndex !== undefined ? options.turnIndex : currTurn.value;
      const currentParticipants = options.participants || participants.value;
      const currentInGameOrder = options.inGameOrder || inGameOrder.value;
      const currentPeerId = options.peerId || peerId.value;

      const isMyTurn = currentParticipants[currentInGameOrder[currentTurnIndex]]?.id === currentPeerId;

      if (isMyTurn) {
        overlay.firstElementChild.src = myTurnImage;
        overlay.lastElementChild.textContent = "멋진 이야기를 적어주세요!";
        overlay.lastElementChild.style.background = "linear-gradient(60deg, rgba(247,140,160,0.7) 0%, rgba(239,144,176,0.7) 25%, rgba(231,151,193,0.7) 50%, rgba(223,157,210,0.7) 75%, rgba(191,176,209,0.7) 100%)";
        // 텍스트 스타일 향상
        overlay.lastElementChild.style.color = "#2d3748";
        overlay.lastElementChild.style.fontWeight = "800";
        overlay.lastElementChild.style.letterSpacing = "0.025em";
        overlay.lastElementChild.style.textShadow = "-2px -2px 0 #ffffff, 2px -2px 0 #ffffff, -2px 2px 0 #ffffff, 2px 2px 0 #ffffff, 0 0 8px rgba(0,0,0,0.3)";
      } else {
        overlay.firstElementChild.src = currTurnImage;
        const currentPlayerName = currentParticipants[currentInGameOrder[currentTurnIndex]]?.name || "플레이어";
        overlay.lastElementChild.textContent = currentPlayerName + "님의 차례";
        overlay.lastElementChild.style.background = "linear-gradient(60deg, rgba(221,124,175,0.7) 0%, rgba(191,176,209,0.7) 25%, rgba(193,164,204,0.7) 50%, rgba(159,186,204,0.7) 75%, rgba(232,193,147,0.7) 100%)";
        // 텍스트 스타일 향상
        overlay.lastElementChild.style.color = "#2d3748";
        overlay.lastElementChild.style.fontWeight = "800";
        overlay.lastElementChild.style.letterSpacing = "0.025em";
        overlay.lastElementChild.style.textShadow = "-2px -2px 0 #ffffff, 2px -2px 0 #ffffff, -2px 2px 0 #ffffff, 2px 2px 0 #ffffff, 0 0 8px rgba(0,0,0,0.3)";
      }
    }

    overlay.classList.remove('scale-0');
    overlay.style.opacity = '1';
    overlay.style.visibility = 'visible';
    if (overlayTimeout.value) clearTimeout(overlayTimeout.value);
    overlayTimeout.value = setTimeout(() => {
      overlay.classList.add('scale-0');
      overlay.style.opacity = '0';
      overlay.style.visibility = 'hidden';
      resolve();
    }, 2000);
  });
}

// 책 데이터 추가
const addBookContent = (newContent) => {
  console.log("📖 addBookContent 호출:", newContent);
  console.log("📖 현재 bookContents 길이:", bookContents.value.length);
  console.log("📖 현재 bookContents:", bookContents.value);
  console.log("📖 첫 번째 항목 content:", bookContents.value[0]?.content);

  if (bookContents.value[0].content === "") {
    console.log("📖 ✅ 첫 번째 항목 업데이트 (정상)");
    bookContents.value[0].content = newContent.content;
    bookContents.value[0].image = newContent.image; // ✅ 이미지도 함께 설정
  } else {
    console.log("📖 ❌ 새 항목 추가 (중복 가능성!)");
    bookContents.value.push(newContent);
  }

  console.log("📖 업데이트 후 길이:", bookContents.value.length);
  console.log("📖 업데이트 후 bookContents:", bookContents.value);
};


const nextTurn = async (data) => {
  const isMyCurrentTurn = inGameOrder.value[currTurn.value] === myTurn.value;
  
  if ((!data || !data.prompt) && isMyCurrentTurn) {
    const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
    currentPlayer.score -= 1;

    const nextTurnIndex = (currTurn.value + 1) % participants.value.length;
    currTurn.value = nextTurnIndex;
    inProgress.value = false;

    // 정확한 턴 정보를 즉시 전달
    await showOverlay('whoTurn', {
      turnIndex: nextTurnIndex,
      participants: participants.value,
      inGameOrder: inGameOrder.value,
      peerId: peerId.value
    });
    
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
  
  if (data?.prompt) {
    const isEnding = data.isEnding === true;
    
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

        // 투표 거절 시 복원을 위해 사용된 카드 백업
        const usedCardObj = storyCards.value.find(card => card.id === usedCard.value.id);
        if (usedCardObj) {
          usedCardBackup.value = { ...usedCardObj };
          console.log(`카드 백업 생성: ID ${usedCardBackup.value.id}, keyword: ${usedCardBackup.value.keyword}`);
        }

        // 백엔드에서 결정한 사용된 카드를 즉시 패에서 제거
        storyCards.value = storyCards.value.filter(card => card.id !== usedCard.value.id);
        console.log(`카드 사용으로 제거됨: ID ${usedCard.value.id}, keyword: ${usedCard.value.keyword}`);

        // 내 카드 정보 업데이트 (다른 플레이어들에게 전송)
        const myCardIds = storyCards.value.map(card => card.id);
        connectedPeers.value.forEach((peer) => {
          if (peer.connection && peer.connection.open) {
            sendMessage("playerCardsSync", {
              userId: peerId.value,
              cardIds: myCardIds
            }, peer.connection);
          }
        });
      } catch (error) {
        toast.errorToast(error.response?.data?.message || "프롬프트 필터링 중 오류가 발생했습니다.");
        return;
      }
    }
    else {
      if (percentage.value < 35) {
        toast.errorToast("긴장감이 충분히 오르지 않았습니다!");
        return;
      }

      if (data.isFreeEnding) {
        // 자유 결말 작성
        usedCard.value.id = 'free_ending'; // 특별한 ID로 구분
        usedCard.value.keyword = data.prompt;
        usedCard.value.isEnding = isEnding;
        usedCard.value.isFreeEnding = true; // 자유 결말 플래그
      } else {
        // 기존 결말카드 사용
        usedCard.value.id = endingCard.value.id;
        usedCard.value.keyword = data.prompt;
        usedCard.value.isEnding = isEnding;
        usedCard.value.isFreeEnding = false;
      }
    }

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
              isFreeEnding: usedCard.value.isFreeEnding || false,
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
        }, 10000);

    addBookContent({ content: data.prompt, image: null });

    inProgress.value = false;
    prompt.value = data.prompt;
    currentVoteSelection.value = "up";
    votings.value = [];

    // 이미지 생성 중 재시도 알림 타이머 변수 선언
    let retryNotificationTimer = null;

    try {
      // 이미지 생성 중 재시도 알림 타이머 설정 (15초 후)
      retryNotificationTimer = setTimeout(() => {
        const retryWarningMessage = {
          type: "retryingContent",
          message: "그림이 조금 이상하네요!\n다시 그려볼게요!"
        };
        showInappropriateWarningModal(retryWarningMessage);
      }, 15000);

      const responseImage = await createImage({
        gameId: gameID.value,
        userId: peerId.value,
        userPrompt: data.prompt,
        turn: totalTurn.value++,
        isEnding: isEnding,
      });

      // 이미지 생성이 성공하면 재시도 알림 타이머 해제
      if (retryNotificationTimer) {
        clearTimeout(retryNotificationTimer);
        retryNotificationTimer = null;
      }
      
      const imageBlob = URL.createObjectURL(responseImage.data);
      const arrayBuffer = await responseImage.data.arrayBuffer();

      connectedPeers.value.forEach((peer, index) => {
        if (peer.id !== peerId.value && peer.connection.open) {
          sendMessage(
            "sendImage",
            { imageBlob: arrayBuffer },
            peer.connection
          )
        }
      });

      // 즉시 책에 추가하지 않고 투표 결과까지 임시 저장
      pendingImage.value = imageBlob;
      console.log("이미지 생성 완료 - 투표 결과 대기 중");

      // ✅ 핵심 추가: waitingForImage 상태 확인하여 processVoteSuccess 호출
      if (waitingForImage.value && currentTurnVoteResult.value) {
        console.log("=== 투표 통과 대기 중 이미지 완성 - processVoteSuccess 호출 ===");
        processVoteSuccess();
        return; // 여기서 함수 종료
      }

      // ✅ 수정: 내가 이미지 생성 후 투표가 이미 완료되었다면 즉시 isElected 트리거
      if (votings.value.length === participants.value.length) {
        console.log("🎯 내 이미지 생성 후 투표 완료 확인 - isElected 즉시 설정");
        const upCount = votings.value.filter(v => v.selected === 'up').length;
        const downCount = votings.value.filter(v => v.selected === 'down').length;
        const voteAccepted = upCount >= downCount;

        if (voteAccepted && pendingImage.value) {
          console.log("🎯 투표 통과 및 이미지 존재 - isElected 설정");
          isElected.value = true;
        }
      }
      
    } catch (error) {
      // 에러 발생 시에도 재시도 알림 타이머 해제
      if (retryNotificationTimer) {
        clearTimeout(retryNotificationTimer);
        retryNotificationTimer = null;
      }

      let errorMessage = "";
      let isInappropriateContent = false;
      
      if (error?.response?.data instanceof Blob) {
        try {
          const errorText = await error.response.data.text();
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.message || "";
        } catch (parseError) {}
      }
      
      isInappropriateContent = error?.response?.status === 503;
      
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
      
      if (isInappropriateContent) {
        if (currTurn.value === myTurn.value) {
          const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];

          // ✅ 핵심 수정: waitingForImage 상태 확인
          if (waitingForImage.value && currentTurnVoteResult.value) {
            console.log("=== 투표 통과 후 이미지 생성 실패 - 투표 부결과 동일한 처리 ===");

            // 1. 사용된 카드를 플레이어 패에 되돌리기 (투표 부결과 동일)
            if (usedCardBackup.value && !usedCard.value.isFreeEnding) {
              storyCards.value.push(usedCardBackup.value);
              console.log(`투표 통과 후 이미지 실패 - 카드 복원: ID ${usedCardBackup.value.id}, keyword: ${usedCardBackup.value.keyword}`);

              // 복원된 카드 정보를 다른 플레이어들에게 전송
              const myCardIds = storyCards.value.map(card => card.id);
              connectedPeers.value.forEach((peer) => {
                if (peer.connection && peer.connection.open) {
                  sendMessage("playerCardsSync", {
                    userId: peerId.value,
                    cardIds: myCardIds
                  }, peer.connection);
                }
              });
            }

            // 2. 백업 정보 및 usedCard 상태 초기화
            usedCardBackup.value = null;
            usedCard.value = {
              id: 0,
              keyword: "",
              isEnding: false,
              isFreeEnding: false
            };

            // 3. 결말모드 해제 (결말카드인 경우)
            if (usedCard.value.isEnding) {
              isEndingMode.value = false;
              console.log("투표 통과 후 이미지 실패 - 결말모드 해제");
            }

            // 4. 임시 이미지 삭제
            if (pendingImage.value) {
              console.log("투표 통과 후 이미지 실패 - pendingImage 정리");
              pendingImage.value = null;
            }

            // 5. 투표 대기 상태 해제
            waitingForImage.value = false;
            currentTurnVoteResult.value = null;

            // 6. 점수 차감 (투표 부결과 동일)
            currentPlayer.score -= 1;

            // 7. 책 내용 제거 (투표 부결과 동일)
            if (bookContents.value.length === 1) {
              bookContents.value = [{ content: "", image: null }];
            } else {
              bookContents.value = bookContents.value.slice(0, -1);
            }

            console.log("=== 투표 통과 후 이미지 실패 - 투표 부결과 동일한 처리 완료 ===");

          } else {
            // 기존 로직: 일반적인 부적절한 이미지 처리
            currentPlayer.score -= 1;

            if (bookContents.value.length === 1) {
              bookContents.value = [{ content: "", image: null }];
            } else {
              bookContents.value = bookContents.value.slice(0, -1);
            }

            const warningMessage = {
              type: "inappropriateContent",
              playerName: currentPlayer.name,
              message: "부적절한 이미지가 생성되었습니다"
            };

            console.log("=== 일반 부적절한 이미지 처리 완료 ===");
          }

          // 공통 처리: 턴 진행
          currTurn.value = (currTurn.value + 1) % participants.value.length;

          if (usedCard.value.isEnding) {
            setTimeout(() => {
              isForceStopped.value = "champ";
            }, 4000); // 2초 → 4초로 변경하여 이미지 적용된 페이지를 충분히 보여줌

            await gameEnd(true).then(() => {
              connectedPeers.value.forEach(async (p) => {
                if (p.id !== peerId.value && p.connection.open) {
                  sendMessage("gameEnd", {}, p.connection);
                }
              });
            });
          } else {
            const stopVotingMessage = {
              type: "stopVotingAndShowWarning",
              warningData: {
                type: "inappropriateContent",
                playerName: currentPlayer.name,
                message: waitingForImage.value ?
                  "투표 통과 후 이미지 생성에 실패했습니다" :
                  "부적절한 이미지가 생성되었습니다"
              },
              currTurn: currTurn.value,
              totalTurn: totalTurn.value,
              imageDelete: true,
              isInappropriate: true
            };

            connectedPeers.value.forEach((peer) => {
              if (peer.id !== peerId.value && peer.connection.open) {
                sendMessage("stopVotingAndShowWarning", stopVotingMessage, peer.connection);
              }
            });
            
            const selfStopVotingMessage = {...stopVotingMessage, skipScoreDeduction: true, skipBookContentRemoval: true};
            stopVotingAndShowWarning(selfStopVotingMessage);
          }
        }
      } else {
        // 일반 에러 시 즉시 턴 넘기기 (재시도하지 않음)
        if (currTurn.value === myTurn.value) {
          const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
          currentPlayer.score -= 1; // 에러로 인한 점수 차감

          // 마지막 추가된 bookContent 제거 (이미지 실패로 인해)
          if (bookContents.value.length === 1) {
            bookContents.value = [{ content: "", image: null }];
          } else {
            bookContents.value = bookContents.value.slice(0, -1);
          }

          currTurn.value = (currTurn.value + 1) % participants.value.length;

          // 다른 플레이어들에게 턴 넘김 알림
          connectedPeers.value.forEach((peer) => {
            if (peer.id !== peerId.value && peer.connection.open) {
              sendMessage("nextTurn", {
                currTurn: currTurn.value,
                imageDelete: true,
                totalTurn: totalTurn.value,
                scoreChange: { type: "decrease", amount: 1, playerIndex: inGameOrder.value[currTurn.value === 0 ? participants.value.length - 1 : currTurn.value - 1] },
                reason: "이미지 생성 실패"
              }, peer.connection);
            }
          });

          toast.errorToast("이미지 생성에 실패하여 턴이 넘어갑니다: " + (error?.message || "알 수 없는 오류"));

          // 다음 턴 오버레이 표시
          await showOverlay('whoTurn');
          inProgress.value = true;
        } else {
          toast.errorToast("이미지 생성에 실패했습니다: " + (error?.message || "알 수 없는 오류"));
        }
      }
    }
  }
};

// 결말카드 리롤 함수
const cardReroll = async () => {
  const response = await endingCardReroll({
    userId: peerId.value,
    gameId: gameID.value,
  });

  endingCard.value.id = response.data.data.id;
  endingCard.value.content = response.data.data.content;
};

// 투표 선택 시 즉시 호출
const onVoteSelected = (voteType) => {
  currentVoteSelection.value = voteType;
};

const voteEnd = async (data) => {
  console.log("=== voteEnd 함수 시작 ===");
  console.log("투표 데이터:", data);
  console.log("현재 투표 상태 - isVoted:", isVoted.value);
  console.log("현재 턴:", currTurn.value, "내 턴:", myTurn.value);

  currentVoteSelection.value = data.selected;
  prompt.value = "";
  isVoted.value = true;

  // 내 투표를 votings 배열에 추가 (중복 방지)
  const voteExists = votings.value.some(v => v.sender === data.sender);
  if (!voteExists) {
    votings.value = [...votings.value, {sender: data.sender, selected: data.selected}];
    console.log("내 투표 추가 완료, 현재 votings:", votings.value);
  }

  const sendVoteResult = async () => {
    console.log("=== sendVoteResult 함수 시작 ===");
    console.log("연결된 피어 수:", connectedPeers.value.length);

    connectedPeers.value.forEach((peer) => {
      if (peer.id !== peerId.value && peer.connection.open) {
        console.log(`피어 ${peer.id}에게 투표 결과 전송:`, { sender: data.sender, selected: data.selected });
        sendMessage("voteResult", { sender: data.sender, selected: data.selected }, peer.connection);
      }
    });

    console.log("=== 투표 집계 시작 ===");
    console.log("현재 투표 수:", votings.value.length);
    console.log("총 참가자 수:", participants.value.length);
    console.log("현재 투표 내역:", votings.value);

    if (votings.value.length == participants.value.length) {
      console.log("=== 모든 투표 완료, 결과 집계 중 ===");

      let upCount = 0;
      votings.value.forEach((vote) => {
        if (vote.selected == 'up') upCount++;
      });

      console.log("찬성 투표 수:", upCount);
      console.log("전체 투표 수:", votings.value.length);
      console.log("과반수 기준:", votings.value.length / 2);

      const voteAccepted = upCount >= (votings.value.length / 2);
      console.log("투표 결과:", voteAccepted ? "통과" : "거절");

      if (currTurn.value === myTurn.value) {
        console.log("=== 현재 턴 플레이어의 투표 처리 시작 ===");
        const currentPlayer = participants.value[inGameOrder.value[currTurn.value]];
        const currentPlayerIndex = inGameOrder.value[currTurn.value];
        const wasEndingCard = usedCard.value.isEnding; // 상태 초기화 전에 저장

        let accepted = voteAccepted;
        if (accepted) {
          console.log("=== 투표 통과 처리 시작 ===");
          console.log("현재 플레이어:", currentPlayer);
          console.log("결말카드 여부:", wasEndingCard);
          console.log("자유결말 여부:", usedCard.value.isFreeEnding);

          const scoreIncrease = wasEndingCard ?
            (usedCard.value.isFreeEnding ? 3 : 5) : 2;
          const wasFreeEnding = usedCard.value.isFreeEnding;

          // ✅ 핵심 수정: 투표 결과 저장 후 이미지 상태 확인
          currentTurnVoteResult.value = {
            accepted: true,
            player: currentPlayer,
            playerIndex: currentPlayerIndex,
            scoreIncrease: scoreIncrease,
            wasEndingCard: wasEndingCard,
            wasFreeEnding: wasFreeEnding
          };

          console.log("투표 결과 저장:", currentTurnVoteResult.value);

          // 이미지가 이미 준비되어 있는지 확인
          if (pendingImage.value) {
            console.log("=== 이미지 이미 준비됨 - 즉시 진행 ===");
            processVoteSuccess();
          } else {
            console.log("=== 이미지 대기 상태로 전환 ===");
            waitingForImage.value = true;

            // 다른 플레이어들에게 대기 상태 알림
            connectedPeers.value.forEach((peer) => {
              if (peer.id !== peerId.value && peer.connection.open) {
                sendMessage("waitingForImage", {
                  message: "이미지 생성 중...",
                  playerName: currentPlayer.name
                }, peer.connection);
              }
            });
          }

          // 결말카드는 이미지 대기 없이 즉시 처리
          if (wasEndingCard) {
            console.log("=== 결말카드 - 즉시 처리 ===");
            processVoteSuccess();
          }

          if (wasEndingCard) {
            console.log("=== 결말카드 처리 - 게임 종료 ===");
            gameEnd(true);
            connectedPeers.value.forEach((p) => {
              if (p.id !== peerId.value && p.connection.open) {
                sendMessage("endingCardScoreUpdate", {
                  scoreChange: {
                    type: "increase",
                    amount: wasFreeEnding ? 3 : 5,
                    playerIndex: currentPlayerIndex
                  }
                }, p.connection);
              }
            });
            
            setTimeout(() => {
              isForceStopped.value = "champ";
              connectedPeers.value.forEach(async (p) => {
                if (p.id !== peerId.value && p.connection.open) {
                  sendMessage("showResultsWithCover", {
                    bookCover: { title: "아주 먼 옛날", imageUrl: "" },
                    ISBN: "generating..."
                  }, p.connection);
                }
              });
            }, 4000); // 2초 → 4초로 변경하여 이미지 적용된 페이지를 충분히 보여줌
          } else {
            console.log("=== 일반카드 처리 - 다음 턴 진행 ===");
            console.log("다음 턴으로 전환하는 메시지 전송 중...");

            connectedPeers.value.forEach(async (p) => {
              if (p.id !== peerId.value && p.connection.open) {
                console.log(`피어 ${p.id}에게 nextTurn 메시지 전송:`, {
                  currTurn: currTurn.value,
                  imageDelete: false,
                  totalTurn: totalTurn.value,
                  scoreChange: { type: "increase", amount: scoreIncrease, playerIndex: currentPlayerIndex },
                  cardRemoval: { cardId: usedCard.value.id }
                });
                sendMessage("nextTurn", {
                  currTurn: currTurn.value,
                  imageDelete: false,
                  totalTurn: totalTurn.value,
                  scoreChange: { type: "increase", amount: scoreIncrease, playerIndex: currentPlayerIndex },
                  cardRemoval: { cardId: usedCard.value.id }
                }, p.connection);
              }
            });

            // 카드는 이미 프롬프트 필터링 시점에 제거됨

            // 투표 찬성 후 백업 정리 및 usedCard 상태 초기화 (결말카드가 아닌 경우에만)
            console.log("usedCard 백업 정리 및 상태 초기화");
            usedCardBackup.value = null; // 백업 정리
            if (!wasEndingCard) {
              usedCard.value = {
                id: 0,
                keyword: "",
                isEnding: false,
                isFreeEnding: false
              };
              console.log("usedCard 상태 초기화 완료");
            }

            console.log("턴 전환 오버레이 표시 시작");
            await showOverlay('whoTurn', {
              turnIndex: currTurn.value,
              participants: participants.value,
              inGameOrder: inGameOrder.value,
              peerId: peerId.value
            });
            console.log("턴 전환 오버레이 완료, 게임 진행 재개");
            inProgress.value = true;
          }
        } else {
          console.log("=== 투표 거절 처리 시작 ===");
          accepted = false;

          // 투표 반대 시 임시 이미지 삭제
          if (pendingImage.value) {
            console.log("투표 반대 - 임시 이미지 삭제");
            pendingImage.value = null;
          }

          // 결말카드가 반대된 경우 상태 초기화
          if (usedCard.value.isEnding) {
            isEndingMode.value = false; // 결말모드 해제
            console.log("결말카드 투표 반대 - 결말모드 해제");
          }

          // 투표 거절 시 사용된 카드를 패에 복원 (자유 결말이 아닌 경우만)
          if (usedCardBackup.value && !usedCard.value.isFreeEnding) {
            storyCards.value.push(usedCardBackup.value);
            console.log(`투표 거절로 카드 복원: ID ${usedCardBackup.value.id}, keyword: ${usedCardBackup.value.keyword}`);

            // 복원된 카드 정보를 다른 플레이어들에게 전송
            const myCardIds = storyCards.value.map(card => card.id);
            connectedPeers.value.forEach((peer) => {
              if (peer.connection && peer.connection.open) {
                sendMessage("playerCardsSync", {
                  userId: peerId.value,
                  cardIds: myCardIds
                }, peer.connection);
              }
            });
          }

          // 백업 정보 및 usedCard 상태 초기화
          usedCardBackup.value = null;
          usedCard.value = {
            id: 0,
            keyword: "",
            isEnding: false,
            isFreeEnding: false
          };

          currTurn.value = (currTurn.value + 1) % participants.value.length;
          connectedPeers.value.forEach((peer) => {
            if (peer.id !== peerId.value && peer.connection.open) {
              sendMessage("nextTurn", {
                currTurn: currTurn.value,
                imageDelete: true,
                totalTurn: totalTurn.value,
                resetEndingState: true, // 다른 플레이어들도 결말상태 리셋 알림
                voteRejected: true, // 투표 거절 명시적 표시
                rejectedPrompt: prompt.value // 거절된 이야기 내용
              }, peer.connection);
            }
          });

          console.log("투표 거절로 인한 책 내용 삭제 처리 (작성자)");
          console.log("삭제 전 책 내용:", bookContents.value);

          if (bookContents.value.length === 1) {
            bookContents.value = [{ content: "", image: null }];
          } else {
            // 마지막 항목(거절된 이야기와 이미지) 완전 제거
            bookContents.value = bookContents.value.slice(0, -1);
          }

          console.log("삭제 후 책 내용:", bookContents.value);
          currentPlayer.score -= 1;
          await showOverlay('whoTurn');
          inProgress.value = true;
        }

        try {
            const response = await voteResultSend({
              gameId: gameID.value,
              userId: peerId.value,
              accepted: accepted,
              cardId: usedCard.value.id,
              isEnding: usedCard.value.isEnding,
            });

            // 백엔드에서 받은 점수 변화 정보 처리
            if (response.data && response.data.scoreChange) {
              const scoreChange = response.data.scoreChange;
              currentPlayer.score += scoreChange;

              // 점수 변화 처리

              // 다른 플레이어들에게 점수 변화 알림
              connectedPeers.value.forEach((p) => {
                if (p.id !== peerId.value && p.connection.open) {
                  sendMessage("scoreUpdate", {
                    userId: peerId.value,
                    scoreChange: scoreChange,
                    playerIndex: currentPlayerIndex,
                    message: response.data.message
                  }, p.connection);
                }
              });
            }

            if (accepted) {
              storyCards.value = storyCards.value.filter(card => card.id !== usedCard.value.id);
            }
        } catch (error) {
            if (error.response?.status === 409) {
              storyCards.value = storyCards.value.filter(card => card.id !== usedCard.value.id);
            }
        }
      } else {
        // 게스트 플레이어 투표 처리
        const wasEndingCard = usedCard.value.isEnding; // 상태 초기화 전에 저장

        if (voteAccepted) {
          // ✅ 핵심 수정: 게스트 플레이어도 이미지 상태 확인
          if (pendingImage.value) {
            console.log("✅ 게스트: pendingImage 존재 - isElected 설정");
            isElected.value = true;
          } else {
            console.log("⏳ 게스트: pendingImage 대기 중 - isElected 설정 보류");
            // 이미지가 없으면 isElected 설정하지 않음
          }

          // ✅ 수정: 이미지 추가는 isElected watch에서 처리됨
          console.log("게스트: 투표 찬성 - 이미지는 isElected watch에서 처리됨");

          // 투표 찬성 후 usedCard 상태 초기화 (결말카드가 아닌 경우에만)
          if (!wasEndingCard) {
            usedCard.value = {
              id: 0,
              keyword: "",
              isEnding: false,
              isFreeEnding: false
            };
          }
        } else {
          // 투표 반대 시 임시 이미지 삭제
          if (pendingImage.value) {
            console.log("게스트: 투표 반대 - 임시 이미지 삭제");
            pendingImage.value = null;
          }

          // 투표 반대 시 - 게스트도 상태 초기화 필요
          if (usedCard.value.isEnding) {
            isEndingMode.value = false;
            console.log("게스트: 결말카드 투표 반대 - 결말모드 해제");
          }
          usedCard.value = {
            id: 0,
            keyword: "",
            isEnding: false,
            isFreeEnding: false
          };
        }

        if (voteAccepted && wasEndingCard && participants.value[0].id === peerId.value) {
          gameEnd(true);
          setTimeout(() => {
            isForceStopped.value = "champ";
            connectedPeers.value.forEach(async (p) => {
              if (p.id !== peerId.value && p.connection.open) {
                sendMessage("showResultsWithCover", {
                  bookCover: { title: "아주 먼 옛날", imageUrl: "" },
                  ISBN: "generating..."
                }, p.connection);
              }
            });
          }, 4000); // 2초 → 4초로 변경하여 이미지 적용된 페이지를 충분히 보여줌
        }
      }
    }
  }

  console.log("=== voteEnd 함수 마지막 부분 ===");
  console.log("현재 턴 vs 내 턴 비교:", currTurn.value, "===", myTurn.value);

  // ✅ 수정: 투표 결과 전송만 담당, 실제 처리는 voteResult 케이스에서 처리
  console.log("=== 📢 NEW 수정된 voteEnd 로직 실행 중 ===");
  console.log("=== 투표 결과 브로드캐스트 ===");
  sendVoteResult();
  console.log("=== voteEnd 함수 완료 ===");
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
  totalTurn.value = 1;
  bookContents.value = [{ content: "", image: null }];
  bookCover.value = {title: "", imageUrl: ""};
  ISBN.value = "";
  votings.value = [];
  myTurn.value = null;
  inProgress.value = false;
  inGameOrder.value = [];
  isForceStopped.value = null;

  // 투표 및 선출 관련 상태 초기화
  isElected.value = false;
  isVoted.value = false;
  pendingImage.value = null; // 임시 이미지 초기화

  // 게임 모드 및 설정 초기화
  isEndingMode.value = false;
  hasReached35Percent.value = false;
  isPreview.value = false;

  // 모달 및 알림 상태 초기화
  showWarningModal.value = false;
  warningModalMessage.value = "";
  showSmallAlert.value = false;
  smallAlertMessage.value = "";

  // 프롬프트 상태 초기화
  prompt.value = "";

  // 카드 상태 초기화
  storyCards.value = [];
  endingCard.value = { id: 0, content: "" };

  // 방 설정 초기화
  roomConfigs.value = {
    currTurnTime: 30,
    currMode: 0,
  };

  // 참가자 점수 초기화
  participants.value.forEach((participant) => {
    participant.score = 10;
  });

  // 사용된 카드 초기화
  usedCard.value = {
    id: 0,
    keyword: "",
    isEnding: false,
    isFreeEnding: false
  };

  router.push("/game/lobby");
};

// 카드 새로고침 처리
const handleCardRefreshed = async (data) => {
  console.log("=== 카드 새로고침 처리 시작 ===");
  console.log("받은 데이터:", data);

  // 다른 플레이어들이 보유한 모든 카드 ID 수집
  const allOtherPlayerCards = [];
  otherPlayersCards.value.forEach((cardIds) => {
    allOtherPlayerCards.push(...cardIds);
  });

  console.log("새로고침 시 제외할 카드들:", allOtherPlayerCards);

  try {
    // 백엔드에 새로고침 요청 (다른 플레이어 카드 제외)
    const response = await refreshStoryCard({
      gameId: data.gameId || gameID.value,
      userId: data.userId || peerId.value,
      cardId: data.oldCard.id,
      excludeCardIds: allOtherPlayerCards // 다른 플레이어 카드 제외
    });

    if (response.data.success) {
      const responseData = response.data.data;
      const newCard = responseData.newCard;
      const updatedRefreshCount = responseData.refreshCount;

      console.log("=== 백엔드 새로고침 응답 ===");
      console.log("새 카드:", newCard);
      console.log("업데이트된 새로고침 횟수:", updatedRefreshCount);
      console.log("응답 전체 데이터:", responseData);

      // storyCards에서 oldCard를 찾아 newCard로 교체
      const cardIndex = storyCards.value.findIndex(card => card.id === data.oldCard.id);
      if (cardIndex !== -1) {
        storyCards.value[cardIndex] = newCard;
      }

      // 내 카드 정보 업데이트 (다른 플레이어들에게 전송용)
      const myCardIds = storyCards.value.map(card => card.id);

      // P2P 메시지로 다른 플레이어들에게 알림
      connectedPeers.value.forEach(peer => {
        if (peer.connection && peer.connection.open) {
          sendMessage("storyCardRefreshed", {
            userId: peerId.value,
            oldCard: data.oldCard,
            newCard: newCard
          }, peer.connection);

          // 업데이트된 내 카드 목록도 전송
          sendMessage("playerCardsSync", {
            userId: peerId.value,
            cardIds: myCardIds
          }, peer.connection);
        }
      });

      console.log(`카드 새로고침 완료: ${data.oldCard.keyword} → ${newCard.keyword}`);

      // 새로운 카드 이미지 프리로딩
      try {
        const newCardImageUrl = CardImage.getStoryCardImage(newCard.id);
        console.log(`🎯 새로고침된 카드 이미지 프리로딩: ${newCard.keyword} (ID: ${newCard.id})`);

        const img = new Image();
        img.onload = () => {
          console.log(`✅ 새로고침된 카드 이미지 로드 완료: ${newCard.keyword}`);
        };
        img.onerror = () => {
          console.warn(`❌ 새로고침된 카드 이미지 로드 실패: ${newCard.keyword}`);
        };
        img.src = newCardImageUrl;
      } catch (error) {
        console.warn(`❌ 새로고침된 카드 이미지 프리로딩 중 오류: ${newCard.keyword}`, error);
      }

      // InGameControl에 성공 알림 및 refreshCount 업데이트
      if (currentViewRef.value && currentViewRef.value.onCardRefreshSuccess) {
        currentViewRef.value.onCardRefreshSuccess();
      }

      // InGameControl의 refreshCount 동기화
      console.log("=== currentViewRef 상태 확인 ===");
      console.log("currentViewRef.value:", currentViewRef.value);
      console.log("currentViewRef.value가 존재하는가?", !!currentViewRef.value);
      console.log("updateCounts 메서드가 존재하는가?", currentViewRef.value && typeof currentViewRef.value.updateCounts === 'function');

      if (currentViewRef.value && currentViewRef.value.updateCounts) {
        // exchangeCount는 현재 값 유지하고 refreshCount만 업데이트
        console.log("=== handleCardRefreshed에서 updateCounts 호출 ===");
        console.log("전달할 updatedRefreshCount:", updatedRefreshCount);
        console.log("exchangeCount는 null로 유지");

        currentViewRef.value.updateCounts(updatedRefreshCount, null);
        console.log("=== updateCounts 호출 완료 ===");
      } else {
        console.error("❌ currentViewRef 또는 updateCounts 메서드가 없습니다!");
        console.log("currentViewRef.value:", currentViewRef.value);
        if (currentViewRef.value) {
          console.log("currentViewRef의 메서드들:", Object.keys(currentViewRef.value));
        console.log("currentViewRef의 모든 속성들:", currentViewRef.value);
        }
      }
    } else {
      // 새로고침 실패
      if (currentViewRef.value && currentViewRef.value.onCardRefreshError) {
        currentViewRef.value.onCardRefreshError("새로고침에 실패했습니다.");
      }
    }
  } catch (error) {
    console.error("=== 카드 새로고침 중 오류 ===");
    console.error("에러 상태:", error.response?.status);
    console.error("에러 데이터:", error.response?.data);
    console.error("게임 ID:", data.gameId || gameID.value);
    console.error("사용자 ID:", data.userId || peerId.value);
    console.error("전체 에러:", error);

    // InGameControl에 에러 알림
    if (currentViewRef.value && currentViewRef.value.onCardRefreshError) {
      const errorMessage = error.response?.data?.message || "새로고침 중 오류가 발생했습니다.";
      currentViewRef.value.onCardRefreshError(errorMessage);
    }
  }
};

// 교환 신청 처리
const handleSendExchangeRequest = (data) => {
  console.log("=== 교환 신청 처리 시작 ===");
  console.log("1. 전달받은 data:", data);

  // 카드 상태 확인
  const cardStatus = getCardExchangeStatus(data.cardId);
  console.log(`1-1. 카드 ${data.cardId} 상태 확인: ${cardStatus}`);

  if (cardStatus !== EXCHANGE_STATUS.IDLE) {
    console.log(`1-1-1. 카드 ${data.cardId}가 이미 교환 상태 ${cardStatus} - 중단`);
    toast.warningToast("해당 카드는 이미 교환 요청 중입니다.");
    return;
  }

  // 전역 교환 처리 중이면 중단
  if (isExchangeProcessing.value) {
    console.log("1-2. 이미 전역 교환 처리 중 - 중단");
    toast.warningToast("다른 교환이 진행 중입니다. 잠시 후 다시 시도해주세요.");
    return;
  }

  // 내가 현재 실제로 소유한 카드인지 확인
  const hasMyCard = storyCards.value.some(card => card.id === data.cardId);
  if (!hasMyCard) {
    console.log(`1-2. 내가 소유하지 않은 카드 ${data.cardId} - 중단`);
    toast.warningToast("이미 교환된 카드입니다.");
    return;
  }

  console.log("2. targetUserId:", data.targetUserId);
  console.log("3. 현재 participants:", participants.value.map(p => ({id: p.id, name: p.name})));
  console.log("4. 현재 connectedPeers:", connectedPeers.value.map(p => ({id: p.id, connectionOpen: p.connection?.open})));

  // participants와 connectedPeers 동기화 상태 확인
  const participantIds = participants.value.map(p => p.id).sort();
  const connectedPeerIds = connectedPeers.value.map(p => p.id).sort();
  console.log("5. participants IDs:", participantIds);
  console.log("6. connectedPeers IDs:", connectedPeerIds);
  console.log("7. 동기화 상태:", JSON.stringify(participantIds) === JSON.stringify(connectedPeerIds) ? "OK" : "불일치");

  const targetPeer = connectedPeers.value.find(peer => peer.id === data.targetUserId);
  console.log("8. 찾은 targetPeer:", targetPeer ? {id: targetPeer.id, connectionOpen: targetPeer.connection?.open} : null);

  if (targetPeer && targetPeer.connection && targetPeer.connection.open) {
    // 디바운싱 적용하여 중복 요청 방지
    debounceExchangeRequest(data.cardId, () => {
      // 재검증 (디바운싱 지연 시간 동안 상태가 변경될 수 있음)
      const currentStatus = getCardExchangeStatus(data.cardId);
      if (currentStatus !== EXCHANGE_STATUS.IDLE) {
        console.log(`4-1. 디바운싱 후 재검증 실패: 카드 ${data.cardId} 상태 ${currentStatus}`);
        toast.warningToast("해당 카드는 이미 교환 요청 중입니다.");
        return;
      }

      // 교환 요청 상태로 설정
      setCardExchangeStatus(data.cardId, EXCHANGE_STATUS.REQUESTING);

      const messageData = {
        fromUserId: peerId.value,
        fromUserName: participants.value.find(p => p.id === peerId.value)?.name || '',
        fromCardId: data.cardId,
        fromCard: data.card,
        toUserId: data.targetUserId
      };
      console.log("5. 전송할 메시지 데이터:", messageData);

      sendMessage("storyCardExchangeRequest", messageData, targetPeer.connection);
      console.log("6. P2P 메시지 전송 완료");

      // 요청 완료 후 상태를 PENDING으로 변경 (응답 대기 중)
      setCardExchangeStatus(data.cardId, EXCHANGE_STATUS.PENDING);
    }, 500); // 500ms 디바운싱
  } else {
    console.log("6. ERROR: targetPeer를 찾을 수 없거나 연결이 닫혀있음");
    console.log("   - targetPeer 존재:", !!targetPeer);
    console.log("   - connection 존재:", !!targetPeer?.connection);
    console.log("   - connection.open:", targetPeer?.connection?.open);
  }
  console.log("=== 교환 신청 처리 끝 ===");
};

// 교환 처리 중인지 추적
const isExchangeProcessing = ref(false);

// 카드별 교환 상태 추적 (Map<cardId, status>)
const cardExchangeStatus = ref(new Map());

// 교환 요청 디바운싱을 위한 타이머 저장
const exchangeDebounceTimers = ref(new Map());

// 교환 상태 열거형
const EXCHANGE_STATUS = {
  IDLE: 'idle',
  REQUESTING: 'requesting',
  PENDING: 'pending',
  PROCESSING: 'processing'
};

// 카드 교환 상태 설정 함수
const setCardExchangeStatus = (cardId, status) => {
  console.log(`🔄 카드 ${cardId} 교환 상태 변경: ${cardExchangeStatus.value.get(cardId) || 'none'} → ${status}`);
  cardExchangeStatus.value.set(cardId, status);
};

// 카드 교환 상태 확인 함수
const getCardExchangeStatus = (cardId) => {
  return cardExchangeStatus.value.get(cardId) || EXCHANGE_STATUS.IDLE;
};

// 교환 요청 디바운싱 함수
const debounceExchangeRequest = (cardId, action, delay = 1000) => {
  // 기존 타이머가 있으면 취소
  if (exchangeDebounceTimers.value.has(cardId)) {
    clearTimeout(exchangeDebounceTimers.value.get(cardId));
  }

  // 새 타이머 설정
  const timer = setTimeout(() => {
    action();
    exchangeDebounceTimers.value.delete(cardId);
  }, delay);

  exchangeDebounceTimers.value.set(cardId, timer);
};


// 교환 수락 처리
const handleCardExchanged = async (data) => {
  console.log("=== 교환 수락 처리 시작 (수신자) ===");
  console.log("1. 받은 데이터:", data);

  // 전역 교환 처리 중이면 중단
  if (isExchangeProcessing.value) {
    console.log("1-1. 이미 전역 교환 처리 중 - 중단");
    toast.warningToast("다른 교환이 진행 중입니다. 잠시 후 다시 시도해주세요.");
    return;
  }

  // 내 카드의 교환 상태 확인
  const myCardStatus = getCardExchangeStatus(data.toCardId);
  if (myCardStatus !== EXCHANGE_STATUS.IDLE) {
    console.log(`1-2. 내 카드 ${data.toCardId}가 이미 교환 상태 ${myCardStatus} - 중단`);
    toast.warningToast("해당 카드는 이미 교환 중입니다.");
    return;
  }

  // 교환할 카드가 내 카드 목록에 있는지 확인
  const hasMyCard = storyCards.value.some(card => card.id === data.toCardId);
  if (!hasMyCard) {
    console.log("1-3. 교환할 내 카드를 찾을 수 없음 - 중단");
    toast.errorToast("이미 교환된 카드입니다.");
    return;
  }

  // 교환 상태 설정
  isExchangeProcessing.value = true;
  setCardExchangeStatus(data.toCardId, EXCHANGE_STATUS.PROCESSING);
  setCardExchangeStatus(data.fromCardId, EXCHANGE_STATUS.PROCESSING);
  console.log("2. 교환 전 내 카드 목록:", storyCards.value.map(c => ({id: c.id, keyword: c.keyword})));

  // 백엔드에 교환 요청 (수신자 측)
  try {
    const exchangeResponse = await exchangeStoryCard({
      gameId: gameID.value,
      fromUserId: data.fromUserId,
      toUserId: data.toUserId,
      fromCardId: data.fromCardId,
      toCardId: data.toCardId,
      status: 'accepted'
    });

    if (exchangeResponse.data.success) {
      console.log("3. 백엔드 교환 처리 성공");
      console.log("3-1. 백엔드 응답 데이터:", exchangeResponse.data.data);

      // 수신자는 자신이 선택한 카드를 신청자의 카드로 교체
      const myCardIndex = storyCards.value.findIndex(card => card.id === data.toCardId);

      console.log("4. myCardIndex (내가 선택한 카드):", myCardIndex);
      console.log("5. 받을 카드 데이터 (신청자 카드):", data.fromCard);

      if (myCardIndex !== -1) {
        console.log("6. 교환 전 내 카드:", storyCards.value[myCardIndex]);

        // 내 카드를 신청자의 카드로 교체
        storyCards.value[myCardIndex] = data.fromCard;

        console.log("7. 교환 후 내 카드:", storyCards.value[myCardIndex]);
      } else {
        console.log("6. ERROR: 내가 선택한 카드를 찾을 수 없음");
        console.log("   - toCardId:", data.toCardId, "index:", myCardIndex);
      }

      console.log("8. 교환 후 내 카드 목록:", storyCards.value.map(c => ({id: c.id, keyword: c.keyword})));

      // 상대방에게 교환 응답 메시지 전송
      const targetPeer = connectedPeers.value.find(peer => peer.id === data.fromUserId);
      if (targetPeer && targetPeer.connection && targetPeer.connection.open) {
        const responseData = {
          accepted: true,
          fromUserId: data.fromUserId,
          toUserId: data.toUserId,
          fromCardId: data.fromCardId,
          toCardId: data.toCardId,
          fromCard: data.fromCard,
          toCard: data.toCard,
          // 수신자의 업데이트된 교환 횟수 포함
          receiverExchangeCount: exchangeResponse.data.data?.exchangeCount
        };
        console.log("9. 신청자에게 전송할 응답 데이터:", responseData);

        sendMessage("storyCardExchangeResponse", responseData, targetPeer.connection);
        console.log("10. 교환 응답 메시지 전송 완료");

        // 교환받은 카드 이미지 프리로딩 (수신자)
        try {
          const receivedCardImageUrl = CardImage.getStoryCardImage(data.fromCardId);
          console.log(`🎯 교환받은 카드 이미지 프리로딩 (수신자): ${data.fromCard.keyword} (ID: ${data.fromCardId})`);

          const img = new Image();
          img.onload = () => {
            console.log(`✅ 교환받은 카드 이미지 로드 완료 (수신자): ${data.fromCard.keyword}`);
          };
          img.onerror = () => {
            console.warn(`❌ 교환받은 카드 이미지 로드 실패 (수신자): ${data.fromCard.keyword}`);
          };
          img.src = receivedCardImageUrl;
        } catch (error) {
          console.warn(`❌ 교환받은 카드 이미지 프리로딩 중 오류 (수신자): ${data.fromCard.keyword}`, error);
        }

        // 교환 완료 - 수신자는 exchangeCount 차감하지 않음 (신청자만 차감)
        console.log("3-2. 수신자 교환 완료 - exchangeCount 차감 안 함 (신청자만 차감)");

        // 교환 완료 후 내 카드 정보 업데이트 (다른 플레이어들에게 전송)
        const myCardIds = storyCards.value.map(card => card.id);
        connectedPeers.value.forEach((peer) => {
          if (peer.connection && peer.connection.open) {
            sendMessage("playerCardsSync", {
              userId: peerId.value,
              cardIds: myCardIds
            }, peer.connection);
          }
        });
      } else {
        console.log("9. ERROR: targetPeer를 찾을 수 없음");
      }
    } else {
      console.log("3. 백엔드 교환 처리 실패:", exchangeResponse.data.message);
      toast.errorToast("교환 처리 중 오류가 발생했습니다.");
    }
  } catch (error) {
    console.log("3. 백엔드 교환 API 호출 실패:", error);
    toast.errorToast("교환 처리 중 오류가 발생했습니다.");
  } finally {
    // 교환 처리 완료 후 모든 상태 해제
    isExchangeProcessing.value = false;
    setCardExchangeStatus(data.toCardId, EXCHANGE_STATUS.IDLE);
    setCardExchangeStatus(data.fromCardId, EXCHANGE_STATUS.IDLE);

    // 혹시 남아있을 수 있는 잘못된 상태들 정리
    cardExchangeStatus.value.forEach((status, cardId) => {
      if (status !== EXCHANGE_STATUS.IDLE &&
          (cardId === data.fromCardId || cardId === data.toCardId)) {
        console.log(`📋 수신자 잔여 상태 정리: 카드 ${cardId} ${status} → idle`);
        cardExchangeStatus.value.set(cardId, EXCHANGE_STATUS.IDLE);
      }
    });

    console.log("📋 수신자 교환 상태 정리 완료");
  }

  console.log("=== 교환 수락 처리 끝 (수신자) ===");
};

// 교환 거절 처리
const handleRejectExchange = (data) => {
  console.log("=== 교환 거절 처리 시작 ===");
  console.log("거절할 교환 요청:", data);

  const targetPeer = connectedPeers.value.find(peer => peer.id === data.fromUserId);
  if (targetPeer && targetPeer.connection && targetPeer.connection.open) {
    sendMessage("storyCardExchangeResponse", {
      accepted: false,
      fromUserId: data.fromUserId,
      toUserId: peerId.value,
      fromCardId: data.fromCardId // 상대방의 카드 ID 포함
    }, targetPeer.connection);

    console.log("교환 거절 응답 전송 완료");
  }

  // 거절 처리 시 내 카드 상태 초기화 (만약 처리 중이었다면)
  if (data.toCardId) {
    setCardExchangeStatus(data.toCardId, EXCHANGE_STATUS.IDLE);
    console.log(`내 카드 ${data.toCardId} 상태 초기화`);
  }

  console.log("=== 교환 거절 처리 완료 ===");
};

// 긴장감 변화 감지 (35% 및 100% 체크)
watch(
  () => [percentage.value, usedCard.value, isElected.value],
  ([newPercent, newUsedCard, newIsElected], [oldPercent, oldUsedCard, oldIsElected]) => {
    // 35% 도달 체크 (한 번만 실행)
    if (newPercent >= 35 && !hasReached35Percent.value && newIsElected) {
      hasReached35Percent.value = true;

      // 작은 알림 표시 (모든 사용자에게)
      smallAlertMessage.value = "긴장감이 35%에 도달했습니다";
      showSmallAlert.value = true;

      // WebRTC로 다른 플레이어들에게 결말카드 사용 가능 알림
      connectedPeers.value.forEach((peer) => {
        sendMessage(
          "endingCardAvailable",
          {
            message: "긴장감이 35%에 도달했습니다"
          },
          peer.connection
        );
      });
    }

    // 100% 도달 체크 (결말 모드 전환)
    if (newPercent >= oldPercent && newPercent >= 100 && newUsedCard.isEnding == false && newIsElected && !isEndingMode.value) {
      // 결말 모드로 전환
      isEndingMode.value = true;

      // 작은 알림 표시 (모든 사용자에게, 100% 타입)
      smallAlertMessage.value = "긴장감이 100%에 도달했습니다!\n이제 결말을 맺어야 할 때입니다!";
      showSmallAlert.value = true;

      // WebRTC로 다른 플레이어들에게 결말 모드 전환 알림
      connectedPeers.value.forEach((peer) => {
        sendMessage(
          "endingModeActivated",
          {
            message: "긴장감이 100%에 도달했습니다! 이제 결말을 맺어야 할 때입니다!"
          },
          peer.connection
        );
      });
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

/* 2025 트렌드한 게임 로고 애니메이션 */
.overlay {
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  transform-origin: center;
  will-change: transform, opacity, filter;
}

.overlay.scale-0 {
  animation: fadeOutBlur 0.8s cubic-bezier(0.4, 0, 1, 1) forwards;
  pointer-events: none;
  opacity: 0 !important;
  visibility: hidden !important;
}

.overlay:not(.scale-0) {
  pointer-events: auto;
  animation: gameLogoReveal 1.2s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  opacity: 1 !important;
  visibility: visible !important;
}

.overlay img {
  filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
  will-change: transform, filter;
  animation: logoGlow 1.5s ease-in-out infinite alternate;
}

.overlay div {
  will-change: transform;
  animation: textSlideUp 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94) 0.4s both;
}

/* 메인 로고 등장 애니메이션 */
@keyframes gameLogoReveal {
  0% {
    transform: translate(-50%, -50%) scale(0.3) rotateY(-180deg);
    opacity: 0;
  }
  30% {
    transform: translate(-50%, -50%) scale(1.1) rotateY(-45deg);
    opacity: 0.7;
  }
  60% {
    transform: translate(-50%, -50%) scale(0.95) rotateY(10deg);
    opacity: 0.9;
  }
  80% {
    transform: translate(-50%, -50%) scale(1.02) rotateY(-5deg);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(1) rotateY(0deg);
    opacity: 1;
  }
}

/* 로고 글로우 효과 */
@keyframes logoGlow {
  0% {
    filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.2))
            drop-shadow(0 0 30px rgba(255, 105, 180, 0.1));
  }
  100% {
    filter: drop-shadow(0 0 25px rgba(255, 255, 255, 0.4))
            drop-shadow(0 0 50px rgba(255, 105, 180, 0.2))
            drop-shadow(0 0 80px rgba(64, 224, 255, 0.1));
  }
}

/* 텍스트 슬라이드 업 */
@keyframes textSlideUp {
  0% {
    transform: translateY(30px);
    opacity: 0;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 블러리한 페이드아웃 효과 */
@keyframes fadeOutBlur {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
    filter: blur(0px);
  }
  50% {
    transform: translate(-50%, -50%) scale(0.95);
    opacity: 0.5;
    filter: blur(2px);
  }
  100% {
    transform: translate(-50%, -50%) scale(0.85);
    opacity: 0;
    filter: blur(8px);
  }
}
</style>
