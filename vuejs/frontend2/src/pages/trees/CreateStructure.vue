<script setup>
import { getTreeStructure } from '@/api/tree';
import { generateCode } from '@/api/common';
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
import NodeListLightVersion from '../nodes/NodeListLightVersion.vue';
import PrefixListLightVersion from '../prefix/PrefixListLightVersion.vue'

const router = useRoute();
const errorMessage = ref('');
const id = ref('');//RootTreeのID
const name = ref('');//RootTreeのName
const receiveData = ref({ id: '', name: '' });
const treeStructure = ref([
  {
    id: '',      // ノードID
    name: '',    // ノード名
    parent: '',  // 親ノードID
    child: '',   // 子ノードID（単一）
    tree: '',    // TreeID
    level: 1     // 階層Level
  }
]);
/**
 * 右クリック 状態の定義
 */
const isShowMenu = ref(false)
const menuPosition = ref({
  top: '0px',
  left: '0px'
})
/**
 *  モーダルの表示制御用
 */
const isModalOpen_nodeList = ref(false);
const isModalOpen_prefixList = ref(false);
/**
 * 右クリックされた要素を保存するための変数を追加
 */
const selectedItem = ref(null);
// TreeStructureの関係を保持するための配列
const relationships = ref([]);








// メニューを表示する
const showContextMenu = (event, item) => {
  // マウスの位置を取得
  menuPosition.value = {
    top: event.clientY + 'px',
    left: event.clientX + 'px'
  }
  // メニュー表示フラグ
  isShowMenu.value = true
  // 右クリックされた要素を保存
  selectedItem.value = item;

  console.log(item)
  // メニュー以外をクリックした時にメニューを閉じる
  document.addEventListener('click', closeMenu)
}

// メニューを閉じる
const closeMenu = () => {
  isShowMenu.value = false
  document.removeEventListener('click', closeMenu)
}

// メニューアクション
const openRegistedNodeListView = () => {
  isModalOpen_nodeList.value = true; // モーダルを表示
  closeMenu()
}

const openPrefixListView = () => {
  isModalOpen_prefixList.value = true;
  closeMenu()
}

const menuAction3 = () => {
  console.log('メニュー3がクリックされました')
  closeMenu()
}

const log = () => {
  console.log(treeStructure.value);
}




const fetchTrees = async (treeId) => {
  try {
    const response = await getTreeStructure(treeId);
    const data = response.data;
    name.value = data.name;

    // 配列初期化
    treeStructure.value = [];
    relationships.value = [];

    // ルートノードの追加
    treeStructure.value.push({
      id: data.id,
      name: data.name,
      parent: '', // ルートノードは親を持たない
      child: '',  // 子ノードIDは後で設定
      tree: treeId,
      level: 1
    });

    // リレーションシップの構築
    if (data.relationships) {
      data.relationships.forEach(rel => {
        const relationship = {
          parentId: rel.parent,
          childId: rel.child,
          level: rel.level,
          treeId: treeId
        };
        relationships.value.push(relationship);

        // 既存のノードの子ノードIDを更新
        const parentNode = treeStructure.value.find(node => node.id === rel.parent);
        if (parentNode) {
          parentNode.child = rel.child;
        }

        // 子ノードを追加
        treeStructure.value.push({
          id: rel.child,
          name: rel.child_name, // APIからの応答に含まれる想定
          parent: rel.parent,
          child: '',
          tree: treeId,
          level: rel.level
        });
      });
    }

  } catch (error) {
    console.error("Error fetching tree data:", error);
    errorMessage.value = 'Failed to load tree data. Please try again later.';
  }
};




/**
 * ツリーに新しいノードを追加する
 * @param {string} id - 新しいノードのID
 * @param {string} name - 新しいノードの名前
 */
const addNodeToTree = (id, name) => {
  if (selectedItem.value) {
    // 新しいノードのデータを作成
    const newNode = {
      id: id,
      name: name,
      parent: selectedItem.value.id,
      child: '',
      tree: id.value,
      level: Number(selectedItem.value.level) + 1
    };

    // 親ノードのインデックスを取得
    const parentIndex = treeStructure.value.findIndex(
      n => n.id === selectedItem.value.id
    );

    if (parentIndex !== -1) {
      // 親ノードを更新
      treeStructure.value[parentIndex] = {
        ...treeStructure.value[parentIndex],
        child: id
      };

      // 新しい配列を構築
      const newStructure = [];

      // 現在の配列をイテレートして新しい構造を作成
      treeStructure.value.forEach((item, index) => {
        // 親ノードまでは通常通り追加
        if (index <= parentIndex) {
          newStructure.push(item);
        }
        // 親ノードの直後に新しいノードを追加
        if (index === parentIndex) {
          newStructure.push(newNode);
        }
        // 親ノード以降の既存のノードを追加
        if (index > parentIndex) {
          newStructure.push(item);
        }
      });

      treeStructure.value = newStructure;
    }
  }

  isModalOpen_nodeList.value = false;
  isModalOpen_prefixList.value = false;
  isShowMenu.value = false;
};

