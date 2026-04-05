<template>
  <div class="admin-panel">
    <el-tabs type="border-card">
      <el-tab-pane label="Статистика">
        <div class="card-header">
          <h2>Аналітика вибору</h2>
          <div class="actions">
            <el-button type="danger" plain @click="handleReset">Очистити всі вибори</el-button>
            <el-button type="success" @click="exportCsv">Експорт CSV</el-button>
          </div>
        </div>
        <el-table :data="dataStore.stats?.discipline_stats" border stripe v-if="dataStore.stats" :key="dataStore.stats?.discipline_stats?.length">
          <el-table-column type="expand">
            <template #default="props">
              <div class="group-stats-box">
                <h4>Розподіл по групах:</h4>
                <el-table :data="props.row.group_stats" size="small" border style="width: 100%; max-width: 400px;">
                  <el-table-column prop="group" label="Група" />
                  <el-table-column prop="count" label="Кількість студентів" align="center" />
                </el-table>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="code" label="Код" width="100" />
          <el-table-column label="Назва">
            <template #default="{ row }">
              <a v-if="row.doc_url" :href="row.doc_url" target="_blank" class="admin-title-link">
                {{ row.title }}
                <el-icon class="link-icon"><Link /></el-icon>
              </a>
              <span v-else>{{ row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="priority1" label="Пріор. 1" width="100" align="center" />
          <el-table-column prop="priority2" label="Пріор. 2" width="100" align="center" />
          <el-table-column prop="priority3" label="Пріор. 3" width="100" align="center" />
          <el-table-column prop="total" label="Всього" width="80" align="center" />
        </el-table>
        <div class="summary" v-if="dataStore.stats">
          Всього студентів що зробили вибір: <strong>{{ dataStore.stats.total_participants }}</strong>
        </div>
      </el-tab-pane>

      <el-tab-pane label="Управління дисциплінами">
        <div class="card-header mb-10">
          <h2>Дисципліни</h2>
          <div class="actions">
            <el-button type="success" plain @click="triggerUpload">Імпорт Excel/CSV</el-button>
            <el-button type="primary" @click="openDialog()">Додати дисципліну</el-button>
            <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none" accept=".xlsx, .csv" />
          </div>
        </div>
        
        <el-table :data="dataStore.adminDisciplines" border stripe>
          <el-table-column prop="code" label="Код" width="100" />
          <el-table-column label="Назва">
            <template #default="{ row }">
              <a v-if="row.doc_url" :href="row.doc_url" target="_blank" class="admin-title-link">
                {{ row.title }}
                <el-icon class="link-icon"><Link /></el-icon>
              </a>
              <span v-else>{{ row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="teacher_name" label="Викладач" width="150" />
          <el-table-column prop="credits" label="Кред." width="70" align="center" />
          <el-table-column prop="active" label="Статус" width="100">
            <template #default="{ row }">
              <el-tag :type="row.active ? 'success' : 'danger'">{{ row.active ? 'Активна' : 'Неактивна' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Дії" width="180" align="center">
            <template #default="{ row }">
              <el-button size="small" @click="openDialog(row)">Ред.</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row.id)">Видалити</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- Dialog for Create / Edit -->
    <el-dialog :title="form.id ? 'Редагувати дисципліну' : 'Нова дисципліна'" v-model="dialogVisible" width="600px">
      <el-form :model="form" label-position="top">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Код дисципліни" required>
              <el-input v-model="form.code" placeholder="ВБ.01" />
            </el-form-item>
          </el-col>
          <el-col :span="16">
            <el-form-item label="Назва" required>
              <el-input v-model="form.title" placeholder="Повна назва" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Викладач">
              <el-input v-model="form.teacher_name" placeholder="ПІБ викладача" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Кредити">
              <el-input-number v-model="form.credits" :min="0" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="Тип">
              <el-select v-model="form.competence_type" placeholder="Оберіть">
                <el-option label="Загальні" value="Загальні" />
                <el-option label="Спеціальні" value="Спеціальні" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Циклова комісія (опц.)">
              <el-input v-model="form.commission_name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Шифр спеціальності (опц.)">
              <el-input v-model="form.specialty_code" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Опис / Компетентності">
          <el-input type="textarea" v-model="form.short_info" :rows="3" />
        </el-form-item>
        
        <el-form-item label="Посилання на Google Disk / Силабус">
          <el-input v-model="form.doc_url" placeholder="https://..." />
        </el-form-item>

        <el-form-item label="Статус">
          <el-switch v-model="form.active" active-text="Активна" inactive-text="Неактивна" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Скасувати</el-button>
          <el-button type="primary" @click="saveDiscipline" :loading="saving">Зберегти</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive } from 'vue';
import { useDataStore } from '../store/data';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Link } from '@element-plus/icons-vue';

const dataStore = useDataStore();

const dialogVisible = ref(false);
const saving = ref(false);
const fileInput = ref(null);

const triggerUpload = () => {
fileInput.value.click();
};

const handleFileUpload = async (event) => {
const file = event.target.files[0];
if (!file) return;

try {
  const result = await dataStore.importDisciplines(file);
  ElMessage.success(result.message);
  dataStore.fetchAdminDisciplines();
  dataStore.fetchStats();
} catch (error) {
  ElMessage.error(error.response?.data?.detail || 'Помилка при імпорті файлу');
} finally {
  event.target.value = ''; // Reset input
}
};

const form = reactive({
  id: null,
  code: '',
  title: '',
  short_info: '',
  doc_url: '',
  commission_name: '',
  specialty_code: '',
  credits: 0,
  teacher_name: '',
  competence_type: '',
  active: true
});

onMounted(() => {
  dataStore.fetchStats().catch(err => console.error('Failed to fetch stats:', err));
  dataStore.fetchAdminDisciplines().catch(err => console.error('Failed to fetch disciplines:', err));
});

const exportCsv = async () => {
  try {
    await dataStore.exportCsv();
    ElMessage.success('Експорт розпочато');
  } catch (error) {
    ElMessage.error('Помилка при експорті');
  }
};

const openDialog = (row = null) => {
  if (row) {
    form.id = row.id;
    form.code = row.code;
    form.title = row.title;
    form.short_info = row.short_info || '';
    form.doc_url = row.doc_url || '';
    form.commission_name = row.commission_name || '';
    form.specialty_code = row.specialty_code || '';
    form.credits = row.credits || 0;
    form.teacher_name = row.teacher_name || '';
    form.competence_type = row.competence_type || '';
    form.active = row.active !== false;
  } else {
    form.id = null;
    form.code = '';
    form.title = '';
    form.short_info = '';
    form.doc_url = '';
    form.commission_name = '';
    form.specialty_code = '';
    form.credits = 0;
    form.teacher_name = '';
    form.competence_type = '';
    form.active = true;
  }
  dialogVisible.value = true;
};

const saveDiscipline = async () => {
  if (!form.code || !form.title) {
    ElMessage.warning('Вкажіть код та назву дисципліни');
    return;
  }
  
  saving.value = true;
  try {
    const payload = {
      code: form.code,
      title: form.title,
      short_info: form.short_info,
      doc_url: form.doc_url,
      commission_name: form.commission_name,
      specialty_code: form.specialty_code,
      credits: form.credits,
      teacher_name: form.teacher_name,
      competence_type: form.competence_type,
      active: form.active
    };
    
    if (form.id) {
      await dataStore.updateDiscipline(form.id, payload);
      ElMessage.success('Дисципліну оновлено');
    } else {
      await dataStore.createDiscipline(payload);
      ElMessage.success('Дисципліну створено');
    }
    
    dataStore.fetchStats(); 
    dialogVisible.value = false;
  } catch (error) {
    ElMessage.error('Помилка при збереженні');
  } finally {
    saving.value = false;
  }
};

const handleReset = () => {
  ElMessageBox.confirm(
    'Це видалить УСІ вибори студентів з бази даних. Ця дія незворотна. Продовжити?',
    'Скидання системи',
    {
      confirmButtonText: 'Так, очистити все',
      cancelButtonText: 'Скасувати',
      type: 'error',
    }
  ).then(async () => {
    try {
      const res = await dataStore.resetChoices();
      ElMessage.success(res.message);
    } catch (error) {
      ElMessage.error('Помилка при очищенні даних');
    }
  }).catch(() => {});
};

const handleDelete = (id) => {
  ElMessageBox.confirm('Ви впевнені, що хочете видалити цю дисципліну?', 'Увага', {
    confirmButtonText: 'Так',
    cancelButtonText: 'Ні',
    type: 'warning',
  }).then(async () => {
    try {
      const res = await dataStore.deleteDiscipline(id);
      ElMessage.success(res.message || 'Видалено успішно');
      dataStore.fetchStats();
    } catch (error) {
      ElMessage.error('Помилка під час видалення');
    }
  }).catch(() => {});
};
</script>

<style scoped>
.admin-panel {
  padding: 1rem;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.mb-10 {
  margin-bottom: 10px;
}
.summary {
  margin-top: 1.5rem;
  font-size: 1.1rem;
}
.group-stats-box {
  padding: 1rem 2rem;
  background-color: #f8fafc;
  border-radius: 4px;
}
.group-stats-box h4 {
  margin-top: 0;
  margin-bottom: 0.75rem;
  color: #64748b;
}

.admin-title-link {
  color: #409eff;
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.admin-title-link:hover {
  text-decoration: underline;
}

.link-icon {
  font-size: 14px;
}
</style>
