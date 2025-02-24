<template>
    <v-app>
        <v-main>
            <v-container>
                <h1>Tree Register</h1>
                <v-text-field v-model="treename" label="Name" outlined></v-text-field>
                <v-text-field v-model="description" label="Description" outlined></v-text-field>
                
                <v-btn color="secondary" @click="submit">登録</v-btn>
                
                <div v-if="submitted">
                    <p>Entered prefix: {{ prefix }}</p>
                    <p>Selected Option: {{ category }}</p>
                </div>
                
                <div v-if="response.data">
                    <h2>Response:</h2>
                    <p>ID: {{ response.data.id }}</p>
                    <p>Name: {{ response.data.name }}</p>
                    <p>Description: {{ response.data.description }}</p>
                    <p>Version: {{ response.data.code_type }}</p>
                    <p>Created At: {{ response.data.create_at }}</p>
                    <p>Updated At: {{ response.data.update_at }}</p>
                </div>
                
                <div v-if="errorMessage">
                    <p style="color: red;">Error: {{ errorMessage }}</p>
                </div>
            </v-container>
        </v-main>
    </v-app>
</template>

<script setup>
import { ref } from 'vue';
import prefixApi from './api';
import router from './router';

// データの定義
const treename = ref('');
const description = ref('');
const submitted = ref(false);
const response = ref({});
const errorMessage = ref('');

const submit = async () => {
    try {
        const result = await prefixApi.createTree({
            name: treename.value,
            description: description.value
        });
        response.value = result.data;
        submitted.value = true;
        errorMessage.value = '';

        router.push({name:'list_tree'});
    } catch (error) {
        errorMessage.value = 'Failed to register tree: ' + error.message;
    }
    
};
</script>

<style scoped>
/* スタイルをここに追加 */
</style>