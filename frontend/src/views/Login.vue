<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>Login to ElectiveChoice</h2>
        </div>
      </template>
      <el-form :model="form" label-position="top" @submit.prevent="handleLogin">
        <el-form-item label="College Email">
          <el-input v-model="form.email" placeholder="example@college.edu" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" block native-type="submit" :loading="loading" class="login-btn">
            Login / Continue
          </el-button>
        </el-form-item>
        <p class="hint">For MVP, just enter your email. An account will be created if it doesn't exist.</p>
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
});

const handleLogin = async () => {
  if (!form.email) return;
  loading.ref = true;
  try {
    await auth.login(form.email);
    ElMessage.success('Successfully logged in');
    router.push('/catalog');
  } catch (error) {
    ElMessage.error('Login failed');
  } finally {
    loading.ref = false;
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
