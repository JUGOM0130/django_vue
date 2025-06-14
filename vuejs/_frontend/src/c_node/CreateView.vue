<script setup>
import { ref, onMounted,defineProps,defineEmits } from 'vue';
import { useRouter } from 'vue-router';
import prefixApi from '@/c_prefix/api'; // Prefix API 呼び出し用のモジュールをインポート
import { generateCode } from '@/common/common';

// フォームデータの定義
const prefix = ref('');
const prefixes = ref([]);
const errorMessage = ref('');
const successMessage = ref('');
const generatedCode = ref(null); // 生成されたコードを保持
const loading = ref(false);

// ルーターの使用
const router = useRouter();

// props
const props = defineProps({
    showAddNodeButton:{
        type:Boolean,
        default:false
    }
});

// Emit
const emit = defineEmits(['addNode']);

// APIからPrefixの一覧を取得
const getAllPrefixes = async () => {
    try {
        const response = await prefixApi.getAllPrefixes();
        prefixes.value = response.data;
        prefixes.value.map(item => ({
            ...item,
            create_at: new Date(item.create_at).toLocaleString(),
            update_at: new Date(item.update_at).toLocaleString(),
        }));
    } catch (error) {
        errorMessage.value = `Failed to fetch prefixes: ${error.message}`;
    }
};



// コンポーネントがマウントされたときにPrefixの一覧を取得
onMounted(() => {
    getAllPrefixes();
    
});


const handleGenerateCode = async () => {
    loading.value = true;
    errorMessage.value = '';
    successMessage.value = '';
    generatedCode.value = null;
    try {
        // ここでコード生成の処理を行う
        const response = await generateCode(prefix.value);
        successMessage.value = 'Code generated successfully!';
        generatedCode.value = response.data.code;

        // 親コンポーネントにイベントを発火してデータを渡す
        console.log("CreateView",prefix.value,generatedCode.value)
        emit('addNode', { prefix: prefix.value, code: generatedCode.value });
        
        // フォームをリセット
        prefix.value = '';

        router.push('/')

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
        <v-form @submit.prevent="handleGenerateCode">
            <v-select
                v-model="prefix"
                :items="prefixes"
                item-title="name"
                item-value="id"
                label="Prefix"
                required
            ></v-select>
            <v-btn type="submit" color="primary" :loading="loading" v-if="!props.showAddNodeButton">Generate</v-btn>
            <v-btn type="submit" color="info" v-if="props.showAddNodeButton">Add Node</v-btn>
            
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