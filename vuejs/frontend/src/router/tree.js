import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
/*
  {
    path: '/',
    name: 'treehome',
    component: () => import('../views/tree/TreeIndex.vue')
  },*/
  {
    path: '/test',
    name: 'test',
    component: () => import('../c_tree/TreeIndex2.vue')
  },{
    path: '/treecomponent',
    name: 'treecomponent',
    component: () => import('../c_tree/TreeComponent.vue')
  },{
    path: '/treecomponent2',
    name: 'treecomponent2',
    component: () => import('../c_tree/TreeComponent2.vue')
  },
]

const router = createRouter({
  history: createWebHashHistory(process.env.VUE_APP_API_BASE_URL+"/tree/"),
  routes
})

export default router
