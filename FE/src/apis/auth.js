// src/apis/auth.js
import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_MAIN_API_SERVER_URL, // API의 기본 URL을 설정하세요.
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false,
});

// API 정의 부분 

// 회원가입
export const postRegister = async (data) => {
  try {
    const response = await apiClient.post(import.meta.env.VITE_USERS, data);
    return response;
  } catch (error) {
    console.log("API 요청 에러:", error);
    throw error;
  }
};

// 로그인
export const postSignIn = async (data) => {
  try {
    const formData = new FormData();
    formData.append("username", data.username);
    formData.append("password", data.password);
    const response = await apiClient.post(
      import.meta.env.VITE_USERS_SIGNIN,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      },
    );
    return response;
  } catch (error) {
    console.log("API 요청 에러:", error);
    throw error;
  }
};
