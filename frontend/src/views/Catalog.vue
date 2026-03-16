<template>
  <div class="catalog">
    <el-row :gutter="20">
      <el-col v-for="discipline in dataStore.disciplines" :key="discipline.id" :xs="24" :sm="12" :md="8">
        <el-card class="discipline-card">
          <template #header>
            <div class="card-header">
              <span class="code">{{ discipline.code }}</span>
              <span class="title">{{ discipline.title }}</span>
            </div>
          </template>
          <p class="description">{{ discipline.short_info }}</p>
          <div class="actions">
            <el-button link type="primary" @click="openDoc(discipline.doc_url)">Read Details</el-button>
            <el-button 
              type="success" 
              plain 
              @click="toggleSelection(discipline.id)"
              :disabled="isSelected(discipline.id) && !canAddMore"
            >
              {{ isSelected(discipline.id) ? 'Selected' : 'Select' }}
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div class="selection-fab" v-if="selectedIds.length > 0">
      <el-button type="primary" size="large" @click="showConfirm = true">
        Submit Selection ({{ selectedIds.length }})
      </el-button>
    </div>

    <el-dialog v-model="showConfirm" title="Confirm Choice" width="30%">
      <div v-for="(id, index) in selectedIds" :key="id" class="priority-item">
        <span>Priority {{ index + 1 }}: {{ getTitle(id) }}</span>
      </div>
      <template #footer>
        <el-button @click="showConfirm = false">Cancel</el-button>
        <el-button type="primary" @click="submitChoices" :loading="submitting">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue';
import { useDataStore } from '../store/data';
import { ElMessage } from 'element-plus';

const dataStore = useDataStore();
const selectedIds = ref([]);
const showConfirm = ref(false);
const submitting = ref(false);

onMounted(() => {
  dataStore.fetchDisciplines();
});

const isSelected = (id) => selectedIds.value.includes(id);
const canAddMore = computed(() => selectedIds.value.length < 3);

const toggleSelection = (id) => {
  const index = selectedIds.value.indexOf(id);
  if (index > -1) {
    selectedIds.value.splice(index, 1);
  } else if (canAddMore.value) {
    selectedIds.value.push(id);
  } else {
    ElMessage.warning('Maximum 3 disciplines allowed');
  }
};

const getTitle = (id) => {
  return dataStore.disciplines.find(d => d.id === id)?.title;
};

const openDoc = (url) => {
  if (url) window.open(url, '_blank');
};

const submitChoices = async () => {
  if (selectedIds.value.length < 2) {
    ElMessage.warning('Select at least 2 disciplines');
    return;
  }
  submitting.value = true;
  try {
    await dataStore.submitChoices(selectedIds.value);
    ElMessage.success('Choices submitted successfully');
    showConfirm.ref = false;
    selectedIds.value = [];
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Submission failed');
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.catalog {
  padding: 1rem;
}
.discipline-card {
  margin-bottom: 20px;
  height: 200px;
  display: flex;
  flex-direction: column;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.code {
  font-weight: bold;
  color: #909399;
}
.title {
  font-weight: bold;
}
.description {
  flex-grow: 1;
  color: #606266;
  font-size: 0.9rem;
}
.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}
.selection-fab {
  position: fixed;
  bottom: 40px;
  right: 40px;
  z-index: 100;
}
.priority-item {
  margin-bottom: 10px;
  padding: 10px;
  background-color: #f0f2f5;
  border-radius: 4px;
}
</style>
