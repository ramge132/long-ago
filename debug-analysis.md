# 🐛 부적절한 이미지 생성 후 투표 결과 표시 버그 분석

## 📝 버그 현상

### 시나리오
1. **사용자 A가 부적절한 이미지 생성** → 사용자 B에게 차례 넘어감 ✅
2. **사용자 B가 프롬프트 제출** → 이미지 찬성으로 책에 등록 ✅  
3. **사용자 B 화면**: 두 사용자 모두 thumbs_up_right.gif 표시 ✅
4. **사용자 A 화면**: 
   - 사용자 B만 thumbs_up_right.gif 표시 ❌
   - 본인(사용자 A)는 표시 안됨 ❌
5. **책 페이지 자동 넘김 실패** ❌

## 🔍 원인 분석

### 핵심 문제점
부적절한 이미지를 생성한 사용자 A의 상태가 `stopVotingAndShowWarning` 함수 실행 후 완전히 초기화되지 않아, 다음 투표에서 정상적으로 참여하지 못하는 것으로 추정됩니다.

### 의심되는 코드 부분

#### 1. `stopVotingAndShowWarning` 함수 (line 1155-1216)
```javascript
// 투표 관련 상태 완전 초기화
votings.value = [];
isVoted.value = true;  // 투표 UI 즉시 숨김
currentVoteSelection.value = "up";
```
- `isVoted.value = true`로 설정 후, 3초 후 warningTimer에서 `false`로 리셋
- 그러나 새로운 투표가 시작되면 warningTimer가 취소되어 리셋이 안 될 수 있음

#### 2. `sendPrompt` 케이스 (line 677-723)
```javascript
isVoted.value = false; // 새로운 투표를 위해 초기화
votings.value = []; // 투표 배열 완전 초기화
```
- 새 프롬프트 수신 시 초기화는 정상적으로 수행됨
- 하지만 사용자 A가 이미 `isVoted.value = true` 상태라면?

#### 3. `voteEnd` 함수 (line 2399-2601)
```javascript
isVoted.value = true;
// 본인이 이미 투표한 상태로 설정
```
- 사용자 A의 `isVoted` 상태가 여전히 `true`일 경우 자동 투표가 실행되지 않음

## 🔧 버그 수정 방향

### 1. stopVotingAndShowWarning 개선
- warningTimer 실행 전에 상태를 즉시 초기화
- 새 투표 시작 시 warningTimer 취소 확인

### 2. sendPrompt 케이스 개선  
- 이전 경고 상태와 관계없이 완전한 초기화 보장
- warningTimer가 실행 중이면 즉시 취소

### 3. 투표 참여 추적
- 각 플레이어의 투표 참여 상태를 명확히 추적
- 부적절한 콘텐츠 발생 후 상태 동기화 확인

## 🎯 로그 추가 위치

### 필수 로그 포인트
1. **stopVotingAndShowWarning 함수**
   - 상태 초기화 전후
   - warningTimer 설정/취소
   - 각 플레이어별 상태

2. **voteEnd 함수**
   - isVoted 상태 변경
   - 투표 배열 업데이트
   - 자동 투표 실행 여부

3. **voteResult 케이스**
   - 투표 수신 및 집계
   - isElected 상태 변경
   - 책 페이지 넘김 트리거

4. **InGameContent.vue의 isElected watch**
   - 페이지 넘김 실행 여부

## 📊 디버깅 체크리스트

- [ ] 사용자 A의 isVoted 상태 추적
- [ ] 사용자 A의 votings 배열 상태
- [ ] warningTimer 취소 시점
- [ ] 새 투표 시작 시 상태 초기화
- [ ] isElected 값 전파
- [ ] InGameContent로의 props 전달

## 💡 해결 방안

### 즉시 적용 가능한 수정
1. `stopVotingAndShowWarning`에서 `isVoted = true` 대신 `false`로 설정
2. `sendPrompt` 케이스에서 warningTimer 체크 및 취소
3. 투표 타이머 만료 시 강제 초기화

### 근본적 해결
- 각 플레이어의 투표 상태를 독립적으로 관리
- P2P 메시지로 상태 동기화 명시적 처리
- 부적절한 콘텐츠 처리 후 완전한 상태 리셋 보장
