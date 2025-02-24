<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from './api'; // API 呼び出し用のモジュールをインポート

// フォームデータの定義
const prefix = ref('');
const codeType = ref('');
const errorMessage = ref('');
const successMessage = ref('');
const generatedCode = ref(null); // 生成されたコードを保持
const loading = ref(false);

// カテゴリ選択肢のバックエンドコードに対応するマッピング
const codeTypeMapping = {
  '組': '1',
  '部品': '2',
  '購入品': '3'
};

// ルーターの使用
const router = useRouter();

// フォームの送信
const generateCode = async () => {
    loading.value = true;
    errorMessage.value = '';
    successMessage.value = '';
    generatedCode.value = null;
    try {
        const response = await api.generateCode({
            prefix: prefix.value,
            code_type: codeType.value,
        });
        successMessage.value = 'Code generated successfully!';
        generatedCode.value = response.data.code; // 生成されたコードを保持
        // フォームをリセット
        prefix.value = '';
        codeType.value = '';
        // 一覧ページにリダイレクト
        router.push({ name: 'list_node' }); // 適切なルート名に変更してください
    } catch (error) {
        errorMessage.value = `Failed to generate code: ${error.message}`;
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <v-container>
        <h1>Generate Code</h1>
        <v-form @submit.prevent="generateCode">
            <v-text-field
                v-model="prefix"
                label="Prefix"
                required
            ></v-text-field>
            <v-radio-group v-model="codeType" label="Code Type" required>
                <v-radio
                    v-for="(value, key) in codeTypeMapping"
                    :key="value"
                    :label="key"
                    :value="value"
                ></v-radio>
            </v-radio-group>
            <v-btn type="submit" color="primary" :loading="loading">Generate</v-btn>
        </v-form>
        <div v-if="errorMessage">
            <p style="color: red;">Error: {{ errorMessage }}</p>
        </div>
        <div v-if="successMessage">
            <p style="color: green;">{{ successMessage }}</p>
            <div v-if="generatedCode">
                <h2>Generated Code:</h2>
                <p>{{ generatedCode }}</p>
            </div>
        </div>
    </v-container>
</template>

<style scoped>
/* 必要に応じてカスタムスタイルを追加できます */
</style>