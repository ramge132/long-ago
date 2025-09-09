# 광고 설정 가이드

## 📋 개요

Long Ago 프로젝트에 광고 시스템이 통합되었습니다. 좌우 사이드바에 광고 영역이 추가되었으며, 반응형 디자인으로 구현되어 있습니다.

## 🎯 광고 영역 위치

- **왼쪽 사이드바**: 메인 콘텐츠 왼쪽에 위치 (300x250 기본)
- **오른쪽 사이드바**: 메인 콘텐츠 오른쪽에 위치 (300x250 기본)
- **반응형**: XL(1280px) 이상에서만 표시, 그 이하에서는 숨김

## 🔧 설정 방법

### 1. Google AdSense 설정

1. **AdSense 계정 생성 및 승인**
   - [Google AdSense](https://adsense.google.com) 가입
   - 웹사이트 등록 및 승인 대기

2. **설정 파일 수정** (`/src/utils/adConfig.js`)
   ```javascript
   export const adConfig = {
     googleAdsense: {
       clientId: 'ca-pub-XXXXXXXXXXXXXXXXX', // 실제 클라이언트 ID로 교체
       enabled: true, // 배포시 true로 변경
       adSlots: {
         leftSidebar: '1234567890',    // 왼쪽 광고 슬롯 ID
         rightSidebar: '0987654321',   // 오른쪽 광고 슬롯 ID
       }
     }
   }
   ```

3. **HTML 헤드 태그 추가** (선택사항 - 자동으로 로드됨)
   ```html
   <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXXX"
        crossorigin="anonymous"></script>
   ```

### 2. 네이버 애드핏 설정

1. **애드핏 계정 생성**
   - [네이버 애드핏](https://adfit.naver.com) 가입

2. **설정 파일 수정**
   ```javascript
   naverAdfit: {
     enabled: true,
     unitId: 'DAN-XXXXXXXXXXXXXXXXX'
   }
   ```

### 3. 카카오 애드핏 설정

1. **카카오 애드핏 계정 생성**
   - [카카오 애드핏](https://adfit.kakao.com) 가입

2. **설정 파일 수정**
   ```javascript
   kakaoAdfit: {
     enabled: true,
     unitId: 'DAN-XXXXXXXXXXXXXXXXX'
   }
   ```

## 📱 반응형 설정

### 화면 크기별 동작
- **XL (1280px+)**: 좌우 광고 모두 표시
- **LG (1024px~1279px)**: 광고 숨김, 메인 콘텐츠 80% 너비
- **MD 이하 (1023px 이하)**: 광고 숨김

### 광고 크기별 설정
```css
/* 1536px+ */
.ad-left, .ad-right { width: 320px; }

/* 1400px+ */
.ad-left, .ad-right { width: 280px; }

/* 1280px+ */
.ad-left, .ad-right { width: 250px; }
```

## 🚫 광고 제외 설정

특정 페이지에서 광고를 표시하지 않으려면:

```javascript
displayConditions: {
  minScreenWidth: 1280,
  excludePages: ['/game/play', '/other-page'] // 제외할 페이지 추가
}
```

## 🧪 테스트 모드

개발 중에는 `enabled: false`로 설정하여 테스트 광고 플레이스홀더가 표시됩니다.

```javascript
googleAdsense: {
  enabled: false, // 개발 모드
  // enabled: true, // 배포 모드
}
```

## 📂 파일 구조

```
src/
├── components/
│   └── Ad/
│       └── AdBanner.vue          # 광고 컴포넌트
├── utils/
│   └── adConfig.js               # 광고 설정 파일
├── App.vue                       # 레이아웃 수정
└── main.js                       # 광고 초기화
```

## 🔍 디버깅

### 콘솔 로그 확인
브라우저 개발자 도구 콘솔에서 다음 메시지 확인:
```
광고 로드: left-sidebar, 형식: vertical, 표시: true
광고 로드: right-sidebar, 형식: vertical, 표시: true
```

### 광고가 표시되지 않는 경우
1. **화면 너비 확인**: 1280px 이상인지 확인
2. **설정 확인**: `adConfig.js`의 `enabled: true` 확인
3. **AdSense 승인**: Google AdSense 계정 승인 상태 확인
4. **콘솔 오류**: 브라우저 콘솔에서 JavaScript 오류 확인

## 💰 수익화 팁

1. **적절한 광고 위치**: 사용자 경험을 해치지 않는 선에서 배치
2. **반응형 최적화**: 다양한 화면 크기에 대응
3. **페이지별 차별화**: 게임 플레이 중에는 광고 숨김으로 몰입도 유지
4. **A/B 테스트**: 다양한 광고 크기와 위치 테스트

## ⚠️ 주의사항

1. **AdSense 정책 준수**: Google AdSense 정책 위반하지 않도록 주의
2. **로딩 성능**: 광고 로딩이 페이지 성능에 영향주지 않도록 비동기 로드
3. **사용자 경험**: 광고가 게임 플레이를 방해하지 않도록 설계
4. **개인정보보호**: 광고 관련 개인정보보호 정책 준수

## 🚀 배포 전 체크리스트

- [ ] AdSense 계정 승인 완료
- [ ] 실제 클라이언트 ID 및 슬롯 ID 설정
- [ ] `enabled: true` 설정
- [ ] 다양한 화면 크기에서 테스트
- [ ] 페이지 로딩 속도 확인
- [ ] 광고 정책 준수 확인

---

**📝 작성일**: 2025년 1월 7일  
**🔧 버전**: v1.0  
**👨‍💻 작성자**: Claude AI Assistant