<script setup>
import { defineProps, ref } from 'vue'
import ThisComponet from './TreeIndex.vue'
import testobject from './testobject';

const props = defineProps({
    parentobj: Object
})

let o

/**デフォルトオブジェクト */
o = ref(testobject.data)
//console.log("mounted",o.value,"props",props.parentobj,"testobject.data",testobject.data)

/**props.parentにデータがあれば */
if (props.parentobj != undefined) {
    /*オブジェクト上書き */
    o = ref(props.parentobj);
}

const objectadd =(c)=>{
    let random = Math.random()%100
    c.push({id:random,content:`tuikasaki${random}`,child:[]})
}


</script>
<template>
    <div>
        <ul>
            <li v-for="d in o" :key="d.id">
                {{ d.content }}
                <button @click="objectadd(d.child)">+</button>
                <ThisComponet :parentobj="d.child" />
            </li>
        </ul>
    </div>
</template>
<style scoped>
* {
    margin: 0;
    padding: 0;
}
ul{
    margin-left: 20px;
    list-style: none;
}
div{
    background-color: azure;
}
</style>
