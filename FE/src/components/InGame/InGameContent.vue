<template>
  <div
    class="flex flex-col items-center justify-center overflow-hidden gap-y-4"
  >
    <ContentTimer />
    <ContentGuage />
    <ContentBook />
  </div>
</template>

<script setup>
import { ContentTimer, ContentBook, ContentGuage } from "@/components";
</script>

<style scoped></style>
