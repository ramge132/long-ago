# 턴 순서 로직 수정 요약

## 문제 설명
게임 시작 시 턴 순서가 일관되지 않게 표시되는 문제:
- "당신의 차례는 n번입니다" 메시지: 참가 순서 표시 (잘못됨)
- 실제 턴 진행: 참가 순서대로 진행 (잘못됨)
- myTurn.svg와 프로필 표시기: 무작위 순서 표시 (올바름)

## 근본 원인
`myTurn` 변수가 무작위 순서(`inGameOrder`)가 아닌 참가 순서(`participants` 배열 인덱스)를 저장하고 있었음

## 수정 내용

### 1. gameStart 함수 (라인 1354-1367)
**이전 코드:**
```javascript
participants.value.forEach((p, i) => {
  if (p.id === peerId.value) {
    myTurn.value = i; // participants 배열에서의 내 인덱스
  }
});
```

**수정된 코드:**
```javascript
// myTurn을 inGameOrder에서의 위치로 설정 (무작위 순서)
participants.value.forEach((p, i) => {
  if (p.id === peerId.value) {
    // i는 participants 배열에서의 인덱스
    // inGameOrder에서 i를 찾아서 그 위치를 myTurn으로 설정
    const turnIndex = inGameOrder.value.indexOf(i);
    myTurn.value = turnIndex; // inGameOrder에서의 내 위치 (무작위 턴 순서)
  }
});
```

### 2. startReceived 함수 (라인 1382-1395)
**이전 코드:**
```javascript
// 내 순서 몇번인지 저장
participants.value.forEach((p, i) => {
  if (p.id === peerId.value) {
    myTurn.value = i; // participants 배열에서의 내 인덱스
  }
});
```

**수정된 코드:**
```javascript
// 내 순서 몇번인지 저장 (무작위 순서)
participants.value.forEach((p, i) => {
  if (p.id === peerId.value) {
    // i는 participants 배열에서의 인덱스
    // inGameOrder에서 i를 찾아서 그 위치를 myTurn으로 설정
    const turnIndex = inGameOrder.value.indexOf(i);
    myTurn.value = turnIndex; // inGameOrder에서의 내 위치 (무작위 턴 순서)
  }
});
```

## 수정 결과
이제 모든 요소가 일관된 무작위 턴 순서를 따름:
1. ✅ "당신의 차례는 n번입니다" - 무작위 순서 표시
2. ✅ 실제 턴 진행 - 무작위 순서대로 진행
3. ✅ myTurn.svg 표시 - 올바른 턴에 표시
4. ✅ 프로필 파란 원 - 올바른 플레이어에 표시

## 테스트 시나리오
1. 여러 플레이어로 게임 시작
2. 게임 시작 시 표시되는 "당신의 차례는 n번입니다" 확인
3. 실제 턴 진행 순서가 표시된 번호와 일치하는지 확인
4. myTurn.svg와 프로필 표시가 올바른 턴에 나타나는지 확인

## 관련 파일
- `FE/src/views/GameView.vue` - 메인 게임 뷰 컴포넌트
