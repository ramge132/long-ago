import endingCardBack from "@/assets/cards/ending_short.svg"
import storyCardBack from "@/assets/cards/story_short.svg"

// 스토리 카드 이미지 매핑 함수
const getStoryCardImage = (cardId) => {
  try {
    // 동적 import를 위한 require 사용
    return new URL(`/src/assets/cards/story/story_${cardId}.png`, import.meta.url).href
  } catch (error) {
    // 스토리 카드 이미지를 찾을 수 없음
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
    // 엔딩 카드 이미지를 찾을 수 없음
    // 기본 카드 뒷면 반환
    return endingCardBack
  }
}

// 엔딩 카드 이미지 프리로딩 함수
const preloadEndingCardImages = (cardIds = []) => {
  return Promise.all(
    cardIds.map(cardId => {
      return new Promise((resolve, reject) => {
        const img = new Image()
        img.onload = () => {
          // 엔딩 카드 프리로드 성공
          resolve(cardId)
        }
        img.onerror = () => {
          // 엔딩 카드 프리로드 실패 시 무시
          resolve(cardId) // resolve anyway to not block other images
        }
        img.src = getEndingCardImage(cardId)
      })
    })
  )
}

// 스토리 카드 이미지 프리로딩 함수
const preloadStoryCardImages = (cardIds = []) => {
  return Promise.all(
    cardIds.map(cardId => {
      return new Promise((resolve, reject) => {
        const img = new Image()
        img.onload = () => {
          // 스토리 카드 프리로드 성공
          resolve(cardId)
        }
        img.onerror = () => {
          // 스토리 카드 프리로드 실패 시 무시
          resolve(cardId) // resolve anyway to not block other images
        }
        img.src = getStoryCardImage(cardId)
      })
    })
  )
}

// 모든 엔딩 카드 이미지 프리로딩 (1-19번)
const preloadAllEndingCards = () => {
  const allEndingCardIds = Array.from({length: 19}, (_, i) => i + 1)
  return preloadEndingCardImages(allEndingCardIds)
}

// 특정 플레이어의 카드들만 프리로딩 (게임 시작 시 사용)
const preloadPlayerCards = (storyCardIds = [], endingCardId = null) => {
  const promises = []

  // 스토리 카드들 프리로드
  if (storyCardIds.length > 0) {
    promises.push(preloadStoryCardImages(storyCardIds))
  }

  // 엔딩 카드 프리로드
  if (endingCardId) {
    promises.push(preloadEndingCardImages([endingCardId]))
  }

  return Promise.all(promises)
}

export default {
    endingCardBack,
    storyCardBack,
    getStoryCardImage,
    getEndingCardImage,
    preloadEndingCardImages,
    preloadStoryCardImages,
    preloadAllEndingCards,
    preloadPlayerCards,
}