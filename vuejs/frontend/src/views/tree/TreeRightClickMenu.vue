<script setup>
import { defineEmits } from 'vue';
import { useStore } from 'vuex';

const store = useStore();

//親からこのイベントを渡してあげる
const emit = defineEmits(['showVisble']);

const menuClick = ()=>{

    //vuexに値をセット
    store.commit('TreeRightClickMenuHide');

    //親コンポーネントで拾ってもらうように親のイベントを呼ぶ
    emit('showVisble')
}

</script>

<template>
    <div>
        <ul style="dynamicStyle">
            <li @click="menuClick">部品情報の追加</li>
            <li @click="menuClick">部品を追加</li>
            <li @click="menuClick">自由入力</li>
            <li @click="menuClick">コピー</li>
            <li @click="menuClick">削除</li>
        </ul>
    </div>
</template>

<style scoped>
    ul{
        border:1px solid;
        width: auto;
        list-style:none;
        background: white;
        padding: 2px;
    }
    li:hover{
        background: gainsboro;
        color: red
    }
</style>