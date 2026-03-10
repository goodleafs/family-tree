import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/auth/login',
      name: 'Login',
      component: () => import('@/views/auth/login.vue')
    },
    {
      path: '/auth/register',
      name: 'Register',
      component: () => import('@/views/auth/register.vue')
    },
    {
      path: '/families',
      name: 'Families',
      component: () => import('@/views/family/list.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/families/:id',
      name: 'FamilyDetail',
      component: () => import('@/views/family/detail.vue'),
      meta: { requiresAuth: true }
    },
{
      path: '/families/:id/edit',
      name: 'FamilyEdit',
      component: () => import('@/views/family/edit.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/users',
      name: 'Users',
      component: () => import('@/views/user/list.vue'),
      meta: { requiresAuth: true, requiresSuperuser: true }
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('@/views/user/profile.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/persons',
      name: 'Persons',
      component: () => import('@/views/person/list.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/persons/:id',
      name: 'PersonDetail',
      component: () => import('@/views/person/detail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/tree',
      name: 'Tree',
      component: () => import('@/views/person/tree.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/memorial',
      name: 'Memorial',
      component: () => import('@/views/memorial/list.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/memorial/create',
      name: 'MemorialCreate',
      component: () => import('@/views/memorial/create.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/memorial/:id',
      name: 'MemorialDetail',
      component: () => import('@/views/memorial/detail.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('@/views/admin/index.vue'),
      meta: { requiresAuth: true, requiresSuperuser: true }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/common/404.vue')
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !token) {
    ElMessage.warning('请先登录')
    next('/auth/login')
  } else if ((to.path === '/auth/login' || to.path === '/auth/register') && token) {
    next('/')
  } else if (to.meta.requiresSuperuser) {
    if (!userStore.user && token) {
      await userStore.fetchUser()
    }
    if (!userStore.isSuperuser) {
      ElMessage.error('需要超级管理员权限')
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
