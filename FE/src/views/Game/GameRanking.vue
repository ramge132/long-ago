<template>
    <div class="relative w-full h-full grid grid-cols-5 grid-rows-3">
        <div></div>
        <!-- 좌측 낮은 포디움 -->
        <div class="w-full h-full row-span-2 col-span-1 place-content-end">
            <div class="bg-gray-300 w-full h-24 row-span-2 col-span-1"></div>
        </div>
        
        <!-- 중앙 가장 높은 포디움 -->
        <div class="w-full h-full row-span-2 col-span-1 place-content-end">
            <div>test</div>
            <div class="bg-yellow-400 w-full h-48 row-span-2 col-span-1"></div>
        </div>
        
        <!-- 우측 중간 포디움 -->
        <div class="w-full h-full row-span-2 col-span-1 place-content-end">
            <div class="bg-gray-400 w-full h-32 row-span-2 col-span-1"></div>
        </div>

        <div class="absolute top-4 right-4 cursor-pointer" @click="goLobby">로비로 돌아가기</div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goLobby = () => {
    router.push("/game/lobby");
};
</script>

<style scoped>
</style>
