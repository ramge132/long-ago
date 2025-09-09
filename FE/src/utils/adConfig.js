// 광고 설정 파일
export const adConfig = {
  // Google AdSense 설정
  googleAdsense: {
    clientId: 'ca-pub-4330240879299258', // 실제 AdSense 클라이언트 ID
    enabled: false, // 승인 전에는 false, 승인 후 true로 변경
    adSlots: {
      leftSidebar: '1234567890',    // 왼쪽 사이드바 광고 슬롯 ID
      rightSidebar: '0987654321',   // 오른쪽 사이드바 광고 슬롯 ID
    }
  },
  
  // 다른 광고 네트워크 설정 (예: 네이버 애드핏, 카카오애드핏 등)
  naverAdfit: {
    enabled: false,
    unitId: 'DAN-XXXXXXXXXXXXXXXXX'
  },
  
  kakaoAdfit: {
    enabled: false,
    unitId: 'DAN-XXXXXXXXXXXXXXXXX'
  },
  
  // 광고 표시 조건
  displayConditions: {
    minScreenWidth: 1280, // 최소 화면 너비
    excludePages: [], // 모든 페이지에서 광고 표시
  }
}

// 페이지별 광고 표시 여부 확인
export const shouldShowAds = (currentPath, screenWidth) => {
  if (screenWidth < adConfig.displayConditions.minScreenWidth) {
    return false
  }
  
  if (adConfig.displayConditions.excludePages.includes(currentPath)) {
    return false
  }
  
  return adConfig.googleAdsense.enabled || 
         adConfig.naverAdfit.enabled || 
         adConfig.kakaoAdfit.enabled
}

// Google AdSense 스크립트 로드
export const loadGoogleAdsense = () => {
  if (!adConfig.googleAdsense.enabled) return
  
  const script = document.createElement('script')
  script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${adConfig.googleAdsense.clientId}`
  script.async = true
  script.crossOrigin = 'anonymous'
  document.head.appendChild(script)
}

// 광고 초기화
export const initializeAds = () => {
  if (typeof window !== 'undefined') {
    loadGoogleAdsense()
    
    // 다른 광고 네트워크 초기화도 여기에 추가
  }
}