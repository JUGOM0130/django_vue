// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// ルート設定
const routes = [
  {
    path: '/',
    name: 'node_list',
    component: () => import('./NodeList.vue'),
    meta: {
      title: 'Node List'
    }
  }]

const router = createRouter({
    history: createWebHistory('/src/pages/nodes'),
    routes: routes
})

export default router
