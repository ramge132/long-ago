// src/apis/auth.js
import axios from "axios";

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_MAIN_API_SERVER_URL, // API의 기본 URL을 설정하세요.
    headers: {
      "Content-Type": "application/json",
    },
    withCredentials: false,
  });