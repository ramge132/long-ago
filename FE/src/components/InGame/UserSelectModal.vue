<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- 화이트 글래스모피즘 사용자 선택 모달 -->
    <div class="relative glassmorphism-white rounded-2xl p-5 max-w-xs w-full mx-4">
      <div class="text-center">
        <h3 class="text-base font-bold text-gray-800 mb-3">교환할 플레이어</h3>

        <!-- 플레이어 목록 -->
        <div class="space-y-2 mb-3">
          <button
            v-for="participant in filteredParticipants"
            :key="participant.id"
            @click="selectUser(participant)"
            class="w-full glassmorphism-white hover:bg-white/30 rounded-xl p-3 transition-all duration-200 flex items-center"
          >
            <img :src="participant.image" :alt="participant.name" class="w-7 h-7 rounded-full mr-3">
            <span class="text-gray-700 font-medium">{{ participant.name }}</span>
          </button>
        </div>

        <!-- 취소 버튼 -->
        <button
          @click="closeModal"
          class="w-full glassmorphism-white hover:bg-white/30 rounded-xl py-2 px-4 text-gray-700 font-medium transition-all duration-200"
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