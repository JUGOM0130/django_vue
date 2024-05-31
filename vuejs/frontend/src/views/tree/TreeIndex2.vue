<script setup>

import TreeComponent from './TreeComponent.vue'
import testobject from './testobject';

const a = testobject.data2;

</script>

<template>
    <div>
        <h1>TreeIndex2</h1>
        <TreeComponent :parentobj="a" />

        
    </div>
</template>
