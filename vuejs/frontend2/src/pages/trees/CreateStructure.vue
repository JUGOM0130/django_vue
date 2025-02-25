<script setup>
import { getTree } from '@/api/tree';
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';



const router = useRoute();
const errorMessage = ref('');
const id = ref('');
const name = ref('');

/**
 * 右クリック 状態の定義
 */
const isShowMenu = ref(false)
const menuPosition = ref({
  top: '0px',
  left: '0px'
})

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
const menuAction1 = () => {
  console.log('メニュー1がクリックされました')
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
  } catch (error) {
    console.error("Error fetching tree data:", error);
    errorMessage.value = 'Failed to load tree data. Please try again later.';
  }
};

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
    <p v-else @contextmenu.prevent="showContextMenu">
      {{ id }} - {{ name }}
    </p>

    <!-- コンテキストメニュー(右クリックメニュー) -->
    <div v-if="isShowMenu" :style="menuPosition" class="context-menu">
      <ul>
        <li @click="menuAction1">メニュー1</li>
        <li @click="menuAction2">メニュー2</li>
        <li @click="menuAction3">メニュー3</li>
      </ul>
    </div>
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
</style>