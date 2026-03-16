<template>
  <el-container class="main-layout">
    <el-header class="header">
      <div class="logo">
        <img src="../assets/logo.svg" alt="ElectiveChoice" style="height: 40px; display: block;" />
      </div>
      <el-menu mode="horizontal" router :default-active="$route.path" class="menu">
        <el-menu-item index="/catalog">Catalog</el-menu-item>
        <el-menu-item index="/my-choices">My Choices</el-menu-item>
        <el-menu-item v-if="auth.isAdmin" index="/admin">Admin Panel</el-menu-item>
      </el-menu>
      <div class="user-info">
        <el-button link @click="$router.push('/profile')" class="profile-link">
          {{ auth.user?.full_name }}
        </el-button>
        <el-button link @click="logout">Logout</el-button>
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useAuthStore } from '../store/auth';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const router = useRouter();

const logout = () => {
  auth.logout();
  router.push('/login');
};
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #ddd;
  background-color: #fff;
}
.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #409eff;
}
.menu {
  flex-grow: 1;
  margin-left: 2rem;
  border-bottom: none;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.profile-link {
  font-size: 1rem;
  color: #303133;
}
.profile-link:hover {
  color: #409eff;
}
</style>
