import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path:'/',
    name:'login',
    component: () => import('../views/login/LoginView.vue')
  }
]

console.log(process.env.BASE_URL,"thisbase")
const router = createRouter({

  history: createWebHashHistory(process.env.BASE_URL),
  routes
})

export default router
