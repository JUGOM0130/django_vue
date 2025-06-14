<template>
    <v-app>
        <v-main>
            <v-container>
                <!-- ページタイトル等のヘッダ部分 -->
                <v-row>
                    <v-col>
                        <h1>Prefix List</h1>
                    </v-col>
                    <v-col class="d-flex justify-end">
                        <v-btn color="secondary" @click="toRegister">登録</v-btn>
                    </v-col>
                </v-row>

                <!-- テーブル部分 -->
                <v-data-table :items="response" :headers="headers" item-key="id" density="compact" :items-per-page="50">
                </v-data-table>

                <!-- エラーメッセージ表示部分 -->
                <div v-if="errorMessage">
                    <p style="color: red;">Error: {{ errorMessage }}</p>
                </div>
            </v-container>
        </v-main>
    </v-app>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import prefixApi from './api';
import router from './router';

// データの定義
const response = ref([]);
const errorMessage = ref('');

// 選択肢の定義
// const categories = ['組', '部品', '購入品'];

// カテゴリ選択肢のバックエンドコードに対応するマッピング
const codeTypeMapping = [
    { key: '組', value: '1' },
    { key: '部品', value: '2' },
    { key: '購入品', value: '3' }
];

// テーブルのヘッダー
const headers = [
    { title: 'ID', value: 'id', align: 'end' },
    { title: 'Name', value: 'name', align: 'center' },
    { title: 'Description', value: 'description', align: 'start' },
    { title: 'Code Type', value: 'code_type', align: 'center' },
    { title: 'Created At', value: 'create_at', align: 'center' },
    { title: 'Updated At', value: 'update_at', align: 'center' },
];

// APIからデータを取得
const getList = async () => {
    try {
        const result = await prefixApi.getAllPrefixes();
        response.value = result.data.map(item => ({
            ...item,
            code_type: (() => {
                const mapping = codeTypeMapping.find(mapping => mapping.value === item.code_type);
                return mapping ? mapping.key : item.code_type;
            })(),//←のカッコは即時実行関数（関数を定義すると同時に実行する）
            create_at: new Date(item.create_at).toLocaleString(),
            update_at: new Date(item.update_at).toLocaleString(),
        }));

        errorMessage.value = '';
    } catch (error) {
        errorMessage.value = `Failed to register prefix: ${error.message}`;
    }
};

function toRegister() {
    router.push({ name: 'create_prefix' });
}

onMounted(() => {
    getList();
});
</script>

<style scoped>
/* 必要に応じてカスタムスタイルを追加できます */
</style>