/**
 * ノードをツリーに追加する
 * @param {Object} node - 追加するノードのデータ
 * @param {string} node.id - ノードのID
 * @param {string} node.name - ノードの名前
 */
const handleNode = (node) => {
  addNodeToTree(node.id, node.name);
};

/**
 * プレフィックスをツリーに追加する
 * @param {Object} prefix - 追加するプレフィックスのデータ
 * @param {string} prefix.id - プレフィックスのID
 * @param {string} prefix.name - プレフィックスの名前
 */
const handlePrefix = async(prefix) => {
  const result = await generateCode(prefix.id)
  const data = result.data

  addNodeToTree(data.id, data.code);

};



// 指定されたノードの子ノードとその子孫を取得する関数
const getChildrenAndDescendants = (parentId) => {
  const result = [];
  const children = treeStructure.value.filter(n => n.parent === parentId);

  children.forEach(child => {
    result.push(child);
    const descendants = getChildrenAndDescendants(child.id);
    result.push(...descendants);
  });

  return result;
};

// ツリー表示のための計算プロパティ
const organizedTree = computed(() => {
  return treeStructure.value;
});





/**
 * 変数に変化が合った場合のイベントを定義
 */
watch(receiveData, (newValue, oldValue) => {
  treeStructure.value.push({
    id: receiveData.value.id,
    name: receiveData.value.name,
    parent: selectedItem.value.id,
    child: "",
    tree: id.value,
    level: Number(selectedItem.value.level) + 1,
  });
})

/**
 * コンポーネントの初期化
 */
onMounted(async () => {
  id.value = router.query.id;
  if (id.value) {
    await fetchTrees(id.value);
  } else {
    errorMessage.value = 'Tree ID is missing.';
  }

});

/**
 *  コンポーネントのクリーンアップ
 */
onUnmounted(() => {
  document.removeEventListener('click', closeMenu)
  console.log(treeStructure.value)
});
</script>

<template>
  <v-container>

    <!--エラーの場合-->
    <p v-if="errorMessage">{{ errorMessage }}</p>

    <div class="tree-view">
      <div v-for="(item, index) in organizedTree" :key="item.id" :style="{
        marginLeft: `${(item.level - 1) * 20}px`,
        borderLeft: item.level > 1 ? '1px solid #ddd' : 'none'
      }" class="tree-node" @contextmenu.prevent="(event) => showContextMenu(event, item)">
        <div class="node-content">
          <v-icon :color="item.child ? 'orange' : 'green'">
            {{ item.child ? 'mdi-folder' : 'mdi-file' }}
          </v-icon>
          <span class="node-name">{{ item.name }}</span>
          <span class="node-level">(Level: {{ item.level }})</span>
        </div>
      </div>
    </div>

    <!--登録するデータを視覚化-->
    <v-data-table :items="treeStructure" density="compact" v-if="false"></v-data-table>


    <!-- コンテキストメニュー(右クリックメニュー) -->
    <div v-if="isShowMenu" :style="menuPosition" class="context-menu">
      <ul>
        <li @click="openPrefixListView">コード発番</li>
        <li @click="openRegistedNodeListView">登録済みノード一覧</li>
      </ul>
    </div>

    <!-- モーダル NodeList -->
    <v-dialog v-model="isModalOpen_nodeList" width="auto">
      <v-card>
        <v-card-title>
          Node List
          <v-btn icon="mdi-close" @click="isModalOpen_nodeList = false" class="float-right"></v-btn>
        </v-card-title>
        <v-card-text>
          <!-- ノード一覧 -->
          <!-- @data-sentが子コンポーネントから発火されるとhandleNodeイベントが発火する -->
          <NodeListLightVersion @data-sent="handleNode" />
        </v-card-text>
      </v-card>
    </v-dialog>

  <!-- モーダル PrefixList -->
  <v-dialog v-model="isModalOpen_prefixList" width="auto">
    <v-card>
      <v-card-title>
        Prefix List
        <v-btn 
          icon="mdi-close" 
          @click="isModalOpen_prefixList = false" 
          class="float-right"
        ></v-btn>
      </v-card-title>
      <v-card-text>
        <!-- プレフィックス一覧 -->
        <!-- @data-sentが子コンポーネントから発火されるとhandlePrefixイベントが発火する -->
        <PrefixListLightVersion @data-sent="handlePrefix" />
      </v-card-text>
    </v-card>
  </v-dialog>

  </v-container>
</template>

<style scoped>
.right-click-area {
  width: 300px;
  height: 200px;
  background-color: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px;
}

.context-menu {
  position: fixed;
  background: white;
  border: 1px solid #ccc;
  box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
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

.float-right {
  float: right;
}

.tree-view {
  padding: 20px;
}

.tree-node {
  display: flex;
  align-items: center;
  padding: 8px;
  margin: 4px 0;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.tree-node:hover {
  background-color: #f5f5f5;
}

.node-name {
  margin-left: 8px;
}
</style>