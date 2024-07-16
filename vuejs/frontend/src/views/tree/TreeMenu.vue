<script setup>
import { useRouter } from 'vue-router';

const port_message_visible = !(process.env.NODE_ENV === 'production');
const router = useRouter();

const homeClick = () => {
  router.push('/')
}
const treeClick = () => {
  router.push('/test')
}
const treeComponentClick = () => {
  router.push('/treecomponent')
}
const treeComponent2Click = () => {
  router.push('/treecomponent2')
}
</script>
<template>
  <div>
    <v-app>
      <v-main>
        <h1>TreeIndex(Menu)</h1>
        <h4 v-if="port_message_visible">※検証環境DjangoのPortは8001です</h4>
        <a href="http://133.18.242.137/api/test" blank="_self">133.18.242.137</a>
        <div>
          <v-btn variant="outlined" @click="homeClick">HOME</v-btn>
          <v-btn variant="outlined" @click="treeClick">Tree</v-btn>
          <v-btn variant="outlined" @click="treeComponentClick">TreeComponent</v-btn>
          <v-btn variant="outlined" @click="treeComponent2Click">TreeComponent2</v-btn>
        </div>
        <router-view />
      </v-main>
    </v-app>

  </div>
</template>
<style scoped></style>
