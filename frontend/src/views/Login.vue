<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>Вхід для студентів</h2>
        </div>
      </template>

      <div class="google-login-section">
        <p class="description">Для доступу до вибору дисциплін увійдіть через ваш корпоративний Google-акаунт</p>
        
        <!-- Google Sign-In Button Container -->
        <div id="googleButtonContainer" class="google-button-wrapper"></div>
        
        <p class="hint">Тільки для студентів @rcit.ukr.education</p>
      </div>
    </el-card>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../store/auth';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const auth = useAuthStore();
const router = useRouter();
const loading = ref(false);

const handleGoogleResponse = async (response) => {
  loading.value = true;
  try {
    // Send the ID Token (credential) to our backend
    await auth.loginWithGoogle(response.credential);
    ElMessage.success('Успішний вхід через Google');
    router.push('/catalog');
  } catch (error) {
    ElMessage.error('Помилка авторизації Google. Спробуйте пізніше.');
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  // Initialize Google Identity Services
  if (window.google) {
    window.google.accounts.id.initialize({
      client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID || "YOUR_REAL_CLIENT_ID_FROM_GOOGLE_CONSOLE",
      callback: handleGoogleResponse,
      auto_select: false,
    });

    window.google.accounts.id.renderButton(
      document.getElementById("googleButtonContainer"),
      { 
        theme: "outline", 
        size: "large", 
        width: "100%",
        text: "signin_with",
        shape: "rectangular"
      }
    );
  } else {
    console.error("Google Identity Services script not loaded");
  }
});
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: url('../assets/bg.svg') center/cover no-repeat, linear-gradient(135deg, #5318A8 0%, #331F4F 100%);
  background-attachment: fixed;
}
.login-card {
  width: 420px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}
.card-header h2 {
  margin: 0;
  text-align: center;
  color: #1e293b;
  font-weight: 700;
}
.google-login-section {
  padding: 20px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}
.description {
  text-align: center;
  color: #64748b;
  line-height: 1.5;
  font-size: 1rem;
}
.google-button-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  min-height: 40px;
}
.hint {
  font-size: 0.85rem;
  color: #94a3b8;
  font-style: italic;
  margin-top: 8px;
}
</style>
