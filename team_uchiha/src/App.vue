<script setup>
// Router 기반으로 변경
</script>

<template>
  <div class="app-container">
    <!-- 네비게이션 바 -->
    <nav class="nav-bar">
      <router-link to="/" class="nav-btn">🏠 홈</router-link>
      <router-link to="/lecture" class="nav-btn">📚 강의분석</router-link>
      <router-link to="/agent" class="nav-btn">🤖 에이전트</router-link>
    </nav>

    <!-- Router View -->
    <router-view />
  </div>
</template>

<!-- CSS는 layout.css에서 관리 -->
