import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path:'/',
    name:'login',
    component: () => import('../views/login/LoginView.vue')
  },
  {
    path:'/login',
    name:'login',
    component: () => import('../views/login/LoginView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
