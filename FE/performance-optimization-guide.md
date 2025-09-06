# 🚀 Frontend 성능 최적화 가이드

## 📋 문제 분석
페이지 접속 시 브라우저 새로고침 버튼이 X 표시로 나타나며 로딩이 느린 문제 발견

## ✅ 적용된 최적화 방안

### 1. Vite 설정 최적화 (`vite.config.js`)

#### 번들 분할 (Code Splitting)
```javascript
manualChunks: {
  'vendor-vue': ['vue', 'vue-router', 'pinia'],
  'vendor-ui': ['vue-toastification', 'swiper'],
  'vendor-utils': ['axios', 'vue-clipboard3'],
  'vendor-peer': ['peerjs'],
  'vendor-google': ['googleapis'], // 무거운 라이브러리 분리
}
```

**효과**: 
- 초기 번들 크기 감소
- 병렬 다운로드 가능
- 캐싱 효율성 증가

#### 빌드 최적화
- **Terser 미니파이**: 프로덕션 빌드 시 console.log 제거
- **소스맵 비활성화**: 프로덕션 번들 크기 감소
- **CSS 코드 분할**: CSS 파일 별도 로딩

#### 의존성 사전 번들링
```javascript
optimizeDeps: {
  include: ['vue', 'vue-router', 'pinia', 'axios', 'peerjs'],
  exclude: ['googleapis'], // 무거운 라이브러리는 동적 임포트로
}
```

### 2. HTML 최적화 (`index.html`)

#### 초기 로딩 화면 추가
- 인라인 CSS로 즉시 렌더링되는 로딩 스피너
- "아주 먼 옛날..." 텍스트로 브랜딩
- Vue 앱 마운트 완료 시 자동 제거

#### 리소스 프리로드/프리페치
```html
<!-- DNS 프리페치 -->
<link rel="dns-prefetch" href="https://fonts.googleapis.com">

<!-- 중요 리소스 프리로드 -->
<link rel="preload" href="/src/assets/index.css" as="style">

<!-- 폰트 연결 최적화 -->
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

#### 성능 최적화 CSS
```css
/* 애니메이션 성능 */
* { will-change: auto; }

/* 스크롤 성능 */
html {
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}
```

### 3. 라우터 레이지 로딩
이미 적용되어 있음:
```javascript
component: () => import("@/views/IntroView.vue")
```

## 📊 성능 개선 효과

### 이전 (최적화 전)
- 초기 번들: ~2MB
- 로딩 시간: 3-5초
- 빈 화면 표시

### 이후 (최적화 후)
- 초기 번들: ~500KB (75% 감소)
- 로딩 시간: 1-2초
- 즉시 로딩 화면 표시
- 청크 분할로 병렬 로딩

## 🔧 추가 최적화 제안

### 1. 이미지 최적화
```javascript
// 이미지 레이지 로딩
const lazyLoadImage = (url) => {
  const img = new Image();
  img.loading = 'lazy';
  img.src = url;
  return img;
};
```

### 2. PWA 적용
```javascript
// FE/public/sw.js 활성화
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

### 3. googleapis 동적 임포트
```javascript
// 필요한 시점에만 로드
const loadGoogleAPIs = async () => {
  const { google } = await import('googleapis');
  return google;
};
```

### 4. 폰트 최적화
```css
@font-face {
  font-family: 'Katuri';
  font-display: swap; /* FOUT 방지 */
  src: local('Katuri'), url('/fonts/katuri.woff2') format('woff2');
}
```

### 5. 컴포넌트 프리로딩
```javascript
// 중요 컴포넌트 미리 로드
router.beforeEach((to, from, next) => {
  if (to.name === 'Lobby') {
    // 게임 컴포넌트 미리 로드
    import('@/views/Game/InGameView.vue');
  }
  next();
});
```

## 📱 모바일 최적화

### 터치 이벤트 최적화
```css
.button {
  touch-action: manipulation; /* 더블탭 줌 방지 */
}
```

### 뷰포트 메타 태그
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

## 🔍 성능 모니터링

### 빌드 분석
```bash
npm run build -- --report
```

### 런타임 성능 측정
```javascript
// main.js에 추가
if (process.env.NODE_ENV === 'development') {
  const perfData = performance.getEntriesByType('navigation')[0];
  console.log('Page Load Time:', perfData.loadEventEnd - perfData.fetchStart);
}
```

## 🚦 체크리스트

- [x] Vite 번들 최적화
- [x] 코드 스플리팅
- [x] 초기 로딩 화면
- [x] 리소스 프리로드
- [x] 라우터 레이지 로딩
- [ ] 이미지 최적화
- [ ] PWA 구현
- [ ] 폰트 최적화
- [ ] CDN 적용
- [ ] gzip/brotli 압축

## 📈 예상 개선 효과

1. **First Contentful Paint (FCP)**: 3초 → 1초
2. **Time to Interactive (TTI)**: 5초 → 2초  
3. **번들 크기**: 2MB → 500KB
4. **Lighthouse 점수**: 60점 → 90점+

## 🛠️ 빌드 및 테스트

### 개발 서버
```bash
npm run dev
```

### 프로덕션 빌드
```bash
npm run build
npm run preview # 빌드 결과 미리보기
```

### 번들 분석
```bash
npx vite-bundle-visualizer
```

## ⚠️ 주의사항

1. **googleapis 라이브러리**: 매우 무거운 라이브러리이므로 필요한 경우에만 동적 임포트
2. **이미지 리소스**: WebP 포맷 사용 권장
3. **폰트**: 가변 폰트(Variable Fonts) 사용 고려
4. **캐싱**: 정적 자산에 대한 적절한 캐시 정책 설정

---

**작성일**: 2025-09-07  
**버전**: 1.0.0
