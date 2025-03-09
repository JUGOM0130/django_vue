// composables/useTreeData.js
import { ref } from 'vue'
import { getTreeStructure, get_root_structure_detail, bulkCreateTreeStructure } from '@/api/tree'
import { getNode } from '@/api/node'
import { useTreeState } from './useTreeState'

export const useTreeData = () => {
    const { state } = useTreeState()
    const treeData = ref({
        structure: [],
        receiveData: {},
        nodeDetails: null
    })



    // fetchTreeStructure 関数を追加
    const fetchTreeStructure = async (id) => {
        try {
            return await fetchTreeData(id) // 既存の fetchTreeData を利用
        } catch (error) {
            console.error('Error fetching tree structure:', error)
            throw new Error('Failed to fetch tree structure')
        }
    }


    const fetchTreeData = async (treeId) => {
        try {
            const response = await getTreeStructure(treeId)
            const structureData = response.data

            // ノードの詳細情報を取得
            const structureWithNames = await Promise.all(
                structureData.map(async (item) => {
                    if (item.child) {
                        try {
                            const nodeResponse = await getNode(item.child)
                            return {
                                ...item,
                                name: nodeResponse.data.name,
                                nodeDetails: nodeResponse.data
                            }
                        } catch (error) {
                            console.error(`Failed to fetch node details for node ${item.child}:`, error)
                            return {
                                ...item,
                                name: 'Unknown Node',
                                nodeDetails: null
                            }
                        }
                    }
                    return {
                        ...item,
                        name: 'Empty Node',
                        nodeDetails: null
                    }
                })
            )

            treeData.value.structure = formatTreeData(structureWithNames)
            return treeData.value.structure
        } catch (error) {
            console.error('Failed to fetch tree data:', error)
            throw error
        }
    }

    const fetchRootStructureDetail = async (nodeId) => {
        try {
            const response = await get_root_structure_detail(nodeId)
            treeData.value.nodeDetails = response.data
            return response.data
        } catch (error) {
            console.error('Failed to fetch root structure detail:', error)
            throw error
        }
    }

    const formatTreeData = (apiResponse) => {
        return apiResponse.map(item => ({
            id: item.id,
            name: item.name || 'Unnamed Node',
            parent: item.parent,
            child: item.child,
            level: item.level,
            tree: item.tree,
            nodeDetails: item.nodeDetails
        }))
    }

    const createBulkStructure = async (data) => {
        try {
            const response = await bulkCreateTreeStructure(data)
            return response.data
        } catch (error) {
            console.error('Failed to bulk create structure:', error)
            throw error
        }
    }


    const addNodeToTree = async (newNode) => {

        // ログ出力
        if (state.isTest) { console.log("useTreeData.addNodeToTree.newNode", newNode) }

        try {
            // 成功したら、ローカルのツリーデータを更新
            treeData.value.structure.push({
                id: newNode.id,
                name: newNode.name,
                parent: newNode.parent,
                child: newNode.child,
                level: newNode.level,
                tree: newNode.tree
            })

        } catch (error) {
            console.error('Failed to add node:', error)
            throw error
        }
    }



    // createNode関数を追加
    const createNode = (nodeData) => {
        return {
            id: nodeData.id,
            name: nodeData.name,
            code: nodeData.code,
            parent: nodeData.parent,
            child: nodeData.child,
            tree: nodeData.tree,
            level: nodeData.level
        }
    }

    // 補助関数
    const createPrefixNode = async (data, treeId) => {
        const response = await generateCode(data.id)
        const generatedCode = response.data.code
        return {
            id: `temp_${new Date().getTime()}`,
            name: generatedCode,
            prefix_id: data.id,
            code_type: data.code_type,
            description: data.description,
            isGenerated: true,
            tree: treeId
        }
    }

    const createRegularNode = (data, treeId) => ({
        id: data.id,
        name: data.name,
        description: data.description,
        isGenerated: false,
        tree: treeId
    })


    return {
        treeData,
        fetchTreeData,
        fetchRootStructureDetail,
        createBulkStructure,
        addNodeToTree,
        fetchTreeStructure,
        createPrefixNode,
        createRegularNode,
    }
}