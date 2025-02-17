// functions/tts.js

/**
 * 음성 목록을 Promise로 반환하여, 음성 목록이 준비될 때 resolve합니다.
 */
export function initVoices() {
    return new Promise((resolve) => {
      let voices = window.speechSynthesis.getVoices();
      if (voices.length) {
        resolve(voices);
      } else {
        window.speechSynthesis.onvoiceschanged = () => {
          voices = window.speechSynthesis.getVoices();
          resolve(voices);
        };
      }
    });
}
  
/**
 * 주어진 텍스트를 읽습니다.
 * @param {string} text - 읽을 텍스트
 * @param {object} [options] - 옵션 객체
 * @param {number} [options.rate=0.8] - 음성 속도 (0.5 ~ 2)
 * @param {string} [options.voiceName='Google 한국의'] - 사용할 음성 이름
 * @returns {Promise} - 음성 읽기가 끝나면 resolve됩니다.
 */
// export function speakText(text, options = {}) {
//     return new Promise(async (resolve, reject) => {
//         if (!text) return resolve();
    
//         const { rate = 0.8, voiceName = 'Google 한국의' } = options;
    
//         // cachedVoices가 미리 로드되어 있다고 가정하거나, await initVoices() 사용
//         const voices = window.speechSynthesis.getVoices();
//         if (!voices.length) {
//             console.error('음성 목록이 아직 로드되지 않았습니다.');
//             return resolve();
//         }
    
//         const voice = voices.find(v => v.name === voiceName) || voices[0];
    
//         const utterance = new SpeechSynthesisUtterance(text);
//         utterance.rate = rate;
//         if (voice) {
//             utterance.voice = voice;
//         }
    
//         utterance.onend = () => {
//             resolve();
//         };
    
//         utterance.onerror = (err) => {
//             console.error(err);
//             resolve();
//         };
    
//         window.speechSynthesis.speak(utterance);
//     });
// }
export async function speakText(text, options = {}) {
    if (!text) return;

    console.log(`🔊 speakText 호출됨: ${text}`); // 🔍 speakText가 몇 번 실행되는지 확인

    const { rate = 0.8, voiceName = 'Google 한국의' } = options;

    // 음성 목록이 준비될 때까지 기다림
    const voices = await initVoices();
    if (!voices.length) {
        console.error('음성 목록을 가져오지 못했습니다.');
        return;
    }

    const voice = voices.find(v => v.name === voiceName) || voices[0];

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = rate;
    if (voice) {
        utterance.voice = voice;
    }

    return new Promise((resolve) => {
        utterance.onstart = () => console.log(`🎙️ 말하기 시작: ${text}`);
        utterance.onend = () => {
            console.log(`✅ 말하기 완료: ${text}`);
            resolve();
        };
        utterance.onerror = (err) => {
            console.error(err);
            resolve();
        };
        
        window.speechSynthesis.speak(utterance);
    });
}

  
  
/**
 * TTS 재생 중지를 위한 함수
 */
export function stopTTS() {
    window.speechSynthesis.cancel();
}
  