<template>
    <v-container>
      <h1>Update Node</h1>
      <v-divider></v-divider>
  
      <v-form v-model="valid">
        <v-text-field v-model="node.name" label="Name" :rules="[rules.required]" required></v-text-field>
        <v-textarea v-model="node.description" label="Description" :rules="[rules.required]" required></v-textarea>
  
        <v-btn color="primary" @click="updateNode" :disabled="!valid">Update Node</v-btn>
      </v-form>
    </v-container>
  </template>
  
  <script>
  import nodeService from "@/api/nodeApi";
  
  export default {
    data() {
      return {
        node: {
          id: null,
          name: "",
          description: "",
        },
        valid: false,
        rules: {
          required: value => !!value || "Required.",
        },
      };
    },
    created() {
      // URLのパラメータからノードIDを取得
      const nodeId = this.$route.params.id;
      // ノード情報をAPIから取得
      nodeService.getNode(nodeId).then((response) => {
        this.node = response.data;
      });
    },
    methods: {
      updateNode() {
        nodeService.updateNode(this.node.id, this.node).then(() => {
          this.$router.push({ name: "node_list" });  // 一覧画面へ遷移
        });
      }
    },
  };
  </script>
  