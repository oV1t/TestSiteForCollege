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
        <div class="profile-pill" @click="$router.push('/profile')">
          <el-avatar :size="32" class="avatar">
            {{ auth.user?.full_name?.charAt(0)?.toUpperCase() || 'U' }}
          </el-avatar>
          <span class="user-name">{{ auth.user?.full_name || 'Profile' }}</span>
        </div>
        <el-tooltip content="Logout" placement="bottom">
          <el-button class="logout-btn" circle @click="logout">
            <LogOut :size="16" />
          </el-button>
        </el-tooltip>
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
import { LogOut } from 'lucide-vue-next';

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
  gap: 12px;
}
.profile-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 16px 4px 4px;
  background-color: #f4f4f5;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 1px solid transparent;
}
.profile-pill:hover {
  background-color: #ecf5ff;
  border-color: #c6e2ff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-1px);
}
.avatar {
  background-color: #409eff;
  color: white;
  font-weight: bold;
  font-size: 1rem;
}
.user-name {
  font-size: 0.95rem;
  font-weight: 500;
  color: #303133;
}
.logout-btn {
  border: none;
  background: transparent;
  color: #909399;
  transition: all 0.3s ease;
}
.logout-btn:hover {
  background-color: #fef0f0;
  color: #f56c6c;
  transform: scale(1.05);
}
</style>
