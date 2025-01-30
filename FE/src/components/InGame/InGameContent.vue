<template>
  <div
    class="col-span-3 row-span-1 bg-red-400 flex flex-col items-center justify-center relative overflow-hidden pt-10"
  >
    <ContentTimer />
    <ContentBook />
  </div>
</template>

<script setup>
import { ContentTimer, ContentBook } from "@/components";
</script>

<style scoped></style>
