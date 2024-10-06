<script setup>
/**
 * 多次元オブジェクトではなく
 * 一次元オブジェクトで表現をするためのサンプル作成
 */
import { ref, onMounted, computed, onBeforeUpdate } from 'vue'
import TreeRightClickMenu from './TreeRightClickMenu.vue'
import { useStore } from 'vuex';
import AddMaterial from './AddMaterial.vue';
import axios from 'axios';
import qs from 'qs';

const defaultErrorMessage = "TreeComponent2.vue内でエラー";
const store = useStore();
const DJANGO_BASEURL=process.env.VUE_APP_API_BASE_URL;
let isShowMenu = ref(store.state.tree_right_click_menu_visible);
let menu2visible = ref(store.state.tree_header_list_visible);
let newdata = ref([]);
let data = ref([
    { id: "1", group_id: "1", deep_level: "1", parent_id: "0", code_id: "ALD-A0001" },
    { id: "2", group_id: "1", deep_level: "2", parent_id: "1", code_id: "ALD-A0002" },
    { id: "3", group_id: "1", deep_level: "3", parent_id: "2", code_id: "ALD-A0003" },
    { id: "4", group_id: "1", deep_level: "2", parent_id: "1", code_id: "ALD-A0004" },
    { id: "5", group_id: "1", deep_level: "2", parent_id: "1", code_id: "ALD-A0005" },
    { id: "140", group_id: "1", deep_level: "3", parent_id: "5", code_id: "ALD-A0006" },
    { id: "141", group_id: "1", deep_level: "4", parent_id: "140", code_id: "ALD-A0007" }
])
let root_node = ref('');
let root_node_temp = ref('');

// グローバルヘッダー設定
axios.defaults.headers.common['My-Token'] = sessionStorage.getItem('user_token');

/**
 * 同期処理でコードのヘッダーを一覧で取得してくるメソッド
 * 取得後は
 */
const getMaterial = async () => {
    await axios.get(`${DJANGO_BASEURL}/api/codeheader`)
        .then((response) => {
            store.commit("SetMaterial", response.data)
        })
        .catch(error => {
            console.error(error);
            alert(defaultErrorMessage)

            //403ならloginにリダイレクト？
        });
}


/**
 * オブジェクトからツリーを生成するメソッド
 */
const createTreeMethod = () => {
    //変数初期化
    newdata.value = [];

    //parentidでソートをかける
    data.value.sort((a, b) => {
        let aa = Number(a.parent_id);
        let bb = Number(b.parent_id);

        if (aa < bb) return -1;
        if (aa > bb) return 1;
        return 0;
    });

    let parent_id_array = [];
    parent_id_array = data.value.map(e => e.parent_id)//オブジェクト配列から特定のキーを取り除いて新しい配列を返す
    parent_id_array = [...new Set(parent_id_array)]//配列から重複値を取り除いた新しい配列を返す


    parent_id_array.forEach((e) => {

        //e.parentid
        let targeta = data.value.filter(fe => fe.parent_id == String(e)).sort((uu, yy) => {
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
    });

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
    const zahyo = { x: e.clientX, y: e.clientY }
    store.commit('TreeRightClickMenuSetPosition', zahyo)
    store.commit('TreeRightClickMenuShow');
    isShowMenu.value = store.state.tree_right_click_menu_visible;


    //クリックされた要素の情報を退避
    const index = Number(e.target.id);

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
    getMaterial();
})

// メニュー表示用のCSS
let dynamicStyle = computed(() => {
    return {
        position: "absolute",
        top: `${store.state.tree_right_click_menu_position.y}px`,
        left: `${store.state.tree_right_click_menu_position.x}px`
    };
});


const getMenuState = () => {
    /**
     * vuexの値を見て
     * Menuの表示非表示を決めてる
     */
    isShowMenu.value = store.state.tree_right_click_menu_visible;
    menu2visible.value = store.state.tree_header_list_visible;
}

/**
 * DOM更新前処理
 */
onBeforeUpdate(() => {
    const { id, group_id, deep_level, parent_id, code_id } = store.state.new_object

    if (id != "" && id != undefined) {
        data.value.push({
            id: id,
            group_id: group_id,
            deep_level: deep_level,
            parent_id: parent_id,
            code_id: code_id
        })
        
        createTreeMethod();
        store.commit("SetEmptyNewObject")
    }
})

/**
 * ルートノード決定ボタンクリック時イベント
 */
const rootNodeDecisionBtnClick = async ()=>{
    /**
     * root_node追加処理とバリデーション
     * DBへ追加API作成
     */
    await axios.post(
        `${DJANGO_BASEURL}/api/rootnode/`,
        qs.stringify({
            "node_name":root_node_temp.value
        })
    ).then((res)=>{
        let {id,node_name} = res.data;

        root_node.value = root_node_temp.value; //仮のRoot名を決定する
        data.value = [                          //ツリー構成配列のリセット
            {
                id: id,
                group_id: node_name,
                deep_level: "1",
                parent_id: "0",
                code_id: node_name
            }
        ];
    }).catch((error)=>{
        console.error(defaultErrorMessage,error)
        alert(error.response.data.node_name)
        root_node_temp.value = "";
    })
}
</script>



<template>
    <div>
        <v-container v-if="root_node==''">
            <v-row class="mb-0 pb-0">
                <v-col>
                    <!-- dense : フィールド自体が少し小さくなります。 -->
                    <!-- hide-details : v-text-fieldにある（v-messagesによって確保されている）領域が不要な場合、スペースを隠すことが可能 -->
                    <v-text-field v-model="root_node_temp" label="ツリーのルート要素を入力してください" class="my-0" dense hide-details></v-text-field>
                </v-col>
            </v-row>
            <v-row class="my-0 py-0">
                <v-col class="my-0 py-0">
                    <v-btn variant="outlined" @click="rootNodeDecisionBtnClick">決定</v-btn>
                </v-col>
            </v-row>
        </v-container>
        <ul v-if="root_node!=''">
            <li v-for="(d, index) in data" :key="d.id" @click.right.prevent="rightClick" :id="index">
                <div v-for="n in Number(d.deep_level)" :key="n + d.id" class="space"></div>
                {{ d.code_id }}
            </li>
        </ul>
        <TreeRightClickMenu v-show="isShowMenu" :style="dynamicStyle" @showVisble="getMenuState" />
        <AddMaterial v-show="menu2visible" :style="dynamicStyle" @showVisble="getMenuState"></AddMaterial>


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
