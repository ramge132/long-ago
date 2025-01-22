<template>
  <div>
    <form
      @submit.prevent="signin"
      class="w-full flex flex-col items-center gap-y-1 font-hs text-sm"
      novalidate
    >
      <div class="relative w-4/5 group">
        <label for="id">아이디</label>
        <input
          v-model="id"
          type="text"
          id="id"
          placeholder=" "
          required
          class="h-4 w-full p-3 border-2 border-gray-300 rounded-md text-base text-black focus:outline-none focus:ring-2 focus:ring-[#E5E091] focus:border-[#E5E091]"
          :class="id ? 'ring-2 ring-[#E5E091] border-[#E5E091]' : ''"
          autocomplete="off"
        />
        <p v-if="validation.idError" class="text-red-900 text-xs mt-1">
          {{ validation.idError }}
        </p>
      </div>

      <!-- 비밀번호 입력 -->
      <div class="relative w-4/5 group">
        <label for="password">비밀번호</label>
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
        <p v-if="validation.pwError" class="text-red-900 text-xs mt-1">
          {{ validation.pwError }}
        </p>
      </div>

      <!-- 구글 로그인 -->
      <div
        id="google-login-button"
        class="flex items-center justify-center cursor-pointer h-5"
      ></div>

      <!-- 카카오 로그인 -->
      <!-- <img
        :src="kakao"
        alt="카카오 로그인"
        class="w-4/5 cursor-pointer"
        @click="kakaoRegister"
        /> -->

      <!-- 비밀번호 찾기 -->
      <div>
        <span
          @click="findMyPassword"
          class="cursor-pointer text-gray-300 hover:text-black"
          >비밀번호 찾기</span
        >
      </div>

      <!-- 로그인 버튼 -->
      <button
        type="submit"
        class="w-2/5 h-8 bg-[#505050] text-white py-2 font-semibold hover:bg-[#E5E091] hover:text-black transition-all rounded cursor-pointer"
      >
        로그인
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, defineEmits } from "vue";
import { postSignIn } from "@/apis/auth";
import toast from "@/functions/toast";
// import kakao from "@/assets/icons/kakao.png";

const id = ref("");
const password = ref("");
const validation = ref({
  idError: "",
  pwError: "",
});

const emit = defineEmits(["signIn"]);

// const kakaoRegister = () => {
//   console.log("카카오 로그인");
// };

const authValidation = () => {
  const passwordRegex =
    /^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/;

  validation.value.idError =
    id.value.length < 5 ? "아이디는 5자리 이상 입력해주세요." : "";
  validation.value.pwError =
    password.value.length < 8
      ? "비밀번호는 8자 이상이어야 합니다."
      : !passwordRegex.test(password.value)
        ? "비밀번호는 영문, 숫자, 특수문자를 각각 최소 1개 이상 포함해야 합니다."
        : "";

  return !validation.value.idError && !validation.value.pwError;
};

const handleGoogleLogin = (response) => {
  const data = jwtDecode(response.credential);
  console.log("Google User Data:", data);
};

const jwtDecode = (token) => {
  const base64Url = token.split(".")[1];
  const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split("")
      .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
      .join(""),
  );
  return JSON.parse(jsonPayload);
};

const signin = async () => {
  if (authValidation) {
    try {
      const response = await postSignIn({
        username: id.value,
        password: password.value,
      });
      toast.successToast(`반갑습니다. ${id.value}님!`);
      emit("signIn", id.value);
      console.log(response);
    } catch (error) {
      console.log("에러", error);
      toast.errorToast("error");
    }
  }
};

/* global google */
onMounted(() => {
  const script = document.createElement("script");
  script.src = "https://accounts.google.com/gsi/client";
  script.async = true;
  script.onload = () => {
    google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      callback: handleGoogleLogin,
    });
    google.accounts.id.renderButton(
      document.getElementById("google-login-button"),
      { theme: "outline", size: "small", width: "158" },
    );
  };
  document.head.appendChild(script);
});
</script>
