import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index.vue'),
      meta: { requiresAuth: true, title: '首页' }
    },
    {
      path: '/auth/login',
      name: 'Login',
      component: () => import('@/views/auth/login.vue'),
      meta: { title: '登录' }
    },
    {
      path: '/auth/register',
      name: 'Register',
      component: () => import('@/views/auth/register.vue'),
      meta: { title: '注册' }
    },
    {
      path: '/families',
      name: 'Families',
      component: () => import('@/views/family/list.vue'),
      meta: { requiresAuth: true, title: '家族列表' }
    },
    {
      path: '/families/:id',
      name: 'FamilyDetail',
      component: () => import('@/views/family/detail.vue'),
      meta: { requiresAuth: true, title: '家族详情' }
    },
    {
      path: '/families/:id/edit',
      name: 'FamilyEdit',
      component: () => import('@/views/family/edit.vue'),
      meta: { requiresAuth: true, title: '编辑家族' }
    },
    {
      path: '/persons',
      name: 'Persons',
      component: () => import('@/views/person/list.vue'),
      meta: { requiresAuth: true, title: '成员列表' }
    },
    {
      path: '/persons/:id',
      name: 'PersonDetail',
      component: () => import('@/views/person/detail.vue'),
      meta: { requiresAuth: true, title: '成员详情' }
    },
    {
      path: '/tree',
      name: 'Tree',
      component: () => import('@/views/person/tree.vue'),
      meta: { requiresAuth: true, title: '族谱树' }
    },
    {
      path: '/memorial',
      name: 'Memorial',
      component: () => import('@/views/memorial/list.vue'),
      meta: { requiresAuth: true, title: '灵堂列表' }
    },
    {
      path: '/memorial/create',
      name: 'MemorialCreate',
      component: () => import('@/views/memorial/create.vue'),
      meta: { requiresAuth: true, title: '创建灵堂' }
    },
    {
      path: '/memorial/:id',
      name: 'MemorialDetail',
      component: () => import('@/views/memorial/detail.vue'),
      meta: { requiresAuth: true, title: '灵堂详情' }
    },
    {
      path: '/families/:id/albums',
      name: 'FamilyAlbums',
      component: () => import('@/views/album/index.vue'),
      meta: { requiresAuth: true, title: '家族相册' }
    },
    {
      path: '/families/:id/albums/:albumId',
      name: 'AlbumDetail',
      component: () => import('@/views/album/detail.vue'),
      meta: { requiresAuth: true, title: '相册详情' }
    },
    {
      path: '/families/:id/documents',
      name: 'FamilyDocuments',
      component: () => import('@/views/document/index.vue'),
      meta: { requiresAuth: true, title: '文献库' }
    },
    {
      path: '/families/:id/biographies',
      name: 'FamilyBiographies',
      component: () => import('@/views/biography/index.vue'),
      meta: { requiresAuth: true, title: '人物传记' }
    },
    {
      path: '/families/:id/biographies/:bioId',
      name: 'BiographyDetail',
      component: () => import('@/views/biography/detail.vue'),
      meta: { requiresAuth: true, title: '传记详情' }
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('@/views/user/profile.vue'),
      meta: { requiresAuth: true, title: '个人资料' }
    },
    {
      path: '/users',
      name: 'Users',
      component: () => import('@/views/user/list.vue'),
      meta: { requiresAuth: true, requiresSuperuser: true, title: '用户管理' }
    },
    {
      path: '/admin',
      name: 'Admin',
      component: () => import('@/views/admin/index.vue'),
      meta: { requiresAuth: true, requiresSuperuser: true, title: '系统管理' }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/common/404.vue'),
      meta: { title: '页面不存在' }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '寻根族谱'} - 寻根族谱管理系统`
  
  const token = localStorage.getItem('token')
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if ((to.path === '/auth/login' || to.path === '/auth/register') && token) {
    next({ name: 'Dashboard' })
  } else if (to.meta.requiresSuperuser) {
    if (!userStore.user && token) {
      await userStore.fetchUser()
    }
    if (!userStore.isSuperuser) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router