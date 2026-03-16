import { defineStore } from 'pinia';
import api from '../api';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        token: localStorage.getItem('token') || null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
        isAdmin: (state) => state.user?.role === 'admin',
    },
    actions: {
        async login(email) {
            // Simplified login for MVP
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', 'nopass'); // Not used in simplified auth

            try {
                const response = await api.post('/auth/token', formData);
                this.token = response.data.access_token;
                localStorage.setItem('token', this.token);
                await this.fetchUser();
            } catch (error) {
                console.error('Login failed', error);
                throw error;
            }
        },
        async fetchUser() {
            if (!this.token) return;
            try {
                const response = await api.get('/auth/me');
                this.user = response.data;
            } catch (error) {
                this.logout();
            }
        },
        async updateProfile(data) {
            try {
                const response = await api.put('/auth/me', data);
                this.user = response.data;
                return response.data;
            } catch (error) {
                console.error('Failed to update profile', error);
                throw error;
            }
        },
        logout() {
            this.user = null;
            this.token = null;
            localStorage.removeItem('token');
        },
    },
});
