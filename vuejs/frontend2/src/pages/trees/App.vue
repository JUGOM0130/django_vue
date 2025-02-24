<script setup>
const envfile = import.meta.env.VITE_ENV_FILE_NAME;
const apiUrl = import.meta.env.VITE_API_URL;
const enviroment = import.meta.env.VITE_ENV;

// スクリプト
</script>

<template>
  <v-app>
    <v-main>
      
      <v-app-bar>
        <v-app-bar-title>Trees</v-app-bar-title>
        <v-spacer></v-spacer>
        <v-btn to="/">ホーム</v-btn>
        </v-app-bar>
        <v-container>
          <v-row>
            <v-col>
                <p>API URL: <span class="orange">{{ apiUrl }}</span></p>
                <p>env FileName: <span class="orange">{{ envfile }}</span></p>
                <p>env : <span class="red">{{ enviroment }}</span></p>
            </v-col>
        </v-row>
        </v-container>
      <!-- View Routerをもとに -->
      <router-view />
    </v-main>
  </v-app>
</template>

<style scoped>
/* スタイル */
.red  {
  color: red;
}
.orange {
  color: orange;
}
</style>