import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../store/auth';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/login',
            name: 'Login',
            component: () => import('../views/Login.vue'),
        },
        {
            path: '/',
            name: 'Layout',
            component: () => import('../layouts/MainLayout.vue'),
            meta: { requiresAuth: true },
            children: [
                {
                    path: '',
                    name: 'Home',
                    redirect: { name: 'Catalog' },
                },
                {
                    path: 'catalog',
                    name: 'Catalog',
                    component: () => import('../views/Catalog.vue'),
                },
                {
                    path: 'my-choices',
                    name: 'MyChoices',
                    component: () => import('../views/MyChoices.vue'),
                },
                {
                    path: 'profile',
                    name: 'Profile',
                    component: () => import('../views/Profile.vue'),
                },
                {
                    path: 'admin',
                    name: 'Admin',
                    component: () => import('../views/Admin.vue'),
                    meta: { requiresAdmin: true },
                },
            ],
        },
    ],
});

router.beforeEach(async (to, from, next) => {
    const auth = useAuthStore();
    if (!auth.user && auth.token) {
        await auth.fetchUser();
    }

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
        next('/login');
    } else if (to.meta.requiresAdmin && !auth.isAdmin) {
        next('/');
    } else {
        next();
    }
});

export default router;
