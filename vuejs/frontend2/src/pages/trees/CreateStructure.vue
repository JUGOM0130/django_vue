<script setup>
import { ref, computed, onMounted, onUnmounted, reactive, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import NodeListLightVersion from '../nodes/NodeListLightVersion.vue';
import PrefixListLightVersion from '../prefix/PrefixListLightVersion.vue';

// ルートとルーター
const route = useRoute();
const router = useRouter();

// APIのベースURL
const apiBaseUrlCode = import.meta.env.VITE_API_BASE_URL + "/code";
const apiBaseUrlTree = import.meta.env.VITE_API_BASE_URL + "/tree";

// 状態管理
const tree = ref(null);
const treeNodes = ref([]);
const organizedTree = ref([]);
const isLoading = ref(true);
const errorMessage = ref('');
const search = ref('');
const isRefreshing = ref(false);
const selectedNode = ref(null);
const selectedStructure = ref(null);
const activeNode = ref([]);
const hasChildren = ref(false);

// コンテキストメニュー関連
const isMenuVisible = ref(false);
const menuPosition = ref({ x: 0, y: 0 });

// ノード追加関連
const addNodeDialog = ref(false);
const isAddNodeFormValid = ref(false);
const addNodeForm = ref(null);
const isAdding = ref(false);
const newNode = reactive({
  parent_id: '',
  node_type: 'code',
  name: '',
  description: '',
  code_id: null,
  relationship_type: 'assembly',
  quantity: 1,
  is_master: false
});

// ノード編集関連
const editNodeDialog = ref(false);
const isEditNodeFormValid = ref(false);
const editNodeForm = ref(null);
const isEditing = ref(false);
const editingNode = reactive({
  id: null,
  name: '',
  description: '',
  node_type: '',
  code_id: null
});
const editingStructure = reactive({
  id: null,
  relationship_type: '',
  quantity: 1,
  is_master: false,
  source_structure: null
});

// ノード削除関連
const deleteNodeDialog = ref(false);
const isDeleting = ref(false);

// 構造共有関連
const shareStructureDialog = ref(false);
const isShareFormValid = ref(false);
const shareForm = ref(null);
const isSharing = ref(false);
const availableTrees = ref([]);
const availableStructures = ref([]);
const loadingStructures = ref(false);
const sourceStructureDetails = ref(null);
const shareData = reactive({
  tree_id: '',
  source_structure_id: '',
  parent_id: ''
});

// モーダル関連
const state = reactive({
  isInitialized: false,
  loading: true,
  errorMessage: '',
  selectedNodeInfo: {
    child: null,
    level: null,
    parent: null
  },
  isTest: false, // デバッグモード
  isModalOpen: {
    nodeList: false,
    prefixList: false
  }
});

// その他のオプション
const nodeTypeOptions = [
  { name: 'コードノード', value: 'code' },
  { name: 'グループノード', value: 'group' }
];

const relationshipTypeOptions = [
  { name: '組立', value: 'assembly' },
  { name: '参照', value: 'reference' },
  { name: 'オプション', value: 'option' },
  { name: '予備品', value: 'spare' },
  { name: '代替品', value: 'alternate' },
  { name: 'ファントム', value: 'phantom' }
];

const codeOptions = ref([]);
const nodeSelectOptions = computed(() => {
  if (!treeNodes.value) return [];
  return flattenNodes(treeNodes.value);
});

// 編集可能かどうか（ツリーのステータスで判定）
const isEditable = computed(() => {
  if (!tree.value) return false;
  return ['draft', 'active'].includes(tree.value.status);
});

// 選択ノードの編集可能性
const canEditNode = computed(() => {
  if (!selectedNode.value) return false;
  if (selectedNode.value.node_type === 'root') return false;
  return true;
});

// 選択ノードの削除可能性
const canDeleteNode = computed(() => {
  if (!selectedNode.value) return false;
  if (selectedNode.value.node_type === 'root') return false;
  return true;
});

// ツリーデータの取得
const fetchTreeData = async () => {
  const treeId = route.query.id;
  if (!treeId) {
    errorMessage.value = 'ツリーIDが指定されていません';
    isLoading.value = false;
    return;
  }

  try {
    // ツリー基本情報を取得
    const treeResponse = await axios.get(`${apiBaseUrlTree}/${treeId}`);
    tree.value = treeResponse.data.data;

    // ツリー構造を取得
    const structureResponse = await axios.get(`${apiBaseUrlTree}/${treeId}/structure/`);
    treeNodes.value = buildTreeStructure(structureResponse.data.data);

    // organizedTreeを構築
    buildOrganizedTree();

    // 利用可能なコードのリストを取得
    await fetchAvailableCodes();

    // 利用可能なツリーのリストを取得
    await fetchAvailableTrees();

    state.isInitialized = true;
  } catch (error) {
    console.error('ツリーデータの取得に失敗しました:', error);
    errorMessage.value = error.response?.data?.message || 'ツリーデータの取得に失敗しました';
    state.errorMessage = errorMessage.value;
  } finally {
    isLoading.value = false;
    state.loading = false;
  }
};

// organizedTreeを構築する関数
const buildOrganizedTree = () => {
  if (!treeNodes.value || treeNodes.value.length === 0) {
    organizedTree.value = [];
    return;
  }

  const result = [];

  // 再帰的にtreeNodesを処理
  const processNode = (node, level, parent) => {
    const item = {
      uniqueKey: `${parent}-${node.id}-${level}`,
      parent: parent,
      child: node.id,
      name: node.name || 'unnamed', // nameがundefinedの場合のデフォルト値
      level: level,
      node_type: node.node_type || 'unknown', // node_typeがundefinedの場合のデフォルト値
      relationship_type: node.relationship_type || 'assembly',
      quantity: node.quantity || 1,
      is_master: node.is_master || false,
      structure_id: node.structure_id
    };

    result.push(item);

    if (node.children && node.children.length > 0) {
      node.children.forEach(child => {
        processNode(child, level + 1, node.id);
      });
    }
  };

  // ルートノードから処理開始
  treeNodes.value.forEach(node => {
    processNode(node, 1, null);
  });

  organizedTree.value = result;
};

// ツリー構造データを整形
const buildTreeStructure = (data) => {
  const nodesMap = new Map();

  // まず全ノードをマップに登録
  data.forEach(item => {
    nodesMap.set(item.id, {
      id: item.id,
      name: item.node.name || 'unnamed', // nameがundefinedの場合のデフォルト値
      node_type: item.node.node_type || 'unknown', // node_typeがundefinedの場合のデフォルト値
      description: item.node.description || '',
      code: item.node.code,
      level: item.level,
      path: item.path,
      relationship_type: item.relationship_type || 'assembly',
      quantity: item.quantity || 1,
      is_master: item.is_master || false,
      source_structure: item.source_structure,
      structure_id: item.id,
      is_shared: !!item.source_structure,
      children: []
    });
  });

  // 親子関係を構築
  const rootNodes = [];
  data.forEach(item => {
    const node = nodesMap.get(item.id);
    if (item.parent) {
      const parentNode = nodesMap.get(item.parent.id);
      if (parentNode) {
        parentNode.children.push(node);
      }
    } else {
      rootNodes.push(node);
    }
  });

  return rootNodes;
};

// ノードを再帰的に平坦化して選択肢用のリストを作成
const flattenNodes = (nodes, result = []) => {
  nodes.forEach(node => {
    result.push({
      id: node.id,
      name: `${'  '.repeat(node.level)} ${node.name}`,
      level: node.level
    });

    if (node.children && node.children.length > 0) {
      flattenNodes(node.children, result);
    }
  });

  return result;
};

// 構造データを再帰的に平坦化
const flattenStructures = (structures, result = []) => {
  structures.forEach(structure => {
    result.push(structure);

    if (structure.children && structure.children.length > 0) {
      flattenStructures(structure.children, result);
    }
  });

  return result;
};

// 利用可能なコードのリストを取得
const fetchAvailableCodes = async () => {
  try {
    const response = await axios.get(`${apiBaseUrlCode}/`, { params: { status: 'active' } });
    // response.data.resultsからデータを取得するように修正
    codeOptions.value = response.data.map(code => ({
      id: code.id,
      code: code.code,
      name: code.name,
      display: `${code.code} - ${code.name}`
    }));
    console.log('取得したコードオプション:', codeOptions.value);
  } catch (error) {
    console.error('コードリストの取得に失敗しました:', error);
  }
};

// 利用可能なツリーのリストを取得
const fetchAvailableTrees = async () => {
  try {
    const response = await axios.get(`${apiBaseUrlTree}/`);
    // 現在のツリーを除外
    availableTrees.value = response.data.data.filter(t => t.id !== tree.value?.id);
  } catch (error) {
    console.error('ツリーリストの取得に失敗しました:', error);
  }
};

// ツリー更新
const refreshTree = async () => {
  isRefreshing.value = true;

  try {
    await fetchTreeData();
  } catch (error) {
    console.error('ツリー更新エラー:', error);
  } finally {
    isRefreshing.value = false;
  }
};

// ノード選択時の処理
const onNodeSelect = (nodes) => {
  if (!nodes || nodes.length === 0) {
    selectedNode.value = null;
    selectedStructure.value = null;
    return;
  }

  const node = nodes[0];
  selectedNode.value = node;

  // 構造情報も設定
  selectedStructure.value = {
    id: node.structure_id,
    relationship_type: node.relationship_type,
    quantity: node.quantity,
    is_master: node.is_master,
    source_structure: node.source_structure,
    level: node.level
  };

  // 子ノードの存在確認
  hasChildren.value = node.children && node.children.length > 0;

  // selectedNodeInfoも更新
  state.selectedNodeInfo = {
    child: node.id,
    level: node.level,
    parent: node.parent ? node.parent.id : null
  };
};

// ノードタイプのラベルを取得
const getNodeTypeLabel = (type) => {
  const typesMap = {
    'root': 'ルートノード',
    'code': 'コードノード',
    'group': 'グループノード'
  };
  return typesMap[type] || type;
};

// 関係タイプのラベルを取得
const getRelationshipTypeLabel = (type) => {
  const typesMap = {
    'assembly': '組立',
    'reference': '参照',
    'option': 'オプション',
    'spare': '予備品',
    'alternate': '代替品',
    'phantom': 'ファントム'
  };
  return typesMap[type] || type;
};

// ステータスラベル取得
const getStatusLabel = (status) => {
  const statusMap = {
    draft: '作成中',
    active: '有効',
    archived: 'アーカイブ',
    locked: 'ロック中'
  };
  return statusMap[status] || status;
};

// ステータスの色を取得
const getStatusColor = (status) => {
  const statusColorMap = {
    draft: 'blue',
    active: 'success',
    archived: 'grey',
    locked: 'error'
  };
  return statusColorMap[status] || 'grey';
};

// ノードアイコン取得
const getNodeIcon = (item) => {
  if (item.node_type === 'root') return 'mdi-source-branch';
  if (item.node_type === 'group') return 'mdi-folder';
  if (item.is_shared) return 'mdi-link-variant';
  return 'mdi-file-document';
};

// ノードアイコン色取得
const getNodeIconColor = (item) => {
  if (item.node_type === 'root') return 'purple';
  if (item.node_type === 'group') return 'orange';
  if (item.is_shared) return 'blue';
  return 'green';
};

// すべてのノードを展開
const expandAll = () => {
  // v-treeviewの場合、これは自動的に処理される
};

// すべてのノードを折りたたむ
const collapseAll = () => {
  // v-treeviewの場合、これは自動的に処理される
};

// 前のページに戻る
const goBack = () => {
  router.push({ name: 'tree_list' });
};

// ノード追加ダイアログを表示
const showAddNodeDialog = () => {
  // フォームをリセット
  newNode.parent_id = selectedNode.value ? selectedNode.value.id : '';
  newNode.node_type = 'code';
  newNode.name = '';
  newNode.description = '';
  newNode.code_id = null;
  newNode.relationship_type = 'assembly';
  newNode.quantity = 1;
  newNode.is_master = false;

  // フォームのバリデーションをリセット
  if (addNodeForm.value) addNodeForm.value.resetValidation();

  // ダイアログを表示
  addNodeDialog.value = true;
};

// ノードを追加
const addNode = async () => {
  if (!isAddNodeFormValid.value) return;

  isAdding.value = true;

  try {
    const response = await axios.post(`${apiBaseUrlTree}/${tree.value.id}/add_node/`, {
      parent_id: newNode.parent_id,
      name: newNode.name,
      description: newNode.description,
      node_type: newNode.node_type,
      code_id: newNode.node_type === 'code' ? newNode.code_id : null,
      relationship_type: newNode.relationship_type,
      quantity: newNode.quantity,
      is_master: newNode.is_master
    });

    if (response.data.success) {
      // ダイアログを閉じる
      addNodeDialog.value = false;

      // ツリーデータを再取得
      await refreshTree();

      // 成功メッセージ表示
      // Vuetifyのスナックバーなどを使用する場合はここで表示
    } else {
      errorMessage.value = response.data.message || 'ノードの追加に失敗しました';
    }
  } catch (error) {
    console.error('ノード追加エラー:', error);
    errorMessage.value = error.response?.data?.message || 'ノードの追加中にエラーが発生しました';
  } finally {
    isAdding.value = false;
  }
};

// ノード編集ダイアログを表示
const showEditNodeDialog = () => {
  if (!selectedNode.value) return;

  // 編集用の値をセット
  editingNode.id = selectedNode.value.id;
  editingNode.name = selectedNode.value.name;
  editingNode.description = selectedNode.value.description || '';
  editingNode.node_type = selectedNode.value.node_type;
  editingNode.code_id = selectedNode.value.code ? selectedNode.value.code.id : null;

  editingStructure.id = selectedStructure.value.id;
  editingStructure.relationship_type = selectedStructure.value.relationship_type;
  editingStructure.quantity = selectedStructure.value.quantity;
  editingStructure.is_master = selectedStructure.value.is_master;
  editingStructure.source_structure = selectedStructure.value.source_structure;

  // フォームのバリデーションをリセット
  if (editNodeForm.value) editNodeForm.value.resetValidation();

  // ダイアログを表示
  editNodeDialog.value = true;
};

// ノードを更新
const updateNode = async () => {
  if (!isEditNodeFormValid.value) return;

  isEditing.value = true;

  try {
    // ノード情報の更新
    const nodeResponse = await axios.patch(`${apiBaseUrlTree}nodes/${editingNode.id}/`, {
      name: editingNode.name,
      description: editingNode.description,
      code_id: editingNode.node_type === 'code' && editingNode.code_id ? editingNode.code_id : null
    });

    // 構造情報の更新
    const structureResponse = await axios.patch(`${apiBaseUrlTree}structures/${editingStructure.id}/`, {
      relationship_type: editingStructure.relationship_type,
      quantity: editingStructure.quantity,
      is_master: !editingStructure.source_structure ? editingStructure.is_master : false
    });

    // 成功したらダイアログを閉じる
    editNodeDialog.value = false;

    // ツリーデータを再取得
    await refreshTree();

    // 成功メッセージ表示
    // Vuetifyのスナックバーなどを使用する場合はここで表示
  } catch (error) {
    console.error('ノード更新エラー:', error);
    errorMessage.value = error.response?.data?.message || 'ノードの更新中にエラーが発生しました';
  } finally {
    isEditing.value = false;
  }
};

// ノード削除の確認ダイアログを表示
const confirmDeleteNode = () => {
  if (!selectedNode.value) return;
  deleteNodeDialog.value = true;
};

// ノードを削除
const deleteNode = async () => {
  if (!selectedStructure.value) return;

  isDeleting.value = true;

  try {
    const response = await axios.delete(`${apiBaseUrlTree}structures/${selectedStructure.value.id}/`);

    // ダイアログを閉じる
    deleteNodeDialog.value = false;

    // 選択状態をクリア
    selectedNode.value = null;
    selectedStructure.value = null;

    // ツリーデータを再取得
    await refreshTree();

    // 成功メッセージ表示
    // Vuetifyのスナックバーなどを使用する場合はここで表示
  } catch (error) {
    console.error('ノード削除エラー:', error);
    errorMessage.value = error.response?.data?.message || 'ノードの削除中にエラーが発生しました';
  } finally {
    isDeleting.value = false;
  }
};

// 構造共有ダイアログを表示
const showShareDialog = () => {
  // 値をリセット
  shareData.tree_id = '';
  shareData.source_structure_id = '';
  shareData.parent_id = selectedNode.value ? selectedNode.value.id : '';

  // フォームのバリデーションをリセット
  if (shareForm.value) shareForm.value.resetValidation();

  // ダイアログを表示
  shareStructureDialog.value = true;
};

// 共有元ツリーが選択されたときに構造リストを取得
const loadSourceStructures = async () => {
  if (!shareData.tree_id) return;

  loadingStructures.value = true;
  availableStructures.value = [];
  shareData.source_structure_id = '';
  sourceStructureDetails.value = null;

  try {
    const response = await axios.get(`${apiBaseUrlTree}trees/${shareData.tree_id}/structure/`);

    // 構造データをフラット化してセレクトボックス用に整形
    const structures = flattenStructures(response.data);
    availableStructures.value = structures.map(s => ({
      id: s.id,
      node_id: s.node.id,
      display_name: `${'  '.repeat(s.level)} ${s.node.name}`,
      level: s.level,
      is_master: s.is_master,
      children_count: s.children ? s.children.length : 0
    }));
  } catch (error) {
    console.error('構造リストの取得に失敗しました:', error);
  } finally {
    loadingStructures.value = false;
  }
};

// 構造を共有
const shareStructure = async () => {
  if (!isShareFormValid.value) return;

  isSharing.value = true;

  try {
    const response = await axios.post(`${apiBaseUrlTree}trees/${tree.value.id}/share_structure/`, {
      source_structure_id: shareData.source_structure_id,
      parent_id: shareData.parent_id
    });

    if (response.data.success) {
      // ダイアログを閉じる
      shareStructureDialog.value = false;

      // ツリーデータを再取得
      await refreshTree();

      // 成功メッセージ表示
      // Vuetifyのスナックバーなどを使用する場合はここで表示
    } else {
      errorMessage.value = response.data.message || '構造の共有に失敗しました';
    }
  } catch (error) {
    console.error('構造共有エラー:', error);
    errorMessage.value = error.response?.data?.message || '構造の共有中にエラーが発生しました';
  } finally {
    isSharing.value = false;
  }
};

// コード詳細表示
const viewCode = () => {
  if (!selectedNode.value || !selectedNode.value.code) return;
  router.push({ name: 'code_detail', params: { id: selectedNode.value.code.id } });
};

// 選択された構造が変更されたときにソース構造の詳細を取得
watch(() => shareData.source_structure_id, async (newId) => {
  if (!newId) {
    sourceStructureDetails.value = null;
    return;
  }

  try {
    const response = await axios.get(`${apiBaseUrlTree}structures/${newId}/`);
    sourceStructureDetails.value = response.data;
  } catch (error) {
    console.error('構造詳細の取得に失敗しました:', error);
    sourceStructureDetails.value = null;
  }
});

// コンテキストメニュー操作
const contextMenuOperations = {
  show: (event, item) => {
    console.log('Context Menu Item:', item);

    menuPosition.value = { x: event.clientX, y: event.clientY };
    isMenuVisible.value = true;

    // 選択したノード情報を記録
    state.selectedNodeInfo = {
      child: item.child,  // これがundefinedになっていないか確認
      level: item.level,
      parent: item.parent
    };

    console.log('Selected Node Info:', state.selectedNodeInfo);

    // ノードを選択状態にする
    const node = findNodeById(treeNodes.value, item.child);
    if (node) {
      activeNode.value = [node];
      onNodeSelect([node]);
    }
  },
  hide: () => {
    isMenuVisible.value = false;
  }
};

// モーダル操作
const modalOperations = {
  openNodeList: () => {
    state.isModalOpen.nodeList = true;
    contextMenuOperations.hide();
  },
  closeNodeList: () => {
    state.isModalOpen.nodeList = false;
  },
  openPrefixList: () => {
    state.isModalOpen.prefixList = true;
    contextMenuOperations.hide();
  },
  closePrefixList: () => {
    state.isModalOpen.prefixList = false;
  }
};

// IDからノードを検索
const findNodeById = (nodes, id) => {
  for (const node of nodes) {
    if (node.id === id) return node;
    if (node.children && node.children.length > 0) {
      const found = findNodeById(node.children, id);
      if (found) return found;
    }
  }
  return null;
};

// ノードリストからデータを受け取る
const handleNodeData = (data) => {
  console.log("Received node data:", data);
  // ここでノードデータを処理
  modalOperations.closeNodeList();

  // 親ノードに新しいノードを追加
  if (state.selectedNodeInfo.child) {
    // 選択されたノードの下に追加するロジック
    newNode.parent_id = state.selectedNodeInfo.child;
    newNode.name = data.name;
    newNode.code_id = data.id;
    newNode.node_type = 'code';

    // 追加ダイアログを表示
    addNodeDialog.value = true;
  }
};

// プレフィックスリストからデータを受け取る
const handlePrefixData = (data) => {
  console.log("Received prefix data:", data);
  // ここでプレフィックスデータを処理
  modalOperations.closePrefixList();
};

// ツリーの一括作成
const bulkCreateTree = async () => {
  try {
    const response = await axios.post(`${apiBaseUrlTree}/${tree.value.id}/bulk_update/`, {
      structures: organizedTree.value
    });

    if (response.data.success) {
      // 成功メッセージ表示
      alert('ツリーを保存しました');

      // ツリーデータを再取得
      await refreshTree();
    } else {
      errorMessage.value = response.data.message || 'ツリーの保存に失敗しました';
      alert(errorMessage.value);
    }
  } catch (error) {
    console.error('ツリー保存エラー:', error);
    errorMessage.value = error.response?.data?.message || 'ツリーの保存中にエラーが発生しました';
    alert(errorMessage.value);
  }
};

// グローバルクリックハンドラー
const handleGlobalClick = (event) => {
  const contextMenu = document.querySelector('.context-menu');
  const treeNode = event.target.closest('.tree-node');

  if (isMenuVisible.value &&
    contextMenu &&
    !contextMenu.contains(event.target) &&
    !treeNode) {
    contextMenuOperations.hide();
  }
};

// 初期化関数
const initialize = async () => {
  await fetchTreeData();
};

// コンポーネントのマウント時に初期化
onMounted(async () => {
  try {
    await initialize();
    // グローバルクリックイベントリスナーを追加
    document.addEventListener('click', handleGlobalClick);
  } catch (error) {
    console.error('Failed to initialize tree editor:', error);
  }
});

// コンポーネントのアンマウント時にイベントリスナーを削除
onUnmounted(() => {
  document.removeEventListener('click', handleGlobalClick);
});
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
        <ul><!--
          <li @click="modalOperations.openPrefixList">コード発番</li>
          <li @click="modalOperations.openNodeList">登録済みノード一覧</li>
          -->
          <li @click="showAddNodeDialog">新規ノード作成</li>
          <li v-if="selectedNode && canEditNode" @click="showEditNodeDialog">ノード編集</li>
          <li v-if="selectedNode && canDeleteNode" @click="confirmDeleteNode" class="danger">ノード削除</li>
        </ul>
      </div>

      <!-- ノード情報表示 -->
      <v-card v-if="selectedNode" class="mt-4">
        <v-card-title>選択ノード情報</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <p><strong>名前:</strong> {{ selectedNode.name }}</p>
              <p><strong>タイプ:</strong> {{ getNodeTypeLabel(selectedNode.node_type) }}</p>
              <p v-if="selectedNode.code"><strong>コード:</strong> {{ selectedNode.code }}</p>
            </v-col>
            <v-col cols="12" md="6">
              <p><strong>レベル:</strong> {{ selectedNode.level }}</p>
              <p><strong>関係タイプ:</strong> {{ getRelationshipTypeLabel(selectedNode.relationship_type) }}</p>
              <p><strong>数量:</strong> {{ selectedNode.quantity || 1 }}</p>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- データ構造の可視化 -->
      <v-data-table :items="organizedTree" density="compact" class="mt-16 pt-16" item-value="uniqueKey">
      </v-data-table>

      <!-- ノード追加モーダル -->
      <v-dialog v-model="addNodeDialog" width="500px">
        <v-card>
          <v-card-title>新規ノード追加</v-card-title>
          <v-card-text>
            <v-form ref="addNodeForm" v-model="isAddNodeFormValid">
              <v-select v-model="newNode.parent_id" label="親ノード*" :items="nodeSelectOptions" item-title="name"
                item-value="id" variant="outlined" density="comfortable" :rules="[v => !!v || '親ノードは必須です']"
                class="mb-3"></v-select>

              <v-select v-model="newNode.node_type" label="ノードタイプ*" :items="nodeTypeOptions" item-title="name"
                item-value="value" variant="outlined" density="comfortable" :rules="[v => !!v || 'ノードタイプは必須です']"
                class="mb-3"></v-select>

              <v-text-field v-model="newNode.name" label="ノード名*" variant="outlined" density="comfortable"
                :rules="[v => !!v || 'ノード名は必須です']" class="mb-3"></v-text-field>

              <v-textarea v-model="newNode.description" label="説明" variant="outlined" density="comfortable" rows="3"
                auto-grow class="mb-3"></v-textarea>

              <v-select v-if="newNode.node_type === 'code'" v-model="newNode.code_id" label="関連コード" :items="codeOptions"
                item-title="display" item-value="id" variant="outlined" density="comfortable" class="mb-3"
                :rules="[v => !!v || '関連コードは必須です']">
              </v-select>

              <v-select v-model="newNode.relationship_type" label="関係タイプ" :items="relationshipTypeOptions"
                item-title="name" item-value="value" variant="outlined" density="comfortable" class="mb-3"></v-select>

              <v-text-field v-model.number="newNode.quantity" label="数量" type="number" min="0.001" step="0.001"
                variant="outlined" density="comfortable" hint="デフォルト: 1.0" class="mb-3"></v-text-field>

              <v-checkbox v-model="newNode.is_master" label="マスター構造として設定" color="primary" hide-details></v-checkbox>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey-darken-1" variant="text" @click="addNodeDialog = false" :disabled="isAdding">
              キャンセル
            </v-btn>
            <v-btn color="primary" @click="addNode" :disabled="!isAddNodeFormValid || isAdding" :loading="isAdding">
              追加
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- ノード編集モーダル -->
      <v-dialog v-model="editNodeDialog" width="500px">
        <v-card>
          <v-card-title>ノード編集</v-card-title>
          <v-card-text>
            <v-form ref="editNodeForm" v-model="isEditNodeFormValid">
              <v-text-field v-model="editingNode.name" label="ノード名*" variant="outlined" density="comfortable"
                :rules="[v => !!v || 'ノード名は必須です']" class="mb-3"></v-text-field>

              <v-textarea v-model="editingNode.description" label="説明" variant="outlined" density="comfortable" rows="3"
                auto-grow class="mb-3"></v-textarea>

              <v-select v-if="editingNode.node_type === 'code' && !editingNode.code_id" v-model="editingNode.code_id"
                label="関連コード" :items="codeOptions" item-title="display" item-value="id" variant="outlined"
                density="comfortable" class="mb-3">
                <template v-slot:selection="{ item }">
                  {{ item.raw.display }}
                </template>
                <template v-slot:item="{ item }">
                  <v-list-item :title="item.raw.code" :subtitle="item.raw.name"></v-list-item>
                </template>
              </v-select>

              <v-select v-model="editingStructure.relationship_type" label="関係タイプ" :items="relationshipTypeOptions"
                item-title="name" item-value="value" variant="outlined" density="comfortable" class="mb-3"></v-select>

              <v-text-field v-model.number="editingStructure.quantity" label="数量" type="number" min="0.001" step="0.001"
                variant="outlined" density="comfortable" class="mb-3"></v-text-field>

              <v-checkbox v-if="!editingStructure.source_structure" v-model="editingStructure.is_master"
                label="マスター構造として設定" color="primary" hide-details></v-checkbox>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey-darken-1" variant="text" @click="editNodeDialog = false" :disabled="isEditing">
              キャンセル
            </v-btn>
            <v-btn color="primary" @click="updateNode" :disabled="!isEditNodeFormValid || isEditing"
              :loading="isEditing">
              更新
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- ノード削除確認ダイアログ -->
      <v-dialog v-model="deleteNodeDialog" max-width="500px">
        <v-card>
          <v-card-title class="text-error">ノード削除の確認</v-card-title>
          <v-card-text>
            <p><strong>{{ selectedNode?.name }}</strong> を削除してもよろしいですか？</p>

            <v-alert v-if="hasChildren" type="warning" class="mt-3">
              このノードには子ノードが含まれています。削除すると子ノードもすべて削除されます。
            </v-alert>

            <p class="text-error mt-2">
              <v-icon color="error" class="mr-1">mdi-alert-circle</v-icon>
              この操作は取り消せません。
            </p>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey-darken-1" variant="text" @click="deleteNodeDialog = false" :disabled="isDeleting">
              キャンセル
            </v-btn>
            <v-btn color="error" @click="deleteNode" :loading="isDeleting" :disabled="isDeleting">
              削除する
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

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

.context-menu li.danger {
  color: #f44336;
}

.context-menu li.danger:hover {
  background-color: rgba(244, 67, 54, 0.05);
}

/* ノード情報表示のスタイル */
.node-details {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.node-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.node-details-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.node-details-property {
  margin-bottom: 5px;
}

.node-details-property .label {
  font-weight: bold;
  margin-right: 5px;
}

.node-details-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* データテーブルの行をハイライト */
.v-data-table .highlighted-row {
  background-color: rgba(33, 150, 243, 0.1);
}
</style>