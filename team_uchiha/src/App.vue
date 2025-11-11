<script setup>
import { ref } from 'vue'
import SpeechInterface from './components/SpeechInterface.vue'
import AgentInterface from './components/AgentInterface.vue'

const currentView = ref('agent')  // 기본값: agent
</script>

<template>
  <div class="app-container">
    <!-- Navigation Tabs -->
    <div class="nav-tabs">
      <button
        @click="currentView = 'agent'"
        :class="['nav-btn', currentView === 'agent' ? 'active' : '']"
      >
        🤖 AI Agent
      </button>
      <button
        @click="currentView = 'speech'"
        :class="['nav-btn', currentView === 'speech' ? 'active' : '']"
      >
        🎤 음성 인터페이스
      </button>
    </div>

    <!-- Views -->
    <AgentInterface v-if="currentView === 'agent'" />
    <SpeechInterface v-else-if="currentView === 'speech'" />
  </div>
</template>

<style scoped>
.app-container {
  width: 100%;
  min-height: 100vh;
}

.nav-tabs {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.nav-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
</style>
