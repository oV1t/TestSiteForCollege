<template>
  <div class="admin-panel">
    <!-- Admin Filters -->
    <div class="admin-filters-container">
      <div class="filter-row">
        <el-input
          v-model="searchQuery"
          placeholder="Пошук за назвою, кодом або викладачем..."
          class="admin-search"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        


        <el-select
          v-model="selectedCommission"
          placeholder="Циклова комісія"
          clearable
          class="admin-filter-select"
        >
          <el-option
            v-for="item in dataStore.allCommissions"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>

        <el-select
          v-model="selectedSpecialty"
          placeholder="Спеціальність"
          clearable
          class="admin-filter-select"
        >
          <el-option
            v-for="item in dataStore.allSpecialties"
            :key="item"
            :label="item"
            :value="item"
          />
        </el-select>

        <el-select
          v-model="selectedGroup"
          placeholder="Вибір групи"
          clearable
          class="admin-filter-select"
        >
          <el-option
            v-for="group in dataStore.allGroups"
            :key="group"
            :label="group"
            :value="group"
          />
        </el-select>
        
        <el-button v-if="searchQuery || selectedGroup || selectedCommission || selectedSpecialty" @click="resetFilters" link>Скинути</el-button>
      </div>
    </div>

    <el-tabs type="border-card">
      <el-tab-pane label="Статистика">
        <div class="card-header">
          <h2>Аналітика вибору</h2>
          <div class="actions">

            <div class="export-controls">
              <el-input-number
                v-model="exportYear"
                :min="2020"
                :max="2035"
                size="default"
                controls-position="right"
                class="year-picker"
              />
              <el-button type="primary" @click="handleExportXlsx">Експорт Excel</el-button>
              <el-button type="success" @click="exportCsv">Експорт CSV</el-button>
              <el-button type="danger" @click="confirmClearChoices = true">Очистити всі вибори</el-button>
            </div>
          </div>
        </div>
        <div class="desktop-view">
          <el-table :data="filteredStats" border stripe v-if="dataStore.stats" :key="dataStore.stats?.discipline_stats?.length">
            <el-table-column type="expand">
              <template #default="props">
                <div class="group-stats-box">
                  <h4>Розподіл по групах:</h4>
                  <el-table :data="props.row.group_stats" size="small" border style="width: 100%; max-width: 600px;">
                    <el-table-column type="expand">
                      <template #default="groupProps">
                        <div class="student-list">
                          <div v-for="st in groupProps.row.students" :key="st.full_name" class="student-item">
                            <span class="student-name">{{ st.full_name }}</span>
                            <el-tag size="small" effect="plain" type="info">{{ st.year }} р.</el-tag>
                          </div>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column prop="group" label="Група" />
                    <el-table-column prop="count" label="Студентів" align="center" width="120" />
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
        </div>

        <div class="mobile-view stats-mobile">
          <div v-for="row in filteredStats" :key="row.code" class="mobile-stat-card">
            <div class="stat-header">
              <el-tag size="small" type="info">{{ row.code }}</el-tag>
              <span class="total-badge">Всього: {{ row.total }}</span>
            </div>
            <h4>{{ row.title }}</h4>
            <div class="stat-grid">
              <div class="grid-item"><span>П1</span><strong>{{ row.priority1 }}</strong></div>
              <div class="grid-item"><span>П2</span><strong>{{ row.priority2 }}</strong></div>
              <div class="grid-item"><span>П3</span><strong>{{ row.priority3 }}</strong></div>
            </div>
            <el-collapse v-if="row.group_stats && row.group_stats.length > 0">
              <el-collapse-item title="Розподіл по групах">
                <div v-for="g in row.group_stats" :key="g.group" class="mobile-group-row">
                  <span>{{ g.group }}</span>
                  <strong>{{ g.count }}</strong>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
        <div class="summary" v-if="dataStore.stats">
          Всього студентів що зробили вибір: <strong>{{ dataStore.stats.total_participants }}</strong>
        </div>
      </el-tab-pane>

      <el-tab-pane label="Кампанії">
        <div class="card-header mb-10">
          <h2>Кампанії вибору</h2>
          <el-button type="primary" @click="openCampaignDialog()">Нова кампанія</el-button>
        </div>
        <el-table :data="dataStore.campaigns" border stripe>
          <el-table-column prop="id" label="ID" width="60" align="center" />
          <el-table-column prop="name" label="Назва" />
          <el-table-column label="Початок" width="160">
            <template #default="{ row }">{{ formatDate(row.start_date) }}</template>
          </el-table-column>
          <el-table-column label="Кінець" width="160">
            <template #default="{ row }">{{ formatDate(row.end_date) }}</template>
          </el-table-column>
          <el-table-column label="Вибір (мін/макс)" width="140" align="center">
            <template #default="{ row }">{{ row.min_choices }}–{{ row.max_choices }}</template>
          </el-table-column>
          <el-table-column label="Статус" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.active ? 'success' : 'info'">{{ row.active ? 'Активна' : 'Неактивна' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Дії" width="160" align="center">
            <template #default="{ row }">
              <el-button size="small" @click="openCampaignDialog(row)">Ред.</el-button>
              <el-button size="small" type="danger" @click="handleDeleteCampaign(row.id)">Видалити</el-button>
            </template>
          </el-table-column>
        </el-table>
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
        
        <div class="desktop-view">
          <el-table :data="filteredAdminDisciplines" border stripe>
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
        </div>

        <div class="mobile-view admin-mobile">
          <div v-for="row in filteredAdminDisciplines" :key="row.id" class="mobile-admin-card">
            <div class="card-top">
              <el-tag size="small">{{ row.code }}</el-tag>
              <el-tag :type="row.active ? 'success' : 'danger'" size="small">{{ row.active ? 'Активна' : 'Неактивна' }}</el-tag>
            </div>
            <h4>{{ row.title }}</h4>
            <p class="teacher">Викладач: {{ row.teacher_name }}</p>
            <div class="card-actions">
              <el-button size="small" @click="openDialog(row)">Редагувати</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row.id)">Видалити</el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Clear All Choices Confirmation -->
    <el-dialog v-model="confirmClearChoices" title="Очистити всі вибори?" width="420px">
      <p>Ця дія <strong>незворотна</strong> — всі вибори всіх студентів будуть видалені. Статистика обнулиться.</p>
      <p>Введіть <strong>ОЧИСТИТИ</strong> для підтвердження:</p>
      <el-input v-model="clearConfirmText" placeholder="ОЧИСТИТИ" />
      <template #footer>
        <el-button @click="confirmClearChoices = false; clearConfirmText = ''">Скасувати</el-button>
        <el-button type="danger" :disabled="clearConfirmText !== 'ОЧИСТИТИ'" :loading="clearingChoices" @click="handleClearAllChoices">
          Видалити всі вибори
        </el-button>
      </template>
    </el-dialog>

    <!-- Campaign Dialog -->
    <el-dialog :title="campaignForm.id ? 'Редагувати кампанію' : 'Нова кампанія'" v-model="campaignDialogVisible" width="500px">
      <el-form :model="campaignForm" label-position="top">
        <el-form-item label="Назва кампанії" required>
          <el-input v-model="campaignForm.name" placeholder="Вибір 2025/2026" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Дата початку">
              <el-date-picker v-model="campaignForm.start_date" type="datetime" placeholder="Початок" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Дата кінця">
              <el-date-picker v-model="campaignForm.end_date" type="datetime" placeholder="Кінець" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Мінімум дисциплін">
              <el-input-number v-model="campaignForm.min_choices" :min="1" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Максимум дисциплін">
              <el-input-number v-model="campaignForm.max_choices" :min="1" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Статус">
          <el-switch v-model="campaignForm.active" active-text="Активна" inactive-text="Неактивна" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="campaignDialogVisible = false">Скасувати</el-button>
        <el-button type="primary" @click="saveCampaign" :loading="savingCampaign">Зберегти</el-button>
      </template>
    </el-dialog>

    <!-- Dialog for Create / Edit -->
    <el-dialog :title="form.id ? 'Редагувати дисципліну' : 'Нова дисципліна'" v-model="dialogVisible" class="admin-dialog">
      <el-form :model="form" label-position="top">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="8">
            <el-form-item label="Код дисципліни" required>
              <el-input v-model="form.code" placeholder="ВБ.01" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="16">
            <el-form-item label="Назва" required>
              <el-input v-model="form.title" placeholder="Повна назва" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="Викладач">
              <el-input v-model="form.teacher_name" placeholder="ПІБ викладача" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="6">
            <el-form-item label="Кредити">
              <el-input-number v-model="form.credits" :min="0" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="6">
            <el-form-item label="Тип">
              <el-select v-model="form.competence_type" placeholder="Оберіть" style="width: 100%">
                <el-option label="Загальні" value="Загальні" />
                <el-option label="Спеціальні" value="Спеціальні" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :xs="24" :sm="12">
            <el-form-item label="Циклова комісія (опц.)">
              <el-input v-model="form.commission_name" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
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
import { onMounted, ref, reactive, computed } from 'vue';
import { useDataStore } from '../store/data';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Link, Search, School } from '@element-plus/icons-vue';

