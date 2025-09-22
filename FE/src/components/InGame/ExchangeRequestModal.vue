<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- 배경 오버레이 (투명) -->
    <div class="absolute inset-0 bg-black/20"></div>

    <!-- 화이트 글래스모피즘 교환 신청 수신 모달 -->
    <div class="relative glassmorphism-white rounded-2xl p-6 max-w-md w-full mx-4">
      <div class="text-center">
        <h3 class="text-lg font-bold text-gray-800 mb-4">카드 교환 신청</h3>

        <!-- 신청자 정보 -->
        <div class="glassmorphism-white rounded-xl p-3 mb-4">
          <p class="text-gray-700 text-sm">
            <span class="font-semibold text-blue-600">{{ senderName }}</span>님이
            <span class="text-green-600 font-medium">{{ senderCard.keyword }}</span> 카드 교환을 신청했습니다.
          </p>
        </div>

        <!-- 교환할 카드 정보 -->
        <div class="flex justify-center items-center mb-4 gap-3">
          <!-- 상대방 카드 -->
          <div class="text-center">
            <img :src="CardImage.getStoryCardImage(senderCard.id)" :alt="`스토리카드 ${senderCard.keyword}`" class="w-16 mx-auto mb-1">
            <p class="text-gray-700 text-xs font-medium">{{ senderCard.keyword }}</p>
          </div>

          <!-- 교환 화살표 -->
          <div class="text-gray-600 text-xl">⇄</div>

          <!-- 내 카드 (선택 영역) -->
          <div class="text-center">
            <div v-if="!selectedMyCard" class="w-16 h-20 border-2 border-dashed border-gray-400 rounded-lg flex items-center justify-center mx-auto mb-1">
              <span class="text-xs text-gray-500">선택</span>
            </div>
            <div v-else>
              <img :src="CardImage.getStoryCardImage(selectedMyCard.id)" :alt="`스토리카드 ${selectedMyCard.keyword}`" class="w-16 mx-auto mb-1">
              <p class="text-gray-700 text-xs font-medium">{{ selectedMyCard.keyword }}</p>
            </div>
          </div>
        </div>

        <!-- 내 카드 목록 -->
        <div class="mb-4">
          <p class="text-gray-700 text-xs mb-2">교환할 카드를 선택하세요:</p>
          <div class="grid grid-cols-4 gap-1">
            <div
              v-for="card in myCards"
              :key="card.id"
              @click="selectMyCard(card)"
              class="cursor-pointer rounded-lg p-1 transition-all duration-200"
              :class="selectedMyCard?.id === card.id ? 'glassmorphism-white border border-blue-300' : 'hover:bg-white/20'"
            >
              <img :src="CardImage.getStoryCardImage(card.id)" :alt="`스토리카드 ${card.keyword}`" class="w-full rounded">
              <p class="text-xs text-center mt-1 text-gray-700">{{ card.keyword }}</p>
            </div>
          </div>
        </div>

        <!-- 버튼들 (macOS 스타일) -->
        <div class="flex space-x-3">
          <button
            @click="acceptExchange"
            :disabled="!selectedMyCard"
            class="flex-1 py-3 px-4 rounded-xl font-semibold transition-all duration-200 shadow-sm border"
            :class="selectedMyCard
              ? 'bg-blue-500 hover:bg-blue-600 text-white border-blue-500'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed border-gray-300'"
          >
            수락
          </button>
          <button
            @click="rejectExchange"
            class="flex-1 py-3 px-4 bg-white hover:bg-gray-50 border border-gray-300 rounded-xl text-gray-700 font-semibold transition-all duration-200 shadow-sm"
          >
            거절
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
/* 화이트 글래스모피즘 효과 */
.glassmorphism-white {
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
}

/* 모달 애니메이션 */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
</style>