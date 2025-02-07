let interval = null;
onmessage = function (e) {
  const { initialTime } = e.data;

  if (e.data === 'reset') {
    clearInterval(interval); // 타이머 초기화
    return;
  }

  let restTime = initialTime;

  if (interval) {
    clearInterval(interval); // 이전 타이머 중지
  }

  interval = setInterval(() => {
    if (restTime > 0) {
      restTime--;
      postMessage(restTime); // 메인 스레드로 남은 시간 전달
    } else {
      clearInterval(interval);
      postMessage('done'); // 타이머 종료 시 'done' 메시지 전달
    }
  }, 1000);
};
