// src/router/index.js
import { createRouter, createWebHashHistory } from 'vue-router'

// ルート設定
const routes = [
  , {
    path: '/',
    name: 'Index',
    component: () => import('./Index.vue'),
    meta: {
      title: 'index'
    }
  },
  {
    path: '/create_structure',
    name: 'create_structure',
    component: () => import('./CreateStructure.vue'),
    meta: {
      title: 'create_structure'
    }
  }
]

const router = createRouter({
  history: createWebHashHistory('/src/pages/trees'),
  routes: routes
})

export default router
