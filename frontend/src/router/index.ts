import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  // Blog pages
  {
    path: '/',
    name: 'blog',
    component: () => import('@/components/layout/BlogLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/views/blog/Home.vue'),
      },
      {
        path: '/posts/:slug',
        name: 'post-detail',
        component: () => import('@/views/blog/PostDetail.vue'),
      },
      {
        path: '/categories',
        name: 'categories',
        component: () => import('@/views/blog/Categories.vue'),
      },
      {
        path: '/categories/:name',
        name: 'category-posts',
        component: () => import('@/views/blog/CategoryPosts.vue'),
      },
      {
        path: '/tags',
        name: 'tags',
        component: () => import('@/views/blog/Tags.vue'),
      },
      {
        path: '/tags/:name',
        name: 'tag-posts',
        component: () => import('@/views/blog/TagPosts.vue'),
      },
      {
        path: '/about',
        name: 'about',
        component: () => import('@/views/blog/About.vue'),
      },
    ],
  },
  
  // Admin pages
  {
    path: '/admin',
    component: () => import('@/components/layout/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'admin',
        component: () => import('@/views/admin/Dashboard.vue'),
      },
      {
        path: 'articles',
        name: 'admin-articles',
        component: () => import('@/views/admin/articles/ArticleList.vue'),
      },
      {
        path: 'articles/create',
        name: 'admin-article-create',
        component: () => import('@/views/admin/articles/ArticleEdit.vue'),
      },
      {
        path: 'ai-generator',
        name: 'admin-ai-generator',
        component: () => import('@/views/admin/articles/AIGenerator.vue'),
      },
      {
        path: 'articles/edit/:slug',
        name: 'admin-article-edit',
        component: () => import('@/views/admin/articles/ArticleEdit.vue'),
      },
      {
        path: 'categories',
        name: 'admin-categories',
        component: () => import('@/views/admin/categories/CategoryManage.vue'),
      },
      {
        path: 'tags',
        name: 'admin-tags',
        component: () => import('@/views/admin/tags/TagManage.vue'),
      },
      {
        path: 'comments',
        name: 'admin-comments',
        component: () => import('@/views/admin/comments/CommentManage.vue'),
      },
      {
        path: 'settings',
        name: 'admin-settings',
        component: () => import('@/views/admin/settings/SiteSettings.vue'),
      },
      {
        path: 'donation',
        name: 'admin-donation',
        component: () => import('@/views/admin/donation/DonationSettings.vue'),
      },
    ],
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: () => import('@/views/admin/Login.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = localStorage.getItem('access_token')
  
  if (requiresAuth && !isAuthenticated) {
    next('/admin/login')
  } else if (to.path === '/admin/login' && isAuthenticated) {
    next('/admin')
  } else {
    next()
  }
})

export default router
