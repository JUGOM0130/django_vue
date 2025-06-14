import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path:'/',
    name:'list_node',
    component: () => import('./ListView.vue')
  }
,  {
    path:'/create',
    name:'create_node',
    component: () => import('./CreateView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(process.env.BASE_URL+"node/"),
  routes
})

export default router

/*
console.log(router.resolve({ name: 'list_prefix' }));
console.log(router.getRoutes());
*/