/**
 * Speech API Client
 * Handles communication with backend STT/TTS endpoints
 */

const API_BASE_URL = 'http://localhost:8000/api/v1/speech';

class SpeechAPIClient {
  /**
   * Send audio for transcription
   * @param {Blob} audioBlob
   * @returns {Promise<string>}
   */
  static async transcribeAudio(audioBlob) {
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'audio.webm');

      const response = await fetch(`${API_BASE_URL}/transcribe`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '음성 인식 실패');
      }

      const data = await response.json();
      return data.text;

    } catch (error) {
      console.error('Transcription error:', error);
      throw error;
    }
  }

  /**
   * Send text for synthesis
   * @param {string} text
   * @param {string} voice - Optional voice selection
   * @returns {Promise<Blob>}
   */
  static async synthesizeText(text, voice = 'alloy') {
    try {
      const response = await fetch(`${API_BASE_URL}/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: text,
          voice: voice
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '음성 합성 실패');
      }

      const data = await response.json();

      // Convert hex string back to blob
      const hexString = data.audio;
      const bytes = new Uint8Array(hexString.length / 2);
      for (let i = 0; i < hexString.length; i += 2) {
        bytes[i / 2] = parseInt(hexString.substr(i, 2), 16);
      }
      const audioBlob = new Blob([bytes], { type: 'audio/mp3' });

      return audioBlob;

    } catch (error) {
      console.error('Synthesis error:', error);
      throw error;
    }
  }

  /**
   * Health check
   * @returns {Promise<boolean>}
   */
  static async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

export default SpeechAPIClient;
