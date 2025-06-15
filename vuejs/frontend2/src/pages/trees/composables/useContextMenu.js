// composables/ui/useContextMenu.js

import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue';

/**
 * コンテキストメニュー管理用Composable
 * 
 * 機能:
 * - 右クリックメニューの表示/非表示制御
 * - メニュー位置の自動調整（画面端での位置補正）
 * - キーボードショートカット対応
 * - 複数メニューの管理
 * - アクセシビリティ対応
 * 
 * 使用例:
 * const { showContextMenu, hideContextMenu, isVisible, position, selectedItem } = useContextMenu();
 * 
 * // 右クリック時
 * const handleRightClick = (event, item) => {
 *   showContextMenu(event, item, menuItems);
 * };
 */
export function useContextMenu() {
    // コンテキストメニューの基本状態
    const contextMenuState = reactive({
        isVisible: false,
        position: { x: 0, y: 0 },
        selectedItem: null,
        menuItems: [],
        zIndex: 1000,
        activeMenuId: null
    });

    // メニューの設定
    const menuConfig = reactive({
        offsetX: 2,        // マウス位置からのオフセット
        offsetY: 2,
        minDistanceFromEdge: 10,  // 画面端からの最小距離
        closeOnScroll: true,      // スクロール時に閉じる
        closeOnResize: true,      // リサイズ時に閉じる
        closeOnEscape: true,      // ESCキーで閉じる
        preventDefaultContextMenu: true  // デフォルトのコンテキストメニューを無効化
    });

    // イベントリスナーの参照
    const eventListeners = {
        globalClick: null,
        keydown: null,
        scroll: null,
        resize: null
    };

    /**
     * コンテキストメニューを表示
     * @param {Event} event - マウスイベント
     * @param {Object} item - 選択されたアイテム
     * @param {Array} menuItems - メニューアイテムの配列
     * @param {Object} options - 追加オプション
     */
    const showContextMenu = async (event, item = null, menuItems = [], options = {}) => {
        // デフォルトのコンテキストメニューを無効化
        if (menuConfig.preventDefaultContextMenu) {
            event.preventDefault();
        }

        // 既存のメニューを閉じる
        hideContextMenu();

        // 位置を計算
        const position = calculatePosition(event, options);

        // 状態を更新
        contextMenuState.isVisible = true;
        contextMenuState.position = position;
        contextMenuState.selectedItem = item;
        contextMenuState.menuItems = processMenuItems(menuItems, item);
        contextMenuState.activeMenuId = options.menuId || 'default';
        contextMenuState.zIndex = options.zIndex || 1000;

        // DOM更新を待ってからイベントリスナーを設定
        await nextTick();
        setupEventListeners();

        console.log('Context menu shown:', {
            position: contextMenuState.position,
            item: contextMenuState.selectedItem,
            menuItems: contextMenuState.menuItems.length
        });
    };

    /**
     * コンテキストメニューを非表示
     */
    const hideContextMenu = () => {
        if (!contextMenuState.isVisible) return;

        contextMenuState.isVisible = false;
        contextMenuState.selectedItem = null;
        contextMenuState.menuItems = [];
        contextMenuState.activeMenuId = null;

        // イベントリスナーを削除
        removeEventListeners();

        console.log('Context menu hidden');
    };

    /**
     * メニュー位置を計算（画面端での調整含む）
     * @param {Event} event - マウスイベント
     * @param {Object} options - 位置オプション
     * @returns {Object} 計算された位置
     */
    const calculatePosition = (event, options = {}) => {
        const offsetX = options.offsetX ?? menuConfig.offsetX;
        const offsetY = options.offsetY ?? menuConfig.offsetY;
        const minDistance = menuConfig.minDistanceFromEdge;

        // 基本位置
        let x = event.clientX + offsetX;
        let y = event.clientY + offsetY;

        // ビューポートサイズを取得
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        // メニューの推定サイズ（実際のサイズは表示後に調整可能）
        const estimatedMenuWidth = options.menuWidth || 200;
        const estimatedMenuHeight = options.menuHeight || 300;

        // 右端を超える場合は左側に表示
        if (x + estimatedMenuWidth > viewportWidth - minDistance) {
            x = event.clientX - estimatedMenuWidth - offsetX;
            // さらに左端を超える場合は画面内に収める
            if (x < minDistance) {
                x = minDistance;
            }
        }

        // 下端を超える場合は上側に表示
        if (y + estimatedMenuHeight > viewportHeight - minDistance) {
            y = event.clientY - estimatedMenuHeight - offsetY;
            // さらに上端を超える場合は画面内に収める
            if (y < minDistance) {
                y = minDistance;
            }
        }

        // 最終的な位置調整
        x = Math.max(minDistance, Math.min(x, viewportWidth - estimatedMenuWidth - minDistance));
        y = Math.max(minDistance, Math.min(y, viewportHeight - estimatedMenuHeight - minDistance));

        return { x, y };
    };

    /**
     * メニューアイテムを処理（条件による表示/非表示、権限チェック等）
     * @param {Array} menuItems - 元のメニューアイテム
     * @param {Object} selectedItem - 選択されたアイテム
     * @returns {Array} 処理されたメニューアイテム
     */
    const processMenuItems = (menuItems, selectedItem) => {
        return menuItems
            .map(item => ({
                id: item.id || `menu-${Date.now()}-${Math.random()}`,
                label: item.label || item.text || 'メニュー項目',
                icon: item.icon || null,
                shortcut: item.shortcut || null,
                disabled: typeof item.disabled === 'function'
                    ? item.disabled(selectedItem)
                    : item.disabled || false,
                visible: typeof item.visible === 'function'
                    ? item.visible(selectedItem)
                    : item.visible !== false,
                handler: item.handler || item.action || (() => { }),
                submenu: item.submenu || null,
                separator: item.separator || false,
                danger: item.danger || false,
                type: item.type || 'normal', // normal, separator, submenu
                data: item.data || {},
                ...item
            }))
            .filter(item => item.visible);
    };

    /**
     * メニューアイテムを実行
     * @param {Object} menuItem - 実行するメニューアイテム
     */
    const executeMenuItem = async (menuItem) => {
        if (menuItem.disabled) return;

        try {
            // ハンドラーを実行
            await menuItem.handler(contextMenuState.selectedItem, menuItem);

            // サブメニューでない場合はメニューを閉じる
            if (!menuItem.submenu) {
                hideContextMenu();
            }
        } catch (error) {
            console.error('Menu item execution error:', error);
        }
    };

    /**
     * 実際のメニューサイズで位置を再調整
     * @param {HTMLElement} menuElement - メニューのDOM要素
     */
    const adjustPositionAfterRender = (menuElement) => {
        if (!menuElement || !contextMenuState.isVisible) return;

        const rect = menuElement.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const minDistance = menuConfig.minDistanceFromEdge;

        let { x, y } = contextMenuState.position;
        let needsUpdate = false;

        // 実際のサイズで右端チェック
        if (x + rect.width > viewportWidth - minDistance) {
            x = viewportWidth - rect.width - minDistance;
            needsUpdate = true;
        }

        // 実際のサイズで下端チェック
        if (y + rect.height > viewportHeight - minDistance) {
            y = viewportHeight - rect.height - minDistance;
            needsUpdate = true;
        }

        // 左端・上端チェック
        if (x < minDistance) {
            x = minDistance;
            needsUpdate = true;
        }
        if (y < minDistance) {
            y = minDistance;
            needsUpdate = true;
        }

        if (needsUpdate) {
            contextMenuState.position = { x, y };
        }
    };

    /**
     * グローバルイベントリスナーを設定
     */
    const setupEventListeners = () => {
        // グローバルクリックでメニューを閉じる
        eventListeners.globalClick = (event) => {
            const contextMenuEl = document.querySelector('.context-menu');
            if (contextMenuEl && !contextMenuEl.contains(event.target)) {
                hideContextMenu();
            }
        };

        // キーボードイベント
        eventListeners.keydown = (event) => {
            if (!contextMenuState.isVisible) return;

            switch (event.key) {
                case 'Escape':
                    if (menuConfig.closeOnEscape) {
                        hideContextMenu();
                    }
                    break;
                case 'ArrowDown':
                    // 次の項目にフォーカス（今後実装）
                    event.preventDefault();
                    break;
                case 'ArrowUp':
                    // 前の項目にフォーカス（今後実装）
                    event.preventDefault();
                    break;
                case 'Enter':
                    // 選択中の項目を実行（今後実装）
                    event.preventDefault();
                    break;
            }
        };

        // スクロールでメニューを閉じる
        if (menuConfig.closeOnScroll) {
            eventListeners.scroll = () => {
                hideContextMenu();
            };
        }

        // リサイズでメニューを閉じる
        if (menuConfig.closeOnResize) {
            eventListeners.resize = () => {
                hideContextMenu();
            };
        }

        // イベントリスナーを登録
        document.addEventListener('click', eventListeners.globalClick);
        document.addEventListener('keydown', eventListeners.keydown);

        if (eventListeners.scroll) {
            window.addEventListener('scroll', eventListeners.scroll, { passive: true });
        }
        if (eventListeners.resize) {
            window.addEventListener('resize', eventListeners.resize);
        }
    };

    /**
     * イベントリスナーを削除
     */
    const removeEventListeners = () => {
        if (eventListeners.globalClick) {
            document.removeEventListener('click', eventListeners.globalClick);
            eventListeners.globalClick = null;
        }
        if (eventListeners.keydown) {
            document.removeEventListener('keydown', eventListeners.keydown);
            eventListeners.keydown = null;
        }
        if (eventListeners.scroll) {
            window.removeEventListener('scroll', eventListeners.scroll);
            eventListeners.scroll = null;
        }
        if (eventListeners.resize) {
            window.removeEventListener('resize', eventListeners.resize);
            eventListeners.resize = null;
        }
    };

    /**
     * 特定の条件でメニューアイテムをフィルタリング
     * @param {Function} filterFn - フィルタリング関数
     * @returns {Array} フィルタリングされたメニューアイテム
     */
    const getFilteredMenuItems = (filterFn) => {
        return contextMenuState.menuItems.filter(filterFn);
    };

    /**
     * メニューアイテムをIDで検索
     * @param {string} id - メニューアイテムのID
     * @returns {Object|null} 見つかったメニューアイテム
     */
    const findMenuItemById = (id) => {
        return contextMenuState.menuItems.find(item => item.id === id) || null;
    };

    /**
     * プリセットメニューアイテムを生成
     */
    const createPresetMenuItems = {
        /**
         * ツリーノード用のメニューアイテム
         * @param {Object} callbacks - コールバック関数群
         * @returns {Array} メニューアイテム配列
         */
        treeNode: (callbacks = {}) => [
            {
                id: 'generate-code',
                label: 'コード発番',
                icon: 'mdi-barcode-scan',
                handler: callbacks.onGenerateCode || (() => { }),
                visible: (item) => item && item.node_type !== 'root'
            },
            {
                id: 'add-existing-node',
                label: '登録済みノード一覧',
                icon: 'mdi-format-list-bulleted',
                handler: callbacks.onShowNodeList || (() => { }),
                visible: (item) => item && item.node_type !== 'root'
            },
            {
                id: 'create-new-node',
                label: '新規ノード作成',
                icon: 'mdi-plus',
                handler: callbacks.onCreateNode || (() => { }),
                visible: (item) => item && item.node_type !== 'root'
            },
            {
                type: 'separator'
            },
            {
                id: 'share-full-tree',
                label: '既存ツリー全体を共有',
                icon: 'mdi-file-tree-outline',
                handler: callbacks.onShareFullTree || (() => { }),
                visible: (item) => item && item.node_type !== 'root'
            },
            {
                id: 'share-partial-tree',
                label: '既存ツリーの一部を共有',
                icon: 'mdi-source-branch',
                handler: callbacks.onSharePartialTree || (() => { }),
                visible: (item) => item && item.node_type !== 'root'
            },
            {
                type: 'separator'
            },
            {
                id: 'edit-node',
                label: 'ノード編集',
                icon: 'mdi-pencil',
                handler: callbacks.onEditNode || (() => { }),
                visible: (item) => item && item.node_type !== 'root',
                disabled: (item) => !callbacks.canEditNode || !callbacks.canEditNode(item)
            },
            {
                id: 'delete-node',
                label: 'ノード削除',
                icon: 'mdi-delete',
                danger: true,
                handler: callbacks.onDeleteNode || (() => { }),
                visible: (item) => item && item.node_type !== 'root',
                disabled: (item) => !callbacks.canDeleteNode || !callbacks.canDeleteNode(item)
            }
        ],

        /**
         * 基本的な編集メニュー
         * @param {Object} callbacks - コールバック関数群
         * @returns {Array} メニューアイテム配列
         */
        basic: (callbacks = {}) => [
            {
                id: 'copy',
                label: 'コピー',
                icon: 'mdi-content-copy',
                shortcut: 'Ctrl+C',
                handler: callbacks.onCopy || (() => { })
            },
            {
                id: 'paste',
                label: '貼り付け',
                icon: 'mdi-content-paste',
                shortcut: 'Ctrl+V',
                handler: callbacks.onPaste || (() => { }),
                disabled: callbacks.isPasteDisabled || false
            },
            {
                type: 'separator'
            },
            {
                id: 'delete',
                label: '削除',
                icon: 'mdi-delete',
                shortcut: 'Delete',
                danger: true,
                handler: callbacks.onDelete || (() => { })
            }
        ]
    };

    // コンポーネントのアンマウント時にイベントリスナーをクリーンアップ
    onUnmounted(() => {
        removeEventListeners();
    });

    // 公開するAPI
    return {
        // 状態
        isVisible: contextMenuState.isVisible,
        position: contextMenuState.position,
        selectedItem: contextMenuState.selectedItem,
        menuItems: contextMenuState.menuItems,
        activeMenuId: contextMenuState.activeMenuId,
        zIndex: contextMenuState.zIndex,

        // 設定
        menuConfig,

        // 基本メソッド
        showContextMenu,
        hideContextMenu,
        executeMenuItem,
        adjustPositionAfterRender,

        // ユーティリティメソッド
        getFilteredMenuItems,
        findMenuItemById,
        createPresetMenuItems,

        // 内部状態（デバッグ用）
        contextMenuState,

        // レガシーサポート（既存コードとの互換性）
        show: showContextMenu,
        hide: hideContextMenu,
        menuPosition: contextMenuState.position,
        isMenuVisible: contextMenuState.isVisible
    };
}