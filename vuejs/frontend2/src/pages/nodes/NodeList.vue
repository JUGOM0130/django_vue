<script setup>
import { ref, onMounted } from 'vue'
import { getAllNode } from '@/api/node'

const nodes = ref([])

/**
 * ノード一覧を取得
 */
const fetchNodes = async () => {
    const list = await getAllNode()
    nodes.value = list.data.map(item => ({
        ...item,
        create_at: new Date(item.create_at).toLocaleString(),
        update_at: new Date(item.update_at).toLocaleString()
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