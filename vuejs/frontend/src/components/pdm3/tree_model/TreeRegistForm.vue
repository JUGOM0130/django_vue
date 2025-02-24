
<script setup>
import { ref } from 'vue';
import treeApi from '@/api/treeApi';
import { useRouter } from 'vue-router';


const tree = ref({
  name: '',
  description: '',
});

const message = ref('');
const isSuccess = ref(false);
const valid = ref(false);
const router = useRouter();

const submitForm = () => {
  treeApi
    .createTree(tree.value)
    .then(() => {
      message.value = '登録に成功しました！';
      isSuccess.value = true;

      // フォームリセット
      tree.value.name = '';
      tree.value.description = '';

      // 一覧ページへ遷移
      router.push({ name: 'tree_list' });
    })
    .catch((error) => {
      message.value = '登録に失敗しました: ' + error.response.data;
      isSuccess.value = false;
    });
};
</script>
<template>
  <v-container class="py-5">
    <v-card class="mx-auto" max-width="500">
      <v-card-title>Tree 登録フォーム</v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <v-text-field v-model="tree.name" label="Tree名" required></v-text-field>

          <v-textarea v-model="tree.description" label="説明" rows="3"></v-textarea>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" :disabled="!valid" @click="submitForm">
          登録
        </v-btn>
      </v-card-actions>
    </v-card>
    <v-alert v-if="message" :type="isSuccess ? 'success' : 'error'" dismissible>
      {{ message }}
    </v-alert>
  </v-container>
</template>


<style scoped>
.v-container {
  max-width: 600px;
}
</style>
