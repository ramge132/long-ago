<template>
  <div
    class="flex flex-col w-full h-full items-center justify-center p-5 gap-y-5"
  >
    <img :src="Logo" alt="로고" class="w-52" />
    <div class="w-full h-full grid grid-cols-3 gap-x-5">
      <LobbyUsers
        :participants="props.participants"
        :connectedPeers="props.connectedPeers"
        :receivedMessages="props.receivedMessages"
        @broadcast-message="broadcastMessage"
      />
      <LobbySettings
        :configurable="props.configurable"
        :connectedPeers="props.connectedPeers"
        :roomConfigs="props.roomConfigs"
        @room-configuration="onRoomConfiguration"
        @open-modal="toggleModal"
      />
      <Transition name="fade">
        <div
          v-if="isOpen"
          @click="toggleModal"
          class="absolute bg-[#00000050] w-full h-full top-0 left-0 flex justify-center items-center"
        >
          <div
            @click.stop
            class="w-96 h-28 text-[#ffffff] text-xl rounded-xl overflow-hidden flex flex-col"
          >
            <div
              class="flex-1 max-w-full bg-[#00000090] overflow-auto flex items-center justify-center"
            >
              <div class="w-11/12">
                <p>초대링크</p>
                <div class="w-full flex">
                  <input
                    type="text"
                    class="bg-white rounded-xl pl-3 grow text-black text-sm mr-3"
                    :value="props.InviteLink"
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
import { ref, defineProps } from "vue";
import { Logo, CopyIcon } from "@/assets";
import useCilpboard from "vue-clipboard3";
import toast from "@/functions/toast";
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
});

const emit = defineEmits(["broadcastMessage", "onRoomConfiguration"]);

const broadcastMessage = (data) => {
  emit("broadcastMessage", data);
};
const onRoomConfiguration = (data) => {
  emit("onRoomConfiguration", data);
};

const { toClipboard } = useCilpboard();

// 초대 링크 표시
const isOpen = ref(false);
const toggleModal = () => {
  isOpen.value = !isOpen.value;
};

// 초대링크 클립보드 복사
const copy = async () => {
  try {
    await toClipboard(props.InviteLink);
    toast.successToast("클립보드에 복사되었습니다.");
    isOpen.value = false;
  } catch (error) {
    console.error(error);
  }
};
</script>
