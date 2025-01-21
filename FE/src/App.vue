<template>
  <div
    class="bg-no-repeat bg-cover bg-center bg-fairytail-image w-screen h-screen flex flex-col justify-center items-center"
  >
    <div
      class="relative border-dashed border-2 border-black rounded-lg shadow-md w-2/3 h-3/4 max-w-4xl max-h-[1000px] min-w-[800px] bg-[#ffffff80] flex flex-col justify-center items-center"
    >
      <RouterView v-slot="{ Component }">
        <Transition name="fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </div>
  </div>
</template>

<script setup></script>

<style>
/* Enter 애니메이션 (슬라이드 없이 나타남) */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease-in-out; /* opacity로 부드럽게 나타남 */
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0; /* 컴포넌트가 처음에는 안 보이게 설정 */
}
</style>
