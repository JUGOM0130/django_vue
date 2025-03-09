/**
 * composable/useTreeOperations.js
 */
import { useTreeState } from './useTreeState'
import { useTreeData } from './useTreeData'

export const useTreeOperations = () => {
  const { state } = useTreeState()
  const { treeData, sortTreeStructure } = useTreeData()

  const showContextMenu = (event, item) => {
    event.preventDefault()
    state.value.menu.position = {
      top: `${event.clientY}px`,
      left: `${event.clientX}px`
    }
    state.value.menu.isShow = true
    treeData.value.selectedItem = item

    state.value.selectedNodeInfo = {
      parent: item.parent,
      child: item.child,
      level: item.level
    }

    document.addEventListener('click', closeContextMenu)
  }

  const closeContextMenu = (event) => {
    if (event.target.closest('.modal')) {
      return
    }
    state.value.menu.isShow = false
    document.removeEventListener('click', closeContextMenu)
  }

  const closeAllModals = () => {
    state.value.modal.isShow = false
  }

  const handleModalOutsideClick = (event) => {
    if (event.target.classList.contains('modal-overlay')) {
      closeAllModals()
    }
  }

  const addNodeToTree = async (node_id, newNodeName) => {
    if (!state.value.selectedNodeInfo.child) return

    try {
      const response = await get_root_structure_detail(node_id)
      const { tree_structures: existingStructures, node: existingNode } = response.data

      if (existingStructures && existingStructures.length > 0 && existingNode) {
        const rootStructure = existingStructures.find(s => s.parent === null)
        if (rootStructure) {
          const levelDiff = (state.value.selectedNodeInfo.level + 1) - rootStructure.level
          const timestamp = Date.now()

          const nodeRelations = new Map()
          existingStructures.forEach(structure => {
            nodeRelations.set(structure.child, structure.parent)
          })

          const adjustedStructures = existingStructures.map((structure, index) => {
            const tempId = `temp_${timestamp}_${index}`
            return {
              ...structure,
              id: tempId,
              tree: Number(state.value.tree_id),
              level: structure.level + levelDiff,
              parent: structure.parent === null
                ? state.value.selectedNodeInfo.child
                : nodeRelations.get(structure.child),
              name: structure.name || newNodeName
            }
          })

          const insertIndex = treeData.value.structure.findIndex(
            node => node.child === state.value.selectedNodeInfo.child
          )

          treeData.value.structure = [
            ...treeData.value.structure.slice(0, insertIndex + 1),
            ...adjustedStructures,
            ...treeData.value.structure.slice(insertIndex + 1)
          ]
        }
      } else {
        const newNode = {
          id: `temp_${Date.now()}`,
          name: newNodeName,
          parent: state.value.selectedNodeInfo.child,
          child: node_id,
          tree: Number(state.value.tree_id),
          level: state.value.selectedNodeInfo.level + 1
        }

        const insertIndex = treeData.value.structure.findIndex(
          node => node.child === state.value.selectedNodeInfo.child
        )

        treeData.value.structure = [
          ...treeData.value.structure.slice(0, insertIndex + 1),
          newNode,
          ...treeData.value.structure.slice(insertIndex + 1)
        ]
      }

      await sortTreeStructure()
      closeAllModals()

    } catch (error) {
      console.error('Error adding node to tree:', error)
      showErrorNotification('ノードの追加に失敗しました')
    }
  }

  return {
    showContextMenu,
    closeContextMenu,
    closeAllModals,
    handleModalOutsideClick,
    addNodeToTree
  }
}