<script setup>

import ThisComponet from './TreeComponent.vue'
import testobject from './testobject';

const a = testobject.data;

</script>

<template>
    <div>
        <h1>TreeIndex2</h1>
        <ThisComponet :parentobj="a" />
    </div>
</template>
