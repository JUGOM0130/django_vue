<script setup>
import { defineProps, ref, onMounted } from 'vue'
import ThisComponet from './TreeComponent.vue'
//import testobject from './testobject';//テストデータ表示用オブジェクト
//import vuex from '@/store/tree'

const props = defineProps({
    parentobj: Object
})
let obj = ref([])


/**
 * +クリック時子オブジェクトに
 * ツリー追加イベント
 * @param c
 */
const objectadd = (child_array,parent_id,deep_level,code_id) => {
    let random = (Math.random()*100) % 100
    child_array.push({
            id:random,/**pushするときはどんな値でもかぶらなければOK あとから追加したりするときにわかりやすいようにprefixとかつけるといいかも*/
            group_id:"hogehoge",
            deep_level:deep_level+1,
            parent_id:parent_id,
            code_id:code_id,
            code_name:"ALD-A0001",
            child:[]
        })

}
const createRootObject = () =>{
    obj.value.push({
            id:"1",/**pushするときはどんな値でもかぶらなければOK あとから追加したりするときにわかりやすいようにprefixとかつけるといいかも*/
            group_id:"hogehoge",
            deep_level:"1",
            parent_id:"0",
            code_id:"1",
            code_name:"ROOT",
            child:[]
        })
}

onMounted(() => {
    /**デフォルトオブジェクト */
    obj.value = []

    /**props.parentにデータがあれば */
    if (props.parentobj != undefined) {
        /*オブジェクト上書き */
        obj.value = props.parentobj;
    }

});


</script>

<template>
    <div>
        <ul>
            <li v-for="d in obj" :key="d.id">
                {{ d.code_name }}
                <button @click="objectadd(d.child,d.id,d.deep_level,d.code_id)">+</button>
                <ThisComponet :parentobj="d.child" />
            </li>
        </ul>
        <p v-if="obj.length==0">ーーーーー<button @click="createRootObject()">+</button></p>
    </div>
</template>

<style scoped>
* {
    margin: 0;
    padding: 0;
}

ul {
    margin-left: 20px;
    list-style: none;
}

div {
    background-color: azure;
}
</style>
