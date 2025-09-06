# 책 페이지 넘김 동기화 버그 분석

## 버그 시나리오
플레이어 A, B 두 명이 있는 상황에서:
1. (첫번째 턴) A가 부적절한 이미지 생성 → B에게 차례 넘어감
2. (두번째 턴) B가 프롬프트 작성 → 찬성 승리 → 책 등록
3. (세번째 턴) **버그**: B 화면에서는 책이 넘어가지만, A 화면에서는 안 넘어감
4. (세번째 턴) A가 프롬프트 작성 → 찬성 승리 → 책 등록
5. (네번째 턴) **버그**: A 화면에서는 책이 넘어가지만, B 화면에서는 안 넘어감

## 책 페이지 넘김 메커니즘 (InGameContent.vue)

```javascript
watch(() => props.isElected,
(newValue) => {
  if (newValue) {
    // 모든 페이지를 넘김
    for (let i of Array.from({length: props.bookContents.length}, (_, index) => index * 2)) {
      if (!isFlipped(i)) {
        flippedPages.add(i);
        flippedPages.add(i + 1);
      }
    }
  }
})
```

isElected가 true가 되면 책 페이지가 자동으로 넘어갑니다.

## 의심되는 문제점

### 1. stopVotingAndShowWarning 함수에서 상태 초기화
```javascript
isElected.value = false; // 선출 상태 초기화
votings.value = [];       // 투표 배열 초기화
```

### 2. voteResult 케이스의 isElected 설정 로직
```javascript
case "voteResult":
  // ... 투표 집계 ...
  
  if (votings.value.length == participants.value.length) {
    const voteAccepted = upCount >= downCount;
    
    if (currTurn.value === myTurn.value) {
      // 내 턴일 때만 isElected 설정
      if (accepted) {
        isElected.value = true;
      }
    } else {
      // 다른 플레이어들도 동일한 투표 결과 처리
      if (voteAccepted) {
        isElected.value = true;  // <-- 이 부분이 실행되지 않을 수 있음
      }
    }
  }
```

### 3. 부적절한 이미지 후 투표 흐름
1. A가 부적절한 이미지 생성
2. stopVotingAndShowWarning 실행 → votings = [], isElected = false
3. B의 턴 시작
4. B가 프롬프트 제출 → sendPrompt 메시지로 A에게 전송
5. A와 B가 투표
6. voteResult 처리 시:
   - B (현재 턴): isElected = true 설정됨
   - A (게스트): voteResult의 else 블록이 실행되어야 하는데...

## 가능한 원인

### 원인 1: voteResult else 블록 미실행
부적절한 이미지 이후 voteResult 케이스의 else 블록(게스트용)이 제대로 실행되지 않을 수 있습니다.

### 원인 2: isElected watch 트리거 문제
isElected가 이미 false인 상태에서 다시 false로 설정되면 watch가 트리거되지 않습니다.

### 원인 3: votings 배열 집계 문제
stopVotingAndShowWarning에서 votings를 초기화한 후, 다음 투표에서 배열이 제대로 채워지지 않을 수 있습니다.

## 디버깅 포인트
1. voteResult 케이스에서 currTurn.value === myTurn.value 조건 확인
2. votings.value.length가 participants.value.length와 일치하는지 확인
3. voteAccepted 변수 값 확인
4. isElected 설정 시점과 값 확인
