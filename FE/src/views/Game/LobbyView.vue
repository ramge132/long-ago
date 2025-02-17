<template>
  <div
    class="flex flex-col w-full h-full items-center justify-center p-5 gap-y-5"
  >
    <RouterLink to="/">
      <img :src="Logo" alt="로고" class="w-52" />
    </RouterLink>
    <div class="w-full flex-1 grid grid-cols-3 gap-x-5">
      <LobbyUsers
        :participants="props.participants"
        :connectedPeers="props.connectedPeers"
        :receivedMessages="props.receivedMessages"
        @broadcast-message="broadcastMessage"
      />
      <LobbySettings
        :configurable="props.configurable"
        :participants="props.participants"
        :roomConfigs="props.roomConfigs"
        :gameStarted="props.gameStarted"
        :InviteLink="props.InviteLink"
        :peerId="props.peerId"
        @room-configuration="onRoomConfiguration"
        @game-start="gameStart"
      />
    </div>
  </div>
</template>

<script setup>
import { defineProps } from "vue";
import { Logo } from "@/assets";
import { LobbyUsers, LobbySettings } from "@/components";

const props = defineProps({
  roomConfigs: {
    Type: Object,
  },
  connectedPeers: {
    Type: Array,
  },
  configurable: {
    Type: Boolean,
  },
  receivedMessages: {
    Type: Array,
  },
  participants: {
    Type: Array,
  },
  InviteLink: {
    Type: String,
  },
  gameStarted: {
    Type: Boolean,
  },
  peerId: {
    Type: String,
  },
});

const emit = defineEmits([
  "broadcastMessage",
  "onRoomConfiguration",
  "gameStart",
]);

const broadcastMessage = (data) => {
  emit("broadcastMessage", data);
};
const onRoomConfiguration = (data) => {
  emit("onRoomConfiguration", data);
};
const gameStart = (data) => {
  emit("gameStart", data);
};
</script>
