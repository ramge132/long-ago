import endingCardBack from "@/assets/cards/ending_short.svg"
import storyCardBack from "@/assets/cards/story_short.svg"

// 스토리 카드 이미지 매핑 함수
const getStoryCardImage = (cardId) => {
  try {
    // 동적 import를 위한 require 사용
    return new URL(`/src/assets/cards/story/story_${cardId}.png`, import.meta.url).href
  } catch (error) {
    console.warn(`Story card image not found for ID: ${cardId}`)
    // 기본 카드 뒷면 반환
    return storyCardBack
  }
}

// 엔딩 카드 이미지 매핑 함수
const getEndingCardImage = (cardId) => {
  try {
    // 동적 import를 위한 require 사용
    return new URL(`/src/assets/cards/ending/ending_${cardId}.png`, import.meta.url).href
  } catch (error) {
    console.warn(`Ending card image not found for ID: ${cardId}`)
    // 기본 카드 뒷면 반환
    return endingCardBack
  }
}

export default {
    endingCardBack,
    storyCardBack,
    getStoryCardImage,
    getEndingCardImage,
}