<script setup>
/**
 * 多次元オブジェクトではなく
 * 一次元オブジェクトで表現をするためのサンプル作成
 */
import { ref, onMounted } from 'vue'

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

onMounted(() => {
    createTreeMethod();
})


</script>

<template>
    <div>
        <div v-for="d in data" :key="d.id">
            <div v-for="n in Number(d.deep_level)" :key="n + d.id" class="space"></div>
            {{ d.code_id }}
        </div>
    </div>
</template>

<style>
.space {
    display: inline-block;
    margin: 0;
    padding: 0;
    width: 20px;
    height: 5px;

}
</style>
