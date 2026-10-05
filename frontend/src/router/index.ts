import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: DefaultLayout,
      children: [
        { path: '', name: 'home', component: () => import('@/views/Home.vue') },
        { path: 'learn', name: 'learn', component: () => import('@/views/Learn.vue') },
        { path: 'practice', name: 'practice', component: () => import('@/views/Practice.vue') },
        { path: 'prompt-train', name: 'prompt-train', component: () => import('@/views/PromptTrain.vue') },
        { path: 'interview', name: 'interview', component: () => import('@/views/InterviewTrain.vue'), meta: { requiresAuth: true } },
        { path: 'debug-train', name: 'debug-train', component: () => import('@/views/DebugTrain.vue'), meta: { requiresAuth: true } },
        { path: 'advisor', name: 'advisor', component: () => import('@/views/LearnAdvisor.vue') },
        { path: 'cases', name: 'cases', component: () => import('@/views/Cases.vue') },
        { path: 'settings/ai', name: 'ai-settings', component: () => import('@/views/SettingsAi.vue') },
        { path: 'profile', name: 'profile', component: () => import('@/views/Profile.vue'), meta: { requiresAuth: true } },
        { path: 'class', name: 'class-center', component: () => import('@/views/ClassCenter.vue'), meta: { requiresAuth: true } },
        { path: 'class/:id', name: 'class-detail', component: () => import('@/views/ClassDetail.vue'), meta: { requiresAuth: true } },
        { path: 'tutor', name: 'tutor', component: () => import('@/views/TutorChat.vue'), meta: { requiresAuth: true } },
        { path: 'mistakes', name: 'mistakes', component: () => import('@/views/Mistakes.vue'), meta: { requiresAuth: true } },
        { path: 'rank', name: 'rank', component: () => import('@/views/Rank.vue'), meta: { requiresAuth: true } },
        { path: 'works', name: 'works', component: () => import('@/views/Works.vue'), meta: { requiresAuth: true } },
        { path: 'checkin', name: 'checkin', component: () => import('@/views/Checkin.vue'), meta: { requiresAuth: true } },
        { path: 'plugins', name: 'plugins', component: () => import('@/views/PluginMarket.vue'), meta: { requiresAuth: true } },
      ],
    },
    { path: '/login', name: 'login', component: () => import('@/views/Login.vue') },
  ],
})

const AUTH_ROUTES = ['profile', 'class-center', 'class-detail', 'tutor', 'mistakes', 'rank', 'works', 'checkin', 'plugins', 'debug-train', 'interview']

router.beforeEach((to) => {
  const user = useUserStore()
  if (AUTH_ROUTES.includes(to.name as string) && !user.isLogin) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && user.isLogin) {
    return { name: 'home' }
  }
  return true
})

export default router
