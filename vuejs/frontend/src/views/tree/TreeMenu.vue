<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const port_message_visible = !(process.env.NODE_ENV === "production");
const router = useRouter();

const homeClick = () => {
  router.push("/");
};

const treeComponent2Click = () => {
  router.push("/treecomponent2");
};
const dismissBanner = ref(true);
</script>
<template>
  <div>
    <v-app>
      <v-main>
        <!--Application Bar-->
        <v-app-bar :elevation="2">
          <template v-slot:prepend>
            <v-app-bar-nav-icon></v-app-bar-nav-icon>
          </template>

          <v-row class="align-center">
            <v-col cols="auto">
              <v-app-bar-title>TreeMenu.vue</v-app-bar-title>
            </v-col>
            <v-col cols="auto">
              <v-btn variant="outlined" @click="homeClick">HOME</v-btn>
            </v-col>
            <v-col cols="auto">
              <v-btn variant="outlined" @click="treeComponent2Click"
                >TreeComponent2</v-btn
              >
            </v-col>
          </v-row>
        </v-app-bar>


        <!-- 連絡事項用のバナー -->
        <v-banner color="blue" dark v-if="port_message_visible">
          <template v-slot:action>
            <v-btn text @click="dismissBanner">閉じる</v-btn>
          </template>
          ※検証環境DjangoのPortは8001です
        </v-banner>
        <v-banner color="blue" dark v-if="port_message_visible">
          <template v-slot:action>
            <v-btn text @click="dismissBanner">閉じる</v-btn>
          </template>
          <a href="http://133.18.242.137/api/test" blank="_self">133.18.242.137</a>
        </v-banner>

        <!--v-container-->
        <v-container>
          <router-view />
        </v-container>
      
      
      </v-main>
    </v-app>
  </div>
</template>
<style scoped></style>
