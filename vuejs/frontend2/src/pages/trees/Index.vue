<script setup>
import {ref,onMounted} from 'vue';
import {getAllTree} from '@/api/tree';


const items = ref([{
        "id": 0,
        "name": "",
        "description": "",
        "version": 0,
        "create_at": "",
        "update_at": ""
    }]);
const errorMessage = ref('');
const headers = [
    { title: 'ID', value: 'id', align: 'end' },
    { title: 'Name', value: 'name', align: 'center' },
    { title: 'Description', value: 'description', align: 'start' },
    { title: 'Version', value: 'version', align: 'center' },
    { title: 'Created At', value: 'create_at', align: 'center' },
    { title: 'Updated At', value: 'update_at', align: 'center' },
    { title: 'Tree Edit', value: 'edit', align: 'center' },
];

/**
 * データ取得
 */
const fetchTrees = async () => {
  try {
    // responseからdataプロパティを取得
    const response = await getAllTree()
    items.value = response.data.map(item=>({
        ...item,
        create_at: new Date(item.create_at).toLocaleString(),
        update_at: new Date(item.update_at).toLocaleString()
    }))  // または response.data.data (APIの構造による)
  } catch (error) {
    console.error('Error:', error)
  }
}

/**
 * 編集ボタンクリック時処理
 */

const editTree = (item) => {
    console.log(item.id);
};


/**
 * マウント処理
 */
onMounted(async() => {
    fetchTrees()
});
</script>


<template>
    <v-container>
        <p v-if="errorMessage">{{ errorMessage }}</p>

        <v-row>
            <v-col>
                <!-- テーブル部分 -->
                <v-data-table
                    :items="items"
                    :headers="headers"
                    item-key="id"
                    density="compact"
                    :items-per-page="50"
                >
                    <template v-slot:[`item.edit`]="{ item }">
                        <v-btn
                            size="small"
                            density="comfortable"
                            color="primary"
                            @click="()=>editTree(item)"
                            variant="outlined"
                        >
                            編集
                        </v-btn>
                    </template>
                </v-data-table></v-col>
        </v-row>
    </v-container>
</template>
