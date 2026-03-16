<template>
  <div class="admin-panel">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <h2>Admin Analytics</h2>
              <el-button type="success" @click="exportCsv">Export CSV</el-button>
            </div>
          </template>
          
          <el-table :data="dataStore.stats?.discipline_stats" border stripe v-if="dataStore.stats">
            <el-table-column prop="code" label="Code" width="100" />
            <el-table-column prop="title" label="Title" />
            <el-table-column prop="priority1" label="P1" width="80" align="center" />
            <el-table-column prop="priority2" label="P2" width="80" align="center" />
            <el-table-column prop="priority3" label="P3" width="80" align="center" />
            <el-table-column prop="total" label="Total" width="100" align="center" />
          </el-table>
          
          <div class="summary" v-if="dataStore.stats">
            Total participants: <strong>{{ dataStore.stats.total_participants }}</strong>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useDataStore } from '../store/data';
import { ElMessage } from 'element-plus';

const dataStore = useDataStore();

onMounted(() => {
  dataStore.fetchStats();
});

const exportCsv = async () => {
  try {
    await dataStore.exportCsv();
    ElMessage.success('Export started');
  } catch (error) {
    ElMessage.error('Export failed');
  }
};
</script>

<style scoped>
.admin-panel {
  padding: 2rem;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.summary {
  margin-top: 1.5rem;
  font-size: 1.1rem;
}
</style>
