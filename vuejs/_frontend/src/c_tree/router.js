import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path:'/',
    name:'list_tree',
    component: () => import('./ListView.vue')
  },{
    path:'/create',
    name:'create_tree',
    component: () => import('./CreateView.vue')
  },{
    path:'/createstracure',
    name:'create_stracure',
    component: () => import('./CreateStructure.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(process.env.BASE_URL+"/tree"),
  routes
})

export default router

/*
console.log(router.resolve({ name: 'list_prefix' }));
console.log(router.getRoutes());
*/