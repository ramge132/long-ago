<template>
  <div>
    <form
      @submit.prevent="signin"
      class="w-full flex flex-col items-center mb-12 gap-y-1"
      novalidate
    >
      <p class="text-3xl">회원가입</p>
      <div class="relative w-4/5 group">
        <label for="steam-id" class="text-gray-500 font-semibold">
          닉네임
        </label>
        <input
          v-model="id"
          type="text"
          id="steam-id"
          placeholder=" "
          required
          class="h-4 w-full p-3 border-2 border-gray-300 rounded-md text-base text-black focus:outline-none focus:ring-2 focus:ring-[#E5E091] focus:border-[#E5E091]"
          :class="password ? 'ring-2 ring-[#E5E091] border-[#E5E091]' : ''"
          autocomplete="off"
        />
        <p v-if="validation.idError" class="text-red-500 text-xs mt-1">
          {{ validation.idError }}
        </p>
      </div>

      <!-- 비밀번호 입력 -->
      <div class="relative w-4/5 mb-4 group">
        <label for="password" class="text-gray-500 font-semibold">
          비밀번호
        </label>
        <input
          v-model="password"
          type="password"
          id="password"
          placeholder=" "
          required
          class="h-4 w-full p-3 border-2 border-gray-300 rounded-md text-base text-black focus:outline-none focus:ring-2 focus:ring-[#E5E091] focus:border-[#E5E091]"
          :class="password ? 'ring-2 ring-[#E5E091] border-[#E5E091]' : ''"
          autocomplete="off"
        />
        <p v-if="validation.pwError" class="text-red-500 text-xs mt-1">
          {{ validation.pwError }}
        </p>
      </div>

      <div>
        <span
          @click="emit('signin')"
          class="cursor-pointer text-gray-600 hover:text-black"
          >이미 회원이신가요? 로그인하기.</span
        >
      </div>

      <!-- 로그인 버튼 -->
      <button
        type="submit"
        class="absolute bottom-0 w-full h-12 bg-[#505050] text-white py-2 font-semibold hover:bg-[#E5E091] hover:text-black transition-all rounded-b-3xl"
      >
        회원가입
      </button>
    </form>
  </div>
</template>
<script setup>
import { ref, defineEmits } from "vue";

const id = ref("");
const password = ref("");
const validation = ref({
  idError: "",
  pwError: "",
});

const emit = defineEmits(["signin"]);

const authValidation = () => {
  // 비밀번호 정규식 (영문, 숫자, 특수문자 각각 최소 1개 이상, 총 8자리 이상)
  const passwordRegex =
    /^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;

  // 아이디 유효성 검사사
  if (!id.value || id.value.length < 5) {
    validation.value.idError = "아이디는 5자리 이상 입력해주세요.";
  } else {
    validation.value.idError = "";
  }

  // 비밀번호 유효성 검사
  if (!password.value || password.value.length < 8) {
    validation.value.pwError = "비밀번호는 8자 이상이어야 합니다.";
  } else if (!passwordRegex.test(password.value)) {
    validation.value.pwError =
      "비밀번호는 영문, 숫자, 특수문자를 각각 최소 1개 이상 포함해야 합니다.";
  } else {
    validation.value.pwError = "";
  }

  if (validation.value.idError || validation.value.pwError) {
    return false;
  } else {
    return true;
  }
};

const signin = async () => {
  console.log(authValidation());
  console.log("아이디:", id.value);
  console.log("비밀번호:", password.value);
};
</script>
<style></style>
