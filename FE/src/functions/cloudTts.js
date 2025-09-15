// functions/cloudTts.js

/**
 * Google Cloud TTS API를 사용하여 텍스트를 음성으로 변환하고 Web Audio API로 재생
 * 동시 실행을 위한 새로운 TTS 시스템
 */

// Cloud TTS API 전용 - 브라우저 TTS 사용하지 않음

// 글로벌 AudioContext 인스턴스
let audioContext = null;

/**
 * AudioContext 초기화
 */
function initAudioContext() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
  
  // AudioContext가 suspended 상태면 resume
  if (audioContext.state === 'suspended') {
    audioContext.resume();
  }
  
  return audioContext;
}

/**
 * 환경에 맞는 API URL 생성
 */
function getApiUrl() {
  const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  if (isDevelopment) {
    return 'http://localhost:8080';
  } else {
    // 프로덕션 환경에서는 상대 경로 사용 (같은 도메인의 백엔드)
    return '';
  }
}

/**
 * 백엔드 TTS API 호출하여 오디오 데이터 가져오기
 * @param {string} text - 읽을 텍스트
 * @returns {Promise<ArrayBuffer>} - 오디오 데이터
 */
async function fetchTTSAudio(text) {
  try {
    
    const apiUrl = getApiUrl();
    const response = await fetch(`${apiUrl}/tts/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        languageCode: 'ko-KR'
      })
    });

    if (!response.ok) {
      throw new Error(`TTS API 호출 실패: ${response.status}`);
    }

    const audioData = await response.arrayBuffer();
    
    // 빈 오디오 데이터인 경우 에러 처리
    if (audioData.byteLength === 0) {
      throw new Error('TTS 서비스 일시 비활성화됨');
    }
    
    return audioData;
  } catch (error) {
    throw error;
  }
}

/**
 * AudioBuffer를 생성하고 재생하는 함수
 * @param {ArrayBuffer} audioData - 오디오 데이터
 * @returns {Promise} - 재생 완료 시 resolve
 */
function playAudioBuffer(audioData) {
  return new Promise((resolve, reject) => {
    const context = initAudioContext();
    
    // ArrayBuffer를 AudioBuffer로 디코딩
    context.decodeAudioData(audioData)
      .then(audioBuffer => {
        // AudioBufferSourceNode 생성
        const source = context.createBufferSource();
        source.buffer = audioBuffer;
        
        // 스피커에 연결
        source.connect(context.destination);
        
        // 재생 완료 이벤트
        source.onended = () => {
          resolve();
        };
        
        // 재생 시작
        source.start();
        
      })
      .catch(error => {
        reject(error);
      });
  });
}

/**
 * Cloud TTS API 전용 동시 실행 함수 (fallback 없음)
 * @param {string} text - 읽을 텍스트
 * @returns {Promise} - 재생 완료 시 resolve
 */
export async function speakTextConcurrent(text) {
  if (!text) return;

  try {
    
    // Cloud TTS API 호출하여 오디오 데이터 가져오기
    const audioData = await fetchTTSAudio(text);
    
    // Web Audio API로 재생 (동시 실행 가능)
    await playAudioBuffer(audioData);
    
  } catch (error) {
    // 에러 발생 시 재생하지 않음 (게임 진행은 계속)
    // throw 하지 않아서 게임 진행이 중단되지 않도록 함
  }
}

/**
 * 현재 재생 중인 모든 TTS 중지
 */
export function stopAllTTS() {
  if (audioContext) {
    // 모든 오디오 소스를 중지하려면 새로운 AudioContext를 생성
    audioContext.close();
    audioContext = null;
  }
}

/**
 * 볼륨 조절을 위한 GainNode 사용 버전
 * @param {string} text - 읽을 텍스트
 * @param {number} volume - 볼륨 (0.0 ~ 1.0)
 * @returns {Promise} - 재생 완료 시 resolve
 */
export async function speakTextWithVolume(text, volume = 1.0, audioStore = null) {
  if (!text) return;

  try {

    const audioData = await fetchTTSAudio(text);
    const context = initAudioContext();

    const audioBuffer = await context.decodeAudioData(audioData);
    const source = context.createBufferSource();
    const gainNode = context.createGain();

    source.buffer = audioBuffer;
    gainNode.gain.value = volume;

    // source -> gainNode -> destination
    source.connect(gainNode);
    gainNode.connect(context.destination);

    return new Promise((resolve) => {
      // audioStore가 제공된 경우 실시간 볼륨/음소거 모니터링
      if (audioStore) {
        const volumeInterval = setInterval(() => {
          if (audioStore.audioData) {
            gainNode.gain.value = audioStore.audioVolume;
          } else {
            gainNode.gain.value = 0; // 음소거
          }
        }, 100); // 100ms마다 체크

        const cleanup = () => {
          clearInterval(volumeInterval);
          resolve();
        };

        source.onended = cleanup;

        // 수동 중단을 위한 참조 저장
        source._cleanup = cleanup;
      } else {
        source.onended = resolve;
      }

      source.start();
    });

  } catch (error) {
    return Promise.resolve();
  }
}