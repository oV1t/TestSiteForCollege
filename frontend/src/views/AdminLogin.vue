<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>Вхід для адміністратора</h2>
        </div>
      </template>
      <el-form :model="form" label-position="top" @submit.prevent="handleLogin">
        <el-form-item label="Електронна пошта">
          <el-input v-model="form.email" placeholder="admin@rcit.ukr.education" />
        </el-form-item>
        <el-form-item label="Пароль">
          <el-input v-model="form.password" type="password" show-password placeholder="Пароль" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" block native-type="submit" :loading="loading" class="login-btn">
            Увійти в панель
          </el-button>
        </el-form-item>
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
    
    // Safety check: ensure they are actually an admin
    if (auth.isAdmin) {
      ElMessage.success('Успішний вхід в адмін-панель');
      router.push('/admin');
    } else {
      ElMessage.error('Ця сторінка лише для адміністраторів');
      // If a student accidentally logs in here, or if role is wrong, 
      // we might want to logout or just redirect to student area.
      // But for now, we just tell them they are not admin.
      auth.logout(); 
    }
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
  /* Keeping the same background as student login */
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
</style>
