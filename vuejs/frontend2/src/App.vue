<script setup>
import { ref } from 'vue'


// スクリプト
</script>

<template>
  <v-app>
    <v-main>
      
      <v-app-bar>
        <v-app-bar-title>ロゴ</v-app-bar-title>
        <v-spacer></v-spacer>
        <v-btn to="/">ホーム</v-btn>
        <v-btn to="/about">About</v-btn>
      </v-app-bar>

      <!-- View Routerをもとに -->
      <router-view />
    </v-main>
  </v-app>
</template>

<style>
/* スタイル */
</style>