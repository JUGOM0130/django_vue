<template>

            <v-container :max-width="1920">
                <!-- ページタイトル等のヘッダ部分 -->
                <v-row>
                    <v-col>
                        <h1>Tree List</h1>
                    </v-col>
                    <v-col class="d-flex justify-end">
                        <v-btn color="secondary" @click="toRegister">登録</v-btn>
                    </v-col>
                </v-row>

                <!-- テーブル部分 -->
                <v-data-table
                    :items="response"
                    :headers="headers"
                    item-key="id"
                    density="compact"
                    :items-per-page="50"
                >
                    <template v-slot:[`item.edit`]="{ item }">
                        <v-btn
                            size="small"
                            density="comfortable"
                            color="primary"
                            @click="()=>editTree(item)"
                            variant="outlined"
                        >
                            編集
                        </v-btn>
                    </template>
                </v-data-table>

                <!-- エラーメッセージ表示部分 -->
                <div v-if="errorMessage">
                    <p style="color: red;">Error: {{ errorMessage }}</p>
                </div>
            </v-container>

</template>

<script setup>
import { ref, onMounted } from 'vue';
import prefixApi from './api';
import router from './router';

// データの定義
const response = ref([]);
const errorMessage = ref('');

// テーブルのヘッダー
const headers = [
    { title: 'ID', value: 'id', align: 'end' },
    { title: 'Name', value: 'name', align: 'center' },
    { title: 'Description', value: 'description', align: 'start' },
    { title: 'Version', value: 'version', align: 'center' },
    { title: 'Created At', value: 'create_at', align: 'center' },
    { title: 'Updated At', value: 'update_at', align: 'center' },
    { title: 'Tree Edit', value: 'edit', align: 'center' },
];


// APIからデータを取得
const getList = async () => {
    try {
        const result = await prefixApi.getAllTree();
        response.value = result.data.map(item => ({
            ...item,
            create_at: new Date(item.create_at).toLocaleString(),
            update_at: new Date(item.update_at).toLocaleString(),
        }));

        errorMessage.value = '';
    } catch (error) {
        errorMessage.value = `Failed to register tree: ${error.message}`;
    }
};

const toRegister = () => {
    router.push('/register'); // 適切な登録画面のルートに変更してください
};

// 編集ボタンのクリックイベント
const editTree = (item) => {
    router.push({ name: 'create_stracure', query: { id: item.id } }); // 適切な編集画面のルートに変更してください
};

onMounted(async() => {
    await getList();
});
</script>

<style scoped>
/* 必要に応じてカスタムスタイルを追加できます */
.small-btn {
    font-size: 12px;
    padding: 2px 4px;
    height: 24px;
    min-height: 24px;
    line-height: 24px;
}

.v-container{
    max-width: 1920px;
}
</style>