<script setup>
import { ref, onMounted } from 'vue'
import { getAllNode } from '@/api/node'

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
 * ページが読み込まれた時に実行
 */
onMounted(async () => {
    await fetchNodes();
})
</script>

<template>
    <v-container>
        <v-data-table :items="nodes" density="compact">

        </v-data-table>
    </v-container>
</template>