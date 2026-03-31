import { defineStore } from 'pinia';
import api from '../api';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        token: localStorage.getItem('token') || null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
        isAdmin(state) {
            if (!state.user) return false;
            // Get role string regardless of if it's a string or an enum object with .value
            const rawRole = state.user.role?.value || state.user.role;
            if (!rawRole) return false;
            
            const role = String(rawRole).toLowerCase().trim();
            console.log('Detected user role:', role);
            return role === 'admin';
        },
    },
    actions: {
        async login(email, password = 'nopass') {
            // Simplified login for MVP
            const formData = new FormData();
            formData.append('username', email);
            formData.append('password', password);

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
