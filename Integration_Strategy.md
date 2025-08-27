# Long Ago 프로젝트 - API 시스템 무중단 전환 전략

## 🎯 전환 목표
기존 RunPod + ComfyUI 시스템을 새로운 OpenAI + Gemini API 시스템으로 **무중단**으로 전환

## 🔄 점진적 전환 전략

### **1단계: 호환 계층 구축**
```
기존 백엔드 → 호환 API 서버 → 새로운 API 시스템
     ↓              ↓               ↓
   동일 요청     형식 변환        실제 처리
```

### **2단계: 환경변수 기반 전환**
```java
// application.properties
USE_NEW_API_SYSTEM=false  # 기존 시스템 사용
NEW_API_SYSTEM_URL=http://localhost:8188  # 호환 API 서버 URL
```

### **3단계: A/B 테스트**
- 일부 게임 세션만 새 시스템 사용
- 성능 및 품질 모니터링
- 점진적으로 비율 증가

## 🛠️ 구현 방법

### **백엔드 수정 (최소한)**
```java
@Value("${USE_NEW_API_SYSTEM:false}")
private boolean useNewApiSystem;

@Value("${NEW_API_SYSTEM_URL:http://localhost:8188}")
private String newApiSystemUrl;

public ResponseEntity<?> createScene(SceneRequest sceneRequest, HttpServletRequest request) {
    // 기존 로직 유지
    
    if (useNewApiSystem) {
        // 새로운 시스템 호출 (호환 API 서버를 통해)
        return callNewApiSystem(sceneRequest, game, request);
    } else {
        // 기존 RunPod 시스템 호출
        return callRunPodSystem(sceneRequest, game, request);
    }
}
```

### **호환 API 서버 배포**
```bash
# AI 디렉토리에서 실행
cd /home/ubuntu/long-ago/AI/imageGeneration
python backend_compatible_api.py  # 포트 8188에서 실행
```

### **환경변수 설정**
```env
# 새로 추가할 환경변수
USE_NEW_API_SYSTEM=false  # 초기에는 false
NEW_API_SYSTEM_URL=http://localhost:8188
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

## 🚀 배포 순서

### **Phase 1: 준비 단계**
1. ✅ 새로운 API 시스템 코드 배포
2. ✅ 호환 API 서버 시작 (8188 포트)
3. ✅ GitHub Secrets에 API 키 추가
4. ✅ 백엔드에 환경변수 기반 스위치 추가

### **Phase 2: 테스트 단계**
1. `USE_NEW_API_SYSTEM=true` 설정
2. 테스트 게임으로 동작 확인
3. 이미지 생성 품질 및 속도 확인
4. 문제 발견 시 `USE_NEW_API_SYSTEM=false`로 즉시 롤백

### **Phase 3: 점진적 전환**
1. 특정 게임 모드만 새 시스템 사용
2. 사용자 피드백 수집
3. 성능 모니터링
4. 단계적으로 모든 기능 전환

### **Phase 4: 완전 전환**
1. 모든 게임에서 새 시스템 사용
2. RunPod 관련 코드 및 설정 제거
3. 기존 환경변수 정리

## 📊 호환성 검증

### **입력 형식 매핑**
```
기존 백엔드 → 호환 API 서버:
✅ gameId → session_id
✅ userPrompt → user_sentence  
✅ drawingStyle → game_mode
✅ status → status
```

### **출력 형식 유지**
```
✅ 일반 이미지: byte[] 반환 (Response with image/png)
✅ 책 표지: JSON 응답 (RunPod 형식)
✅ 에러 처리: 동일한 HTTP 상태 코드
```

### **기능 호환성**
```
✅ 캐릭터 카드 시스템 (14개 캐릭터)
✅ 9가지 그림체 모드
✅ 게임 상태 관리 (status: 0, 1, 2)
✅ 세션 기반 스토리 연속성
✅ S3 이미지 저장 (선택적)
```

## 🔧 롤백 계획

### **즉시 롤백 (30초 내)**
```bash
# 환경변수만 변경으로 즉시 전환
export USE_NEW_API_SYSTEM=false
# 또는 application.properties 수정 후 재시작
```

### **완전 롤백**
1. 새로운 API 서버 중지
2. RunPod 관련 설정 복원
3. 기존 코드 경로로 복귀

## ⚡ 성능 비교 예상

### **속도**
- **기존**: ComfyUI 워크플로우 (30-60초)
- **신규**: OpenAI + Gemini API (10-30초)

### **품질**
- **기존**: FLUX + LoRA (높은 일관성)
- **신규**: Gemini 2.5 Flash (높은 다양성)

### **비용**
- **기존**: GPU 서버 임대비 (고정 비용)
- **신규**: API 사용량 기반 (변동 비용)

### **유지보수**
- **기존**: 복잡한 인프라 관리
- **신규**: 간단한 API 호출

## 🎯 성공 지표

### **기술적 지표**
- ✅ 이미지 생성 성공률 > 95%
- ✅ 평균 응답 시간 < 30초
- ✅ API 오류율 < 1%
- ✅ 캐릭터 일관성 유지

### **사용자 경험**
- ✅ 게임 중단 없음
- ✅ 이미지 품질 만족도 유지
- ✅ 로딩 시간 개선 체감

## 📞 비상 연락망

### **모니터링 포인트**
1. API 서버 상태 (8188 포트)
2. OpenAI/Gemini API 응답률
3. 백엔드 에러 로그
4. 사용자 게임 완료율

### **문제 발생 시 대응**
1. **즉시 롤백**: `USE_NEW_API_SYSTEM=false`
2. **로그 확인**: 백엔드 및 API 서버 로그 분석
3. **사용자 알림**: 게임 내 안내 메시지
4. **상황 복구**: 문제 해결 후 점진적 재전환

---

이 전략을 통해 **사용자 경험 중단 없이** 새로운 API 시스템으로 안전하게 전환할 수 있습니다.