<template>
    <v-container class="py-5">
      <v-card class="mx-auto" max-width="500">
        <v-card-title>Node 登録フォーム</v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-text-field
              v-model="node.name"
              label="Node名"
              required
            ></v-text-field>
  
            <v-textarea
              v-model="node.description"
              label="説明"
              rows="3"
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="primary"
            :disabled="!valid"
            @click="submitForm"
          >
            登録
          </v-btn>
        </v-card-actions>
      </v-card>
      <v-alert v-if="message" :type="isSuccess ? 'success' : 'error'" dismissible>
        {{ message }}
      </v-alert>
    </v-container>
  </template>
  
  <script>
  import nodeService from "@/api/nodeApi";
  
  export default {
    data() {
      return {
        node: {
          name: "",
          description: "",
        },
        message: "",
        isSuccess: false,
        valid: false,
      };
    },
    methods: {
      submitForm() {
        nodeService
          .createNode(this.node)
          .then(() => {
            this.message = "登録に成功しました！";
            this.isSuccess = true;
  
            // フォームリセット
            this.node.name = "";
            this.node.description = "";
  
            // 一覧ページへ遷移
            this.$router.push({name:'node_list'});
          })
          .catch((error) => {
            this.message = "登録に失敗しました: " + error.response.data;
            this.isSuccess = false;
          });
      },
    },
  };
  </script>
  
  <style>
  .v-container {
    max-width: 600px;
  }
  </style>
  