const dataStore = useDataStore();

const dialogVisible = ref(false);
const saving = ref(false);
const fileInput = ref(null);

const searchQuery = ref('');

const selectedGroup = ref('');
const selectedCommission = ref('');
const selectedSpecialty = ref('');
const exportYear = ref(new Date().getFullYear());

const filteredStats = computed(() => {
  if (!dataStore.stats?.discipline_stats) return [];
  return dataStore.stats.discipline_stats.filter(item => {
    const s = searchQuery.value.toLowerCase();
    const matchesSearch = !s || 
      item.title.toLowerCase().includes(s) || 
      item.code.toLowerCase().includes(s);
    
    const matchesCommission = !selectedCommission.value || item.commission_name === selectedCommission.value;
    const matchesSpec = !selectedSpecialty.value || item.specialty_code === selectedSpecialty.value;
    
    // Group filter logic: check if this group made ANY choices for this discipline
    let matchesGroup = true;
    if (selectedGroup.value) {
      const gStat = item.group_stats?.find(g => g.group === selectedGroup.value);
      matchesGroup = !!(gStat && gStat.count > 0);
    }

    return matchesSearch && matchesCommission && matchesSpec && matchesGroup;
  });
});

const filteredAdminDisciplines = computed(() => {
  return dataStore.adminDisciplines.filter(item => {
    const s = searchQuery.value.toLowerCase();
    const matchesSearch = !s || 
      item.title.toLowerCase().includes(s) || 
      item.code.toLowerCase().includes(s) ||
      (item.teacher_name && item.teacher_name.toLowerCase().includes(s));
    
    const matchesCommission = !selectedCommission.value || item.commission_name === selectedCommission.value;
    const matchesSpec = !selectedSpecialty.value || item.specialty_code === selectedSpecialty.value;
    
    return matchesSearch && matchesCommission && matchesSpec;
  });
});

