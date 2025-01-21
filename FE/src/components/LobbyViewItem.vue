<template>
    <div class="w-[80%] h-[80%] border drop-shadow-md rounded-xl grid grid-cols-7"> 
        <div class="col-span-4 grid grid-rows-7">
        
                <label>1턴 당 시간</label>
                <div>
                    <span class="mx-2" v-for="n in 6">{{ n + 9 }}</span>
                    <input type="range" min="10" max="15" step="1" class="range-slider">
                </div>
           
            </div>
            <div class="col-span-4 row-span-5">
                dasd
            </div>
        <div class="col-span-3 row-span-2">
            sdaa
        </div>
        <div class="col-span-3 row-span-5">
        wqeqwe
        </div>
        
    </div>
</template>

<script setup>

</script>

<style scoped>

</style>
