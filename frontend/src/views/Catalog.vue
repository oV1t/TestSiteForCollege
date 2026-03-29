<template>
  <div class="catalog">
    <div class="catalog-header">
      <h1>Каталог вибіркових дисциплін</h1>
      <p>Оберіть 2 або 3 пріоритетні дисципліни для вашого навчання</p>
    </div>

    <el-row :gutter="24">
      <el-col v-for="discipline in dataStore.disciplines" :key="discipline.id" :xs="24" :sm="12" :lg="8">
        <el-card class="discipline-card" shadow="hover">
          <div class="card-content">
            <div class="header-row">
              <el-tag effect="dark" type="info" class="code-tag">{{ discipline.code }}</el-tag>
              <h3 class="discipline-title">{{ discipline.title }}</h3>
            </div>
            
            <div class="description-container">
              <p class="description">{{ discipline.short_info || 'Опис дисципліни відсутній.' }}</p>
            </div>

            <div class="card-footer">
              <el-button link type="primary" class="details-btn" @click="openDoc(discipline.doc_url)">
                Детальніше
              </el-button>
              <el-button 
                :type="dataStore.isSelected(discipline.id) ? 'success' : 'primary'"
                :plain="!dataStore.isSelected(discipline.id)"
                class="select-btn"
                @click="toggleSelection(discipline.id)"
                :disabled="!dataStore.isSelected(discipline.id) && !dataStore.canAddMore"
              >
                {{ dataStore.isSelected(discipline.id) ? 'Обрано' : 'Обрати' }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div class="selection-fab" v-if="dataStore.selectedIds.length > 0">
      <el-button type="primary" size="large" class="submit-fab" @click="showConfirm = true">
        Підтвердити вибір ({{ dataStore.selectedIds.length }})
      </el-button>
    </div>

    <el-dialog v-model="showConfirm" title="Підтвердження вибору" width="400px" center>
      <div class="confirm-list">
        <p>Ваші обрані дисципліни за пріоритетністю:</p>
        <div v-for="(id, index) in dataStore.selectedIds" :key="id" class="priority-item">
          <span class="priority-badge">{{ index + 1 }}</span>
          <span class="item-title">{{ getTitle(id) }}</span>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showConfirm = false">Скасувати</el-button>
          <el-button type="primary" @click="submitChoices" :loading="submitting">Відправити</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useDataStore } from '../store/data';
import { ElMessage } from 'element-plus';

const dataStore = useDataStore();
const showConfirm = ref(false);
const submitting = ref(false);

onMounted(() => {
  dataStore.fetchDisciplines();
});

const toggleSelection = (id) => {
  const success = dataStore.toggleSelection(id);
  if (!success) {
    ElMessage.warning('Максимум можна обрати 3 дисципліни');
  }
};

const getTitle = (id) => {
  return dataStore.disciplines.find(d => d.id === id)?.title;
};

const openDoc = (url) => {
  if (url) window.open(url, '_blank');
};

const submitChoices = async () => {
  if (dataStore.selectedIds.length < 2) {
    ElMessage.warning('Оберіть принаймні 2 дисципліни');
    return;
  }
  submitting.value = true;
  try {
    await dataStore.submitChoices(dataStore.selectedIds);
    ElMessage.success('Вибір успішно збережено');
    showConfirm.value = false;
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Помилка при збереженні');
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.catalog {
  padding: 2rem;
  background-color: #f8fafc;
  min-height: calc(100vh - 60px);
}

.catalog-header {
  margin-bottom: 2.5rem;
  text-align: center;
}

.catalog-header h1 {
  font-size: 2.25rem;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
}

.catalog-header p {
  color: #64748b;
  font-size: 1.1rem;
}

.discipline-card {
  margin-bottom: 24px;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
}

.discipline-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -10px rgba(0, 0, 0, 0.1) !important;
  border-color: #3b82f6;
}

.card-content {
  padding: 8px;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 220px;
}

.header-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.code-tag {
  width: fit-content;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 0 12px;
  border-radius: 8px;
}

.discipline-title {
  margin: 0;
  font-size: 1.25rem;
  line-height: 1.4;
  font-weight: 700;
  color: #1e293b;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.description-container {
  flex-grow: 1;
  margin-bottom: 20px;
}

.description {
  margin: 0;
  color: #475569;
  font-size: 0.95rem;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.details-btn {
  font-weight: 600;
  font-size: 0.95rem;
}

.select-btn {
  padding: 0 24px;
  height: 40px;
  border-radius: 10px;
  font-weight: 600;
  transition: all 0.2s;
}

.selection-fab {
  position: fixed;
  bottom: 40px;
  right: 40px;
  z-index: 100;
}

.submit-fab {
  height: 56px !important;
  padding: 0 32px !important;
  border-radius: 28px !important;
  font-size: 1.1rem !important;
  font-weight: 700 !important;
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4) !important;
}

.confirm-list {
  padding: 10px 0;
}

.confirm-list p {
  margin-top: 0;
  margin-bottom: 20px;
  font-weight: 600;
  color: #64748b;
}

.priority-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background-color: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  margin-bottom: 12px;
}

.priority-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background-color: #3b82f6;
  color: rgb(0, 0, 0);
  border-radius: 10%;
  font-weight: 700;
  font-size: 0.85rem;
}

.item-title {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.95rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
