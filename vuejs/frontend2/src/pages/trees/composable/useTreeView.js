// composables/useTreeView.js
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTreeState } from './useTreeState'
import { useTreeData } from './useTreeData'
import { useContextMenu } from './useContextMenu'
import { generateCode } from '@/api/prefix'
import { bulkCreateTreeStructure } from '@/api/tree'


export const useTreeView = () => {
    // ルーターのルート情報を取得
    const route = useRoute()

    // ツリー状態管理用のステートとアクションを取得
    const { state, actions } = useTreeState()

    // ツリーデータ関連の機能をカスタムフックから取得
    const {
        treeData,                    // ツリーデータ本体
        fetchTreeData,              // ツリーデータを取得する関数
        fetchRootStructureDetail,   // ルート構造の詳細を取得する関数
        addNodeToTree,             // ツリーにノードを追加する関数
        fetchTreeStructure: fetchTree  // 名前の衝突を避けるため別名で取得
    } = useTreeData()

    // コンテキストメニュー関連の機能をカスタムフックから取得
    const {
        menuPosition,              // メニューの表示位置
        isMenuVisible,            // メニューの表示/非表示状態
        selectedNode,             // 選択されたノード
        show: showContextMenu,    // メニューを表示する関数
        hide: hideContextMenu,    // メニューを非表示にする関数
        setupClickListener        // クリックイベントリスナーのセットアップ関数
    } = useContextMenu(actions);

    // モーダル操作関連の関数をオブジェクトにまとめる
    const modalOperations = {
        openNodeList: () => {     // ノードリストモーダルを開く
            actions.setModalState('nodeList', true)
            isMenuVisible.value = false
        },
        closeNodeList: () => {    // ノードリストモーダルを閉じる
            actions.setModalState('nodeList', false)
        },
        openPrefixList: () => {   // プレフィックスリストモーダルを開く
            actions.setModalState('prefixList', true)
            isMenuVisible.value = false
        },
        closePrefixList: () => {  // プレフィックスリストモーダルを閉じる
            actions.setModalState('prefixList', false)
        }
    }

    // コンテキストメニュー操作をシンプルなオブジェクトにまとめる
    const contextMenuOperations = {
        show: showContextMenu,    // コンテキストメニューを表示
        hide: hideContextMenu     // コンテキストメニューを非表示
    }


    /**
     * ツリー構造のデータを整理してソートするメソッド
     * 
     * このメソッドは以下の処理を行います：
     * 1. 親子関係に基づいてノードを整理
     * 2. 同じレベルのノードをアルファベット順にソート
     * 3. ツリー構造を保持しながら一次元配列に変換
     * 
     * @param {Array} structures - 整理前のツリー構造データ配列
     *   各要素は以下のプロパティを持つ:
     *   - id: ノードのID
     *   - name: ノード名
     *   - parent: 親ノードのID
     *   - level: ツリーにおけるレベル
     *   - child: ノードのID(名前が悪い＝NodeIDが適切な名前)
     *   - tree: ツリーの識別子
     * 
     * @returns {Array} 整理・ソート済みのノード配列
     */
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



    /**
     * ツリー構造を整理・ソートして返すcomputedプロパティ
     * @returns {Array} ソート済みのツリー構造の配列
     */
    const organizedTree = computed(() => {
        try {
            const structures = treeData.value.structure;
            //console.log('Input structures:', JSON.stringify(structures));
            const result = sortTreeStructure(structures);
            //console.log('Organized result:', JSON.stringify(result));
            return result;
        } catch (error) {
            console.error('Error organizing tree structure:', error);
            return [];
        }
    });


    /**
     * ツリー構造に新しいノードを追加する処理を行います。
     * 選択中のノードの子として新規ノードを追加し、循環参照のチェックを行います。
     * ノードのタイプは既存ノード('node')または新規コード発番('prefix')の2種類から選択できます。
     * 
     * @param {Object} data - 追加するノードのデータまたはプレフィックスデータ 
     * @param {Object} selectedInfo - 選択中の親ノードの情報
     * @param {string} selectedInfo.child - 選択中ノードのID
     * @param {number} selectedInfo.level - 選択中ノードのレベル
     * @param {string} [type='node'] - ノードのタイプ。'node'(既存ノード)または'prefix'(新規コード発番)
     * @returns {Promise<boolean>} 追加処理の成功/失敗を返す
     * @throws {Error} ノード追加時にエラーが発生した場合
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

    /**
     * 既存ノードをツリー構造に追加するためのハンドラー関数
     * 選択中のノード配下に既存ノードを追加し、モーダルを閉じます
     * 
     * @param {Object} data - 追加する既存ノードのデータ
     * @returns {Promise<void>} 
     * @throws {Error} ノードの追加処理に失敗した場合
     */
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

    /**
     * プレフィックスから新規コードを発番してツリー構造に追加するハンドラー関数
     * 選択中のノード配下に新規発番したコードのノードを追加し、モーダルを閉じます
     * 
     * @param {Object} data - プレフィックスのデータ
     * @param {string} data.prefix - プレフィックスコード
     * @param {string} data.name - プレフィックス名称
     * @returns {Promise<void>}
     * @throws {Error} コードの発番・追加処理に失敗した場合
     */
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


    /**
     * 指定されたノードIDの詳細情報を取得する非同期関数
     * 取得中はローディング状態を管理し、エラー発生時はエラーメッセージを設定します
     * 
     * @param {string} nodeId - 詳細を取得するノードのID
     * @returns {Promise<Object|undefined>} ノードの詳細情報。エラー時はundefined
     * @throws {Error} API呼び出しに失敗した場合
     */
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

    /**
     * ツリービューの初期化を行う非同期関数
     * URLクエリパラメータからツリーIDを取得し、対応するツリーデータを読み込みます
     * 初期化状態、ローディング状態、エラー状態を管理します
     * 
     * @returns {Promise<void>}
     * @throws {Error} ツリーIDが不正な場合やデータ取得に失敗した場合
     * 
     * 処理フロー:
     * 1. URLからツリーIDを取得
     * 2. ツリーIDの存在確認
     * 3. ツリーデータのフェッチ
     * 4. ステート更新
     */
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

    /**
     * プレフィックスから新規コードを発番してノードデータを生成する非同期関数
     * APIを使用して新しいコードを生成し、ツリーノード用のデータ構造に変換します
     * 
     * @param {Object} prefix - プレフィックスデータ
     * @param {string} prefix.id - プレフィックスのID
     * @param {string} prefix.name - プレフィックスの名称
     * @param {string} treeId - ツリーのID
     * @returns {Promise<Object>} 生成されたノードデータ
     * @returns {string} returns.id - 生成されたコードID
     * @returns {string} returns.name - 生成されたコード名
     * @returns {string} returns.prefix - プレフィックス名
     * @returns {string} returns.tree - ツリーID
     * @throws {Error} コード生成APIの呼び出しに失敗した場合
     */
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

    /**
     * 既存ノードデータからツリー用のノードデータを生成する関数
     * 既存ノードの情報を保持しながら、ツリー用のデータ構造に変換します
     * 
     * @param {Object} node - 既存ノードのデータ
     * @param {string} node.id - ノードのID
     * @param {string} node.name - ノードの名称
     * @param {string} node.code - ノードのコード
     * @param {string} treeId - ツリーのID
     * @returns {Object} ツリー用のノードデータ
     * @returns {string} returns.id - ノードID
     * @returns {string} returns.name - ノード名称
     * @returns {string} returns.code - ノードコード
     * @returns {string} returns.tree - ツリーID
     */
    const createRegularNode = (node, treeId) => {
        return {
            id: node.id,
            name: node.name,
            code: node.code,
            tree: treeId
        }
    }


    const bulkCreateTree = async () => {
        const response = await bulkCreateTreeStructure(treeData.value.structure);
        const { data } = response;

        console.log(data)

        window.location.reload()
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
        createPrefixNode,
        bulkCreateTree
    }
}