<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from './api'; // API 呼び出し用のモジュールをインポート

// データの定義
const nodes = ref([]);
const errorMessage = ref('');
const loading = ref(true); // ローディング状態の追加

// テーブルのヘッダー
const headers = [
    { title: 'ID', value: 'id', align: 'end' },
    { title: 'Name', value: 'name', align: 'center' },
    { title: 'Description', value: 'description', align: 'start' },
    { title: 'Created At', value: 'create_at', align: 'center' },
    { title: 'Updated At', value: 'update_at', align: 'center' },
    { title: 'Actions', value: 'actions', align: 'center' }, // 編集ボタンのカラム
];

// APIからデータを取得
const getNodes = async () => {
    loading.value = true;
    try {
        const response = await api.getNodes();
        nodes.value = response.data.map(item => ({
            ...item,
            create_at: new Date(item.create_at).toLocaleString(),
            update_at: new Date(item.update_at).toLocaleString(),
        }));
        errorMessage.value = '';
    } catch (error) {
        errorMessage.value = `Failed to fetch nodes: ${error.message}`;
    } finally {
        loading.value = false;
    }
};

// コンポーネントがマウントされたときにデータを取得
onMounted(() => {
    getNodes();
});

// ルーターの使用
const router = useRouter();

// 編集ボタンのクリックイベント
const editNode = (item) => {
    // 編集画面への遷移などの処理を追加
    console.log('Edit node:', item);
};

// 登録ボタンのクリックイベント
const toCreateNode = () => {
    router.push({ name: 'create_node' }); // 適切なルート名に変更してください
};
</script>

<template>
    <v-container>
        <v-row>
            <v-col>
                <h1>Node List</h1>
            </v-col>
            <v-col class="d-flex justify-end">
                <v-btn color="secondary" @click="toCreateNode">登録</v-btn>
            </v-col>
        </v-row>
        <div v-if="errorMessage">
            <p style="color: red;">Error: {{ errorMessage }}</p>
        </div>
        <v-progress-circular v-if="loading" indeterminate color="primary"></v-progress-circular>
        <v-data-table v-else :items="nodes" :headers="headers" item-key="id" density="compact" :items-per-page="50">
            <template v-slot:[`item.actions`]="{ item }">
                <v-btn size="small" density="comfortable" color="primary" @click="editNode(item)" variant="outlined">
                    編集
                </v-btn>
            </template>
        </v-data-table>
    </v-container>
</template>

<style scoped>
.small-btn {
    font-size: 12px;
    padding: 2px 4px;
    height: 24px;
    min-height: 24px;
    line-height: 24px;
}
</style>