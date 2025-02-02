import { defineStore } from "pinia";

export const useUserStore = defineStore("userData", {
  state: () => ({
    userData: {
      userEmail: localStorage.getItem("userEmail"),
      userNickname: localStorage.getItem("userNickname"),
      userProfile: null,
    },
  }),
  actions: {
    setUserEmail(data) {
      this.userData.userEmail = data;
    },
    setUserNickname(data) {
      this.userData.userNickname = data;
    },
    setUserProfile(data) {
      this.userData.userProfile = data;
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
