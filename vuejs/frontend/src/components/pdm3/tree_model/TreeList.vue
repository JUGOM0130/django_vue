<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import treeApiMethod from '@/api/treeApi'

// リアクティブな変数を定義
const trees = ref([])

// テーブルのヘッダー設定
const headers = [
    { title: 'ID', key: 'id',align: 'start',sortable: true, },
    { title: 'Name', key: 'name',align: 'start',sortable: true, },
    { title: 'Description', key: 'description',align: 'start',sortable: true, },
    { title: 'Created At', key: 'create_at',align: 'start',sortable: true, },
    { title: 'Updated At', key: 'update_at',align: 'start',sortable: true, },
    { title: 'Actions', key: 'actions',align: 'start',sortable: true, },
]
// ルーターインスタンスの取得
const router = useRouter()

// 詳細ビューへの遷移
const viewTree = (id) => {
    // 詳細ページに遷移（必要に応じて実装）
    console.log(`View tree with id: ${id}`)
    router.push({ name: 'tree_detail', params: { id } })
}

// コンポーネントのマウント時にAPIからデータを取得
onMounted(() => {
    treeApiMethod.getAllTrees().then((response) => {
        trees.value = response.data
    })
})
</script>

<template>
    <v-container>
        <h1>Tree List</h1>
        <v-divider></v-divider>

        <!-- v-data-table -->
        <v-data-table :headers="headers" :items="trees" item-key="id">

            <template v-slot:item="props">
                <tr>
                    <td>{{ props.item.id }}</td>
                    <td>{{ props.item.name }}</td>
                    <td>{{ props.item.description }}</td>
                    <td>{{ props.item.create_at }}</td>
                    <td>{{ props.item.update_at }}</td>
                    <!-- 詳細ボタン -->
                    <td>
                        <v-btn color="secondary" @click="viewTree(props.item.id)">詳細</v-btn>
                    </td>
                </tr>
            </template>
        </v-data-table>
    </v-container>
</template>




<style scoped>
/* カードのスタイル調整など */
</style>