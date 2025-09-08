# 가비아 DNS TXT 레코드 설정 가이드 (Google Search Console)

## 🎯 **TXT 레코드 설정이 필요한 이유**
Google Search Console에서 **도메인 속성**을 선택하면 TXT 레코드로 도메인 소유권을 확인해야 합니다. 이 방법이 가장 권장되는 방식입니다.

---

## 📋 **1단계: Google Search Console에서 TXT 값 받기**

### 1.1 Google Search Console 속성 추가
1. https://search.google.com/search-console/ 접속
2. **"속성 추가"** 클릭
3. **⭐ "도메인" 탭 선택** (권장)
4. `longago.io` 입력 (프로토콜 없이)
5. **"계속"** 클릭

### 1.2 TXT 레코드 값 복사
Google에서 다음과 같은 형태의 TXT 값을 제공합니다:
```
google-site-verification=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567
```
**⚠️ 이 값을 복사해두세요! 다음 단계에서 사용합니다.**

---

## 🔧 **2단계: 가비아 DNS 관리 설정**

### 2.1 가비아 My 가비아 접속
1. https://www.gabia.com/ → 로그인
2. **"My 가비아"** 클릭
3. **"도메인"** → **"DNS 관리"** 클릭
4. `longago.io` 도메인 선택

### 2.2 DNS 레코드 추가
**"DNS 설정" 탭**에서:

| 필드명 | 입력값 |
|--------|--------|
| **타입** | `TXT` |
| **호스트** | `@` 또는 **빈칸** |
| **값(Value)** | `google-site-verification=abc123...` (Google에서 받은 전체 값) |
| **TTL** | `3600` (기본값) |

### 2.3 중요한 설정 포인트

#### 🔹 **호스트 필드에는:**
- **`@`** 입력 (루트 도메인을 의미)
- 또는 **빈칸**으로 둘 것
- ❌ `www`나 `longago.io` 입력하지 마세요

#### 🔹 **값 필드에는:**
- Google에서 제공한 **전체 문자열** 입력
- `google-site-verification=` 포함해서 입력
- ❌ 따옴표는 입력하지 마세요

### 2.4 설정 저장
1. **"추가"** 또는 **"저장"** 버튼 클릭
2. 변경사항 적용까지 **10분~1시간** 소요

---

## ⏰ **3단계: DNS 전파 대기 및 확인**

### 3.1 DNS 전파 확인 (선택사항)
온라인 도구로 TXT 레코드가 정상 등록되었는지 확인:
- https://dnschecker.org/
- 도메인: `longago.io`
- 레코드 타입: `TXT`

### 3.2 터미널에서 확인
```bash
# Windows (CMD)
nslookup -type=TXT longago.io

# Windows (PowerShell)
Resolve-DnsName -Name longago.io -Type TXT

# macOS/Linux
dig TXT longago.io
```

**정상 결과 예시:**
```
longago.io	text = "google-site-verification=abc123def456..."
```

---

## ✅ **4단계: Google Search Console에서 확인**

### 4.1 소유권 확인
1. Google Search Console로 돌아가기
2. **"확인"** 버튼 클릭
3. ✅ **"소유권이 확인됨"** 메시지 확인

### 4.2 확인 안 될 때
- **10분~1시간 더 기다리기** (DNS 전파 시간)
- 가비아에서 TXT 값 다시 확인
- 브라우저 새로고침 후 재시도

---

## 📋 **5단계: 사이트맵 제출**

소유권 확인 완료 후:
1. **"색인 생성" > "Sitemaps"** 메뉴
2. `sitemap.xml` 입력
3. **"제출"** 클릭

---

## 🔧 **예상 문제 해결**

### ❌ **"DNS 레코드를 찾을 수 없음"**
**원인**: TXT 값 입력 오류
**해결**:
- 가비아에서 `google-site-verification=` 전체 포함 확인
- 호스트 필드가 `@` 또는 빈칸인지 확인

### ❌ **"소유권 확인 실패"**
**원인**: DNS 전파 미완료
**해결**:
- 1-2시간 더 기다리기
- `nslookup` 명령어로 TXT 레코드 확인

### ❌ **여러 개 TXT 레코드 문제**
**원인**: 기존 TXT 레코드와 충돌
**해결**:
- 기존 TXT 레코드 삭제 후 새로 생성
- 또는 기존 레코드와 병합

---

## 📊 **설정 완료 체크리스트**

- [ ] Google Search Console에서 도메인 속성 추가
- [ ] TXT 레코드 값 복사
- [ ] 가비아 DNS 관리에서 TXT 레코드 추가
  - [ ] 타입: TXT
  - [ ] 호스트: @ (또는 빈칸)
  - [ ] 값: google-site-verification=...
- [ ] 10분~1시간 대기
- [ ] Google Search Console에서 소유권 확인
- [ ] 사이트맵 제출 (sitemap.xml)

---

## 💡 **추가 팁**

### 🎯 **도메인 vs URL 접두어**
- **도메인 방식** (TXT): `longago.io` 전체 하위도메인 포함
- **URL 접두어** (HTML 파일): `https://longago.io/` 특정 경로만

### 🔄 **다른 서비스도 동시 설정**
가비아에서 다음 TXT 레코드들도 함께 설정 가능:
- **네이버 웹마스터**: `naver-site-verification=...`
- **Bing 웹마스터**: `msvalidate.01=...`

---

**🕒 예상 완료 시간**: 30분 (설정) + 1시간 (DNS 전파)  
**✅ 성공 지표**: Google Search Console에서 "소유권이 확인됨" 메시지