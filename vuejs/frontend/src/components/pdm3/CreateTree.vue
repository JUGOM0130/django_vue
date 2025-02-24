<template>
    <div class="container" @click="closeMenu">
        <h1>Create and Edit Tree</h1>
        <hr>

        <!-- ツリー表示 -->
        <ul class="treeview">
            <li v-for="item in formattedTreeData" :key="item.id">
                <span @click="toggleNode(item)" @contextmenu="onRightClick($event, item)" class="tree-node">
                    {{ item.name }}
                </span>
                <!-- 子ノードを展開するための条件 -->
                <ul v-if="item.isOpen && item.children.length > 0">
                    <li v-for="child in item.children" :key="child.id" class="tree-node-child">
                        <span @click="toggleNode(child)" @contextmenu="onRightClick($event, child)" class="tree-node">
                            {{ child.name }}
                        </span>
                        <!-- 子ノードの子ノード -->
                        <ul v-if="child.isOpen && child.children.length > 0">
                            <li v-for="grandchild in child.children" :key="grandchild.id" class="tree-node-child">
                                <span @click="toggleNode(grandchild)" @contextmenu="onRightClick($event, grandchild)"
                                    class="tree-node">
                                    {{ grandchild.name }}
                                </span>
                            </li>
                        </ul>
                    </li>
                </ul>
            </li>
        </ul>

        <!-- 右クリックメニュー -->
        <div v-if="menuVisible" :style="{ top: menuY + 'px', left: menuX + 'px' }" class="context-menu">
            <button @click="addNodeToRoot">Add Node</button>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            menuVisible: false,
            menuX: 0,
            menuY: 0,
            selectedNodeId: null,
            newNodeName: '',
            treeData: [
                { id: 1, parentId: null, name: 'Root Node', isOpen: true },
                { id: 2, parentId: 1, name: 'Child Node 1', isOpen: false },
                { id: 3, parentId: 1, name: 'Child Node 2', isOpen: false },
                { id: 4, parentId: 2, name: 'Child of Child 1', isOpen: false },
                { id: 5, parentId: 2, name: 'Child of Child 2', isOpen: false },
                { id: 6, parentId: 3, name: 'Child of Child 3', isOpen: false },
            ],
        };
    },
    computed: {
        formattedTreeData() {
            const formatted = [];
            const map = {};

            // 初期化
            this.treeData.forEach((item) => {
                map[item.id] = { ...item, children: [] };
            });

            this.treeData.forEach((item) => {
                if (item.parentId === null) {
                    formatted.push(map[item.id]);
                } else {
                    map[item.parentId].children.push(map[item.id]);
                }
            });

            return formatted;
        }
    },
    methods: {
        onRightClick(event, item) {
            event.preventDefault(); // 右クリックのデフォルトアクションを無効化
            this.menuX = event.clientX;
            this.menuY = event.clientY;
            this.menuVisible = true;
            this.selectedNodeId = item.id; // 右クリックしたノードのIDを保存
        },
        closeMenu(event) {
            // 右クリックメニュー外をクリックした場合に閉じる
            if (this.menuVisible && !event.target.closest('.context-menu')) {
                this.menuVisible = false;
            }
        },
        addNodeToRoot() {
            if (this.newNodeName) {
                const newNode = {
                    id: this.treeData.length + 1,
                    parentId: null,
                    name: this.newNodeName,
                    isOpen: false,  // 新しいノードも展開状態を持つ
                };
                this.treeData.push(newNode);
                this.newNodeName = ''; // 新しいノード名のリセット
                this.menuVisible = false; // メニューを閉じる
            }
        },
        toggleNode(node) {
            // 左クリックでノードの展開/折りたたみを切り替える処理
            node.isOpen = !node.isOpen;
        }
    }
};
</script>

<style scoped>
.container {
    padding: 20px;
}

.treeview {
    list-style-type: none;
    padding-left: 20px;
}

.tree-node {
    cursor: pointer;
    font-weight: bold;
}

.tree-node:hover {
    text-decoration: underline;
}

.tree-node-child {
    padding-left: 20px;
    /* 子ノードにインデントを追加 */
}

.context-menu {
    position: absolute;
    background-color: white;
    border: 1px solid #ccc;
    box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
    padding: 10px;
    z-index: 100;
}

.context-menu button {
    display: block;
    margin: 5px 0;
    padding: 5px 10px;
    cursor: pointer;
}
</style>