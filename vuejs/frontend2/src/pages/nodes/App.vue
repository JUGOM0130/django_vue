<script setup>
import { ref } from 'vue'
import envComponent from '@/components/EnviromentVariable.vue'


// スクリプト
</script>

<template>
  <v-app>
    <v-main>
      <v-app-bar>
        <v-app-bar-title>Nodes</v-app-bar-title>
        <v-spacer></v-spacer>
        <v-btn to="/">ホーム</v-btn>
      </v-app-bar>
      <v-container>
        <v-row>
          <v-col>
            <!-- 環境変数コンポーネント -->
            <envComponent></envComponent>
          </v-col>
        </v-row>
      </v-container>
      <!-- View Routerをもとに -->
      <router-view />
    </v-main>
  </v-app>
</template>

<style>
/* スタイル */
</style>