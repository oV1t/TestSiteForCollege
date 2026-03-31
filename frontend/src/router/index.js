import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../store/auth';
import Admin from '../views/Admin.vue';

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
                    component: Admin,
                    meta: { requiresAdmin: true },
                },
            ],
        },
    ],
});

router.beforeEach(async (to, from, next) => {
    const auth = useAuthStore();
    console.log(`Navigating to: ${to.path}`, { 
        requiresAuth: to.meta.requiresAuth, 
        requiresAdmin: to.meta.requiresAdmin,
        isAuthenticated: auth.isAuthenticated,
        isAdmin: auth.isAdmin,
        user: auth.user
    });

    if (!auth.user && auth.token) {
        console.log('User not present but token exists, fetching...');
        await auth.fetchUser();
    }

    if (to.meta.requiresAuth && !auth.isAuthenticated) {
        console.log('Access denied: requires auth. Redirecting to /login');
        next('/login');
    } else if (to.meta.requiresAdmin && !auth.isAdmin) {
        console.log('Access denied: requires admin. Redirecting to /');
        next('/');
    } else if (auth.isAdmin && (to.path === '/catalog' || to.path === '/my-choices' || to.path === '/')) {
        console.log('Admin accessing student page, redirecting to /admin');
        next('/admin');
    } else {
        console.log('Access granted');
        next();
    }
});

export default router;
