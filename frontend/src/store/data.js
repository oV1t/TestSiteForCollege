import { defineStore } from 'pinia';
import api from '../api';

export const useDataStore = defineStore('data', {
    state: () => ({
        disciplines: [],
        adminDisciplines: [],
        myChoices: [],
        stats: null,
    }),
    actions: {
        async fetchDisciplines() {
            const response = await api.get('/disciplines');
            this.disciplines = response.data;
        },
        async fetchMyChoices() {
            const response = await api.get('/choices/my');
            this.myChoices = response.data;
        },
        async submitChoices(disciplineIds) {
            await api.post('/choices/submit', disciplineIds);
            await this.fetchMyChoices();
        },
        async fetchStats() {
            const response = await api.get('/admin/stats');
            this.stats = response.data;
        },
        async fetchAdminDisciplines() {
            const response = await api.get('/admin/disciplines');
            this.adminDisciplines = response.data;
        },
        async createDiscipline(data) {
            await api.post('/admin/disciplines', data);
            await this.fetchAdminDisciplines();
        },
        async updateDiscipline(id, data) {
            await api.put(`/admin/disciplines/${id}`, data);
            await this.fetchAdminDisciplines();
        },
        async deleteDiscipline(id) {
            await api.delete(`/admin/disciplines/${id}`);
            await this.fetchAdminDisciplines();
        },
        async exportCsv() {
            const response = await api.get('/admin/export/csv', { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'elective_choices.csv');
            document.body.appendChild(link);
            link.click();
        }
    },
});
