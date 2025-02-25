<script setup>
const envfile = import.meta.env.VITE_ENV_FILE_NAME;
const apiUrl = import.meta.env.VITE_API_URL;
const enviroment = import.meta.env.VITE_ENV;

</script>
<template>
    <p>API URL: <span class="orange">{{ apiUrl }}</span></p>
    <p>env FileName: <span class="orange">{{ envfile }}</span></p>
    <p>env : <span class="red">{{ enviroment }}</span></p>
</template>
<style scoped>
/* スタイル */
.red {
    color: red;
}

.orange {
    color: orange;
}
</style>