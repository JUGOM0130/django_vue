<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import treeApi from './api'; // API 呼び出し用のモジュールをインポート
import CreateNode from '@/c_node/CreateView' // CreateNode コンポーネントをインポート

// ルートからパラメータを取得
const route = useRoute();
const treeRoot = ref(null);
const treeData = ref(null);
const treeStructure = ref([{
    parent: "",
    parent_name: "",
    child: "",
    child_name: "",
    tree: "",
    tree_name: "",
    level: 0
}]);
const errorMessage = ref('');
const showModal = ref(false);
const selectedItem = ref(null);
const contextMenuVisible = ref(false);
const contextMenuStyle = ref({ top: '0px', left: '0px' });

onMounted(async () => {
    //treeのRootを指定
    treeRoot.value = route.query.id;

    // treeStructure の1番目の要素に treeRoot を設定
    treeStructure.value[0].tree = treeRoot.value;

    try {
        const result = await treeApi.getTree(treeRoot.value);
        treeData.value = result.data;
        treeStructure.value[0].tree_name = treeData.value.name;
    } catch (error) {
        errorMessage.value = `Failed to fetch tree data: ${error.message}`;
    }
});

const handleRightClick = (item, event) => {
    event.preventDefault();
    selectedItem.value = item;
    contextMenuStyle.value = {
        top: `${event.clientY}px`,
        left: `${event.clientX}px`
    };
    contextMenuVisible.value = true;
};

const closeContextMenu = () => {
    contextMenuVisible.value = false;
};

const openModal = () => {
    showModal.value = true;
    closeContextMenu();
};

const closeModal = () => {
    showModal.value = false;
    selectedItem.value = null;
};


const handleAddNode = (node) => {
    // 受け取ったデータを treeStructure に追加
    treeStructure.value.push(node);
    closeModal();
};
</script>

<template>
    <div @click="closeContextMenu">
        <div class="tree">
            <h1>Create Structure</h1>
            <p v-for="(item, index) in treeStructure" :key="index" @contextmenu="handleRightClick(item, $event)">
                {{ item.tree }}:{{ item.tree_name }}
            </p>
        </div>
        <hr>
        <div class="info">
            <h1>Tree Info</h1>
            <p>Tree Root ID: {{ treeRoot }}</p>
            <div v-if="treeData">
                <h2>Tree Data:</h2>
                <p>ID: {{ treeData.id }}</p>
                <p>Name: {{ treeData.name }}</p>
                <p>Description: {{ treeData.description }}</p>
                <!-- 他の必要な情報を表示 -->
            </div>
            <div v-if="errorMessage">
                <p style="color: red;">Error: {{ errorMessage }}</p>
            </div>
        </div>

        <!-- コンテキストメニュー -->
        <div v-if="contextMenuVisible" :style="contextMenuStyle" class="context-menu">
            <ul>
                <li @click="openModal">ノードを追加</li>
                <!-- 他のメニュー項目を追加 -->
            </ul>
        </div>

        <!-- モーダル -->
        <v-dialog v-model="showModal" max-width="500px">
            <v-card>
                <CreateNode :showAddNodeButton="true" @addNode="handleAddNode"></CreateNode>
                <v-btn color="blue darken-1" text @click="closeModal">Close</v-btn>
            </v-card>
        </v-dialog>
    </div>
</template>

<style scoped>
.info,
.tree {
    margin: 1rem;
}

.context-menu {
    position: absolute;
    background-color: white;
    border: 1px solid #ccc;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.context-menu ul {
    list-style: none;
    margin: 0;
    padding: 0;
}

.context-menu li {
    padding: 8px 12px;
    cursor: pointer;
}

.context-menu li:hover {
    background-color: #f0f0f0;
}
</style>