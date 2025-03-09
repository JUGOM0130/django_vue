// composables/useTreeView.js
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTreeState } from './useTreeState'
import { useTreeData } from './useTreeData'
import { useContextMenu } from './useContextMenu'
import { generateCode } from '@/api/common'


export const useTreeView = () => {
    const route = useRoute()
    const { state, actions } = useTreeState()
    const {
        treeData,
        fetchTreeData,
        fetchRootStructureDetail,
        addNodeToTree,
        fetchTreeStructure: fetchTree  // 名前を変更して衝突を避ける
    } = useTreeData()
    // コンテキストメニューの機能をインポート
    const {
        menuPosition,
        isMenuVisible,
        selectedNode,
        show: showContextMenu,
        hide: hideContextMenu,
        setupClickListener
    } = useContextMenu(actions);


    const modalOperations = {
        openNodeList: () => {
            actions.setModalState('nodeList', true)
            isMenuVisible.value = false
        },
        closeNodeList: () => {
            actions.setModalState('nodeList', false)
        },
        openPrefixList: () => {
            actions.setModalState('prefixList', true)
            isMenuVisible.value = false
        },
        closePrefixList: () => {
            actions.setModalState('prefixList', false)
        }
    }

    // contextMenuOperationsをコンテキストメニューの機能で置き換え
    const contextMenuOperations = {
        show: showContextMenu,
        hide: hideContextMenu
    }

    const sortTreeStructure = (structures) => {
        if (!structures || structures.length === 0) {
            return [];
        }

        // ノードをparentIdをキーとしたマップに整理
        const nodesByParent = new Map();
        structures.forEach(node => {
            const parentId = node.parent;
            if (!nodesByParent.has(parentId)) {
                nodesByParent.set(parentId, []);
            }
            nodesByParent.get(parentId).push(node);
        });

        const organizedNodes = [];

        // 再帰的にノードを追加する関数
        const addNodesRecursively = (parentId, level) => {
            const nodes = nodesByParent.get(parentId) || [];

            // 同じレベルのノードを名前でソート
            nodes.sort((a, b) => a.name.localeCompare(b.name));

            nodes.forEach(node => {
                organizedNodes.push(node);
                // このノードのchild_idを親として持つノードを検索
                if (nodesByParent.has(node.child)) {
                    addNodesRecursively(node.child, level + 1);
                }
            });
        };

        // ルートノード（parent: null）から開始
        addNodesRecursively(null, 0);

        return organizedNodes.map(item => ({
            id: item.id || '',
            name: item.name,
            parent: item.parent,
            level: parseInt(item.level) || 0,
            child: item.child,
            tree: item.tree || '',
        }));
    };

    // computedプロパティ
    const organizedTree = computed(() => {
        try {
            const structures = treeData.value.structure;
            console.log('Input structures:', JSON.stringify(structures));
            const result = sortTreeStructure(structures);
            console.log('Organized result:', JSON.stringify(result));
            return result;
        } catch (error) {
            console.error('Error organizing tree structure:', error);
            return [];
        }
    });


    const updateTreeStructure = async (id) => {
        try {
            await fetchTree(id)  // fetchTreeStructure から fetchTree に変更
        } catch (error) {
            console.error('Failed to update tree structure:', error)
            actions.setErrorMessage('ツリー構造の更新に失敗しました。')
        }
    }

    /**
     * ノードをツリー構造に追加する
     * @param {Object} data - ノードデータまたはプレフィックスデータ
     * @param {Object} selectedInfo - 選択中のノード情報
     * @param {string} type - 'node'（既存ノード）または'prefix'（新規コード発番）
     */
    const addNodeToStructure = async (data, selectedInfo, type = 'node') => {
        // 循環参照をチェックする関数
        const isCircular = (parent, childId) => {
            if (parent.id === childId) return true;
            if (parent.children) {
                return parent.children.some(child => isCircular(child, childId));
            }
            return false;
        };

        const addNode = (current) => {
            if (current.id === parentId) {
                // 追加前に循環参照をチェック
                if (isCircular(newNode, current.id)) {
                    console.warn('循環参照の作成が試みられました');
                    return false;
                }

                current.children = current.children || [];
                current.children.push(newNode);
                return true;
            }

            if (current.children) {
                for (const child of current.children) {
                    if (addNode(child)) return true;
                }
            }
            return false;
        };

        const currentTreeId = state.treeId
        if (!currentTreeId || !data || !selectedInfo) {
            console.error('Missing required data for node addition')
            return false
        }

        try {
            // 新しいノードのデータを準備
            let nodeData = type === 'prefix'
                ? await createPrefixNode(data, currentTreeId)
                : createRegularNode(data, currentTreeId)//これなんだ・・・

            // log
            if (state.isTest) {
                console.log("useTreeView.addNodeToStructure.nodeData", nodeData)
                console.log("useTreeView.addNodeToStructure child", nodeData.id)
                console.log("useTreeView.addNodeToStructure parent", selectedInfo.child)
                console.log("useTreeView.addNodeToStructure level", selectedInfo.level + 1)
                console.log("useTreeView.addNodeToStructure name", nodeData.name)
            }

            // ツリー構造用のノードデータを作成
            const newNode = {
                ...nodeData,
                id: '',  //新しいNodeはDBに登録されていないのでIDは付与されない
                name: nodeData.name,
                parent: selectedInfo.child,  // 変更: child → id
                child: nodeData.id,
                level: selectedInfo.level + 1,
                tree: currentTreeId
            }

            // log
            if (state.isTest) { console.log("useTreeView.addNodeToStructure.newNode", newNode) }


            /*
            // 既存の親ノードを更新（selectedNodeInfoを使用）
            const parentNode = treeData.value.structure.find(node =>
                node.parent === selectedInfo.parent &&
                node.level === selectedInfo.level
            )

            // log
            if (state.isTest) { console.log("useTreeView.addNodeToStructure.parentNode", parentNode) }

            if (parentNode) {
                parentNode.child = newNode.id  // 親ノードの child を新しいノードの id に設定
            }
            */

            treeData.value.structure.push({
                id: newNode.id,
                name: newNode.name,
                parent: newNode.parent,
                child: newNode.child,
                level: newNode.level,
                tree: newNode.tree
            });

            // log
            if (state.isTest) { console.log("useTreeView.addNodeToStructure.treeData", treeData.value) }


            /**
             * 
             * 
             * ここでツリーをソートする処理をする
             */


            return true

        } catch (error) {
            console.error('Error adding node to tree:', error)
            return false
        }
    }

    // 既存ノードを追加するハンドラー
    const handleNodeData = async (data) => {

        if (!state.selectedNodeInfo) {
            console.error('No node selected')
            modalOperations.closeNodeList()
            return
        }

        try {
            const result = await addNodeToStructure(data, state.selectedNodeInfo, 'node')
            if (!result) {
                console.error('Failed to add node')
            }
        } catch (error) {
            console.error('Failed to handle node data:', error)
        } finally {
            modalOperations.closeNodeList()
        }
    }

    // プレフィックスからコードを発番して追加するハンドラー
    const handlePrefixData = async (data) => {
        if (!state.selectedNodeInfo) {
            console.error('No node selected')
            modalOperations.closePrefixList()
            return
        }

        try {
            const result = await addNodeToStructure(data, state.selectedNodeInfo, 'prefix')
            if (!result) {
                console.error('Failed to add prefix code')
            }
        } catch (error) {
            console.error('Failed to handle prefix data:', error)
        } finally {
            modalOperations.closePrefixList()
        }
    }


    const getNodeDetail = async (nodeId) => {
        actions.setLoading(true)
        try {
            const details = await fetchRootStructureDetail(nodeId)
            return details
        } catch (error) {
            actions.setErrorMessage('ノード詳細の取得に失敗しました。')
        } finally {
            actions.setLoading(false)
        }
    }

    const initialize = async () => {
        const treeid = route.query.id
        if (!treeid) {
            actions.setErrorMessage('Tree IDが見つかりません。')
            actions.updateState({ isInitialized: false })
            return
        }

        try {
            actions.setLoading(true)
            await fetchTree(treeid)  // fetchTreeStructure から fetchTree に変更
            actions.setTreeId(treeid)
            actions.updateState({ isInitialized: true })
        } catch (error) {
            console.error('Initialization failed:', error)
            actions.setErrorMessage('ツリーの初期化に失敗しました。')
            actions.updateState({ isInitialized: false })
        } finally {
            actions.setLoading(false)
        }
    }

    // 新規コード発番用の関数
    const createPrefixNode = async (prefix, treeId) => {

        try {
            // APIを使用して新しいコードを生成
            const { data } = await generateCode(prefix.id)
            const code_name = data.code
            const code_id = data.id

            return {
                id: code_id, // 生成されたコードをIDとして使用
                name: code_name,
                prefix: prefix.name,
                tree: treeId
            }
        } catch (error) {
            console.error('Error creating prefix node:', error)
            throw error
        }
    }

    // 既存ノード用の関数
    const createRegularNode = (node, treeId) => {
        return {
            id: node.id,
            name: node.name,
            code: node.code,
            tree: treeId
        }
    }



    return {
        state,
        organizedTree,
        modalOperations,
        contextMenuOperations,
        handleNodeData,
        handlePrefixData,
        getNodeDetail,
        menuPosition,
        isMenuVisible,
        selectedNode,
        initialize,
        createRegularNode,
        createPrefixNode
    }
}