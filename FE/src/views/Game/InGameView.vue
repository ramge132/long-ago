<template>
  <div class="w-full h-full grid grid-cols-5 grid-rows-2">
    <div class="col-span-1 row-span-2 bg-slate-400">test</div>
    <InGameContent />
    <div class="col-span-1 row-span-2 bg-yellow-400">test3</div>
    <div class="col-span-3 row-span-1 bg-green-400">test4</div>
  </div>
</template>
<script setup>
import { InGameContent } from "@/components";
</script>
<style></style>
