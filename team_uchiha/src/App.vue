<script setup>
import { ref } from 'vue'
import AgentInterface from './components/AgentInterface.vue'

const currentView = ref('agent')  // 기본값: agent
</script>

<template>
  <div class="app-container">
    <!-- Views -->
    <AgentInterface />
  </div>
</template>

<style scoped>
.app-container {
  width: 100%;
  min-height: 100vh;
}


</style>
