<!-- TreeCreate.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { createTree, getTree } from '@/api/tree'

const router = useRouter()
const route = useRoute()

// ツリーの状態管理
const treeData = ref({
    name: '',
    description: '',
    nodes: []
})

// 選択中のノード
const selectedNode = ref(null)

// モーダルの状態
const showNodeModal = ref(false)
const showPrefixModal = ref(false)

// ローディング状態
const loading = ref(false)

// エラーメッセージ
const errorMessage = ref('')

// ツリーの初期化
const initializeTree = async () => {
    const id = route.query.id
    if (id) {
        loading.value = true
        try {
            const response = await getTree(id)
            treeData.value = {
                name: response.data.name,
                description: response.data.description,
                nodes: response.data.nodes || []
            }
        } catch (error) {
            console.error('Error:', error)
            errorMessage.value = 'ツリーの取得に失敗しました'
        } finally {
            loading.value = false
        }
    }
}

// ノードの追加
const addNode = (parentNode = null) => {
    const newNode = {
        id: Date.now(), // 一時的なID
        name: '新規ノード',
        children: [],
        parent: parentNode
    }

    if (parentNode) {
        parentNode.children.push(newNode)
    } else {
        treeData.value.nodes.push(newNode)
    }

    selectedNode.value = newNode
}

// ノードの削除
const deleteNode = (node) => {
    if (!node.parent) {
        treeData.value.nodes = treeData.value.nodes.filter(n => n.id !== node.id)
    } else {
        node.parent.children = node.parent.children.filter(n => n.id !== node.id)
    }
    selectedNode.value = null
}

// ノードの編集
const editNode = (node) => {
    selectedNode.value = node
}

// ノードの移動
const moveNode = (node, direction) => {
    if (!node.parent) {
        const index = treeData.value.nodes.findIndex(n => n.id === node.id)
        if (direction === 'up' && index > 0) {
            [treeData.value.nodes[index], treeData.value.nodes[index - 1]] =
                [treeData.value.nodes[index - 1], treeData.value.nodes[index]]
        } else if (direction === 'down' && index < treeData.value.nodes.length - 1) {
            [treeData.value.nodes[index], treeData.value.nodes[index + 1]] =
                [treeData.value.nodes[index + 1], treeData.value.nodes[index]]
        }
    } else {
        const index = node.parent.children.findIndex(n => n.id === node.id)
        if (direction === 'up' && index > 0) {
            [node.parent.children[index], node.parent.children[index - 1]] =
                [node.parent.children[index - 1], node.parent.children[index]]
        } else if (direction === 'down' && index < node.parent.children.length - 1) {
            [node.parent.children[index], node.parent.children[index + 1]] =
                [node.parent.children[index + 1], node.parent.children[index]]
        }
    }
}

// ツリーの保存
const saveTree = async () => {
    loading.value = true
    try {
        await createTree(treeData.value)
        router.push({ name: 'trees_index' })
    } catch (error) {
        console.error('Error:', error)
        errorMessage.value = 'ツリーの保存に失敗しました'
    } finally {
        loading.value = false
    }
}

// コンポーネントのマウント
onMounted(() => {
    initializeTree()
})
</script>

<template>
    <v-container>
        <v-row>
            <v-col>
                <h2 class="text-h4 mb-4">ツリー構造の作成</h2>

                <!-- エラーメッセージ -->
                <v-alert v-if="errorMessage" type="error" class="mb-4">
                    {{ errorMessage }}
                </v-alert>

                <!-- ツリー情報フォーム -->
                <v-card class="mb-4">
                    <v-card-text>
                        <v-text-field v-model="treeData.name" label="ツリー名" required class="mb-4"></v-text-field>
                        <v-textarea v-model="treeData.description" label="説明" rows="3" class="mb-4"></v-textarea>
                    </v-card-text>
                </v-card>

                <!-- ツリー構造 -->
                <v-card>
                    <v-card-text>
                        <div class="d-flex justify-space-between align-center mb-4">
                            <h3 class="text-h6">ノード構造</h3>
                            <v-btn color="primary" @click="addNode">
                                <v-icon start>mdi-plus</v-icon>
                                ルートノード追加
                            </v-btn>
                        </div>

                        <!-- ツリー表示 -->
                        <div class="tree-container">
                            <template v-for="node in treeData.nodes" :key="node.id">
                                <div class="node-item">
                                    <div class="node-content">
                                        <v-icon>mdi-folder</v-icon>
                                        <span class="node-name">{{ node.name }}</span>
                                        <div class="node-actions">
                                            <v-btn icon="mdi-plus" size="small" @click="addNode(node)"></v-btn>
                                            <v-btn icon="mdi-pencil" size="small" @click="editNode(node)"></v-btn>
                                            <v-btn icon="mdi-delete" size="small" @click="deleteNode(node)"></v-btn>
                                            <v-btn icon="mdi-arrow-up" size="small"
                                                @click="moveNode(node, 'up')"></v-btn>
                                            <v-btn icon="mdi-arrow-down" size="small"
                                                @click="moveNode(node, 'down')"></v-btn>
                                        </div>
                                    </div>

                                    <!-- 子ノード -->
                                    <div v-if="node.children.length > 0" class="child-nodes">
                                        <template v-for="child in node.children" :key="child.id">
                                            <div class="node-item">
                                                <div class="node-content">
                                                    <v-icon>mdi-folder</v-icon>
                                                    <span class="node-name">{{ child.name }}</span>
                                                    <div class="node-actions">
                                                        <v-btn icon="mdi-plus" size="small"
                                                            @click="addNode(child)"></v-btn>
                                                        <v-btn icon="mdi-pencil" size="small"
                                                            @click="editNode(child)"></v-btn>
                                                        <v-btn icon="mdi-delete" size="small"
                                                            @click="deleteNode(child)"></v-btn>
                                                        <v-btn icon="mdi-arrow-up" size="small"
                                                            @click="moveNode(child, 'up')"></v-btn>
                                                        <v-btn icon="mdi-arrow-down" size="small"
                                                            @click="moveNode(child, 'down')"></v-btn>
                                                    </div>
                                                </div>
                                            </div>
                                        </template>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </v-card-text>
                </v-card>

                <!-- アクションボタン -->
                <div class="d-flex justify-end mt-4">
                    <v-btn color="grey" variant="outlined" class="mr-2" @click="router.push({ name: 'trees_index' })">
                        キャンセル
                    </v-btn>
                    <v-btn color="primary" :loading="loading" @click="saveTree">
                        保存
                    </v-btn>
                </div>
            </v-col>
        </v-row>
    </v-container>
</template>

<style scoped>
.tree-container {
    padding: 16px;
}

.node-item {
    margin-bottom: 8px;
}

.node-content {
    display: flex;
    align-items: center;
    padding: 8px;
    background-color: #f5f5f5;
    border-radius: 4px;
}

.node-name {
    margin: 0 16px;
    flex-grow: 1;
}

.node-actions {
    display: flex;
    gap: 4px;
}

.child-nodes {
    margin-left: 32px;
    border-left: 2px solid #e0e0e0;
    padding-left: 16px;
}
</style>