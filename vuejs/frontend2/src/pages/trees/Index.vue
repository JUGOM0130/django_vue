<script setup>
//このページの説明

import { ref, computed, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { getAllTree } from '@/api/tree';
import axios from 'axios';

// ルーター
const router = useRouter();

// リアクティブステート
const items = ref([]);
const isLoading = ref(false);
const errorMessage = ref('');
const search = ref('');
const statusFilter = ref('');
const page = ref(1);
const itemsPerPage = ref(10);
const newTreeDialog = ref(false);
const deleteDialog = ref(false);
const isCreating = ref(false);
const isDeleting = ref(false);
const treeToDelete = ref(null);
const isFormValid = ref(false);
const form = ref(null);

// 新規ツリーのデータ
const newTree = reactive({
    name: '',
    description: '',
    version_name: '初期バージョン',
});

// ステータスオプション
const statusOptions = [
    { title: 'すべて', value: '' },
    { title: '作成中', value: 'draft' },
    { title: '有効', value: 'active' },
    { title: 'アーカイブ', value: 'archived' },
    { title: 'ロック中', value: 'locked' }
];

// テーブルヘッダー
const headers = [
    { title: 'ID', key: 'id', align: 'end' },
    { title: '名前', key: 'name', align: 'start' },
    { title: '説明', key: 'description', align: 'start' },
    { title: 'ステータス', key: 'status', align: 'center' },
    { title: 'バージョン', key: 'version', align: 'center' },
    { title: '作成日時', key: 'create_at', align: 'center' },
    { title: '更新日時', key: 'update_at', align: 'center' },
    { title: '操作', key: 'actions', align: 'center', sortable: false }
];

// フィルタリングされたアイテム
const filteredItems = computed(() => {
    if (!statusFilter.value) return items.value;
    return items.value.filter(item => item.status === statusFilter.value);
});

// API基本URL
const apiBaseUrlTree = import.meta.env.VITE_API_BASE_URL + "/tree";

// ステータスラベル取得
const getStatusLabel = (status) => {
    const statusMap = {
        draft: '作成中',
        active: '有効',
        archived: 'アーカイブ',
        locked: 'ロック中'
    };
    return statusMap[status] || status;
};

// ステータスの色を取得
const getStatusColor = (status) => {
    const statusColorMap = {
        draft: 'blue',
        active: 'success',
        archived: 'grey',
        locked: 'error'
    };
    return statusColorMap[status] || 'grey';
};

// ツリーデータの取得
const fetchTrees = async () => {
    isLoading.value = true;
    errorMessage.value = '';

    try {
        const response = await getAllTree();
        const array = response.data.data;

        items.value = array.map(item => ({
            ...item,
            create_at: new Date(item.created_at).toLocaleString(),
            update_at: new Date(item.updated_at).toLocaleString()
        }));
    } catch (error) {
        console.error('ツリーデータの取得に失敗しました:', error);
        errorMessage.value = 'データの取得に失敗しました。';
    } finally {
        isLoading.value = false;
    }
};

// 新規ツリー作成ダイアログを表示
const createNewTree = () => {
    // フォームをリセット
    newTree.name = '';
    newTree.description = '';
    newTree.version_name = '初期バージョン';

    // フォームのバリデーションをリセット
    if (form.value) form.value.resetValidation();

    // ダイアログを表示
    newTreeDialog.value = true;
};

// ツリーの作成
const createTree = async () => {
    if (!isFormValid.value) return;

    isCreating.value = true;

    try {
        const response = await axios.post(`${apiBaseUrlTree}/`, {
            name: newTree.name,
            description: newTree.description,
            version_name: newTree.version_name
        });

        // 成功時の処理
        if (response.data.success) {
            // ダイアログを閉じる
            newTreeDialog.value = false;

            // 成功メッセージを表示
            // VuetifyのSnackbarやAlertを使用する場合はここで表示

            // ツリーデータを再取得
            fetchTrees();

            // 作成したツリーの詳細ページに遷移
            if (response.data.data?.id) {
                router.push({ name: 'create_structure', query: { id: response.data.data.id } });
            }
        } else {
            // エラーメッセージ
            errorMessage.value = response.data.message || 'ツリーの作成に失敗しました';
        }
    } catch (error) {
        console.error('ツリー作成エラー:', error);
        errorMessage.value = error.response?.data?.message || 'ツリーの作成中にエラーが発生しました';
    } finally {
        isCreating.value = false;
    }
};

// ツリーの表示
const viewTree = (item) => {
    router.push({ name: 'tree_view', query: { id: item.id } });
};

// ツリーの編集
const editTree = (item) => {
    router.push({ name: 'create_structure', query: { id: item.id } });
};

// ツリーの複製
const duplicateTree = async (item) => {
    // ダイアログでの入力または固定値
    const newName = `${item.name} (コピー)`;

    try {
        const response = await axios.post(`${apiBaseUrlTree}trees/${item.id}/clone/`, {
            name: newName,
            description: `${item.description || ''} (複製元: ${item.name})`
        });

        if (response.data.success) {
            // 成功メッセージ
            // VuetifyのSnackbarやAlertを使用する場合はここで表示

            // ツリーデータを再取得
            fetchTrees();
        } else {
            errorMessage.value = response.data.message || 'ツリーの複製に失敗しました';
        }
    } catch (error) {
        console.error('ツリー複製エラー:', error);
        errorMessage.value = error.response?.data?.message || 'ツリーの複製中にエラーが発生しました';
    }
};

// ツリーのエクスポート
const exportTree = (item) => {
    window.open(`${apiBaseUrlTree}trees/${item.id}/export/`, '_blank');
};

// ツリーの有効化
const activateTree = async (item) => {
    try {
        const response = await axios.post(`${apiBaseUrlTree}trees/${item.id}/activate/`);
        if (response.data.success) {
            // 成功メッセージ
            // VuetifyのSnackbarやAlertを使用する場合はここで表示

            // ツリーデータを再取得
            fetchTrees();
        } else {
            errorMessage.value = response.data.message || 'ツリーの有効化に失敗しました';
        }
    } catch (error) {
        console.error('ツリー有効化エラー:', error);
        errorMessage.value = error.response?.data?.message || 'ツリーの有効化中にエラーが発生しました';
    }
};

// ツリーのアーカイブ
const archiveTree = async (item) => {
    try {
        const response = await axios.post(`${apiBaseUrlTree}trees/${item.id}/archive/`);
        if (response.data.success) {
            // 成功メッセージ
            // VuetifyのSnackbarやAlertを使用する場合はここで表示

            // ツリーデータを再取得
            fetchTrees();
        } else {
            errorMessage.value = response.data.message || 'ツリーのアーカイブに失敗しました';
        }
    } catch (error) {
        console.error('ツリーアーカイブエラー:', error);
        errorMessage.value = error.response?.data?.message || 'ツリーのアーカイブ中にエラーが発生しました';
    }
};

// ツリーのロック
const lockTree = async (item) => {
    try {
        const response = await axios.post(`${apiBaseUrlTree}trees/${item.id}/lock/`);
        if (response.data.success) {
            // 成功メッセージ
            // VuetifyのSnackbarやAlertを使用する場合はここで表示

            // ツリーデータを再取得
            fetchTrees();
        } else {
            errorMessage.value = response.data.message || 'ツリーのロックに失敗しました';
        }
    } catch (error) {
        console.error('ツリーロックエラー:', error);
        errorMessage.value = error.response?.data?.message || 'ツリーのロック中にエラーが発生しました';
    }
};

// ツリー削除の確認ダイアログを表示
const confirmDeleteTree = (item) => {
    treeToDelete.value = item;
    deleteDialog.value = true;
};

// ツリーの削除
const deleteTree = async () => {
    if (!treeToDelete.value) return;

    isDeleting.value = true;

    try {
        const response = await axios.delete(`${apiBaseUrlTree}trees/${treeToDelete.value.id}/`);

        // 成功メッセージ
        // VuetifyのSnackbarやAlertを使用する場合はここで表示

        // ダイアログを閉じて状態をリセット
        deleteDialog.value = false;
        treeToDelete.value = null;

        // ツリーデータを再取得
        fetchTrees();
    } catch (error) {
        console.error('ツリー削除エラー:', error);
        errorMessage.value = error.response?.data?.message || 'ツリーの削除中にエラーが発生しました';
    } finally {
        isDeleting.value = false;
    }
};

// コンポーネントのマウント時にデータを取得
onMounted(() => {
    fetchTrees();
});
</script>

<template>
    <v-container>
        <!-- エラーメッセージ表示 -->
        <v-alert v-if="errorMessage" type="error" class="mb-4">
            {{ errorMessage }}
        </v-alert>

        <!-- ヘッダー部分 -->
        <v-row class="mb-4">
            <v-col cols="12" sm="6">
                <h1 class="text-h4">ツリー一覧</h1>
            </v-col>
            <v-col cols="12" sm="6" class="d-flex justify-end align-center">
                <v-btn color="primary" prepend-icon="mdi-plus-circle" @click="createNewTree">
                    新規ツリー作成
                </v-btn>
                <v-btn class="ml-2" variant="outlined" prepend-icon="mdi-refresh" @click="fetchTrees"
                    :loading="isLoading">
                    更新
                </v-btn>
            </v-col>
        </v-row>

        <!-- 検索・フィルタリング部分 -->
        <v-row class="mb-4">
            <v-col cols="12" sm="6">
                <v-text-field v-model="search" label="検索" prepend-inner-icon="mdi-magnify" single-line hide-details
                    variant="outlined" density="comfortable"></v-text-field>
            </v-col>
            <v-col cols="12" sm="6">
                <v-select v-model="statusFilter" label="ステータス" :items="statusOptions" variant="outlined"
                    density="comfortable" hide-details></v-select>
            </v-col>
        </v-row>

        <!-- テーブル部分 -->
        <v-data-table v-model:page="page" :headers="headers" :items="filteredItems" :items-per-page="itemsPerPage"
            :loading="isLoading" density="comfortable" item-value="id" class="elevation-1 rounded" :search="search">
            <!-- ステータス列のカスタマイズ -->
            <template v-slot:item.status="{ item }">
                <v-chip :color="getStatusColor(item.status)" size="small" text-color="white">
                    {{ getStatusLabel(item.status) }}
                </v-chip>
            </template>

            <!-- 操作列のカスタマイズ -->
            <template v-slot:item.actions="{ item }">
                <div class="d-flex">
                    <v-btn icon size="small" color="info" class="mr-1" @click="viewTree(item)" variant="text">
                        <v-icon>mdi-eye</v-icon>
                        <v-tooltip activator="parent" location="top">表示</v-tooltip>
                    </v-btn>

                    <v-btn icon size="small" color="primary" class="mr-1" @click="editTree(item)" variant="text"
                        :disabled="item.status === 'locked'">
                        <v-icon>mdi-pencil</v-icon>
                        <v-tooltip activator="parent" location="top">編集</v-tooltip>
                    </v-btn>

                    <v-menu>
                        <template v-slot:activator="{ props }">
                            <v-btn icon size="small" color="grey-darken-1" variant="text" v-bind="props">
                                <v-icon>mdi-dots-vertical</v-icon>
                            </v-btn>
                        </template>
                        <v-list density="compact">
                            <v-list-item @click="duplicateTree(item)">
                                <template v-slot:prepend>
                                    <v-icon size="small">mdi-content-copy</v-icon>
                                </template>
                                <v-list-item-title>複製</v-list-item-title>
                            </v-list-item>

                            <v-list-item @click="exportTree(item)">
                                <template v-slot:prepend>
                                    <v-icon size="small">mdi-export</v-icon>
                                </template>
                                <v-list-item-title>エクスポート</v-list-item-title>
                            </v-list-item>

                            <v-divider></v-divider>

                            <v-list-item v-if="item.status === 'draft'" @click="activateTree(item)"
                                class="text-success">
                                <template v-slot:prepend>
                                    <v-icon size="small" color="success">mdi-check-circle</v-icon>
                                </template>
                                <v-list-item-title>有効化</v-list-item-title>
                            </v-list-item>

                            <v-list-item v-if="item.status === 'active'" @click="archiveTree(item)">
                                <template v-slot:prepend>
                                    <v-icon size="small">mdi-archive</v-icon>
                                </template>
                                <v-list-item-title>アーカイブ</v-list-item-title>
                            </v-list-item>

                            <v-list-item v-if="['draft', 'active'].includes(item.status)" @click="lockTree(item)">
                                <template v-slot:prepend>
                                    <v-icon size="small">mdi-lock</v-icon>
                                </template>
                                <v-list-item-title>ロック</v-list-item-title>
                            </v-list-item>

                            <v-divider></v-divider>

                            <v-list-item @click="confirmDeleteTree(item)" class="text-error">
                                <template v-slot:prepend>
                                    <v-icon size="small" color="error">mdi-delete</v-icon>
                                </template>
                                <v-list-item-title>削除</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                </div>
            </template>

            <!-- データがない場合のメッセージ -->
            <template v-slot:no-data>
                <v-alert type="info" class="ma-2">
                    データがありません。「新規ツリー作成」ボタンからツリーを作成してください。
                </v-alert>
            </template>
        </v-data-table>

        <!-- 新規ツリー作成ダイアログ -->
        <v-dialog v-model="newTreeDialog" max-width="500">
            <v-card>
                <v-card-title>新規ツリー作成</v-card-title>
                <v-card-text>
                    <v-form ref="form" v-model="isFormValid">
                        <v-text-field v-model="newTree.name" label="ツリー名" required :rules="[v => !!v || 'ツリー名は必須です']"
                            variant="outlined" density="comfortable"></v-text-field>

                        <v-textarea v-model="newTree.description" label="説明" variant="outlined" density="comfortable"
                            rows="3" auto-grow></v-textarea>

                        <v-text-field v-model="newTree.version_name" label="初期バージョン名" variant="outlined"
                            density="comfortable" placeholder="初期バージョン"></v-text-field>
                    </v-form>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="grey-darken-1" variant="text" @click="newTreeDialog = false" :disabled="isCreating">
                        キャンセル
                    </v-btn>
                    <v-btn color="primary" @click="createTree" :disabled="!isFormValid || isCreating"
                        :loading="isCreating">
                        作成
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- 削除確認ダイアログ -->
        <v-dialog v-model="deleteDialog" max-width="500">
            <v-card>
                <v-card-title class="text-error">ツリー削除の確認</v-card-title>
                <v-card-text>
                    <p><strong>{{ treeToDelete?.name }}</strong> を削除してもよろしいですか？</p>
                    <p class="text-error mt-2">
                        <v-icon color="error" class="mr-1">mdi-alert-circle</v-icon>
                        この操作は取り消せません。ツリーとそのすべての構造データが完全に削除されます。
                    </p>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="grey-darken-1" variant="text" @click="deleteDialog = false" :disabled="isDeleting">
                        キャンセル
                    </v-btn>
                    <v-btn color="error" @click="deleteTree" :loading="isDeleting" :disabled="isDeleting">
                        削除する
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>


<style scoped>
/* 必要に応じてスタイルを追加 */
.v-data-table {
    border-radius: 8px;
}
</style>