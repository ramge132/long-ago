<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- 배경 오버레이 -->
    <div class="absolute inset-0 bg-black bg-opacity-50"></div>

    <!-- 교환 신청 수신 모달 -->
    <div class="relative bg-white rounded-lg shadow-lg p-6 max-w-lg w-full mx-4">
      <div class="text-center">
        <h3 class="text-xl font-semibold mb-4">카드 교환 신청</h3>

        <!-- 신청자 정보 -->
        <div class="mb-4 p-3 bg-blue-50 rounded-lg">
          <p class="text-lg font-medium">
            <span class="text-blue-600">{{ senderName }}</span>님이
            <span class="text-green-600">{{ senderCard.keyword }}</span> 카드 교환을 신청했습니다.
          </p>
        </div>

        <!-- 교환할 카드 정보 -->
        <div class="flex justify-center items-center mb-6 gap-4">
          <!-- 상대방 카드 -->
          <div class="text-center">
            <p class="text-sm text-gray-600 mb-2">{{ senderName }}의 카드</p>
            <img :src="CardImage.getStoryCardImage(senderCard.id)" :alt="`스토리카드 ${senderCard.keyword}`" class="w-20 mx-auto">
            <p class="mt-1 font-medium">{{ senderCard.keyword }}</p>
          </div>

          <!-- 교환 화살표 -->
          <div class="text-2xl text-gray-400">⇄</div>

          <!-- 내 카드 (선택 영역) -->
          <div class="text-center">
            <p class="text-sm text-gray-600 mb-2">교환할 내 카드</p>
            <div v-if="!selectedMyCard" class="w-20 h-28 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center mx-auto">
              <span class="text-xs text-gray-400">선택하세요</span>
            </div>
            <div v-else>
              <img :src="CardImage.getStoryCardImage(selectedMyCard.id)" :alt="`스토리카드 ${selectedMyCard.keyword}`" class="w-20 mx-auto">
              <p class="mt-1 font-medium">{{ selectedMyCard.keyword }}</p>
            </div>
          </div>
        </div>

        <!-- 내 카드 목록 -->
        <div class="mb-6">
          <p class="text-sm text-gray-600 mb-2">교환할 카드를 선택하세요:</p>
          <div class="grid grid-cols-4 gap-2">
            <div
              v-for="card in myCards"
              :key="card.id"
              @click="selectMyCard(card)"
              class="cursor-pointer border-2 rounded-lg p-1 transition-colors duration-200"
              :class="selectedMyCard?.id === card.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-400'"
            >
              <img :src="CardImage.getStoryCardImage(card.id)" :alt="`스토리카드 ${card.keyword}`" class="w-full">
              <p class="text-xs text-center mt-1">{{ card.keyword }}</p>
            </div>
          </div>
        </div>

        <!-- 버튼들 -->
        <div class="flex space-x-3">
          <button
            @click="acceptExchange"
            :disabled="!selectedMyCard"
            class="flex-1 py-3 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors duration-200"
          >
            교환 수락
          </button>
          <button
            @click="rejectExchange"
            class="flex-1 py-3 px-4 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-colors duration-200"
          >
            거절하기
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import CardImage from "@/assets/cards"

const props = defineProps({
  show: Boolean,
  senderName: {
    type: String,
    default: ''
  },
  senderCard: {
    type: Object,
    default: () => ({ id: 0, keyword: '' })
  },
  myCards: {
    type: Array,
    default: () => []
  },
  exchangeData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['close', 'accept', 'reject'])

const selectedMyCard = ref(null)

const selectMyCard = (card) => {
  selectedMyCard.value = card
}

const acceptExchange = () => {
  if (selectedMyCard.value) {
    emit('accept', {
      ...props.exchangeData,
      toCardId: selectedMyCard.value.id
    })
  }
}

const rejectExchange = () => {
  emit('reject', props.exchangeData)
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