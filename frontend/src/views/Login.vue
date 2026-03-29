<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>Login to ElectiveChoice</h2>
        </div>
      </template>
      <el-form :model="form" label-position="top" @submit.prevent="handleLogin">
        <el-form-item label="Електронна пошта">
          <el-input v-model="form.email" placeholder="example@college.edu" />
        </el-form-item>
        <el-form-item label="Пароль">
          <el-input v-model="form.password" type="password" show-password placeholder="Ваш пароль" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" block native-type="submit" :loading="loading" class="login-btn">
            Увійти
          </el-button>
        </el-form-item>
        <p class="hint">Пароль за замовчуванням для студентів: <code>password123</code></p>
      </el-form>
    </el-card>

  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useAuthStore } from '../store/auth';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const auth = useAuthStore();
const router = useRouter();
const loading = ref(false);
const adminDialogVisible = ref(false);
const adminPassword = ref('');

const form = reactive({
  email: '',
  password: '',
});

const handleLogin = async () => {
  if (!form.email || !form.password) {
    ElMessage.warning('Введіть email та пароль');
    return;
  }
  
  loading.value = true;
  try {
    await auth.login(form.email, form.password);
    ElMessage.success('Успішний вхід');
    router.push('/catalog');
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.error('Неправильний email або пароль');
    } else {
      ElMessage.error('Помилка входу. Переконайтеся, що сервер запущено.');
    }
  } finally {
    loading.value = false;
  }
};
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
  width: 400px;
}
.card-header h2 {
  margin: 0;
  text-align: center;
  color: #409eff;
}
.login-btn {
  width: 100%;
}
.hint {
  font-size: 0.8rem;
  color: #999;
  text-align: center;
}
</style>
