// tree.js
import axios from "./settings";

export const getAllTree = () => {
  return axios.get("/tree/");
};

export const getTree = (id) => {
  return axios.get(`/tree/${id}/get_root/`);
};

export const createTree = (data) => {
  return axios.post("/tree/", data);
};

export const updateTree = (id, data) => {
  return axios.put(`/tree/${id}/`, data);
};

export const deleteTree = (id) => {
  return axios.delete(`/tree/${id}/`);
};






/**
 * ツリー構造を配列で一気に登録するメソッド
 * @param {*} data 
 * @returns 
 */
export const bulkCreateTreeStructure = (data) =>{
  return axios.post("tree-structure/bulk_create/", data);
};

/**
 * ツリー構造を配列で一気に登録するメソッド
 * @param {*} tree_id
 * @returns 
 */
export const getTreeStructure = (tree_id) =>{
  const id = tree_id;
  return axios.get(`tree-structure/${id}/get_tree_structure/`);
};

/**
 * 指定されたNodeIDをchildに持ち、parentがNullであるTreeStructureの詳細情報を取得する
 * 
 * @param {number} node_id - 検索対象のNodeID
 * @returns {Promise<{
*   tree_structures: Array<{
*     id: number,
*     child: number,
*     parent: null,
*     tree: number,
*     level: number
*   }>,
*   node: {
*     id: number,
*     name: string,
*     description: string
*   },
*   trees: Array<{
*     id: number,
*     name: string
*   }>,
*   children_count: number
* }>} TreeStructureの配列と関連する詳細情報
*/
export const get_root_structure_detail = (node_id) => {
 return axios.get(`tree-structure/get_root_structure_detail/?node_id=${node_id}`)
}