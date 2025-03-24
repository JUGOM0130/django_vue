<!-- PrefixListLightVersion.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// APIのベースURL
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

// 状態管理
const isLoading = ref(false);
const errorMessage = ref('');
const prefixes = ref([]);
const selectedPrefix = ref(null);
const generatedCode = ref(null);
const search = ref('');
const isGenerating = ref(false);
const codeNameInput = ref('');

// Prefixの型オプション
const codeTypeOptions = {
    '1': '組 (A0001Z000形式)',
    '2': '部品 (AA0001Z000形式)',
    '3': '購入品 (A0001Z00形式)'
};

// エミット定義
const emit = defineEmits(['data-sent', 'close']);

// Prefixリストを取得
const fetchPrefixes = async () => {
    isLoading.value = true;
    errorMessage.value = '';

    try {
        const response = await axios.get(`${apiBaseUrl}/prefix/`);

        // APIレスポンスの形式によって調整
        if (response.data && Array.isArray(response.data)) {
            prefixes.value = response.data;
        } else if (response.data && Array.isArray(response.data.data)) {
            prefixes.value = response.data.data;
        } else if (response.data && response.data.results) {
            prefixes.value = response.data.results;
        } else {
            prefixes.value = [];
            errorMessage.value = 'Prefixデータが見つかりませんでした';
        }

        console.log('取得したPrefix:', prefixes.value);
    } catch (error) {
        console.error('Prefixの取得に失敗しました:', error);
        errorMessage.value = 'Prefixデータの取得中にエラーが発生しました';
    } finally {
        isLoading.value = false;
    }
};

// コードのプレビューを取得
const previewCode = async (prefix) => {
    if (!prefix) return;

    selectedPrefix.value = prefix;
    generatedCode.value = null;
    isGenerating.value = true;

    try {
        const response = await axios.get(`${apiBaseUrl}/prefix/${prefix.id}/preview_next_code/`);
        console.log('Code preview response:', response.data);

        if (response.data && response.data.preview_code) {
            generatedCode.value = {
                code: response.data.preview_code,
                prefix_id: prefix.id,
                prefix_name: prefix.name,
                next_number: response.data.next_number
            };
        } else {
            errorMessage.value = 'コードのプレビューに失敗しました';
        }
    } catch (error) {
        console.error('コードプレビューエラー:', error);
        errorMessage.value = 'コードのプレビュー取得中にエラーが発生しました';
    } finally {
        isGenerating.value = false;
    }
};

// コードを生成して送信
const generateAndSendCode = async () => {
    if (!selectedPrefix.value) {
        errorMessage.value = 'Prefixを選択してください';
        return;
    }

    if (!codeNameInput.value) {
        errorMessage.value = 'コード名を入力してください';
        return;
    }

    isGenerating.value = true;

    try {
        // コード生成APIを呼び出し
        const response = await axios.post(`${apiBaseUrl}/prefix/${selectedPrefix.value.id}/generate_code/`, {
            name: codeNameInput.value,
            description: '',
            status: 'active'
        });

        console.log('Code generation response:', response.data);

        if (response.data && response.data.code) {
            // 親コンポーネントにデータを送信
            emit('data-sent', {
                code: response.data.code.code,
                name: response.data.code.name,
                id: response.data.code.id,
                code_type: selectedPrefix.value.code_type,
                prefix_id: selectedPrefix.value.id
            });
        } else {
            errorMessage.value = 'コードの生成に失敗しました';
        }
    } catch (error) {
        console.error('コード生成エラー:', error);
        errorMessage.value = 'コードの生成中にエラーが発生しました';
    } finally {
        isGenerating.value = false;
    }
};

// 選択したプレビューコードを送信（プレビューのみ使用する場合）
const sendPreviewCode = () => {
    if (!generatedCode.value) {
        errorMessage.value = 'プレビューコードがありません';
        return;
    }

    if (!codeNameInput.value) {
        errorMessage.value = 'コード名を入力してください';
        return;
    }

    // 親コンポーネントにデータを送信
    emit('data-sent', {
        code: generatedCode.value.code,
        name: codeNameInput.value,
        prefix_id: selectedPrefix.value.id,
        code_type: selectedPrefix.value.code_type,
        // 実際のコードIDはないので、代わりに一時的な識別子として使用
        temp_code: true
    });
};

// 閉じるボタン
const close = () => {
    emit('close');
};

// コンポーネントのマウント時にデータを取得
onMounted(() => {
    fetchPrefixes();
});
</script>

