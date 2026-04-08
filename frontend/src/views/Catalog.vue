<template>
  <div class="catalog">
    <div class="catalog-header">
      <h1>Каталог вибіркових дисциплін</h1>
      <p>Оберіть 2 або 3 пріоритетні дисципліни для вашого навчання</p>
    </div>

    <!-- Filters Section -->
    <div class="catalog-filters">
      <div class="filter-group-primary">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук за назвою або викладачем..."
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <div class="filter-group-secondary">

        
        <el-button 
          v-if="searchQuery" 
          @click="resetFilters" 
          link 
          class="reset-link"
        >
          Скинути
        </el-button>
      </div>
    </div>

    <el-row :gutter="24" v-if="filteredDisciplines.length > 0">
      <el-col v-for="discipline in filteredDisciplines" :key="discipline.id" :xs="24" :sm="12" :lg="8">
        <el-card class="discipline-card" shadow="hover">
          <div class="card-content">
            <div class="card-header">
              <h3 class="discipline-title">
                <a v-if="discipline.doc_url" :href="discipline.doc_url" target="_blank" class="title-link">
                  {{ discipline.title }}
                  <el-icon class="link-icon" :size="14"><Link /></el-icon>
                </a>
                <span v-else>{{ discipline.title }}</span>
              </h3>
              <el-tag :type="discipline.active ? 'success' : 'info'" size="small" class="code-tag">
                {{ discipline.code }}
              </el-tag>
            </div>
            
            <div class="description-container">
              <p class="description">{{ discipline.short_info || 'Опис дисципліни відсутній.' }}</p>
            </div>

            <div class="discipline-meta">
              <div class="meta-item popularity" v-if="discipline.choice_count > 0">
                <el-icon><UserFilled /></el-icon>
                <span>Обрали: <b>{{ discipline.choice_count }}</b> студентів</span>
              </div>
              <div class="meta-item" v-if="discipline.teacher_name">
                <el-icon><User /></el-icon>
                <span>{{ discipline.teacher_name }}</span>
              </div>
              <div class="meta-tags">
                <el-tag size="small" type="warning" v-if="discipline.credits">
                  {{ discipline.credits }} кред.
                </el-tag>
                <el-tag size="small" type="success" v-if="discipline.competence_type">
                  {{ discipline.competence_type }}
                </el-tag>
              </div>
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

    <!-- Empty State -->
    <el-empty 
      v-else 
      description="Нічого не знайдено за вашим запитом" 
      class="empty-state"
    >
      <el-button type="primary" @click="resetFilters">Скинути всі фільтри</el-button>
    </el-empty>

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
import { onMounted, ref, computed } from 'vue';
import { useDataStore } from '../store/data';
import { ElMessage } from 'element-plus';
import { User, Link, UserFilled, Search } from '@element-plus/icons-vue';

const dataStore = useDataStore();
const showConfirm = ref(false);
const submitting = ref(false);

const searchQuery = ref('');


const filteredDisciplines = computed(() => {
  return dataStore.disciplines.filter(d => {
    const matchesSearch = !searchQuery.value || 
      d.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (d.teacher_name && d.teacher_name.toLowerCase().includes(searchQuery.value.toLowerCase()));
    
    const matchesSpec = true;
    
    return matchesSearch && matchesSpec;
  });
});

const resetFilters = () => {
  searchQuery.value = '';

};

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

.catalog-filters {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 900px;
  margin: 0 auto 2.5rem;
  background: white;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.05);
}

@media (min-width: 768px) {
  .catalog-filters {
    flex-direction: row;
    align-items: center;
  }
}

.filter-group-primary {
  flex: 1;
}

.filter-group-secondary {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 8px 16px;
  box-shadow: 0 0 0 1px #e2e8f0 inset;
}



.reset-link {
  color: #94a3b8;
  font-weight: 500;
}

.empty-state {
  margin-top: 4rem;
  background: white;
  padding: 60px;
  border-radius: 24px;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.card-content {
  padding: 8px;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 220px;
}

.discipline-title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.4;
  flex: 1;
}

.title-link {
  color: #1e293b;
  text-decoration: none;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-link:hover {
  color: #409eff;
  text-decoration: underline;
}

.link-icon {
  opacity: 0.5;
  transition: opacity 0.2s;
}

.title-link:hover .link-icon {
  opacity: 1;
}

.code-tag {
  font-weight: 600;
  width: fit-content;
  letter-spacing: 0.05em;
  padding: 0 12px;
  border-radius: 8px;
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

.discipline-meta {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.popularity {
  color: #3b82f6;
  background-color: #eff6ff;
  padding: 4px 10px;
  border-radius: 6px;
  width: fit-content;
}

.meta-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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