const resetFilters = () => {
  searchQuery.value = '';
  selectedGroup.value = '';
  selectedCommission.value = '';
  selectedSpecialty.value = '';
};

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
  dataStore.fetchCampaigns().catch(err => console.error('Failed to fetch campaigns:', err));
});

// Campaign management
const confirmClearChoices = ref(false);
const clearConfirmText = ref('');
const clearingChoices = ref(false);

const handleClearAllChoices = async () => {
  clearingChoices.value = true;
  try {
    const res = await dataStore.clearAllChoices();
    ElMessage.success(`Видалено ${res.deleted_choices} виборів`);
    confirmClearChoices.value = false;
    clearConfirmText.value = '';
  } catch { ElMessage.error('Помилка при очищенні'); }
  finally { clearingChoices.value = false; }
};

const campaignDialogVisible = ref(false);
const savingCampaign = ref(false);
const campaignForm = reactive({
  id: null,
  name: '',
  start_date: new Date(),
  end_date: new Date(),
  min_choices: 2,
  max_choices: 3,
  active: true,
});

const formatDate = (d) => d ? new Date(d).toLocaleString('uk-UA') : '—';

const toLocalISO = (d) => {
  if (!d) return null;
  const date = new Date(d);
  const pad = (n) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth()+1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
};