<template>
    <div class="prefix-list-container">
        <div class="prefix-header">
            <h2>プレフィックス選択</h2>
            <p class="subtitle">コード採番のためのプレフィックスを選択してください</p>
        </div>

        <!-- エラーメッセージ -->
        <v-alert v-if="errorMessage" type="error" class="mb-4" density="compact" closable>
            {{ errorMessage }}
        </v-alert>

        <!-- ローディング表示 -->
        <div v-if="isLoading" class="text-center my-4">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <p>プレフィックスを読み込み中...</p>
        </div>

        <div v-else>
            <!-- 検索バー -->
            <v-text-field v-model="search" label="プレフィックスを検索" prepend-inner-icon="mdi-magnify" variant="outlined"
                density="comfortable" hide-details class="mb-4"></v-text-field>

            <!-- Prefixリスト -->
            <div class="prefix-list">
                <v-card v-for="prefix in prefixes" :key="prefix.id" class="mb-2" variant="outlined"
                    :class="{ 'selected': selectedPrefix && selectedPrefix.id === prefix.id }"
                    @click="previewCode(prefix)">
                    <v-card-item>
                        <v-card-title>{{ prefix.name }}</v-card-title>
                        <v-card-subtitle>
                            {{ codeTypeOptions[prefix.code_type] || '不明なタイプ' }}
                            <span class="next-number">次の番号: {{ prefix.next_number }}</span>
                        </v-card-subtitle>

                        <template v-slot:append>
                            <v-btn variant="text" icon="mdi-arrow-right" color="primary"
                                @click.stop="previewCode(prefix)"></v-btn>
                        </template>
                    </v-card-item>

                    <v-card-text v-if="prefix.description">
                        {{ prefix.description }}
                    </v-card-text>
                </v-card>

                <!-- データがない場合 -->
                <v-alert v-if="prefixes.length === 0" type="info" class="mt-2">
                    プレフィックスが見つかりません
                </v-alert>
            </div>

            <!-- コードプレビュー -->
            <v-card v-if="selectedPrefix" class="mt-4" variant="outlined">
                <v-card-title>コードプレビュー</v-card-title>
                <v-card-text>
                    <p><strong>選択したプレフィックス:</strong> {{ selectedPrefix.name }}</p>
                    <p><strong>コードタイプ:</strong> {{ codeTypeOptions[selectedPrefix.code_type] || '不明なタイプ' }}</p>

                    <div v-if="isGenerating" class="text-center my-4">
                        <v-progress-circular indeterminate color="primary" size="24"></v-progress-circular>
                        <span class="ml-2">プレビュー生成中...</span>
                    </div>

                    <div v-else-if="generatedCode" class="generated-code">
                        <p class="mb-2">次に生成されるコード:</p>
                        <div class="code-display">{{ generatedCode.code }}</div>
                    </div>

                    <v-text-field v-model="codeNameInput" label="コード名 (例: 組立部品A)" required variant="outlined"
                        density="comfortable" class="mt-4"></v-text-field>
                </v-card-text>

                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" @click="generateAndSendCode" :disabled="!codeNameInput || isGenerating"
                        :loading="isGenerating">
                        コードを生成して選択
                    </v-btn>
                </v-card-actions>
            </v-card>
        </div>

        <!-- アクションボタン -->
        <div class="actions mt-4">
            <v-btn color="grey" variant="outlined" @click="close">キャンセル</v-btn>
        </div>
    </div>
</template>

<style scoped>
.prefix-list-container {
    min-height: 300px;
    max-height: 600px;
    overflow-y: auto;
    padding: 16px;
}

.prefix-header {
    margin-bottom: 16px;
}

.subtitle {
    color: #666;
    font-size: 14px;
    margin-top: 4px;
}

.prefix-list {
    margin-bottom: 16px;
}

.selected {
    border: 2px solid #1976d2;
    background-color: #e3f2fd;
}

.next-number {
    margin-left: 8px;
    font-size: 12px;
    background-color: #e0e0e0;
    padding: 2px 6px;
    border-radius: 10px;
}

.generated-code {
    margin: 16px 0;
}

.code-display {
    font-family: 'Roboto Mono', monospace;
    font-size: 18px;
    padding: 12px;
    background-color: #f5f5f5;
    border-radius: 4px;
    text-align: center;
    font-weight: bold;
    color: #1976d2;
    letter-spacing: 1px;
}

.actions {
    display: flex;
    justify-content: flex-end;
}
</style>