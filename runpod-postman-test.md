# RunPod API Postman 테스트 가이드

## 1. Postman 설정

### Request 정보:
- **Method**: POST
- **URL**: `https://api.runpod.ai/v2/34tmym7s3c36fa/run`

### Headers:
```
Authorization: Bearer rpa_V1J79G6FQCCPCSJ1FYXP3UD6RZROI616D54EY7QVnbi6hb
Content-Type: application/json
```

### Body (raw - JSON):
```json
{
  "input": {
    "session_id": "test-001",
    "game_mode": 0,
    "user_sentence": "공주가 숲에서 마법사를 만났습니다",
    "status": 0,
    "character_cards": ["공주", "마법사"]
  }
}
```

## 2. 예상 응답:

### 성공 시:
```json
{
  "id": "job-id-xxxxx",
  "status": "IN_QUEUE" 또는 "COMPLETED",
  "output": {
    "filename": "test-001_00001.png",
    "s3_url": "https://...",
    "image": "base64_encoded_image_data...",
    "media_type": "image/png",
    "character_cards": ["공주", "마법사"],
    "session_info": {
      "count": 1,
      "summary": "..."
    }
  }
}
```

### 실패 시:
```json
{
  "error": "에러 메시지"
}
```

## 3. 테스트 순서:

1. Postman 열기
2. New Request 생성
3. POST 메소드 선택
4. URL 입력
5. Headers 탭에서 Authorization과 Content-Type 추가
6. Body 탭에서 raw 선택, JSON 형식으로 위 내용 입력
7. Send 클릭

## 4. 상태 확인 (비동기 응답인 경우):

만약 `status: "IN_QUEUE"`로 응답이 오면:

**Status Check URL**:
```
GET https://api.runpod.ai/v2/34tmym7s3c36fa/status/{job_id}
```

**Headers**:
```
Authorization: Bearer rpa_V1J79G6FQCCPCSJ1FYXP3UD6RZROI616D54EY7QVnbi6hb
```

## 5. 다양한 테스트 케이스:

### 테스트 1: 기본 장면 생성
```json
{
  "input": {
    "session_id": "test-basic",
    "game_mode": 0,
    "user_sentence": "용감한 기사가 드래곤을 만났다",
    "status": 0,
    "character_cards": []
  }
}
```

### 테스트 2: 책 표지 생성 (status = 1)
```json
{
  "input": {
    "session_id": "test-cover",
    "game_mode": 0,
    "user_sentence": "그리고 모두 행복하게 살았습니다",
    "status": 1,
    "character_cards": ["공주", "기사", "마법사"]
  }
}
```

### 테스트 3: 다른 게임 모드
```json
{
  "input": {
    "session_id": "test-mode",
    "game_mode": 3,
    "user_sentence": "숲 속에서 신비한 빛이 반짝였다",
    "status": 0,
    "character_cards": ["마법사"]
  }
}
```

## 6. 문제 해결:

### 401 Unauthorized
- API 키가 올바른지 확인
- Bearer 앞에 공백이 있는지 확인

### 404 Not Found
- Endpoint ID가 올바른지 확인
- URL 형식이 정확한지 확인

### 500 Internal Server Error
- RunPod 서버 문제일 수 있음
- 몇 분 후 재시도

### Timeout
- Cold start일 수 있음 (첫 요청은 시간이 걸림)
- 최대 5분까지 기다려보기
