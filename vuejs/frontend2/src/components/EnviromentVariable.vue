<script setup>
import { ref } from 'vue';

// 環境変数を変数に格納
const mode = import.meta.env.MODE;
const envfile = import.meta.env.VITE_ENV_FILE_NAME;
const apiUrl = import.meta.env.VITE_API_URL;
const enviroment = import.meta.env.VITE_ENV;
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

// すべての環境変数をオブジェクトとして格納
const allEnv = { ...import.meta.env };

console.log('Current Environment:', {
    mode,
    envfile,
    apiUrl,
    enviroment,
    apiBaseUrl
});
</script>

<template>
    <div>
        <h2>環境変数確認</h2>
        <p>Current Mode: <span class="blue">{{ mode }}</span></p>
        <p>API URL: <span class="orange">{{ apiUrl || 'Not set' }}</span></p>
        <p>API_BASE_URL: <span class="orange">{{ apiBaseUrl || 'Not set' }}</span></p>
        <p>env FileName: <span class="orange">{{ envfile || 'Not set' }}</span></p>
        <p>env : <span class="red">{{ enviroment || 'Not set' }}</span></p>

        <!-- デバッグ用：全ての環境変数を表示 -->
        <details>
            <summary>All Environment Variables</summary>
            <pre>{{ JSON.stringify(allEnv, null, 2) }}</pre>
        </details>
    </div>
</template>

<style scoped>
.red {
    color: red;
}

.orange {
    color: orange;
}

.blue {
    color: blue;
}

details {
    margin-top: 20px;
    padding: 10px;
    background: #f5f5f5;
}

pre {
    white-space: pre-wrap;
}
</style>