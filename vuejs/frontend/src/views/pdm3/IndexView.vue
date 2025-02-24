<script setup>
</script>

<template>
  <!-- Vuetifyのアプリケーションラッパー -->
  <v-app>
    <!-- ヘッダー部分 -->
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>PDM3 IndexView</v-toolbar-title>
      <v-spacer></v-spacer>

      <!-- ナビゲーションリンク -->
      <v-btn text="" :to="{ name: 'home' }">Home</v-btn>
      <v-btn text="" :to="{ name: 'node_list' }">Node List</v-btn>
      <v-btn text="" :to="{ name: 'node_register' }">Node Create</v-btn>
      
      <v-btn text="" :to="{ name: 'tree_list' }">Tree List</v-btn>
      <v-btn text="" :to="{ name: 'tree_regist' }">Tree Create</v-btn>
      
      
    </v-app-bar>

    <!-- メインコンテンツ -->
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<style scoped>
.v-btn {
  font-weight: bold;
}
</style>
