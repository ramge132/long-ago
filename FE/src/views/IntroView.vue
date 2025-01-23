<template>
  <div class="w-full h-full flex flex-col justify-center">
    <TopBar />
    <div class="h-full">
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { TopBar } from "@/components";
import { RouterView } from "vue-router";
</script>
