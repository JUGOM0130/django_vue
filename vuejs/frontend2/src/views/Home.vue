<script setup lang="js">

const title = import.meta.env.VITE_ENV_LOCAL;
const apiUrl = import.meta.env.VITE_API_URL;
</script>



<template>
    <div>
        <v-container>
            <v-row>
                <v-col>
                    <h1>Home.vue</h1>
                </v-col>
                </v-row>

                <v-row>
                    <v-col>
                    <h3>環境変数</h3>
                        <p>envlocal = {{ title }}</p>
                        <p>apiUrl = {{ apiUrl }}</p>
                    </v-col>
                </v-row>
                
                
                <v-row>
                    <v-col>
                        <h3>各ページへのリンク</h3>
                        <ul>
                            <li>
                                <a href="../../src/pages/nodes/">nodes</a>

                            </li>
                            <li>
                                <a href="../../src/pages/trees/">trees</a>
                            </li>
                        </ul>
                    </v-col>
                </v-row>

        </v-container>
    </div>
</template>