// composables/useContextMenu.js
import { ref } from 'vue'

export const useContextMenu = (actions) => {
    const menuPosition = ref({ x: 0, y: 0 })
    const isMenuVisible = ref(false)
    const selectedNode = ref(null)

    const show = (event, item) => {
        event.preventDefault()

        const viewportWidth = window.innerWidth
        const viewportHeight = window.innerHeight
        const menuWidth = 200
        const menuHeight = 150

        let x = event.clientX
        if (x + menuWidth > viewportWidth) {
            x = viewportWidth - menuWidth
        }

        let y = event.clientY
        if (y + menuHeight > viewportHeight) {
            y = viewportHeight - menuHeight
        }

        menuPosition.value = { x, y }
        isMenuVisible.value = true
        selectedNode.value = item

        actions.setSelectedNodeInfo({
            parent: item.parent,
            child: item.child,
            level: item.level
        })
    }

    const hide = () => {
        isMenuVisible.value = false
    }

    // クリックイベントのセットアップと解除
    const setupClickListener = () => {
        const handleClickOutside = (event) => {
            if (!event.target.closest('.context-menu')) {
                hide()
            }
        }

        document.addEventListener('click', handleClickOutside)

        // クリーンアップ関数を返す
        return () => {
            document.removeEventListener('click', handleClickOutside)
        }
    }

    // グローバルクリックハンドラー
    const handleGlobalClick = (event) => {
        // コンテキストメニューの要素を取得
        const contextMenu = document.querySelector('.context-menu')

        // クリックされた要素がコンテキストメニュー内のものでない場合、
        // かつ tree-node クラスを持つ要素でない場合にメニューを非表示にする
        if (
            contextMenu &&
            !contextMenu.contains(event.target) &&
            !event.target.closest('.tree-node')
        ) {
            contextMenuOperations.hide()
        }
    }



    return {
        menuPosition,
        isMenuVisible,
        selectedNode,
        show,
        hide,
        setupClickListener,
        handleGlobalClick
    }
}