<template>
    <div
      @click="closeEBook"
      class="absolute bg-[#00000050] w-full h-full top-0 left-0 flex justify-center items-center"
    >
      <div
        @click.stop
        class="rounded-lg w-4/5 h-5/6 max-w-6xl max-h-[700px] min-w-[1000px] min-h-[600px] bg-[#ffffff70] border-[1px] border-white backdrop-blur-[15px] flex flex-col gap-y-8 justify-center items-center"
      >
        <!-- 책 -->
        <div class="relative w-[600px] h-[400px]">
          <InGameContent :bookContents="bookContents" :bookCover="bookCover" />
        </div>

        <div @click="closeEBook" class="bg-black rounded-xl cursor-pointer w-40 h-10">
            <div class="w-full h-full flex gap-x-2 justify-center items-center hover:scale-110 transition-transform">
                <img :src="StartIcon" alt="시작하기 아이콘" class="h-5 w-5">
                <span class="text-white">메인으로</span>
            </div>
        </div>
      </div>
    </div>
</template>
<script setup>
import { ref, onMounted } from "vue";
import { InGameContent } from "@/components";
import { StartIcon } from "@/assets";
import { getBook } from "@/apis/book";

const props = defineProps({
    ISBN: {
        Type: String,
    },
})
const emit = defineEmits(["closeEBook"]);

const bookContents = ref([{content: "", image: null}])
const bookCover = ref({
  imageUrl: "",
  title: "",
});

const closeEBook = () => {
    emit("closeEBook");
};

onMounted(async () => {
  try {
    const response = await getBook({ id: props.ISBN });

    bookCover.value = {
      imageUrl: response.data.bookCover,
      title: response.data.data.title,
    };

    bookContents.value = response.data.data.sceneResponseList
      .sort((a, b) => a.order - b.order) // order 오름차순 정렬
      .map(scene => ({
        content: scene.prompt,  // prompt -> content
        image: scene.imageUrl   // imageUrl -> image
      }));

  } catch (error) {
    console.error(error);
  }
    
});
</script>
<style scoped>
    
</style>