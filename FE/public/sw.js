/**
 * Service Worker for Long Ago Project
 * 캐싱 최적화 (로그 제거된 버전)
 */

const CACHE_NAME = 'long-ago-images-v2';
const CACHE_URLS = [
  // 중요한 배경 이미지들
  '/src/assets/background.svg',
  '/src/assets/backgroundGame.svg',
  
  // 모든 모드 이미지들 - PNG
  '/src/assets/images/modes/img/mode_0_animals.png',
  '/src/assets/images/modes/img/mode_1_animals.png',
  '/src/assets/images/modes/img/mode_2_animals.png',
  '/src/assets/images/modes/img/mode_3_animals.png',
  '/src/assets/images/modes/img/mode_4_animals.png',
  '/src/assets/images/modes/img/mode_5_animals.png',
  '/src/assets/images/modes/img/mode_6_animals.png',
  '/src/assets/images/modes/img/mode_7_animals.png',
  '/src/assets/images/modes/img/mode_8_animals.png',
  
  // 모든 모드 이미지들 - GIF
  '/src/assets/images/modes/gif/mode_0.gif',
  '/src/assets/images/modes/gif/mode_1.gif',
  '/src/assets/images/modes/gif/mode_2.gif',
  '/src/assets/images/modes/gif/mode_3.gif',
  '/src/assets/images/modes/gif/mode_4.gif',
  '/src/assets/images/modes/gif/mode_5.gif',
  '/src/assets/images/modes/gif/mode_6.gif',
  '/src/assets/images/modes/gif/mode_7.gif',
  '/src/assets/images/modes/gif/mode_8.gif'
];

// Service Worker 설치
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        // 중요한 이미지들만 설치 시 캐시 (배경 이미지)
        const criticalUrls = CACHE_URLS.filter(url => 
          url.includes('background.svg') || url.includes('backgroundGame.svg')
        );
        return cache.addAll(criticalUrls);
      })
      .then(() => {
        // 설치 완료 즉시 활성화
        return self.skipWaiting();
      })
      .catch((error) => {
        // 에러 처리 (로그 없음)
      })
  );
});

// Service Worker 활성화
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        // 이전 버전 캐시 삭제
        const deletePromises = cacheNames
          .filter(cacheName => cacheName !== CACHE_NAME)
          .map(cacheName => caches.delete(cacheName));
        
        return Promise.all(deletePromises);
      })
      .then(() => {
        return self.clients.claim();
      })
      .then(() => {
        // 활성화 후 모드 이미지들을 백그라운드에서 캐시
        backgroundCacheImages();
      })
  );
});

// 백그라운드에서 모드 이미지들 캐시
async function backgroundCacheImages() {
  try {
    const cache = await caches.open(CACHE_NAME);
    
    // PNG 이미지들을 먼저 캐시
    const pngUrls = CACHE_URLS.filter(url => url.endsWith('.png'));
    await cache.addAll(pngUrls);
    
    // 잠시 대기 후 GIF 이미지들 캐시
    setTimeout(async () => {
      try {
        const gifUrls = CACHE_URLS.filter(url => url.endsWith('.gif'));
        await cache.addAll(gifUrls);
      } catch (error) {
        // 에러 처리 (로그 없음)
      }
    }, 2000);
    
  } catch (error) {
    // 에러 처리 (로그 없음)
  }
}

// 네트워크 요청 가로채기
self.addEventListener('fetch', (event) => {
  // 이미지 요청인지 확인
  if (event.request.destination === 'image' || 
      event.request.url.includes('.png') || 
      event.request.url.includes('.gif') || 
      event.request.url.includes('.svg') ||
      event.request.url.includes('.jpg') ||
      event.request.url.includes('.jpeg')) {
    
    event.respondWith(
      caches.match(event.request)
        .then((cachedResponse) => {
          if (cachedResponse) {
            // 캐시에서 제공 (로그 없음)
            return cachedResponse;
          }
          
          // 캐시에 없으면 네트워크에서 가져와서 캐시에 저장
          return fetch(event.request)
            .then((response) => {
              // 성공적인 응답인지 확인
              if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
              }
              
              // 응답 복제 (스트림은 한 번만 사용 가능)
              const responseToCache = response.clone();
              
              caches.open(CACHE_NAME)
                .then((cache) => {
                  cache.put(event.request, responseToCache);
                });
              
              return response;
            })
            .catch((error) => {
              // 네트워크 실패 시 기본 이미지나 오프라인 메시지 반환 가능
              return new Response('Image not available', {
                status: 404,
                statusText: 'Not Found'
              });
            });
        })
    );
  }
  
  // 이미지가 아닌 요청은 그대로 통과
});

// 메시지 리스너 (메인 애플리케이션과의 통신)
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'CACHE_STATUS') {
    // 캐시 상태 확인
    caches.open(CACHE_NAME)
      .then((cache) => cache.keys())
      .then((keys) => {
        event.ports[0].postMessage({
          type: 'CACHE_STATUS_RESPONSE',
          cachedCount: keys.length,
          cachedUrls: keys.map(req => req.url)
        });
      });
  }
  
  if (event.data && event.data.type === 'PRELOAD_IMAGES') {
    // 특정 이미지들을 즉시 캐시하도록 요청
    const urls = event.data.urls || [];
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urls))
      .then(() => {
        event.ports[0].postMessage({
          type: 'PRELOAD_COMPLETE',
          count: urls.length
        });
      })
      .catch((error) => {
        event.ports[0].postMessage({
          type: 'PRELOAD_ERROR',
          error: error.message
        });
      });
  }
});