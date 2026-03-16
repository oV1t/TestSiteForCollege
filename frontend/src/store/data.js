import { defineStore } from 'pinia';
import api from '../api';

export const useDataStore = defineStore('data', {
    state: () => ({
        disciplines: [],
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
