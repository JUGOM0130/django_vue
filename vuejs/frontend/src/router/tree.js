import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'treehome',
    component: () => import('../views/tree/TreeIndex.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(process.env.BASE_URL+"/tree"),
  routes
})

export default router
