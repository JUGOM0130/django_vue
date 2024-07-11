<script setup>
import { ref } from "vue";
import axios from "axios";

// 環境変数からAPI URLを取得
const apiUrl = process.env.VUE_APP_API_BASE_URL;
// データとエラーメッセージを管理するリアクティブな変数を定義
const data = ref(null);

const test = () =>{
        axios.get(`${apiUrl}/codeheader`).then(response => {
        data.value = response.data;
      })
      .catch(error => {
        error.value = error.message;
        alert("TreeHeaderListでエラー",error.message)
        console.log("TreeHeaderListでエラー",error)
      });
}


</script>
<template>
    <div>
        <button @click="test">event</button>
        <ul>
            <li v-for="d in data" :key="d.id">
                {{ d.code_header }}
            </li>
        </ul>
    </div>
</template>

<style scoped>
div{
    background: white;
}
</style>