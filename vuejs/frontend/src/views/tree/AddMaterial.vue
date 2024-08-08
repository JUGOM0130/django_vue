<script setup>
import axios from 'axios';
import { defineEmits, ref, onBeforeUpdate } from 'vue'
import { useStore } from 'vuex';
import qs from 'qs';

const defaultErrorMessage = "AddMaterial.vueでエラー"
const store = useStore();
const DJANGO_BASEURL = process.env.VUE_APP_API_BASE_URL;
//親コンポーネントからこのイベントを渡してあげる
const emit = defineEmits(['showVisble']);
let material_object = []
let material = []
let cmbdt = ref([])
let kind = ref("1")



onBeforeUpdate(() => {
    /*非同期処理が追いつかない場合があるので、DOM更新の前に変数へ値を代入して選択値を表示されるようにする */
    const Combobox_visble = store.state.tree_header_list_visible;
    if (Combobox_visble && material_object.length == 0) {
        material_object = store.state.material_list
        material = material_object.map(m => m.name)/*オブジェクト配列からnameキーを取り出して配列にして返す */
        cmbdt.value = material[0]
    }
})

/**
 * メニューメニューを閉じるメソッド
 */
const close = () => {
    store.commit('HideHeaderList')
    emit('showVisble')
}
/**
 * 決定ボタン押下時処理
 */
const btn_kettei = async () => {
    let index = material.indexOf(cmbdt.value)

    /*パラメータセット */
    let param = {
        code_header: material_object[index].id,
        kind: kind.value  /**ここ1~3に要修正 */
    }
    /*APIコール */
    await axios.post(
        `${DJANGO_BASEURL}/api/code/maxCode/`,
        qs.stringify(param)/**クエリストリングの生成 （シリアライズ＝直列化）*/
    )
        .then((response) => {
            let d = response.data
            let pyload = { id: d.code_id, code_id: d.code }
            store.commit('SetAddTarget', pyload)
        })
        .catch(error => {
            console.error(error)
            alert(defaultErrorMessage)
        })

    /**ツリーで選択済のオブジェクトを取得 分割代入*/
    /**オブジェクトの値は全て文字列にする必要がある */
    const { id, group_id, deep_level } = store.state.select_object
    let pyload = {
        id: String(store.state.add_target_code.id),
        group_id: String(group_id),
        deep_level: String((Number(deep_level) + 1)),
        parent_id: String(id),
        code_id: store.state.add_target_code.code_id
    }
    store.commit('SetNewObject', pyload)


    /**メニュー閉じる */
    close()
}

/*
let dynamicStyle = computed(() => {
    return {
        position: "absolute",
        top: `${store.state.tree_right_click_menu_position.y}px`,
        left: `${store.state.tree_right_click_menu_position.x}px`
    }
});
console.log(dynamicStyle)
*/
</script>
<template>
    <div style="width: 500px; height: 100%;" @click.self="close">

        <div class="area">
            <v-row>
                <v-col class="v-col-4">
                    <v-radio-group v-model="kind">
                        <v-radio label="組" value="1"></v-radio>
                        <v-radio label="部品" value="2"></v-radio>
                        <v-radio label="購入品" value="3"></v-radio>
                    </v-radio-group>
                </v-col>
                <!-- 選択エリア -->
                <v-col class="v-col-8">
                    <v-combobox :label="kind=='1'?'組'
                                :kind=='2'?'部品'
                                :kind=='3'?'購入品'
                                :''"
                                :items=material variant="underlined" v-model="cmbdt">
                    </v-combobox>
                </v-col>
            </v-row>

            <v-row>
                <v-col>
                    <v-btn @click="btn_kettei">決定</v-btn>
                </v-col>
                <v-col></v-col>
                <v-col></v-col>
            </v-row>
        </div>
    </div>
</template>
<style scoped>
.area {
    padding: 10px;
    border: 1px solid green;
    background: white;
}
</style>