<!-- CreateStructure.vue -->
<script setup>
import { onMounted, onUnmounted } from 'vue'
import NodeListLightVersion from '../nodes/NodeListLightVersion.vue'
import PrefixListLightVersion from '../prefix/PrefixListLightVersion.vue'
import { useTreeView } from './composable/useTreeView'

const {
  state,
  organizedTree,
  modalOperations,
  contextMenuOperations,
  handleNodeData,
  handlePrefixData,
  menuPosition,
  isMenuVisible,
  selectedNode,
  initialize,
  bulkCreateTree
} = useTreeView()

onMounted(async () => {
  try {
    await initialize()
    // グローバルクリックイベントリスナーを追加
    document.addEventListener('click', handleGlobalClick)
  } catch (error) {
    console.error('Failed to initialize tree view:', error)
  }
})

onUnmounted(() => {
  // クリーンアップ：イベントリスナーを削除
  document.removeEventListener('click', handleGlobalClick)
})
// グローバルクリックハンドラー
const handleGlobalClick = (event) => {
  const contextMenu = document.querySelector('.context-menu')
  const treeNode = event.target.closest('.tree-node')

  if (isMenuVisible.value &&
    contextMenu &&
    !contextMenu.contains(event.target) &&
    !treeNode) {
    contextMenuOperations.hide()
  }
}


</script>

<template>
  <v-container>
    <!-- ローディング表示 -->
    <v-progress-circular v-if="!state.isInitialized && state.loading" indeterminate color="primary" />


    <template v-else>
      <!-- エラーメッセージ -->
      <p v-if="state.errorMessage" class="error-message">{{ state.errorMessage }}</p>


      <v-row>
        <v-col>
          <v-btn variant="outlined" color="primary" class="mb-5" @click="bulkCreateTree">登録</v-btn>
        </v-col>
        <v-col>
          <!-- 右クリックした際のオブジェクトの値 -->
          <p v-if="state.isTest" class="">
            Selected = nodeID:{{ state.selectedNodeInfo.child }}
            level:{{ state.selectedNodeInfo.level }}
            parent:{{ state.selectedNodeInfo.parent }}</p>
        </v-col>
      </v-row>

      <!-- ツリービュー -->
      <div class="tree-view" @click.self="contextMenuOperations.hide">
        <div v-for="item in organizedTree" :key="`${item.parent}-${item.child}-${item.level}`" class="tree-node" :style="{
          marginLeft: `${(item.level - 1) * 20}px`,
          borderLeft: item.level > 1 ? '1px solid #ddd' : 'none'
        }" @contextmenu.prevent="(event) => contextMenuOperations.show(event, item)">
          <div class="node-content">
            <v-icon :color="item.child ? 'orange' : 'green'">
              {{ item.child ? 'mdi-folder' : 'mdi-file' }}
            </v-icon>
            <span class="node-name">{{ item.name }}</span>
            <span class="node-level">(Level: {{ item.level }})</span>
          </div>
        </div>
      </div>

      <!-- コンテキストメニュー -->
      <div v-if="isMenuVisible" class="context-menu" :style="{
        position: 'fixed',
        top: `${menuPosition.y}px`,
        left: `${menuPosition.x}px`,
        zIndex: 1000
      }" @click.stop>
        <ul>
          <li @click="modalOperations.openPrefixList">コード発番</li>
          <li @click="modalOperations.openNodeList">登録済みノード一覧</li>
        </ul>
      </div>




      <!-- データ構造の可視化 -->
      <v-data-table :items="organizedTree" density="compact" class="mt-16 pt-16"></v-data-table>

      <!-- NodeListモーダル -->
      <v-dialog v-model="state.isModalOpen.nodeList" width="auto">
        <v-card>
          <v-card-title>
            Node List
            <v-btn icon="mdi-close" @click="modalOperations.closeNodeList" class="float-right" />
          </v-card-title>
          <v-card-text>
            <NodeListLightVersion @data-sent="handleNodeData" />
          </v-card-text>
        </v-card>
      </v-dialog>

      <!-- PrefixListモーダル -->
      <v-dialog v-model="state.isModalOpen.prefixList" width="auto">
        <v-card>
          <v-card-title>
            Prefix List
            <v-btn icon="mdi-close" @click="modalOperations.closePrefixList" class="float-right" />
          </v-card-title>
          <v-card-text>
            <PrefixListLightVersion @data-sent="handlePrefixData" />
          </v-card-text>
        </v-card>
      </v-dialog>
    </template>
  </v-container>
</template>

<style scoped>
.error-message {
  color: red;
  margin: 1rem 0;
}

.tree-view {
  padding: 12px;
}

.tree-node {
  padding: 4px 8px;
  margin: 2px 0;
  cursor: context-menu;
  transition: background-color 0.2s ease;
}

.tree-node:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.node-content {
  display: flex;
  align-items: center;
  gap: 6px;
  min-height: 24px;
}

.node-name {
  font-size: 13px;
}

.node-level {
  font-size: 11px;
  color: #666;
  margin-left: 4px;
}

.context-menu {
  min-width: 180px;
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 4px 0;
}

.context-menu ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.context-menu li {
  padding: 6px 12px;
  font-size: 13px;
  color: rgba(0, 0, 0, 0.87);
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.context-menu li:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.context-menu li:active {
  background-color: rgba(0, 0, 0, 0.1);
}

.context-menu li.divider {
  height: 1px;
  margin: 3px 0;
  background-color: rgba(0, 0, 0, 0.1);
  padding: 0;
}

.context-menu li.disabled {
  color: rgba(0, 0, 0, 0.38);
  cursor: default;
  pointer-events: none;
}
</style>