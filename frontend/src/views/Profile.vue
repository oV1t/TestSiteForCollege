<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header profile-header">
          <el-avatar :size="64" :src="auth.user?.picture_url" class="profile-avatar">
            {{ auth.user?.full_name?.charAt(0)?.toUpperCase() || 'U' }}
          </el-avatar>
          <div class="header-text">
            <span>Мій профіль</span>
            <p class="role-badge">{{ auth.isAdmin ? 'Адміністратор' : 'Студент' }}</p>
          </div>
        </div>
      </template>
      <el-form :model="form" :rules="rules" ref="profileForm" label-width="120px" @submit.prevent="submitForm">
        <el-form-item label="Email">
          <el-input v-model="auth.user.email" disabled></el-input>
        </el-form-item>
        <el-form-item label="ПІБ" prop="full_name">
          <el-input v-model="form.full_name"></el-input>
        </el-form-item>
        <el-form-item label="Група" prop="group_name" v-if="!auth.isAdmin">
          <el-input v-model="form.group_name"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading">Зберегти</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { useAuthStore } from '../store/auth';
import { ElMessage } from 'element-plus';

const auth = useAuthStore();
const profileForm = ref(null);
const loading = ref(false);

const form = reactive({
  full_name: '',
  group_name: ''
});

const rules = {
  full_name: [
    { required: true, message: 'Будь ласка, введіть ПІБ', trigger: 'blur' }
  ]
};

const populateForm = () => {
  if (auth.user) {
    form.full_name = auth.user.full_name || '';
    form.group_name = auth.user.group_name || '';
  }
};

onMounted(() => {
  populateForm();
});

watch(() => auth.user, () => {
  populateForm();
});

const submitForm = async () => {
  if (!profileForm.value) return;
  await profileForm.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        await auth.updateProfile(form);
        ElMessage.success('Профіль успішно оновлено');
      } catch (error) {
        ElMessage.error('Не вдалося оновити профіль');
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.profile-container {
  width: 95%;
  max-width: 600px;
  margin: 1rem auto;
}
.card-header {
  font-weight: bold;
  font-size: 1.2rem;
}
.profile-header {
  display: flex;
  align-items: center;
  gap: 16px;
}
.profile-avatar {
  background-color: #409eff;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.header-text {
  display: flex;
  flex-direction: column;
}
.role-badge {
  margin: 0;
  font-size: 0.8rem;
  font-weight: normal;
  color: #909399;
}
</style>
