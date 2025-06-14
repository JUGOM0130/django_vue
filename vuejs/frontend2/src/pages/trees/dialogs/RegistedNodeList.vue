<script setup>
import { ref, computed, watch } from 'vue'
import axios from '@/api/settings'

// Props と Emits の定義
const props = defineProps({
    modelValue: {
        type: Boolean,
        required: true
    }
})
const emits = defineEmits(['modal-close', 'data-sent']);

// 計算属性
const show = computed(() => props.modelValue)

/**
 * 変数宣言
 */
const nodes = ref([])
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
const loading = ref(false)

/**
 * データ取得関数
 */
const fetchNodes = async () => {
    // すでにデータがある場合は取得しない
    if (nodes.value.length > 0) return

    loading.value = true
    try {
        const list = await axios.get(`${apiBaseUrl}/tree-node/`)
        nodes.value = list.data.map(({ create_at, update_at, description, ...item }) => ({
            id: item.id,
            name: item.name,
            node_type: item.node_type,
            status: item.status,
            code: item.code,
        }))
    } catch (error) {
        console.error('Error fetching nodes:', error)
    } finally {
        loading.value = false
    }
}

// モーダルが開かれたときにデータを取得
watch(() => show.value, async (newVal) => {
    if (newVal) {
        fetchNodes()
    }
})

/**
 * モーダルを閉じる
 */
const modalClose = () => {
    emits('modal-close')
}

/**
 * 親コンポーネントへ送るデータ
 */
const sendDataToParent = (event, rowData) => {
    const item = rowData.item
    emits('data-sent', { id: item.id, name: item.name })
}
</script>

<template>
    <v-dialog v-model="show" width="auto">
        <v-card>
            <v-card-title>
                Node List
                <v-btn icon="mdi-close" @click="modalClose" class="float-right" />
            </v-card-title>
            <v-card-text>
                <v-data-table :loading="loading" :items="nodes" density="compact" @click:row="sendDataToParent"
                    :hover="true">
                    <template v-slot:loading>
                        <v-skeleton-loader type="table-row" :loading="loading"></v-skeleton-loader>
                    </template>
                </v-data-table>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>