const openCampaignDialog = (row = null) => {
  if (row) {
    campaignForm.id = row.id;
    campaignForm.name = row.name;
    campaignForm.start_date = new Date(row.start_date);
    campaignForm.end_date = new Date(row.end_date);
    campaignForm.min_choices = row.min_choices;
    campaignForm.max_choices = row.max_choices;
    campaignForm.active = row.active;
  } else {
    campaignForm.id = null;
    campaignForm.name = '';
    campaignForm.start_date = new Date();
    campaignForm.end_date = new Date();
    campaignForm.min_choices = 2;
    campaignForm.max_choices = 3;
    campaignForm.active = true;
  }
  campaignDialogVisible.value = true;
};

const saveCampaign = async () => {
  if (!campaignForm.name) { ElMessage.warning('Вкажіть назву кампанії'); return; }
  savingCampaign.value = true;
  try {
    const payload = {
      name: campaignForm.name,
      start_date: toLocalISO(campaignForm.start_date),
      end_date: toLocalISO(campaignForm.end_date),
      min_choices: campaignForm.min_choices,
      max_choices: campaignForm.max_choices,
      active: campaignForm.active,
    };
    if (campaignForm.id) {
      await dataStore.updateCampaign(campaignForm.id, payload);
      ElMessage.success('Кампанію оновлено');
    } else {
      await dataStore.createCampaign(payload);
      ElMessage.success('Кампанію створено');
    }
    campaignDialogVisible.value = false;
  } catch { ElMessage.error('Помилка при збереженні кампанії'); }
  finally { savingCampaign.value = false; }
};

const handleDeleteCampaign = (id) => {
  ElMessageBox.confirm('Видалити кампанію?', 'Увага', {
    confirmButtonText: 'Так', cancelButtonText: 'Ні', type: 'warning',
  }).then(async () => {
    try {
      await dataStore.deleteCampaign(id);
      ElMessage.success('Кампанію видалено');
    } catch { ElMessage.error('Помилка при видаленні'); }
  }).catch(() => {});
};

const exportCsv = async () => {
  try {
    await dataStore.exportCsv();
    ElMessage.success('Експорт CSV розпочато');
  } catch (error) {
    ElMessage.error('Помилка при експорті CSV');
  }
};

const handleExportXlsx = async () => {
  try {
    await dataStore.exportXlsx(exportYear.value);
    ElMessage.success(`Експорт Excel за ${exportYear.value} рік розпочато`);
  } catch (error) {
    ElMessage.error('Помилка при експорті Excel');
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
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.actions {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.admin-filters-container {
  margin-bottom: 1.5rem;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.filter-row {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.admin-search {
  flex: 1;
  max-width: 400px;
}



.admin-filter-select {
  width: 180px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
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

.student-list {
  padding: 0.75rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background-color: #ffffff;
}

.student-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
}

.student-name {
  font-weight: 500;
  color: #334155;
}

.export-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.year-picker {
  width: 100px;
}

.mobile-view {
  display: none;
}

.mobile-stat-card, .mobile-admin-card {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.stat-header, .card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.total-badge {
  font-weight: 700;
  color: #409eff;
}

.mobile-stat-card h4, .mobile-admin-card h4 {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
  line-height: 1.4;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 12px;
  background: #f8fafc;
  padding: 10px;
  border-radius: 6px;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 0.85rem;
}

.grid-item span { color: #94a3b8; margin-bottom: 4px; }
.grid-item strong { color: #1e293b; font-size: 1rem; }

.mobile-group-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}

.teacher {
  font-size: 0.9rem;
  color: #64748b;
  margin-bottom: 16px;
}

.card-actions {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .admin-panel {
    padding: 0.5rem;
  }
  .desktop-view {
    display: none;
  }
  .mobile-view {
    display: block;
  }
  .admin-search {
    max-width: none;
    width: 100%;
  }
  .admin-filter-select {
    width: 100%;
  }
  .actions {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }
  .export-controls {
    flex-direction: column;
    align-items: stretch;
  }
  .year-picker {
    width: 100% !important;
  }
  .admin-dialog {
    width: 98% !important;
    margin-top: 5vh !important;
  }
  .admin-dialog :deep(.el-dialog__body) {
    padding: 15px 10px !important;
  }
}

.admin-dialog {
  width: 600px;
}
</style>
