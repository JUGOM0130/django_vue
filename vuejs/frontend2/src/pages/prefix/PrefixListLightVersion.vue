<script setup>
import { ref, onMounted, defineEmits } from 'vue'
import { getAllPrefixes, CODE_TYPE_CHOICES } from '@/api/prefix'

// 親コンポーネントにデータを送信する
const emit = defineEmits(['data-sent'])

const prefixes = ref([])

/**
 * プレフィックス一覧を取得
 */
const fetchPrefixes = async () => {
    const list = await getAllPrefixes()

    // 余計なデータを削除
    prefixes.value = list.data.map(({ create_at, update_at, ...item }) => ({
        ...item,
        // コードタイプの表示を変換
        code_type_display: getCodeTypeLabel(item.code_type)
    }))
}

/**
 * コードタイプの数値から表示用ラベルを取得
 * @param {string} code - コードタイプの値
 * @returns {string} 表示用ラベル
 */
const getCodeTypeLabel = (code) => {
    return CODE_TYPE_CHOICES[code] || code
}

/**
 * 親コンポーネントへ送るデータ
 * @param {Event} event - イベントオブジェクト
 * @param {Object} rowData - 行データ
 */
const sendDataToParent = (event, rowData) => {
    const item = rowData.item
    emit('data-sent', { 
        id: item.id, 
        name: item.name,
        code_type: item.code_type,
        description: item.description
    })
}

/**
 * ページが読み込まれた時に実行
 */
onMounted(async () => {
    await fetchPrefixes()
})

// テーブルのヘッダー定義
const headers = [
    { title: 'ID', key: 'id' },
    { title: 'プレフィックス名', key: 'name' },
    { title: 'コードタイプ', key: 'code_type_display' },
    { title: '説明', key: 'description' }
]
</script>

<template>
    <v-container>
        <v-data-table
            :headers="headers"
            :items="prefixes"
            density="compact"
            @click:row="sendDataToParent"
            :hover="true"
        >
        </v-data-table>
    </v-container>
</template>