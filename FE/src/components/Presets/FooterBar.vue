<template>
    <div
      class="w-4/5 max-w-6xl min-w-[1000px] h-16 py-2 flex justify-between items-center z-10"
    >
        <div class="w-full h-full rounded-lg bg-[#00000080] flex items-center justify-between px-4 text-white">
            <div>test</div>
            <div>&copy; 2025. 아주 먼 옛날 All rights reserved.</div>
        </div>
    </div>
  </template>
  <script setup>
  import { ref } from "vue";
  import { useUserStore } from "@/stores/auth";
  import {
    TopBarFairyTail,
    TopBarHallOfFame,
    TopBarSignIn,
    Logo,
  } from "@/assets";
  import { SignIn, SignUp } from "@/components";
  
  const userStore = useUserStore();
  const isLoggedIn = ref(localStorage.getItem("userEmail") ? true : false);
  const modal = ref({
    isOpen: false,
    status: "signin",
  });
  
  const toggleModal = () => {
    modal.value.isOpen = !modal.value.isOpen;
  };
  
  const toggleSignIn = (status) => {
    modal.value.status = status;
  };
  
  const sign = (userId) => {
    localStorage.setItem("userEmail", userId);
    isLoggedIn.value = true;
    userStore.setUserEmail(userId);
    modal.value.isOpen = false;
  };
  </script>
  