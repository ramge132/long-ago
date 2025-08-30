// functions/cloudTts.js

/**
 * Google Cloud TTS API를 사용하여 텍스트를 음성으로 변환하고 Web Audio API로 재생
 * 동시 실행을 위한 새로운 TTS 시스템
 */

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
 * 백엔드 TTS API 호출하여 오디오 데이터 가져오기
 * @param {string} text - 읽을 텍스트
 * @returns {Promise<ArrayBuffer>} - 오디오 데이터
 */
async function fetchTTSAudio(text) {
  try {
    console.log(`🔊 TTS API 호출: ${text}`);
    
    const response = await fetch('http://localhost:8080/tts/synthesize', {
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

    return await response.arrayBuffer();
  } catch (error) {
    console.error('TTS API 호출 오류:', error);
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
          console.log('✅ TTS 재생 완료');
          resolve();
        };
        
        // 재생 시작
        source.start();
        console.log('🎙️ TTS 재생 시작');
        
      })
      .catch(error => {
        console.error('오디오 디코딩 실패:', error);
        reject(error);
      });
  });
}

/**
 * 새로운 동시 실행 가능한 TTS 함수
 * @param {string} text - 읽을 텍스트
 * @returns {Promise} - 재생 완료 시 resolve
 */
export async function speakTextConcurrent(text) {
  if (!text) return;

  try {
    console.log(`🔊 동시 TTS 시작: ${text}`);
    
    // TTS API 호출하여 오디오 데이터 가져오기
    const audioData = await fetchTTSAudio(text);
    
    // Web Audio API로 재생 (동시 실행 가능)
    await playAudioBuffer(audioData);
    
    console.log(`✅ 동시 TTS 완료: ${text}`);
  } catch (error) {
    console.error('TTS 실행 실패:', error);
    // 에러 발생해도 진행을 멈추지 않음
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
    console.log('🛑 모든 TTS 중지됨');
  }
}

/**
 * 볼륨 조절을 위한 GainNode 사용 버전
 * @param {string} text - 읽을 텍스트
 * @param {number} volume - 볼륨 (0.0 ~ 1.0)
 * @returns {Promise} - 재생 완료 시 resolve
 */
export async function speakTextWithVolume(text, volume = 1.0) {
  if (!text) return;

  try {
    console.log(`🔊 볼륨 조절 TTS 시작: ${text}, 볼륨: ${volume}`);
    
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
      source.onended = resolve;
      source.start();
    });
    
  } catch (error) {
    console.error('볼륨 조절 TTS 실행 실패:', error);
  }
}