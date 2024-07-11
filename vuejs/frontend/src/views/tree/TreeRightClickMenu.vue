<script setup>
import { defineEmits,defineProps,ref} from 'vue';
import { useStore } from 'vuex';

const store = useStore();

//親から変数の値をもらう
const props = defineProps({
    dynamicStyle: Object
})
//親からこのイベントを渡してあげる
const emit = defineEmits(['showVisble']);

let dynamicStyle = ref(props.dynamicStyle)


/**
 * メニュー閉じるイベント
 */
const menuClose = ()=>{

    //vuexに値をセット
    store.commit('TreeRightClickMenuHide');
    //親コンポーネントで拾ってもらうように親のイベントを呼ぶ
    emit('showVisble')
}

/**
 * 部品の追加処理
 */
const addBuhin = ()=>{

    //コンポーネント表示_フラグ管理メソッド
    store.commit('ShowHeaderList');
    //右クリックメニューは閉じる
    store.commit('TreeRightClickMenuHide');
    //親コンポーネントで拾ってもらうように親のイベントを呼ぶ
    emit('showVisble')
    //右クリック時に表示したメニューを閉じる
    menuClose();
}

/**
 * コピーイベント
 */
const materialCopy = () =>{
    console.log("部品コピーメソッド")
    menuClose()
}

/**
 * 削除イベント
 */
const materialDelete = () =>{
    console.log("部品削除メソッド")
    menuClose()
}
</script>

<template>
    <div>
        <ul :style="dynamicStyle">
            <li @click="addBuhin">部品を追加</li>
            <li @click="menuClose">部品情報の追加</li>
            <li @click="menuClose">自由入力</li>
            <li @click="materialCopy">コピー</li>
            <li @click="materialDelete">削除</li>
        </ul>
    </div>
</template>

<style scoped>
    ul,.menu{
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