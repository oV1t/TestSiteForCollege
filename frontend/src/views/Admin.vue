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
        <el-table :data="dataStore.stats?.discipline_stats" border stripe v-if="dataStore.stats">
          <el-table-column prop="code" label="Код" width="100" />
          <el-table-column prop="title" label="Назва" />
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
          <el-button type="primary" @click="openDialog()">Додати дисципліну</el-button>
        </div>
        
        <el-table :data="dataStore.adminDisciplines" border stripe>
          <el-table-column prop="code" label="Код" width="100" />
          <el-table-column prop="title" label="Назва" />
          <el-table-column prop="short_info" label="Короткий опис" />
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
    <el-dialog :title="form.id ? 'Редагувати дисципліну' : 'Нова дисципліна'" v-model="dialogVisible" width="500px">
      <el-form :model="form" label-position="top">
        <el-form-item label="Код дисципліни" required>
          <el-input v-model="form.code" placeholder="Наприклад, ВБ.01" />
        </el-form-item>
        <el-form-item label="Назва" required>
          <el-input v-model="form.title" placeholder="Повна назва дисципліни" />
        </el-form-item>
        <el-form-item label="Короткий опис">
          <el-input type="textarea" v-model="form.short_info" />
        </el-form-item>
        <el-form-item label="Посилання на силабус (URL)">
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

const dataStore = useDataStore();

const dialogVisible = ref(false);
const saving = ref(false);

const form = reactive({
  id: null,
  code: '',
  title: '',
  short_info: '',
  doc_url: '',
  active: true
});

onMounted(() => {
  dataStore.fetchStats();
  dataStore.fetchAdminDisciplines();
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
    form.active = row.active !== false;
  } else {
    form.id = null;
    form.code = '';
    form.title = '';
    form.short_info = '';
    form.doc_url = '';
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
</style>
