<template>
  <v-container>
    <h1>Node List</h1>
    <v-divider></v-divider>

    <!-- 登録画面へのリンクボタン -->
    <v-btn color="primary lighten-3" @click="goToCreatePage">Create New Node</v-btn>

    <!-- v-data-table -->
    <v-data-table :headers="headers" :items="nodes" item-key="id">
      <template v-slot:column="props">
        <th>{{ props.column.text }}</th>
      </template>

      <template v-slot:item="props">
        <tr>
          <td>{{ props.item.id }}</td>
          <td>{{ props.item.name }}</td>
          <td>{{ props.item.description }}</td>
          <td>{{ props.item.create_at }}</td>
          <td>{{ props.item.update_at }}</td>
          <!-- 更新ボタン -->
          <td>
            <v-btn color="secondary" @click="goToUpdatePage(props.item.id)">編集</v-btn>
          </td>
        </tr>
      </template>
    </v-data-table>
  </v-container>
</template>

<script>
import nodeService from "@/api/nodeApi";

export default {
  data() {
    return {
      nodes: [],
      headers: [
        { text: 'ID', value: 'id' },
        { text: 'Name', value: 'name' },
        { text: 'Description', value: 'description' },
        { text: 'Created At', value: 'create_at' },
        { text: 'Updated At', value: 'update_at' },
        { text: '編集', value: 'edit' },
      ],
    };
  },
  created() {
    nodeService.getAllNodes().then((response) => {
      this.nodes = response.data;
    });
  },
  methods: {
    goToCreatePage() {
      // 登録画面への遷移
      this.$router.push({ name: 'node_register' });
    },
    goToUpdatePage(nodeId) {
      // 更新画面への遷移
      this.$router.push({ name: 'node_update', params: { id: nodeId } });
    }
  },
};
</script>
