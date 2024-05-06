import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'treehome',
    component: () => import('../views/tree/TreeIndex.vue')
  },
  {
    path: '/test',
    name: 'test',
    component: () => import('../views/tree/TreeIndex2.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(process.env.BASE_URL+"/tree/"),
  routes
})

export default router
