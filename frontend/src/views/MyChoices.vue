<template>
  <div class="my-choices">
    <el-card class="choices-card">
      <template #header>
        <div class="card-header">
          <h2>My Submitted Choices</h2>
        </div>
      </template>

      <div v-if="dataStore.myChoices.length > 0">
        <el-table :data="dataStore.myChoices" border style="width: 100%">
          <el-table-column prop="priority" label="Priority" width="100" align="center" />
          <el-table-column prop="discipline.code" label="Code" width="120" />
          <el-table-column prop="discipline.title" label="Discipline Title" />
          <el-table-column label="Details">
            <template #default="scope">
              <el-button link type="primary" @click="openDoc(scope.row.discipline.doc_url)">View Link</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="footer-note">
          <p>You can change your selection by going back to the <router-link to="/catalog">Catalog</router-link>.</p>
        </div>
      </div>
      
      <el-empty v-else description="No choices submitted yet.">
        <el-button type="primary" @click="$router.push('/catalog')">Go to Catalog</el-button>
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
  max-width: 800px;
  margin: 2rem auto;
}
.choices-card {
  padding: 1rem;
}
.footer-note {
  margin-top: 2rem;
  text-align: center;
  color: #909399;
}
</style>
