// composables/useTreeState.js
import { reactive, readonly } from 'vue'

// 初期状態の定義
const initialState = {
  treeId: null,
  menu: {
    isShow: false,
    position: {
      top: '0px',
      left: '0px'
    }
  },
  isModalOpen: {
    nodeList: false,
    prefixList: false
  },
  selectedNodeInfo: {
    parent: null,
    child: null,
    level: null
  },
  isLoading: false,
  errorMessage: '',
  isTest: false,
  isInitialized: false
}

// リアクティブな状態の作成
const state = reactive({ ...initialState })

// アクションの定義
const actions = {
  // 一般的な状態更新
  updateState(updates) {
    Object.assign(state, updates)
  },

  // ツリーID更新
  setTreeId(id) {
    state.treeId = id
  },

  // エラーメッセージ更新
  setErrorMessage(message) {
    state.errorMessage = message
  },

  // モーダル状態更新
  setModalState(modalName, isOpen) {
    state.isModalOpen[modalName] = isOpen
  },

  // メニュー状態更新
  setMenuState(isShow, position = null) {
    state.menu.isShow = isShow
    if (position) {
      state.menu.position = position
    }
  },

  // 選択されたノード情報更新
  setSelectedNodeInfo(nodeInfo) {
    state.selectedNodeInfo = {
      parent: nodeInfo.parent ?? null,
      child: nodeInfo.child ?? null,
      level: nodeInfo.level ?? null
    }
  },

  // 読み込み状態更新
  setLoading(isLoading) {
    state.isLoading = isLoading
  },

  // 状態のリセット
  resetState() {
    Object.assign(state, initialState)
  }
}

export const useTreeState = () => {
  return {
    state: readonly(state),
    actions
  }
}

// デバッグ用のstate監視（開発環境のみ）
if (process.env.NODE_ENV === 'development') {
  const watchState = () => {
    console.log('State updated:', JSON.parse(JSON.stringify(state)))
  }
  watchState()
}