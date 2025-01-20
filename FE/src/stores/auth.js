import { defineStore } from "pinia";

export const useUserStore = defineStore("userData", {
  state: () => ({
    userData: {
      userEmail: localStorage.getItem("userEmail"),
      userNickname: localStorage.getItem("userNickname"),
    },
  }),
  actions: {
    setUserEmail(data) {
      this.userData.userEmail = data;
    },
    setUserNickname(data) {
      this.userData.userNickname = data;
    },
    clearUserData() {
      this.userData = {
        id: null,
        username: "",
        email: "",
        nickname: "",
        role: "",
      };
    },
  },
});
