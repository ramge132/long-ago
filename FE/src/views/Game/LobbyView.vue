<template>
    <div
      class="flex flex-col w-full h-full items-center justify-center p-5 gap-y-5"
    >
      <img :src="Logo" alt="로고" class="w-52" />
      <div class="w-full h-full grid grid-cols-3 gap-x-5">
        <LobbyUsers
            :participants="participants"
            :connectedPeers="connectedPeers"
            :receivedMessages="receivedMessages"
            @broadcast-message="broadcastMessage"
        />
        <LobbySettings
            :configurable="configurable"
            :connectedPeers="connectedPeers"
            :roomConfigs="roomConfigs"
            @room-configuration="onRoomConfiguration"
            @open-modal="toggleModal"
        />
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
  import { ref, onMounted } from "vue";
  import { useRoute } from "vue-router";
  import Peer from "peerjs";
  import { useUserStore } from "@/stores/auth";
  import { Logo, CopyIcon } from "@/assets";
  import useCilpboard from "vue-clipboard3";
  import toast from "@/functions/toast";
  import { LobbyUsers, LobbySettings } from "@/components";
  
  const userStore = useUserStore();
  const route = useRoute();
  const peer = ref(null);
  const peerId = ref("");
  const compressedId = ref("");
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
  const { toClipboard } = useCilpboard();
  const configurable = ref(false);
  
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
          },
          peer.connection,
        );
      });
  
      // 자신의 메시지도 표시
      receivedMessages.value.push({
        message: data.message,
        sender: data.sender,
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
              roomConfigs: roomConfigs.value
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
      toast.successToast("클립보드에 복사되었습니다.");
      isOpen.value = false;
    } catch (error) {
      console.error(error);
    }
  };
  
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
        )
    });
  };
  </script>
  