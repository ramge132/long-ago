<template>
  <div class="ad-banner" v-if="shouldRenderAd">
    <!-- 실제 광고가 활성화된 경우 -->
    <div v-if="adConfig.googleAdsense.enabled" class="ad-container">
      <!-- Google AdSense 광고 -->
      <ins class="adsbygoogle"
           style="display:block"
           :data-ad-client="adConfig.googleAdsense.clientId"
           :data-ad-slot="getAdSlotId"
           data-ad-format="auto"
           data-full-width-responsive="true">
      </ins>
    </div>
    
    <!-- 개발/테스트 모드일 때 표시되는 플레이스홀더 -->
    <div v-else class="ad-container">
      <div class="ad-placeholder">
        <p class="ad-label">Advertisement</p>
        <div class="ad-content">
          <div class="demo-ad">
            <h3>{{ adSlot }} 광고</h3>
            <p>{{ adFormat }} 형식</p>
            <small>300x250</small>
            <div class="ad-info">
              <p>실제 배포시 여기에 광고가 표시됩니다</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed, defineProps } from 'vue'
import { useRoute } from 'vue-router'
import { adConfig, shouldShowAds } from '@/utils/adConfig'

const props = defineProps({
  adSlot: {
    type: String,
    default: 'default'
  },
  adFormat: {
    type: String,
    default: 'rectangle'
  }
})

const route = useRoute()

// 광고 표시 여부 결정
const shouldRenderAd = computed(() => {
  const screenWidth = window.innerWidth || 1280
  return shouldShowAds(route.path, screenWidth)
})

// 광고 슬롯 ID 가져오기
const getAdSlotId = computed(() => {
  return adConfig.googleAdsense.adSlots[props.adSlot] || adConfig.googleAdsense.adSlots.leftSidebar
})

onMounted(() => {
  if (adConfig.googleAdsense.enabled && shouldRenderAd.value) {
    // Google AdSense 광고 로드
    try {
      if (window.adsbygoogle) {
        (window.adsbygoogle = window.adsbygoogle || []).push({})
      }
    } catch (error) {
      console.error('광고 로드 오류:', error)
    }
  }
  
  console.log(`광고 로드: ${props.adSlot}, 형식: ${props.adFormat}, 표시: ${shouldRenderAd.value}`)
})
</script>

<style scoped>
.ad-banner {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  min-height: 250px;
}

.ad-container {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  backdrop-filter: blur(10px);
  padding: 16px;
  width: 300px;
  height: 250px;
  display: flex;
  flex-direction: column;
}

.ad-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ad-label {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.5);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.ad-content {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.demo-ad {
  text-align: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
  width: 100%;
}

.demo-ad h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
}

.demo-ad p {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 14px;
}

.demo-ad small {
  color: #999;
  font-size: 12px;
}

.ad-info {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.ad-info p {
  font-size: 11px;
  color: #888;
  margin: 0;
}

/* 반응형 스타일 */
@media (max-width: 1400px) {
  .ad-container {
    width: 250px;
    height: 200px;
  }
}

@media (max-width: 1200px) {
  .ad-banner {
    display: none;
  }
}
</style>