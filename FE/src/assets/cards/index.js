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

// 엔딩 카드 이미지 프리로딩 함수
const preloadEndingCardImages = (cardIds = []) => {
  return Promise.all(
    cardIds.map(cardId => {
      return new Promise((resolve, reject) => {
        const img = new Image()
        img.onload = () => {
          console.log(`Ending card ${cardId} preloaded successfully`)
          resolve(cardId)
        }
        img.onerror = () => {
          console.warn(`Failed to preload ending card ${cardId}`)
          resolve(cardId) // resolve anyway to not block other images
        }
        img.src = getEndingCardImage(cardId)
      })
    })
  )
}

// 모든 엔딩 카드 이미지 프리로딩 (1-19번)
const preloadAllEndingCards = () => {
  const allEndingCardIds = Array.from({length: 19}, (_, i) => i + 1)
  return preloadEndingCardImages(allEndingCardIds)
}

export default {
    endingCardBack,
    storyCardBack,
    getStoryCardImage,
    getEndingCardImage,
    preloadEndingCardImages,
    preloadAllEndingCards,
}