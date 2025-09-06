import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // 개발 환경에서만 devtools 사용
    process.env.NODE_ENV === 'development' && vueDevTools(),
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    // 번들 크기 경고 임계값 증가
    chunkSizeWarningLimit: 1000,
    // 롤업 옵션
    rollupOptions: {
      output: {
        // 번들 분할 최적화
        manualChunks: {
          // 벤더 청크 분할
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-ui': ['vue-toastification', 'swiper'],
          'vendor-utils': ['axios', 'vue-clipboard3'],
          'vendor-peer': ['peerjs'],
          // googleapis는 무거우므로 별도 청크로
          'vendor-google': ['googleapis'],
        },
        // 청크 파일명 설정
        chunkFileNames: (chunkInfo) => {
          const facadeModuleId = chunkInfo.facadeModuleId ? chunkInfo.facadeModuleId.split('/').pop().split('.')[0] : 'index';
          return `assets/js/${facadeModuleId}-[hash].js`;
        },
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      }
    },
    // esbuild를 사용한 minification (기본값, terser보다 빠름)
    minify: 'esbuild',
    esbuildOptions: {
      drop: ['console', 'debugger'],
    },
    // 소스맵 비활성화 (프로덕션)
    sourcemap: false,
    // CSS 코드 분할
    cssCodeSplit: true,
  },
  // 개발 서버 최적화
  server: {
    // HMR 최적화
    hmr: {
      overlay: false,
    },
    // 브라우저 자동 열기 비활성화
    open: false,
  },
  // 의존성 최적화
  optimizeDeps: {
    // 미리 번들링할 의존성 지정
    include: [
      'vue',
      'vue-router',
      'pinia',
      'axios',
      'peerjs',
      'vue-toastification',
    ],
    // 제외할 의존성
    exclude: ['googleapis'], // 무거운 googleapis는 동적 임포트로 처리
  },
  // 에셋 인라인 임계값 (4kb 이하 파일은 base64로 인라인)
  assetsInlineLimit: 4096,
})
