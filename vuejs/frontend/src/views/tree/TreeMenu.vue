<script setup>
import {useRouter} from 'vue-router';

const router = useRouter();

const homeClick =()=>{
  router.push('/')
}
const treeClick = () =>{
  router.push('/test')
}
const treeComponentClick = () =>{
  router.push('/treecomponent')
}
const treeComponent2Click = () =>{
  router.push('/treecomponent2')
}
</script>
<template>
  <v-app>
    <v-main>
      <h1>TreeIndex(Menu)</h1>
      <div>
        <v-btn variant="outlined" @click="homeClick">HOME</v-btn>
        <v-btn variant="outlined" @click="treeClick">Tree</v-btn>
        <v-btn variant="outlined" @click="treeComponentClick">TreeComponent</v-btn>
        <v-btn variant="outlined" @click="treeComponent2Click">TreeComponent2</v-btn>
      </div>
      <router-view />
    </v-main>
  </v-app>
</template>

