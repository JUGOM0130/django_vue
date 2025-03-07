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

