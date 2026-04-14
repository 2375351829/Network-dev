import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/files',
    name: 'Files',
    component: () => import('../views/Files.vue')
  },
  {
    path: '/share',
    name: 'Share',
    component: () => import('../views/Share.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/Chat.vue')
  },
  {
    path: '/multimedia',
    name: 'Multimedia',
    component: () => import('../views/Multimedia.vue')
  },
  {
    path: '/backup',
    name: 'Backup',
    component: () => import('../views/Backup.vue')
  },
  {
    path: '/notification',
    name: 'Notification',
    component: () => import('../views/Notification.vue')
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('../views/Users.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router