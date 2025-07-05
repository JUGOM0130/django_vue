<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useTheme } from 'vuetify';

/**
 * ContextMenu コンポーネント
 * 
 * Props:
 * - isVisible: メニューの表示状態
 * - position: メニューの表示位置 {x, y}
 * - menuItems: メニューアイテムの配列
 * - theme: テーマ ('default', 'rounded', 'minimal')
 * - compact: コンパクト表示
 * - ariaLabel: アクセシビリティ用ラベル
 * - emptyText: 空の状態のテキスト
 * - zIndex: z-index値
 * 
 * Events:
 * - item-click: メニューアイテムクリック時
 * - menu-show: メニュー表示時
 * - menu-hide: メニュー非表示時
 * - position-adjusted: 位置調整時
 */

const props = defineProps({
    isVisible: {
        type: Boolean,
        default: false
    },
    position: {
        type: Object,
        default: () => ({ x: 0, y: 0 })
    },
    menuItems: {
        type: Array,
        default: () => []
    },
    theme: {
        type: String,
        default: 'default', // 'default', 'rounded', 'minimal'
        validator: (value) => ['default', 'rounded', 'minimal'].includes(value)
    },
    compact: {
        type: Boolean,
        default: false
    },
    ariaLabel: {
        type: String,
        default: 'コンテキストメニュー'
    },
    emptyText: {
        type: String,
        default: 'メニューアイテムがありません'
    },
    zIndex: {
        type: Number,
        default: 1000
    }
});

const emit = defineEmits([
    'item-click',
    'menu-show',
    'menu-hide',
    'position-adjusted'
]);

// テンプレート参照
const contextMenuRef = ref(null);

// 内部状態
const focusedIndex = ref(-1);

// Vuetifyテーマ
const theme = useTheme();
const isDark = computed(() => theme.global.current.value.dark);

// メニューのスタイル計算
const menuStyle = computed(() => ({
    position: 'fixed',
    left: `${props.position.x}px`,
    top: `${props.position.y}px`,
    zIndex: props.zIndex
}));

// アイコンを持つアイテムが存在するかチェック
const hasAnyIcon = computed(() => {
    return props.menuItems.some(item => item.icon);
});

/**
 * アイコンの色を取得
 * @param {Object} item - メニューアイテム
 * @returns {string} アイコンの色
 */
const getIconColor = (item) => {
    if (item.disabled) {
        return 'grey-lighten-1';
    }
    if (item.danger) {
        return 'error';
    }
    return 'default';
};

/**
 * メニューアイテムクリック時の処理
 * @param {Object} item - クリックされたメニューアイテム
 */
const handleItemClick = (item) => {
    if (item.disabled) return;

    emit('item-click', item);
};

/**
 * メニューアイテムホバー時の処理
 * @param {number} index - ホバーされたアイテムのインデックス
 */
const handleItemHover = (index) => {
    const item = props.menuItems[index];
    if (!item.disabled) {
        focusedIndex.value = index;
    }
};

/**
 * メニューアイテムホバー終了時の処理
 * @param {number} index - ホバーが終了したアイテムのインデックス
 */
const handleItemLeave = (index) => {
    if (focusedIndex.value === index) {
        focusedIndex.value = -1;
    }
};

/**
 * キーボードナビゲーション
 * @param {KeyboardEvent} event - キーボードイベント
 */
const handleKeydown = (event) => {
    if (!props.isVisible) return;

    const visibleItems = props.menuItems.filter(item =>
        item.type !== 'separator' && !item.disabled
    );

    switch (event.key) {
        case 'ArrowDown':
            event.preventDefault();
            if (focusedIndex.value < visibleItems.length - 1) {
                focusedIndex.value++;
            } else {
                focusedIndex.value = 0;
            }
            break;

        case 'ArrowUp':
            event.preventDefault();
            if (focusedIndex.value > 0) {
                focusedIndex.value--;
            } else {
                focusedIndex.value = visibleItems.length - 1;
            }
            break;

        case 'Enter':
        case ' ':
            event.preventDefault();
            if (focusedIndex.value >= 0) {
                const item = visibleItems[focusedIndex.value];
                handleItemClick(item);
            }
            break;

        case 'Escape':
            event.preventDefault();
            emit('menu-hide');
            break;
    }
};

/**
 * メニュー表示時のアニメーション開始
 * @param {HTMLElement} el - DOM要素
 */
const onEnter = (el) => {
    // 初期状態を設定
    el.style.opacity = '0';
    el.style.transform = 'scale(0.95) translateY(-10px)';
    el.style.transformOrigin = 'top left';
};

/**
 * メニュー表示アニメーション完了時
 * @param {HTMLElement} el - DOM要素
 */
const onAfterEnter = async (el) => {
    // 位置の再調整
    await nextTick();
    adjustPosition();

    emit('menu-show');
};

