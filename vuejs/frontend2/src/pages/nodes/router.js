// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// ルート設定
const routes = [
  {
    path: '/',
    name: 'Index',
    component: () => import('./Index.vue'),
    meta: {
      title: 'index'
    }
  }]

const router = createRouter({
    history: createWebHistory('/src/pages/nodes'),
    routes: routes
})

export default router
