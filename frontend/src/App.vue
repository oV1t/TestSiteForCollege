<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from './store/auth';

const auth = useAuthStore();

onMounted(() => {
  if (auth.token) {
    auth.fetchUser();
  }
});
</script>

<style>
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}
body {
  background: url('./assets/bg.svg') center/cover no-repeat, linear-gradient(135deg, #5318A8 0%, #331F4F 100%);
  background-attachment: fixed;
  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}
</style>
