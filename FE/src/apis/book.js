// src/apis/book.js
import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_MAIN_API_SERVER_URL, // API의 기본 URL을 설정하세요.
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false,
});

// 책 조회
export const getBook = async (data) => {
    try {
        const params = data;
        const response = await apiClient.get("/apis/book", {params});
        return response;
    } catch (error) {
        console.log(error);
        throw error;
    }
}