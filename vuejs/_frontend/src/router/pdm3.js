import { createRouter, createWebHashHistory } from 'vue-router';
import HomeView from '@/components/pdm3/HomeView.vue';
import NodeList from '@/components/pdm3/node_model/NodeList.vue';
import NodeRegisterForm from '@/components/pdm3/node_model/NodeRegisterForm.vue';
import NodeUpdate from '@/components/pdm3/node_model/NodeUpdate.vue';
import TreeList from '@/components/pdm3/tree_model/TreeList.vue';
import TreeRegistForm from '@/components/pdm3/tree_model/TreeRegistForm.vue';
import CreateTree from '@/components/pdm3/CreateTree.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/node',
    name: 'node_list',
    component: NodeList,
    meta: { title: 'Node List' },
  },
  {
    path: '/node/create',
    name: 'node_register',
    component: NodeRegisterForm,
    meta: { title: 'Node Create' },
  },
  {
    path: '/node/update/:id',
    name: 'node_update',
    component: NodeUpdate,
    meta: { title: 'Node Update' },
    props: true,
  },
  {
    path: '/tree',
    name: 'tree_list',
    component: TreeList,
    meta: { title: 'Tree List' },
  },
  {
    path: '/tree/create',
    name: 'tree_regist',
    component: TreeRegistForm,
    meta: { title: 'Tree Regist' },
  },
  {
    path: '/test',
    name: 'test',
    component: CreateTree,
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
