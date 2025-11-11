/**
 * Audio Utility Functions
 * Handles recording and playback of audio
 */

class AudioRecorder {
  constructor() {
    this.mediaRecorder = null;
    this.audioContext = null;
    this.chunks = [];
    this.isRecording = false;
  }

  /**
   * Start recording audio from microphone
   * @returns {Promise<void>}
   */
  async startRecording() {
    try {
      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });

      // Create MediaRecorder
      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm'
      });

      this.chunks = [];
      this.isRecording = true;

      // Collect audio chunks
      this.mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          this.chunks.push(e.data);
        }
      };

      this.mediaRecorder.start();
      console.log('Recording started');

    } catch (error) {
      console.error('Microphone access denied:', error);
      throw new Error('마이크 접근 권한이 없습니다');
    }
  }

  /**
   * Stop recording and return audio blob
   * @returns {Promise<Blob>}
   */
  async stopRecording() {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('Recording not started'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.chunks, { type: 'audio/webm' });
        this.isRecording = false;
        this.chunks = [];
        
        // Stop all tracks
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        console.log('Recording stopped, blob size:', audioBlob.size);
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Get recording status
   * @returns {boolean}
   */
  isCurrentlyRecording() {
    return this.isRecording;
  }
}

/**
 * Play audio from blob or base64
 * @param {Blob|string} audioData - Audio blob or base64 string
 * @returns {Promise<void>}
 */
export async function playAudio(audioData) {
  return new Promise((resolve, reject) => {
    try {
      let audioBlob;

      // Handle hex string from API response
      if (typeof audioData === 'string') {
        const binaryString = atob(audioData);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        audioBlob = new Blob([bytes], { type: 'audio/mp3' });
      } else {
        audioBlob = audioData;
      }

      const audioUrl = URL.createObjectURL(audioBlob);
      const audioElement = new Audio();

      audioElement.onended = () => {
        URL.revokeObjectURL(audioUrl);
        resolve();
      };

      audioElement.onerror = (error) => {
        URL.revokeObjectURL(audioUrl);
        reject(new Error('오디오 재생 실패: ' + error));
      };

      audioElement.src = audioUrl;
      audioElement.play().catch(reject);

    } catch (error) {
      reject(new Error('오디오 처리 실패: ' + error.message));
    }
  });
}

/**
 * Convert audio blob to hex string for transmission
 * @param {Blob} blob
 * @returns {Promise<string>}
 */
export async function blobToHex(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const bytes = new Uint8Array(reader.result);
      let hex = '';
      for (let i = 0; i < bytes.length; i++) {
        hex += bytes[i].toString(16).padStart(2, '0');
      }
      resolve(hex);
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(blob);
  });
}

/**
 * Convert hex string to audio blob
 * @param {string} hexString
 * @param {string} mimeType
 * @returns {Blob}
 */
export function hexToBlob(hexString, mimeType = 'audio/mp3') {
  const bytes = new Uint8Array(hexString.length / 2);
  for (let i = 0; i < hexString.length; i += 2) {
    bytes[i / 2] = parseInt(hexString.substr(i, 2), 16);
  }
  return new Blob([bytes], { type: mimeType });
}

export default AudioRecorder;
