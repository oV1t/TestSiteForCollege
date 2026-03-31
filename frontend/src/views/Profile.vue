<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>My Profile</span>
        </div>
      </template>
      <el-form :model="form" :rules="rules" ref="profileForm" label-width="120px" @submit.prevent="submitForm">
        <el-form-item label="Email">
          <el-input v-model="auth.user.email" disabled></el-input>
        </el-form-item>
        <el-form-item label="Full Name" prop="full_name">
          <el-input v-model="form.full_name"></el-input>
        </el-form-item>
        <el-form-item label="Group Name" prop="group_name" v-if="!auth.isAdmin">
          <el-input v-model="form.group_name"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading">Save</el-button>
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
    { required: true, message: 'Please input full name', trigger: 'blur' }
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
        ElMessage.success('Profile updated successfully');
      } catch (error) {
        ElMessage.error('Failed to update profile');
      } finally {
        loading.value = false;
      }
    }
  });
};
</script>

<style scoped>
.profile-container {
  max-width: 600px;
  margin: 2rem auto;
}
.card-header {
  font-weight: bold;
  font-size: 1.2rem;
}
</style>
