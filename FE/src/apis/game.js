// src/apis/auth.js
import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_MAIN_API_SERVER_URL, // API의 기본 URL을 설정하세요.
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false,
});

// 게임 api 부분

// 방 생성 (방장인 경우만 요청하면 됩니둥~)
export const createGame = async (data) => {
  try {
    const response = await apiClient.post(import.meta.env.VITE_GAME, data);
    return response;
  } catch (error) {
    console.log(error);
    throw error;
  }
}

// 방 입장 (방장 외 참가자들만 요청하면 됩니둥둥~~)
export const enterGame = async (data) => {
  try {
    const params = data;
    const response = await apiClient.get(
      import.meta.env.VITE_GAME, {params}
    );
    return response;
  } catch (error) {
    console.log(error);
    throw error;
  }
}

// 방 삭제 (방장만 게임 종료 시 삭제하면 됩니둥둥둥~)
export const deleteGame = async (data) => {
  try {
    const response = await apiClient.delete(import.meta.env.VITE_GAME, {data: data});
    return response;
  } catch (error) {
    console.log(error);
    throw error;
  }
}

// 엔딩카드 리롤하는 겁니둥둥둥둥둥둥
export const endingCardReroll = async (data) => {
  try {
    const response = await apiClient.patch(import.meta.env.VITE_GAME + import.meta.env.VITE_GAME_SHUFFLE,
      {},
      { params: { gameId: data.gameId, userId: data.userId } }
    );
    return response;
  } catch (error) {
    console.log(error);
    throw error;
  }
}


// 프롬프트 필터링
export const promptFiltering = async (data) => {
  try {
    const response = await apiClient.post(import.meta.env.VITE_SCENE + import.meta.env.VITE_SCENE_FILTERING, data);
    return response;
  } catch(error) {
    console.log(error);
    throw error;
  }
}


// 이미지 생성 부분
export const createImage = async (data) => {
  try {
    const response = await apiClient.post(import.meta.env.VITE_SCENE, data, { responseType: "blob", });
    return response;
  } catch(error) {
    console.log(error);
    throw error;
  }
}

// 투표 결과 반대 시 이미지 삭제
export const voteResultSend = async (data) => {
  try {
    const response = await apiClient.post(import.meta.env.VITE_SCENE + import.meta.env.VITE_SCENE_VOTE, data);
    return response;
  } catch(error) {
    console.log(error);
    throw error;
  }
} 

// 시연 모드 게임 시작
export const testGame = async (data) => {
  try {
    const response = await apiClient.post("/apis/game/test", data);
    return response;
  } catch (error) {
    console.log(error);
    throw error;
  }
}