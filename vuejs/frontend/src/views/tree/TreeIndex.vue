<script setup>
import { ref } from 'vue'
let node = ref(0);
let countup = () =>{
    node.value++;
}
</script>
<template>
    <div>
        <ul>
            <li @click="countup">
                ALC-AA000Z000{{ node }}
            </li>
        </ul>
    </div>
</template>
<style>
* {
    margin:0;
    padding:0;
}
</style>
