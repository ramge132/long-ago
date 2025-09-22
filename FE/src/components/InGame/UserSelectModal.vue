<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- 배경 오버레이 -->
    <div class="absolute inset-0 bg-black bg-opacity-50" @click="closeModal"></div>

    <!-- 사용자 선택 모달 -->
    <div class="relative bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
      <div class="text-center">
        <h3 class="text-xl font-semibold mb-4">교환할 플레이어 선택</h3>

        <!-- 선택된 카드 정보 -->
        <div class="mb-4 p-3 bg-gray-100 rounded-lg">
          <p class="text-sm text-gray-600">교환할 카드:</p>
          <div class="flex items-center justify-center mt-2">
            <img :src="CardImage.getStoryCardImage(selectedCard.id)" :alt="`스토리카드 ${selectedCard.keyword}`" class="w-16 mr-2">
            <span class="font-semibold">{{ selectedCard.keyword }}</span>
          </div>
        </div>

        <!-- 플레이어 목록 -->
        <div class="space-y-2 mb-4">
          <button
            v-for="participant in filteredParticipants"
            :key="participant.id"
            @click="selectUser(participant)"
            class="w-full p-3 border border-gray-300 hover:border-blue-500 hover:bg-blue-50 rounded-lg transition-colors duration-200 flex items-center"
          >
            <img :src="participant.image" :alt="participant.name" class="w-8 h-8 rounded-full mr-3">
            <span class="font-medium">{{ participant.name }}</span>
          </button>
        </div>

        <!-- 취소 버튼 -->
        <button
          @click="closeModal"
          class="w-full py-2 px-4 bg-gray-400 hover:bg-gray-500 text-white rounded-lg font-semibold transition-colors duration-200"
        >
          취소
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits } from 'vue'
import CardImage from "@/assets/cards"

const props = defineProps({
  show: Boolean,
  selectedCard: {
    type: Object,
    default: () => ({ id: 0, keyword: '' })
  },
  participants: {
    type: Array,
    default: () => []
  },
  myId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'selectUser'])

// 자신을 제외한 참가자 목록
const filteredParticipants = computed(() => {
  return props.participants.filter(p => p.id !== props.myId)
})

const closeModal = () => {
  emit('close')
}

const selectUser = (participant) => {
  emit('selectUser', participant)
}
</script>

<style scoped>
/* 모달 애니메이션 */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
</style>