<script setup>
/**
 * 多次元オブジェクトではなく
 * 一次元オブジェクトで表現をするためのサンプル作成
 */
import { ref, onMounted, computed } from 'vue'
import TreeRightClickMenu from './TreeRightClickMenu.vue'
import { useStore } from 'vuex';

const store = useStore();
let ax = ref(0);
let ay = ref(0);
let isShowMenu = ref(store.state.tree_right_click_menu_visible);
let newdata = ref([]);
let data = ref([
    { id: "1", group_id: "1", deep_level: "1", parent_id: "0", code_id: "ALD-A0001" },
    { id: "2", group_id: "1", deep_level: "2", parent_id: "1", code_id: "ALD-A0002" },
    { id: "3", group_id: "1", deep_level: "3", parent_id: "2", code_id: "ALD-A0003" },
    { id: "4", group_id: "1", deep_level: "2", parent_id: "1", code_id: "ALD-A0004" },
    { id: "5", group_id: "1", deep_level: "2", parent_id: "1", code_id: "ALD-A0005" },
    { id: "6", group_id: "1", deep_level: "3", parent_id: "4", code_id: "ALD-A0006" },
    { id: "7", group_id: "1", deep_level: "4", parent_id: "6", code_id: "ALD-A0007" }
])

/**
 * オブジェクトからツリーを生成するメソッド
 */
const createTreeMethod = () => {
    //parentidでソートをかける
    data.value.sort((a, b) => {
        let aa = Number(a.parent_id);
        let bb = Number(b.parent_id);

        if (aa < bb) return -1;
        if (aa > bb) return 1;
        return 0;
    });

    for (let i = 0; i < data.value.length; i++) {

        let parent_index = i;

        //e.parentid
        let targeta = data.value.filter(fe => fe.parent_id == String(parent_index)).sort((uu, yy) => {
            let aa = Number(uu.id);
            let bb = Number(yy.id);

            if (aa < bb) return -1;
            if (aa > bb) return 1;
            return 0;
        });
        targeta.reverse().forEach(t => {
            if (t.parent_id != "0") {
                let findid = t.parent_id;
                let targetidx = newdata.value.findIndex(p => p.id == findid);
                newdata.value.splice(targetidx, 0, t)
            } else {
                //最初の１回
                newdata.value.push(t);
            }
        });
    }
    data.value = [];
    newdata.value.reverse().forEach(e => {
        data.value.push(e)
    });


}

/**
 * ツリー右クリック時にメニュ表示用イベント
 * @param e マウスカーソルの位置を取得するための引数
 *
 */
const rightClick = (e) => {
    //右クリック時のカーソル位置取得
    //表示非常時のフラグをVuexにて管理
    ax.value = e.clientX;
    ay.value = e.clientY;
    store.commit('TreeRightClickMenuShow');
    isShowMenu.value = store.state.tree_right_click_menu_visible;


    //クリックされた要素の情報を退避
    const index = Number(e.target.id);
    console.log(newdata.value[index])
    /*
    let id = newdata.value[index].id;
    let group_id = newdata.value[index].group_id;
    let deep_level = newdata.value[index].deep_level;
    let parent_id = newdata.value[index].parent_id;
    let code_id = newdata.value[index].code_id;
    */
    const { id, group_id, deep_level, parent_id, code_id } = newdata.value[index];
    const pyload = { id: id, group_id: group_id, deep_level: deep_level, parent_id: parent_id, code_id: code_id }
    store.commit('SetObject', pyload)
}

/**
 * マウントした時のイベント
 */
onMounted(() => {
    createTreeMethod();
})

// メニュー表示用のCSS
let dynamicStyle = computed(() => {
    return {
        position: "absolute",
        top: `${ay.value}px`,
        left: `${ax.value}px`
    };
});


const getMenuState = () => {
    /**
     * vuexの値を見て
     * Menuの表示非表示を決めてる
     */
    isShowMenu.value = store.state.tree_right_click_menu_visible;
}

</script>

<template>
    <div>
        <ul>
            <li v-for="(d, index) in data" :key="d.id" @click.right.prevent="rightClick" :id="index">
                <div v-for="n in Number(d.deep_level)" :key="n + d.id" class="space"></div>
                {{ d.code_id }}
            </li>
        </ul>
        <TreeRightClickMenu v-show="isShowMenu" :style="dynamicStyle" @showVisble="getMenuState" />
    </div>
</template>

<style scoped>
.space {
    display: inline-block;
    margin: 0;
    padding: 0;
    width: 20px;
    height: 5px;
}

ul {
    list-style: none;
}

li:hover {
    background: gainsboro;
}
</style>
