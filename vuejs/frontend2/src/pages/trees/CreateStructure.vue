<script setup>
import { getTree } from '@/api/tree';
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import NodeListLightVersion from '../nodes/NodeListLightVersion.vue';


const router = useRoute();
const errorMessage = ref('');
const id = ref('');//treeのID
const name = ref('');//treeのName
const receiveData = ref({ id: '', name: '' });
const treeStructure = ref([
  {
    id: '',//フロントエンド独自
    name: '',//フロントエンド独自
    parent: '',//親NodeID
    child: '',//子NodeID
    tree: '',//TreeID     基本的に変数idが入る
    level: ''//階層Level
  }
])


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
const isModalOpen = ref(false);



// メニューを表示する
const showContextMenu = (event) => {
  // マウスの位置を取得
  menuPosition.value = {
    top: event.clientY + 'px',
    left: event.clientX + 'px'
  }
  isShowMenu.value = true

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
  console.log('openRegistedNodeListViewがクリックされました')
  isModalOpen.value = true; // モーダルを表示
  closeMenu()
}

const menuAction2 = () => {
  console.log('メニュー2がクリックされました')
  closeMenu()
}

const menuAction3 = () => {
  console.log('メニュー3がクリックされました')
  closeMenu()
}


const fetchTrees = async (id) => {
  try {
    const response = await getTree(id);
    name.value = response.data.name;

    //配列初期化
    treeStructure.value = [];
    treeStructure.value.push({
      id: id,
      name: name.value
    });
  } catch (error) {
    console.error("Error fetching tree data:", error);
    errorMessage.value = 'Failed to load tree data. Please try again later.';
  }
};

/**
 * 子コンポーネントからデータを受け取る
 * @param {Object} node 
 */
const handleNode = (node) => {
  // 受け取ったデータを格納 → watchによってcreatStructureへ追加される
  receiveData.value = node;

  // モーダルを閉じる
  isModalOpen.value = false;
  // メニューを閉じる
  isShowMenu.value = false;
}

/**
 * 変数に変化が合った場合のイベントを定義
 */
watch(receiveData, (newValue, oldValue) => {
  treeStructure.value.push({
    id: receiveData.value.id,
    name: receiveData.value.name
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
});
</script>

<template>
  <v-container>
    <!--エラーの場合-->
    <p v-if="errorMessage">{{ errorMessage }}</p>

    <!--正常な場合-->
    <p v-for="item in treeStructure" :key="item.id" @contextmenu.prevent="showContextMenu">
      {{ item.id }} - {{ item.name }}
    </p>

    <!-- コンテキストメニュー(右クリックメニュー) -->
    <div v-if="isShowMenu" :style="menuPosition" class="context-menu">
      <ul>
        <li @click="openRegistedNodeListView">登録済みノード一覧</li>
        <li @click="menuAction2">メニュー2</li>
        <li @click="menuAction3">メニュー3</li>
      </ul>
    </div>

    <!-- モーダル -->
    <v-dialog v-model="isModalOpen" width="auto">
      <v-card>
        <v-card-title>
          Node List
          <v-btn icon="mdi-close" @click="isModalOpen = false" class="float-right"></v-btn>
        </v-card-title>
        <v-card-text>
          <!-- ノード一覧 -->
          <!-- @data-sentが子コンポーネントから発火されるとhandleNodeイベントが発火する -->
          <NodeListLightVersion @data-sent="handleNode" />
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
</style>