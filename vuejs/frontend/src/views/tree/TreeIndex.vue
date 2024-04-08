<script setup>
import { defineProps, ref } from 'vue'
import ThisComponet from './TreeIndex.vue'

const props = defineProps({
    parentobj: Object
})
/**デフォルトオブジェクト */
let o = ref([
    {
        id: "1",
        child: [
            {
                id: "2",
                child: [

                ]
            }
        ],
    }, {
        id: "3",
        child: [
            {
                id: "4",
                child: [

                ]
            }
        ]
    }
])

if (props.parentobj != null) {
    /*オブジェクト上書き */
    o = ref(props.value);
}

console.log(o.value)


</script>
<template>
    <div>
        <ul>
            <li v-for="d in o" :key="d.id">
                {{ d.id }}
                <ThisComponet :parentobj="d.child" />
            </li>
        </ul>
    </div>
</template>
<style>
* {
    margin: 0;
    padding: 0;
}
</style>