/**
 * メニュー非表示時のアニメーション
 * @param {HTMLElement} el - DOM要素
 */
const onLeave = (el) => {
    el.style.opacity = '0';
    el.style.transform = 'scale(0.95) translateY(-10px)';

    emit('menu-hide');
};

/**
 * メニュー位置の調整
 */
const adjustPosition = () => {
    if (!contextMenuRef.value) return;

    const rect = contextMenuRef.value.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const minDistance = 10;

    let { x, y } = props.position;
    let adjusted = false;

    // 右端チェック
    if (x + rect.width > viewportWidth - minDistance) {
        x = viewportWidth - rect.width - minDistance;
        adjusted = true;
    }

    // 下端チェック
    if (y + rect.height > viewportHeight - minDistance) {
        y = viewportHeight - rect.height - minDistance;
        adjusted = true;
    }

    // 左端・上端チェック
    if (x < minDistance) {
        x = minDistance;
        adjusted = true;
    }
    if (y < minDistance) {
        y = minDistance;
        adjusted = true;
    }

    if (adjusted) {
        emit('position-adjusted', { x, y });
    }
};

// ウォッチャー
watch(() => props.isVisible, (newVal) => {
    if (newVal) {
        focusedIndex.value = -1;
        nextTick(() => {
            // フォーカスをメニューに設定
            if (contextMenuRef.value) {
                contextMenuRef.value.focus();
            }
        });
    }
});

// ライフサイクル
onMounted(() => {
    document.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
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
</template>


<style scoped>
.context-menu {
    min-width: 180px;
    max-width: 300px;
    background: rgb(var(--v-theme-surface));
    border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
    border-radius: 6px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.08);
    padding: 4px 0;
    font-size: 14px;
    line-height: 1.4;
    overflow: hidden;
    user-select: none;
    outline: none;
}

/* テーマバリエーション */
.context-menu--rounded {
    border-radius: 12px;
}

.context-menu--minimal {
    border: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.context-menu--compact {
    min-width: 150px;
    font-size: 13px;
}

.context-menu--dark {
    background: rgb(var(--v-theme-surface-dark));
    border-color: rgba(255, 255, 255, 0.12);
}

/* メニューアイテム */
.context-menu__item {
    display: flex;
    align-items: center;
    padding: 8px 12px;
    cursor: pointer;
    transition: background-color 0.2s ease;
    position: relative;
}

.context-menu__item:hover:not(.context-menu__item--disabled) {
    background: rgba(var(--v-theme-primary), 0.08);
}

.context-menu__item--focused {
    background: rgba(var(--v-theme-primary), 0.12);
}

.context-menu__item--disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.context-menu__item--danger {
    color: rgb(var(--v-theme-error));
}

.context-menu__item--danger:hover:not(.context-menu__item--disabled) {
    background: rgba(var(--v-theme-error), 0.08);
}

.context-menu__item--compact {
    padding: 6px 12px;
}

/* アイコン */
.context-menu__item-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 8px;
    flex-shrink: 0;
}

/* ラベル */
.context-menu__item-label {
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ショートカット */
.context-menu__item-shortcut {
    margin-left: 16px;
    font-size: 12px;
    opacity: 0.7;
    flex-shrink: 0;
}

/* サブメニュー矢印 */
.context-menu__item-arrow {
    margin-left: 8px;
    flex-shrink: 0;
}

/* 区切り線 */
.context-menu__separator {
    height: 1px;
    background: rgba(var(--v-border-color), var(--v-border-opacity));
    margin: 4px 0;
}

/* 空の状態 */
.context-menu__empty {
    padding: 16px 12px;
    text-align: center;
    color: rgba(var(--v-theme-on-surface), 0.6);
    font-size: 13px;
}

/* アニメーション */
.context-menu-enter-active {
    transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.context-menu-leave-active {
    transition: all 0.1s cubic-bezier(0.4, 0, 1, 1);
}

.context-menu-enter-from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
}

.context-menu-leave-to {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
}

/* コンパクトモード */
.context-menu--compact .context-menu__item {
    padding: 6px 12px;
}

.context-menu--compact .context-menu__item-icon {
    width: 16px;
    height: 16px;
    margin-right: 6px;
}

.context-menu--compact .context-menu__item-shortcut {
    margin-left: 12px;
    font-size: 11px;
}

/* ダークモード対応 */
.context-menu--dark .context-menu__separator {
    background: rgba(255, 255, 255, 0.12);
}

.context-menu--dark .context-menu__empty {
    color: rgba(255, 255, 255, 0.6);
}

/* フォーカス時のアウトライン */
.context-menu:focus-visible {
    outline: 2px solid rgb(var(--v-theme-primary));
    outline-offset: -2px;
}

/* レスポンシブ対応 */
@media (max-width: 600px) {
    .context-menu {
        min-width: 160px;
        font-size: 13px;
    }

    .context-menu__item {
        padding: 10px 12px;
    }
}
</style>