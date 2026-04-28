<template>
  <div class="my-choices">
    <el-card class="choices-card">
      <template #header>
        <div class="card-header">
          <h2>Обрані дисципліни</h2>
        </div>
      </template>

      <div v-if="dataStore.myChoices.length > 0">
        <!-- Desktop Table -->
        <div class="desktop-view">
          <el-table :data="dataStore.myChoices" border style="width: 100%">
            <el-table-column prop="priority" label="Пріоритет" width="100" align="center" />
            <el-table-column prop="discipline.code" label="Код" width="100" />
            <el-table-column prop="discipline.title" label="Назва дисципліни" />
            <el-table-column label="Деталі" width="120" align="center">
              <template #default="scope">
                <el-button link type="primary" @click="openDoc(scope.row.discipline.doc_url)">Переглянути</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Mobile Cards -->
        <div class="mobile-view">
          <div v-for="item in dataStore.myChoices" :key="item.id" class="mobile-choice-card">
            <div class="choice-header">
              <span class="priority-label">Пріоритет {{ item.priority }}</span>
              <el-tag size="small">{{ item.discipline.code }}</el-tag>
            </div>
            <div class="choice-body">
              <h4>{{ item.discipline.title }}</h4>
            </div>
            <div class="choice-footer">
              <el-button v-if="item.discipline.doc_url" type="primary" plain size="small" @click="openDoc(item.discipline.doc_url)">
                Переглянути силлабус
              </el-button>
            </div>
          </div>
        </div>
        <div class="footer-note">
          <p>Ви можете обрати дисципліни в <router-link to="/catalog">Каталогу дисциплін</router-link>.</p>
        </div>
      </div>
      
      <el-empty v-else description="Ви ще не обрали жодної дисципліни.">
        <el-button type="primary" @click="$router.push('/catalog')">Перейти до Каталогу дисциплін</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useDataStore } from '../store/data';

const dataStore = useDataStore();

onMounted(() => {
  dataStore.fetchMyChoices();
});

const openDoc = (url) => {
  if (url) window.open(url, '_blank');
};
</script>

<style scoped>
.my-choices {
  width: 95%;
  max-width: 800px;
  margin: 1rem auto;
}
.choices-card {
  padding: 1rem;
}
.footer-note {
  margin-top: 2rem;
  text-align: center;
  color: #909399;
}

.mobile-view {
  display: none;
}

.mobile-choice-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}

.choice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.priority-label {
  font-weight: 700;
  color: #3b82f6;
  font-size: 0.9rem;
}

.choice-body h4 {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
  color: #1e293b;
  line-height: 1.4;
}

.choice-footer {
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .desktop-view {
    display: none;
  }
  .mobile-view {
    display: block;
  }
  .choices-card {
    padding: 0.5rem;
  }
}
</style>
