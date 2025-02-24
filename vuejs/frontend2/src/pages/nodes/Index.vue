<script setup>
const env = import.meta.env.VITE_ENV_LOCAL
const apiUrl = import.meta.env.VITE_API_URL
</script>


<template>
    <v-container>
        <v-row>
            <v-col>
                <p>API URL: {{ apiUrl }}</p>
                <p>env File: {{ env }}</p>
            </v-col>
        </v-row>
        <v-data-table>
            
        </v-data-table>
    </v-container>
    <div>
    </div>
</template>
