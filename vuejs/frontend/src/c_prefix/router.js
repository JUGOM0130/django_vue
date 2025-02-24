import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path:'/',
    name:'list_prefix',
    component: () => import('./ListView.vue')
  }
,  {
    path:'/create',
    name:'create_prefix',
    component: () => import('./CreateView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(process.env.BASE_URL+"prefix/"),
  routes
})

export default router

/*
console.log(router.resolve({ name: 'list_prefix' }));
console.log(router.getRoutes());
*/