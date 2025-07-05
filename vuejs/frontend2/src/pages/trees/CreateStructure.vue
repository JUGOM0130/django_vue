<script setup>
import { ref, computed, onMounted, onUnmounted, reactive, watch, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import NodeListLightVersion from '../nodes/NodeListLightVersion.vue';
import PrefixListLightVersion from '../prefix/PrefixListLightVersion.vue';
import RegistedNodeList from './dialogs/RegistedNodeList.vue';
import { useSnackbar } from './composables/useSnackbar';


// スナックバー機能を使用
const {
  showSuccess,
  showError,
  showWarning,
  showInfo,
  showApiResult,
  showWithUndo,
  showValidationErrors,
  snackbar
} = useSnackbar();

// ルートとルーター
const route = useRoute();
const router = useRouter();

// APIのベースURL
const apiBaseUrlCode = import.meta.env.VITE_API_BASE_URL + "/code";
const apiBaseUrlTree = import.meta.env.VITE_API_BASE_URL + "/tree";
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;


// 状態管理
const tree = ref(null);
const treeNodes = ref([]);
const organizedTree = ref([]);
const isLoading = ref(true);
const errorMessage = ref('');
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


// ===== 既存ツリー共有関連の状態管理を追加 =====
// 既存のreactiveの定義の後に追加

// 既存ツリー全構造共有関連
const addSharedTreeDialog = ref(false);
const isAddSharedTreeFormValid = ref(false);
const addSharedTreeForm = ref(null);
const isAddingSharedTree = ref(false);

// 既存ツリー全構造共有用のデータ
const addSharedTreeData = reactive({
  source_tree_id: '',
  parent_structure_id: '',
  include_root: false,
  relationship_type: 'assembly',
  quantity: 1.0
});

// 利用可能なツリーリスト（全構造共有用）
const availableTreesForFullShare = ref([]);

/**
 * 既存ツリー全構造共有ダイアログを表示
 */
const showAddSharedTreeDialog = () => {
  // フォームをリセット
  addSharedTreeData.source_tree_id = '';
  addSharedTreeData.parent_structure_id = selectedNode.value ? selectedNode.value.structure_id : '';
  addSharedTreeData.include_root = false;
  addSharedTreeData.relationship_type = 'assembly';
  addSharedTreeData.quantity = 1.0;

  // バリデーションをリセット
  if (addSharedTreeForm.value) {
    addSharedTreeForm.value.resetValidation();
  }

  // 利用可能なツリーリストを取得
  fetchAvailableTreesForFullShare();

  // ダイアログを表示
  addSharedTreeDialog.value = true;
};

/**
 * 全構造共有用のツリーリストを取得
 */
const fetchAvailableTreesForFullShare = async () => {
  try {
    const response = await axios.get(`${apiBaseUrlTree}/`);

    if (response.data && response.data.data) {
      availableTreesForFullShare.value = response.data.data
        .filter(t => t.id !== tree.value?.id)
        .map(t => ({
          id: t.id,
          name: t.name,
          status: t.status,
          description: t.description || '',
          display: `${t.name} (${getStatusLabel(t.status)})`
        }));
    }
  } catch (error) {
    console.error('全構造共有用ツリーリストの取得に失敗しました:', error);
    showError(
      'ツリーリストの取得に失敗しました',
      { timeout: 3000 }
    );
  }
};

/**
 * 既存ツリーの全構造を共有として追加
 */
const addSharedTreeStructure = async () => {
  if (!isAddSharedTreeFormValid.value) return;

  // 必須パラメータの確認
  if (!addSharedTreeData.source_tree_id || !addSharedTreeData.parent_structure_id) {
    showError('必須項目が入力されていません', { timeout: 3000 });
    return;
  }

  isAddingSharedTree.value = true;

  try {
    const requestData = {
      source_tree_id: addSharedTreeData.source_tree_id,
      parent_structure_id: addSharedTreeData.parent_structure_id,
      include_root: addSharedTreeData.include_root,
      relationship_type: addSharedTreeData.relationship_type,
      quantity: addSharedTreeData.quantity
    };

    console.log('既存ツリー全構造共有リクエスト:', requestData);

    const response = await axios.post(
      `${apiBaseUrlTree}/${tree.value.id}/add_shared_tree_structure/`,
      requestData
    );

    console.log('既存ツリー全構造共有レスポンス:', response.data);

    if (response.data.success) {
      // ダイアログを閉じる
      addSharedTreeDialog.value = false;

      // ツリーデータを再取得
      await refreshTree();

      // 成功メッセージを表示
      showSuccess(
        `既存ツリーの全構造を共有しました。${response.data.data.shared_structures_count}個のノードが追加されました。`,
        { timeout: 4000 }
      );

    } else {
      showError(
        response.data.message || '既存ツリーの全構造共有に失敗しました',
        { timeout: 3000 }
      );
    }
  } catch (error) {
    console.error('既存ツリー全構造共有エラー:', error);
    showError(
      error.response?.data?.message || '既存ツリーの全構造共有中にエラーが発生しました',
      { timeout: 5000 }
    );
  } finally {
    isAddingSharedTree.value = false;
  }
};
// ===== 特定ノード部分の共有機能を追加 =====

// 特定ノード部分共有関連の状態管理
const addPartialTreeDialog = ref(false);
const isAddPartialTreeFormValid = ref(false);
const addPartialTreeForm = ref(null);
const isAddingPartialTree = ref(false);

// 特定ノード部分共有用のデータ
const addPartialTreeData = reactive({
  source_tree_id: '',
  source_structure_id: '',
  parent_structure_id: '',
  include_children: true,
  relationship_type: 'assembly',
  quantity: 1.0
});

// 利用可能なツリーと構造のリスト（部分共有用）
const availableTreesForPartialShare = ref([]);
const availableStructuresForPartialShare = ref([]);
const loadingPartialStructures = ref(false);

/**
 * 特定ノード部分共有ダイアログを表示
 */
const showAddPartialTreeDialog = () => {
  // フォームをリセット
  addPartialTreeData.source_tree_id = '';
  addPartialTreeData.source_structure_id = '';
  addPartialTreeData.parent_structure_id = selectedNode.value ? selectedNode.value.structure_id : '';
  addPartialTreeData.include_children = true;
  addPartialTreeData.relationship_type = 'assembly';
  addPartialTreeData.quantity = 1.0;

  // バリデーションをリセット
  if (addPartialTreeForm.value) {
    addPartialTreeForm.value.resetValidation();
  }

  // 利用可能なツリーリストを取得
  fetchAvailableTreesForPartialShare();

  // ダイアログを表示
  addPartialTreeDialog.value = true;
};

/**
 * 部分共有用のツリーリストを取得
 */
const fetchAvailableTreesForPartialShare = async () => {
  try {
    const response = await axios.get(`${apiBaseUrlTree}/`);

    if (response.data && response.data.data) {
      availableTreesForPartialShare.value = response.data.data
        .filter(t => t.id !== tree.value?.id)
        .map(t => ({
          id: t.id,
          name: t.name,
          status: t.status,
          description: t.description || '',
          display: `${t.name} (${getStatusLabel(t.status)})`
        }));
    }
  } catch (error) {
    console.error('部分共有用ツリーリストの取得に失敗しました:', error);
    showError(
      'ツリーリストの取得に失敗しました',
      { timeout: 3000 }
    );
  }
};

/**
 * 選択されたツリーの構造リストを取得
 */
const loadPartialStructures = async () => {
  if (!addPartialTreeData.source_tree_id) {
    availableStructuresForPartialShare.value = [];
    return;
  }

  loadingPartialStructures.value = true;
  availableStructuresForPartialShare.value = [];
  addPartialTreeData.source_structure_id = '';

  try {
    // 1. まずツリー構造を取得
    const structureResponse = await axios.get(`${apiBaseUrlTree}/${addPartialTreeData.source_tree_id}/structure/`);
    console.log('Structure API response:', structureResponse.data);

    let structureData;
    if (structureResponse.data && Array.isArray(structureResponse.data.data)) {
      structureData = structureResponse.data.data;
    } else if (Array.isArray(structureResponse.data)) {
      structureData = structureResponse.data;
    } else {
      throw new Error('ツリー構造データの形式が不正です');
    }

    if (structureData.length === 0) {
      availableStructuresForPartialShare.value = [];
      return;
    }

    // 2. 各構造のノード詳細情報を並行取得
    const nodeIds = [...new Set(structureData.map(item => item.node))]; // 重複除去
    const nodeDetailsPromises = nodeIds.map(nodeId =>
      axios.get(`${apiBaseUrl}/tree-node/${nodeId}/`)
        .catch(error => {
          console.warn(`Node ${nodeId} fetch failed:`, error);
          return { data: { id: nodeId, name: 'Unknown', node_type: 'unknown' } };
        })
    );

    const nodeDetailsResponses = await Promise.all(nodeDetailsPromises);
    const nodeDetailsMap = new Map();

    nodeDetailsResponses.forEach(response => {
      const data = response.data.data || response.data;
      if (data && data.id) {
        nodeDetailsMap.set(data.id, data);
      }
    });

    console.log('Node details map:', nodeDetailsMap);

    // 3. 構造データとノード詳細を結合
    availableStructuresForPartialShare.value = structureData
      .filter(structure => structure.level > 0) // ルートノードを除外
      .map(structure => {
        const nodeDetails = nodeDetailsMap.get(structure.node) || {};
        const nodeName = nodeDetails.name || `Node-${structure.node}`;

        return {
          id: structure.id,
          node_id: structure.node,
          node_name: nodeName,
          level: structure.level,
          path: structure.path,
          parent_id: structure.parent,
          node_type: nodeDetails.node_type || 'unknown',
          display: `${'  '.repeat(structure.level - 1)} ${nodeName} (Level: ${structure.level})`
        };
      });

    console.log('Available structures for partial share:', availableStructuresForPartialShare.value);

  } catch (error) {
    console.error('部分共有用構造リスト取得エラー:', error);
    showError('構造リストの取得に失敗しました: ' + (error.message || '不明なエラー'), { timeout: 3000 });

  } finally {
    loadingPartialStructures.value = false;
  }
};

/**
 * 特定ノード部分を共有として追加
 */
const addPartialTreeStructure = async () => {
  if (!isAddPartialTreeFormValid.value) return;

  // 必須パラメータの確認
  if (!addPartialTreeData.source_tree_id ||
    !addPartialTreeData.source_structure_id ||
    !addPartialTreeData.parent_structure_id) {
    showError('必須項目が入力されていません', { timeout: 3000 });
    return;
  }

  isAddingPartialTree.value = true;

  try {
    // ✅ 正しいエンドポイントに変更
    const requestData = {
      source_structure_id: addPartialTreeData.source_structure_id,
      parent_id: addPartialTreeData.parent_structure_id
    };

    console.log('構造共有リクエストパラメータ:', requestData);

    // ✅ share_structure エンドポイントを使用
    const response = await axios.post(
      `${apiBaseUrlTree}/${tree.value.id}/share_structure/`,
      requestData
    );

    console.log('構造共有レスポンス:', response.data);

    if (response.data.success) {
      // ダイアログを閉じる
      addPartialTreeDialog.value = false;

      // ツリーデータを再取得
      await refreshTree();

      // 選択された構造の情報を表示
      const selectedStructure = availableStructuresForPartialShare.value.find(
        s => s.id == addPartialTreeData.source_structure_id
      );

      // 成功メッセージを表示
      showSuccess(
        `構造「${selectedStructure?.node_name || 'Unknown'}」を共有グループに追加しました。他のツリーにも自動同期されます。`,
        { timeout: 4000 }
      )
    } else {
      showError(
        response.data.message || '構造共有に失敗しました',
        { timeout: 3000 }
      );
    }
  } catch (error) {
    console.error('構造共有エラー:', error);
    console.error('エラーレスポンス:', error.response?.data);

    showError(error.response?.data?.message || '構造共有中にエラーが発生しました', { timeout: 5000 });
  } finally {
    isAddingPartialTree.value = false;
  }
};

// watchで共有元ツリー変更を監視
watch(() => addPartialTreeData.source_tree_id, () => {
  loadPartialStructures();
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
    prefixList: false  // Prefixリストモーダル用
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


// fetchTreeDataメソッドの修正
const fetchTreeData = async () => {
  const treeId = route.query.id;
  if (!treeId) {
    errorMessage.value = 'ツリーIDが指定されていません';
    isLoading.value = false;
    return;
  }

  try {
    // ローディング開始
    isLoading.value = true;

    // まずツリー自体の情報を取得
    try {
      const treeResponse = await axios.get(`${apiBaseUrlTree}/${treeId}/`);

      // APIレスポンスの形式によって調整が必要
      // データがdataプロパティにネストされているか確認
      if (treeResponse.data && treeResponse.data.data) {
        tree.value = treeResponse.data.data;
      } else {
        tree.value = treeResponse.data;
      }

      console.log('Fetched tree data:', tree.value);

      // tree.valueがオブジェクトでidプロパティを持っていることを確認
      if (!tree.value || typeof tree.value !== 'object' || !tree.value.id) {
        throw new Error('取得したツリーデータが不正です');
      }
    } catch (error) {
      console.error('ツリー基本情報の取得に失敗しました:', error);
      errorMessage.value = 'ツリー基本情報の取得に失敗しました';
      isLoading.value = false;
      return;
    }

    // ツリー構造を取得
    const structureResponse = await axios.get(`${apiBaseUrlTree}/${treeId}/structure/`);
    console.log('Structure response:', structureResponse.data);

    // レスポンスからデータを抽出（APIの形式に応じて調整）
    let structureData;
    if (structureResponse.data && Array.isArray(structureResponse.data.data)) {
      structureData = structureResponse.data.data;
    } else if (Array.isArray(structureResponse.data)) {
      structureData = structureResponse.data;
    } else {
      throw new Error('ツリー構造データの形式が不正です');
    }

    // ノード情報を並行して取得
    if (structureData.length === 0) {
      // 構造が空の場合
      treeNodes.value = [];
      organizedTree.value = [];
    } else {
      const nodeIds = structureData.map(item => item.node);
      const nodeDetailsPromises = nodeIds.map(nodeId =>
        axios.get(`${apiBaseUrl}/tree-node/${nodeId}/`)
      );

      const nodeDetailsResponses = await Promise.all(nodeDetailsPromises);
      const nodeDetailsMap = new Map(
        nodeDetailsResponses.map(response => {
          // レスポンスの形式によって調整
          const data = response.data.data || response.data;
          return [data.id, data];
        })
      );

      // ツリー構造を構築
      treeNodes.value = buildTreeStructure(structureData, nodeDetailsMap);

      // organizedTreeを構築
      buildOrganizedTree();
    }

    console.log('Processed Tree Nodes:', treeNodes.value);
    console.log('Organized Tree:', organizedTree.value);

  } catch (error) {
    console.error('ツリーデータの取得に失敗しました:', error);
    errorMessage.value = error.response?.data?.message || error.message || 'ツリーデータの取得に失敗しました';
  } finally {
    // 状態の更新
    state.isInitialized = true;
    isLoading.value = false;
  }
};

const buildTreeStructure = (data, nodeDetailsMap) => {
  console.log('Building tree structure from:', data);

  const nodesMap = new Map();

  // まず全ノードをマップに登録
  data.forEach(item => {
    const nodeDetails = nodeDetailsMap.get(item.node) || {};

    const node = {
      id: item.id,
      node_id: item.node,
      name: nodeDetails.name || 'Unknown',
      node_type: nodeDetails.node_type || 'unknown',
      description: nodeDetails.description || '',
      code: nodeDetails.code,
      level: item.level,
      path: item.path,
      relationship_type: item.relationship_type || 'assembly',
      quantity: parseFloat(item.quantity) || 1,
      is_master: item.is_master || false,
      parent_id: item.parent,
      source_structure: item.source_structure,
      structure_id: item.id,
      children: []
    };

    nodesMap.set(item.id, node);
  });

  // 親子関係を構築
  const rootNodes = [];
  data.forEach(item => {
    const node = nodesMap.get(item.id);

    if (item.parent) {
      const parentNode = nodesMap.get(item.parent);
      if (parentNode) {
        // 子ノードを親ノードのchildrenに追加
        parentNode.children.push(node);
      }
    } else {
      rootNodes.push(node);
    }
  });

  console.log('Root Nodes:', rootNodes);
  return rootNodes;
};



// buildOrganizedTreeメソッドを修正
const buildOrganizedTree = () => {
  console.log('ツリーデータ:', treeNodes.value);
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
      name: node.name || 'unnamed',
      level: level,
      node_type: node.node_type || 'unknown',
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


// ノードを追加
const addNode = async () => {
  if (!isAddNodeFormValid.value) return;

  // ツリー情報の再確認
  if (!tree.value || !tree.value.id) {
    errorMessage.value = 'ツリー情報が正しく設定されていません。ページを再読み込みしてください。';
    console.error('Tree information is not set when trying to add node:', tree.value);
    return;
  }

  // 親ノードIDの確認
  if (!newNode.parent_id) {
    errorMessage.value = '親ノードが選択されていません';
    return;
  }

  isAdding.value = true;

  try {
    console.log('Adding node to tree:', tree.value.id);
    console.log('Request data:', {
      parent_id: newNode.parent_id,
      name: newNode.name,
      description: newNode.description,
      node_type: newNode.node_type,
      code_id: newNode.node_type === 'code' ? newNode.code_id : null,
      relationship_type: newNode.relationship_type,
      quantity: newNode.quantity,
      is_master: newNode.is_master
    });

    // code_idが指定されていない場合でもコード形式の名前を使用
    const requestData = {
      parent_id: newNode.parent_id,
      name: newNode.name,
      description: newNode.description,
      node_type: newNode.node_type,
      code_id: newNode.node_type === 'code' ? newNode.code_id : null,
      relationship_type: newNode.relationship_type,
      quantity: newNode.quantity,
      is_master: newNode.is_master
    };

    const response = await axios.post(`${apiBaseUrlTree}/${tree.value.id}/add_node/`, requestData);

    console.log('Add node response:', response.data);

    // addNode 関数内で
    if (response.data.success) {
      // ダイアログを閉じる
      addNodeDialog.value = false;

      // ツリーデータを再取得
      await refreshTree();

      // 成功メッセージ表示
      showSuccess(
        `ノード「${newNode.name}」を追加しました。`,
        { timeout: 3000 }
      );
    }
  } catch (error) {
    console.error('ノード追加エラー:', error);
    // エラーメッセージの表示
    showError(
      error.response?.data?.message || 'ノードの追加中にエラーが発生しました',
      { timeout: 5000 }
    );
  } finally {
    isAdding.value = false;
  }
};

// ノード追加ダイアログを表示（手動入力の場合）
const showAddNodeDialog = () => {
  // ツリー情報が設定されているか確認
  if (!tree.value || !tree.value.id) {
    errorMessage.value = 'ツリー情報が正しく設定されていません。ページを再読み込みしてください。';
    console.error('Tree information is not set when showing add node dialog:', tree.value);
    return;
  }

  // フォームをリセット
  newNode.parent_id = selectedNode.value ? selectedNode.value.id : '';
  newNode.node_type = 'code';
  newNode.name = ''; // 空に設定（Prefixから採番されるべき）
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
    const nodeResponse = await axios.patch(`${apiBaseUrl}/tree-node/${editingNode.id}/`, {
      name: editingNode.name,
      description: editingNode.description,
      code_id: editingNode.node_type === 'code' && editingNode.code_id ? editingNode.code_id : null
    });

    // 構造情報の更新
    const structureResponse = await axios.patch(`${apiBaseUrl}/tree-structure/${editingStructure.id}/`, {
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
    const deletedNodeName = selectedNode.value.name;
    const response = await axios.delete(`${apiBaseUrlTree}structures/${selectedStructure.value.id}/`);

    if (response.data.success) {
      // 削除成功を元に戻し機能付きで表示
      showWithUndo(
        `ノード「${deletedNodeName}」を削除しました`,
        async () => {
          // 元に戻す処理（実際の復元ロジックを実装）
          showInfo('削除を取り消しました');
          await refreshTree();
        }
      );

      deleteNodeDialog.value = false;
      selectedNode.value = null;
      selectedStructure.value = null;
      await refreshTree();
    }
  } catch (error) {
    console.error('ノード削除エラー:', error);
    showError('ノードの削除中にエラーが発生しました');
  } finally {
    isDeleting.value = false;
  }
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

// ===== コンテキストメニューに追加 =====
// 既存のcontextMenuOperationsの定義を以下のように修正

const contextMenuOperations = {
  show: (event, item) => {
    console.log('Context Menu Item:', item);

    menuPosition.value = { x: event.clientX, y: event.clientY };
    isMenuVisible.value = true;

    // 選択したノード情報を記録
    state.selectedNodeInfo = {
      child: item.child,
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

// モーダル操作に新しい関数を追加
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
    // データが null や undefined でないことを確認
    if (data && data.id) {
      // 選択されたノードの下に追加するロジック
      newNode.parent_id = state.selectedNodeInfo.child;
      newNode.name = data.name;
      newNode.code_id = data.id;
      newNode.node_type = 'code';

      // 追加ダイアログを表示
      addNodeDialog.value = true;
    } else {
      console.error("Invalid node data received:", data);
      // ユーザーにエラーを通知するロジックを追加できます
      // 例: errorMessage.value = 'ノードデータが不正です';
    }
  }
};


// Prefixリストからデータを受け取る処理を追加
const handlePrefixData = (data) => {
  console.log("Received prefix data:", data);
  modalOperations.closePrefixList();

  // 選択されたノードがあるか確認
  if (state.selectedNodeInfo.child) {
    // 採番されたコードを使用してノード追加ダイアログを表示
    // Prefixから取得したコードをセット
    newNode.parent_id = state.selectedNodeInfo.child;
    newNode.name = data.code; // 採番されたコード
    newNode.description = data.name; // 入力されたコード名を説明に設定
    newNode.code_id = data.id; // コードIDをセット（あれば）
    newNode.node_type = 'code';

    // 採番済みのコードの場合はcode_id、そうでない場合はnull
    newNode.code_id = data.temp_code ? null : data.id;

    // ダイアログを表示
    addNodeDialog.value = true;
  }
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
// 初期化時にPrefixListLightVersionコンポーネントを確認
const initialize = async () => {
  try {
    // ローディング開始
    isLoading.value = true;
    state.loading = true;

    // URLからツリーIDが指定されているか確認
    const treeId = route.query.id;
    if (!treeId) {
      errorMessage.value = 'ツリーIDが指定されていません。ツリー一覧に戻ってください。';
      console.error('No tree ID specified in the URL');
      return;
    }

    console.log('Initializing with tree ID:', treeId);

    // ツリーデータを取得
    await fetchTreeData();

    // ツリー情報が正常に取得できたか確認
    if (!tree.value || !tree.value.id) {
      errorMessage.value = 'ツリー情報の取得に失敗しました。';
      console.error('Failed to fetch tree information');
      return;
    }

    // 他の初期化処理
    await Promise.all([
      fetchAvailableCodes(),
      fetchAvailableTrees()
    ]);

    console.log('Initialization complete');
    state.isInitialized = true;

  } catch (error) {
    console.error('初期化エラー:', error);
    errorMessage.value = 'システムの初期化に失敗しました: ' + (error.message || '不明なエラー');
  } finally {
    // 必ずローディングを終了
    isLoading.value = false;
    state.loading = false;
  }
};



// コンポーネントのマウント時に初期化
onMounted(async () => {
  try {
    console.log('Component mounted, starting initialization');
    await initialize();

    // グローバルクリックイベントリスナーを追加
    document.addEventListener('click', handleGlobalClick);

    console.log('Initialization complete, tree:', tree.value);
  } catch (error) {
    console.error('Failed to initialize tree editor:', error);
    // エラー時もローディングを終了
    isLoading.value = false;
    state.loading = false;
    errorMessage.value = '初期化中にエラーが発生しました: ' + (error.message || '不明なエラー');
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
          <v-btn variant="outlined" color="primary" class="mb-5" @click="bulkCreateTree" :disabled="true">登録</v-btn>
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
          <!-- Prefixリストを開くオプションを追加 -->
          <li @click="modalOperations.openPrefixList">コード発番</li>
          <li @click="modalOperations.openNodeList">登録済みノード一覧</li>
          <li @click="showAddNodeDialog">新規ノード作成</li>
          <li @click="showAddSharedTreeDialog">
            <v-icon size="small" class="mr-2">mdi-file-tree-outline</v-icon>
            既存ツリー全体を共有
          </li>
          <li @click="showAddPartialTreeDialog">
            <v-icon size="small" class="mr-2">mdi-source-branch</v-icon>
            既存ツリーの一部を共有
          </li>
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
      <!-- ノード追加モーダル -->
      <v-dialog v-model="addNodeDialog" width="500px">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            新規ノード追加
            <v-btn v-if="newNode.name" icon="mdi-refresh" size="small" @click="modalOperations.openPrefixList"
              variant="text" color="primary" class="ml-2">
              <v-tooltip activator="parent" location="bottom">別のコードを発番</v-tooltip>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-form ref="addNodeForm" v-model="isAddNodeFormValid">
              <v-select v-model="newNode.parent_id" label="親ノード*" :items="nodeSelectOptions" item-title="name"
                item-value="id" variant="outlined" density="comfortable" :rules="[v => !!v || '親ノードは必須です']"
                class="mb-3"></v-select>

              <v-select v-model="newNode.node_type" label="ノードタイプ*" :items="nodeTypeOptions" item-title="name"
                item-value="value" variant="outlined" density="comfortable" :rules="[v => !!v || 'ノードタイプは必須です']"
                class="mb-3"></v-select>

              <!-- コード部分 -->
              <v-text-field v-model="newNode.name" label="コード*" variant="outlined" density="comfortable"
                :rules="[v => !!v || 'コードは必須です']" hint="例: AAA-A0001Z000" class="mb-3" :readonly="!!newNode.name"
                append-inner-icon="mdi-barcode-scan" @click:append-inner="modalOperations.openPrefixList">
                <template v-slot:append-inner v-if="!newNode.name">
                  <v-btn icon="mdi-barcode-scan" variant="text" size="small" color="primary"
                    @click.stop="modalOperations.openPrefixList">
                    <v-tooltip activator="parent" location="bottom">コードを発番</v-tooltip>
                  </v-btn>
                </template>
              </v-text-field>

              <v-alert v-if="!newNode.name" type="info" density="compact" variant="outlined" class="mb-3">
                「コード発番」ボタンをクリックして、Prefixからコードを採番できます。
              </v-alert>

              <v-textarea v-model="newNode.description" label="説明" variant="outlined" density="comfortable" rows="3"
                auto-grow hint="この部品の説明を入力してください" class="mb-3"></v-textarea>

              <v-select v-if="newNode.node_type === 'code' && !newNode.name" v-model="newNode.code_id" label="関連コード"
                :items="codeOptions" item-title="display" item-value="id" variant="outlined" density="comfortable"
                class="mb-3" :rules="[v => !!v || '関連コードは必須です']">
                <template v-slot:selection="{ item }">
                  {{ item.raw.display }}
                </template>
                <template v-slot:item="{ item }">
                  <v-list-item :title="item.raw.code" :subtitle="item.raw.name"></v-list-item>
                </template>
              </v-select>

              <v-select v-model="newNode.relationship_type" label="関係タイプ" :items="relationshipTypeOptions"
                item-title="name" item-value="value" variant="outlined" density="comfortable" class="mb-3"></v-select>

              <v-text-field v-model.number="newNode.quantity" label="数量" type="number" min="0.001" step="0.001"
                variant="outlined" density="comfortable" hint="デフォルト: 1.0" class="mb-3"></v-text-field>

              <v-checkbox v-model="newNode.is_master" label="マスター構造として設定" color="primary" hint="他のツリーから共有可能にする場合はチェック"
                hide-details></v-checkbox>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey-darken-1" variant="text" @click="addNodeDialog = false" :disabled="isAdding">
              キャンセル
            </v-btn>
            <v-btn color="primary" @click="addNode" :disabled="!isAddNodeFormValid || isAdding || !newNode.name"
              :loading="isAdding">
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

      <!-- NodeListモーダル 既存ノートからの追加-->
      <RegistedNodeList v-model="state.isModalOpen.nodeList" @data-sent="handleNodeData"
        @modal-close="modalOperations.closeNodeList" />

      <!-- PrefixListモーダル -->
      <v-dialog v-model="state.isModalOpen.prefixList" width="600px">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            コード発番
            <v-btn icon="mdi-close" variant="text" @click="modalOperations.closePrefixList"
              density="comfortable"></v-btn>
          </v-card-title>
          <v-card-text>
            <PrefixListLightVersion @data-sent="handlePrefixData" @close="modalOperations.closePrefixList" />
          </v-card-text>
        </v-card>
      </v-dialog>
    </template>

    <!-- 既存ツリー全構造共有ダイアログ -->
    <!-- テンプレートの最後（スナックバーの前）に追加 -->
    <v-dialog v-model="addSharedTreeDialog" width="600px" persistent>
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span class="text-h6">既存ツリー全構造を共有</span>
          <v-btn icon="mdi-close" variant="text" @click="addSharedTreeDialog = false"
            :disabled="isAddingSharedTree"></v-btn>
        </v-card-title>

        <v-card-text>
          <p class="text-body-2 mb-4 text-medium-emphasis">
            他のツリーの全構造を真の共有として追加します。
            共有元での変更が自動的に反映されます。
          </p>

          <v-form ref="addSharedTreeForm" v-model="isAddSharedTreeFormValid">
            <!-- 共有先の親ノード選択 -->
            <v-select v-model="addSharedTreeData.parent_structure_id" label="共有先の親ノード *" :items="nodeSelectOptions"
              item-title="name" item-value="id" variant="outlined" density="comfortable"
              :rules="[v => !!v || '親ノードは必須です']" hint="このノードの下に共有構造が追加されます" persistent-hint class="mb-4">
            </v-select>

            <!-- 共有元ツリー選択 -->
            <v-select v-model="addSharedTreeData.source_tree_id" label="共有元ツリー *" :items="availableTreesForFullShare"
              item-title="display" item-value="id" variant="outlined" density="comfortable"
              :rules="[v => !!v || '共有元ツリーは必須です']" hint="全構造をコピーする元のツリー" persistent-hint class="mb-4">
              <template v-slot:selection="{ item }">
                <div class="d-flex align-center">
                  <v-icon :color="getStatusColor(item.raw.status)" class="mr-2">
                    mdi-file-tree
                  </v-icon>
                  {{ item.raw.name }}
                </div>
              </template>
              <template v-slot:item="{ item, props }">
                <v-list-item v-bind="props">
                  <template v-slot:prepend>
                    <v-icon :color="getStatusColor(item.raw.status)">
                      mdi-file-tree
                    </v-icon>
                  </template>
                  <v-list-item-title>{{ item.raw.name }}</v-list-item-title>
                  <v-list-item-subtitle>
                    ステータス: {{ getStatusLabel(item.raw.status) }}
                  </v-list-item-subtitle>
                </v-list-item>
              </template>
            </v-select>

            <!-- 共有オプション -->
            <v-row>
              <v-col cols="12" md="6">
                <v-select v-model="addSharedTreeData.relationship_type" label="関係タイプ" :items="relationshipTypeOptions"
                  item-title="name" item-value="value" variant="outlined" density="comfortable" class="mb-3">
                </v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model.number="addSharedTreeData.quantity" label="数量" type="number" min="0.001"
                  step="0.001" variant="outlined" density="comfortable" class="mb-3">
                </v-text-field>
              </v-col>
            </v-row>

            <!-- チェックボックスオプション -->
            <div class="mb-4">
              <v-checkbox v-model="addSharedTreeData.include_root" label="ルートノードも含める" color="primary"
                hint="共有元ツリーのルートノードも一緒に共有します" hide-details="auto">
              </v-checkbox>
            </div>

            <!-- 真の共有についての説明 -->
            <v-alert type="info" variant="outlined" density="compact" class="mb-4">
              <template v-slot:title>
                <div class="d-flex align-center">
                  <v-icon class="mr-2">mdi-information</v-icon>
                  真の共有について
                </div>
              </template>
              <div class="text-body-2">
                <p class="mb-2">
                  • 同じノードオブジェクトを複数のツリーで共有参照します
                </p>
                <p class="mb-2">
                  • 共有元での変更（名前、説明等）が自動的に全ての共有先に反映されます
                </p>
                <p class="mb-0">
                  • データの整合性が自動的に保たれます
                </p>
              </div>
            </v-alert>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="addSharedTreeDialog = false"
            :disabled="isAddingSharedTree">
            キャンセル
          </v-btn>
          <v-btn color="primary" @click="addSharedTreeStructure"
            :disabled="!isAddSharedTreeFormValid || isAddingSharedTree" :loading="isAddingSharedTree">
            <v-icon class="mr-2">mdi-share-variant</v-icon>
            全構造を共有
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


    <!-- 特定ノード部分共有ダイアログ -->
    <v-dialog v-model="addPartialTreeDialog" width="700px" persistent>
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span class="text-h6">既存ツリーの一部を共有</span>
          <v-btn icon="mdi-close" variant="text" @click="addPartialTreeDialog = false"
            :disabled="isAddingPartialTree"></v-btn>
        </v-card-title>

        <v-card-text>
          <p class="text-body-2 mb-4 text-medium-emphasis">
            他のツリーから特定のノード部分（例：NODE2以下）を真の共有として追加します。
            共有元での変更が自動的に反映されます。
          </p>

          <v-form ref="addPartialTreeForm" v-model="isAddPartialTreeFormValid">
            <!-- 共有先の親ノード選択 -->
            <v-select v-model="addPartialTreeData.parent_structure_id" label="共有先の親ノード *" :items="nodeSelectOptions"
              item-title="name" item-value="id" variant="outlined" density="comfortable"
              :rules="[v => !!v || '親ノードは必須です']" hint="このノードの下に共有構造が追加されます" persistent-hint class="mb-4">
            </v-select>

            <!-- 共有元ツリー選択 -->
            <v-select v-model="addPartialTreeData.source_tree_id" label="共有元ツリー *"
              :items="availableTreesForPartialShare" item-title="display" item-value="id" variant="outlined"
              density="comfortable" :rules="[v => !!v || '共有元ツリーは必須です']" hint="構造をコピーする元のツリー" persistent-hint
              class="mb-4">
              <template v-slot:selection="{ item }">
                <div class="d-flex align-center">
                  <v-icon :color="getStatusColor(item.raw.status)" class="mr-2">
                    mdi-file-tree
                  </v-icon>
                  {{ item.raw.name }}
                </div>
              </template>
              <template v-slot:item="{ item, props }">
                <v-list-item v-bind="props">
                  <template v-slot:prepend>
                    <v-icon :color="getStatusColor(item.raw.status)">
                      mdi-file-tree
                    </v-icon>
                  </template>
                  <v-list-item-title>{{ item.raw.name }}</v-list-item-title>
                  <v-list-item-subtitle>
                    ステータス: {{ getStatusLabel(item.raw.status) }}
                  </v-list-item-subtitle>
                </v-list-item>
              </template>
            </v-select>

            <!-- 共有元構造選択 -->
            <v-select v-model="addPartialTreeData.source_structure_id" label="共有したいノード *"
              :items="availableStructuresForPartialShare" item-title="display" item-value="id" variant="outlined"
              density="comfortable" :rules="[v => !!v || '共有元ノードは必須です']" :loading="loadingPartialStructures"
              :disabled="!addPartialTreeData.source_tree_id" hint="このノード以下が共有されます（例：NODE2を選択するとNODE2とNODE3が共有される）"
              persistent-hint class="mb-4">
              <template v-slot:selection="{ item }">
                <div class="d-flex align-center">
                  <v-icon color="primary" class="mr-2">mdi-source-branch</v-icon>
                  {{ item.raw.node_name }}
                </div>
              </template>
              <template v-slot:item="{ item, props }">
                <v-list-item v-bind="props">
                  <template v-slot:prepend>
                    <v-icon color="primary">mdi-source-branch</v-icon>
                  </template>
                  <v-list-item-title>{{ item.raw.node_name }}</v-list-item-title>
                  <v-list-item-subtitle>
                    Level: {{ item.raw.level }} | Path: {{ item.raw.path }}
                  </v-list-item-subtitle>
                </v-list-item>
              </template>
            </v-select>

            <!-- 共有オプション -->
            <v-row>
              <v-col cols="12" md="6">
                <v-select v-model="addPartialTreeData.relationship_type" label="関係タイプ" :items="relationshipTypeOptions"
                  item-title="name" item-value="value" variant="outlined" density="comfortable" class="mb-3">
                </v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field v-model.number="addPartialTreeData.quantity" label="数量" type="number" min="0.001"
                  step="0.001" variant="outlined" density="comfortable" class="mb-3">
                </v-text-field>
              </v-col>
            </v-row>

            <!-- チェックボックスオプション -->
            <div class="mb-4">
              <v-checkbox v-model="addPartialTreeData.include_children" label="子ノードも含める" color="primary"
                hint="選択したノードの子ノードも一緒に共有します" hide-details="auto">
              </v-checkbox>
            </div>

            <!-- 使用例の説明 -->
            <v-alert type="success" variant="outlined" density="compact" class="mb-4">
              <template v-slot:title>
                <div class="d-flex align-center">
                  <v-icon class="mr-2">mdi-lightbulb-outline</v-icon>
                  使用例
                </div>
              </template>
              <div class="text-body-2">
                <p class="mb-2">
                  <strong>TREE A:</strong> NODE1 → NODE2 → NODE3
                </p>
                <p class="mb-2">
                  <strong>共有したい部分:</strong> NODE2以下（NODE2とNODE3）
                </p>
                <p class="mb-0">
                  <strong>結果:</strong> TREE BにNODE2とNODE3が真の共有として追加されます
                </p>
              </div>
            </v-alert>

            <!-- 真の共有についての説明 -->
            <v-alert type="info" variant="outlined" density="compact" class="mb-4">
              <template v-slot:title>
                <div class="d-flex align-center">
                  <v-icon class="mr-2">mdi-information</v-icon>
                  真の共有について
                </div>
              </template>
              <div class="text-body-2">
                <p class="mb-2">
                  • 同じノードオブジェクトを複数のツリーで共有参照します
                </p>
                <p class="mb-2">
                  • 共有元での変更（名前、説明等）が自動的に全ての共有先に反映されます
                </p>
                <p class="mb-0">
                  • データの整合性が自動的に保たれます
                </p>
              </div>
            </v-alert>
          </v-form>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="addPartialTreeDialog = false"
            :disabled="isAddingPartialTree">
            キャンセル
          </v-btn>
          <v-btn color="primary" @click="addPartialTreeStructure"
            :disabled="!isAddPartialTreeFormValid || isAddingPartialTree" :loading="isAddingPartialTree">
            <v-icon class="mr-2">mdi-share-variant</v-icon>
            部分構造を共有
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


    <!-- スナックバーコンポーネント（既存のものを置き換え） -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout"
      :multi-line="snackbar.multiline" :vertical="snackbar.vertical" location="bottom">
      {{ snackbar.text }}

      <!-- アクションボタンがある場合 -->
      <template v-slot:actions v-if="snackbar.actions && snackbar.actions.length > 0">
        <v-btn v-for="(action, index) in snackbar.actions" :key="index" :color="action.color || 'white'" variant="text"
          @click="action.handler">
          {{ action.text }}
        </v-btn>
        <v-btn icon="mdi-close" variant="text" @click="snackbar.show = false"></v-btn>
      </template>

      <!-- 通常の閉じるボタン -->
      <template v-slot:actions v-else>
        <v-btn icon="mdi-close" variant="text" @click="snackbar.show = false"></v-btn>
      </template>
    </v-snackbar>


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

/* コード入力フィールド用のスタイル */
.code-input {
  font-family: 'Roboto Mono', monospace;
  letter-spacing: 0.5px;
}

.code-input.readonly {
  background-color: #f5f5f5;
  color: #1976d2;
  font-weight: 500;
}

/* プレフィックス選択モーダル用のスタイル追加 */
.prefix-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.prefix-item {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.prefix-item:hover {
  background-color: #f5f5f5;
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.prefix-item.selected {
  border-color: #1976d2;
  background-color: #e3f2fd;
}

.prefix-item .prefix-name {
  font-weight: 500;
}

.prefix-item .prefix-type {
  font-size: 12px;
  color: #666;
}

/* 発番されたコード表示用のスタイル */
.generated-code-display {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
  text-align: center;
  font-family: 'Roboto Mono', monospace;
}

.generated-code-display .code {
  font-size: 18px;
  font-weight: 500;
  color: #1976d2;
  letter-spacing: 1px;
}

.generated-code-display .hint {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

/* モーダルアクションボタンの配置 */
.modal-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

/* コンテキストメニューの改善 */
.context-menu li .icon {
  margin-right: 8px;
}

.context-menu li.prefix-option {
  color: #1976d2;
}
</style>