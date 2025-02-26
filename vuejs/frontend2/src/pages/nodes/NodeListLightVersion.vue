<script setup>
import { ref, onMounted, defineEmits } from 'vue'
import { getAllNode } from '@/api/node'


// 親コンポーネントにデータを送信する
const emit = defineEmits(['data-sent'])

const nodes = ref([])

/**
 * ノード一覧を取得
 */
const fetchNodes = async () => {
    const list = await getAllNode()

    // 余計なデータを削除
    nodes.value = list.data.map(({ create_at, update_at, description, ...item }) => ({
        ...item
    }))
}

/**
 * 親コンポーネントへ送るデータ
 * @param event 
 * @param rowData 
 */
const sendDataToParent = (event, rowData) => {
    const item = rowData.item;
    emit('data-sent', { id: item.id, name: item.name });
}

/**
 * ページが読み込まれた時に実行
 */
onMounted(async () => {
    await fetchNodes();
})
</script>

<template>
    <v-container>
        <v-data-table :items="nodes" density="compact" @click:row="sendDataToParent" hover="true">

        </v-data-table>
    </v-container>
</template>