<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- 배경 오버레이 -->
    <div class="absolute inset-0 bg-black bg-opacity-50" @click="closeMenu"></div>

    <!-- 메뉴 모달 -->
    <div class="relative bg-white rounded-lg shadow-lg p-6 max-w-sm w-full mx-4">
      <div class="text-center">
        <!-- 선택된 카드 표시 -->
        <div class="mb-4">
          <img :src="CardImage.getStoryCardImage(selectedCard.id)" :alt="`스토리카드 ${selectedCard.keyword}`" class="w-24 mx-auto">
          <h3 class="mt-2 text-lg font-semibold">{{ selectedCard.keyword }}</h3>
        </div>

        <!-- 버튼들 -->
        <div class="space-y-3">
          <!-- 교환하기 버튼 -->
          <button
            @click="openExchangeModal"
            :disabled="exchangeCount <= 0"
            class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors duration-200"
          >
            교환하기 ({{ exchangeCount }}회 남음)
          </button>

          <!-- 새로고침 버튼 -->
          <button
            @click="refreshCard"
            :disabled="refreshCount <= 0"
            class="w-full py-3 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-colors duration-200"
          >
            새로고침 ({{ refreshCount }}회 남음)
          </button>

          <!-- 취소 버튼 -->
          <button
            @click="closeMenu"
            class="w-full py-3 px-4 bg-gray-400 hover:bg-gray-500 text-white rounded-lg font-semibold transition-colors duration-200"
          >
            취소
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'
import CardImage from "@/assets/cards"

const props = defineProps({
  show: Boolean,
  selectedCard: {
    type: Object,
    default: () => ({ id: 0, keyword: '' })
  },
  exchangeCount: {
    type: Number,
    default: 3
  },
  refreshCount: {
    type: Number,
    default: 3
  }
})

const emit = defineEmits(['close', 'exchange', 'refresh'])

const closeMenu = () => {
  emit('close')
}

const openExchangeModal = () => {
  if (props.exchangeCount > 0) {
    emit('exchange')
  }
}

const refreshCard = () => {
  if (props.refreshCount > 0) {
    emit('refresh')
  }
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