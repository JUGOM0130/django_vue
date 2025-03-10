// prefix.js
import axios from "./settings";

// 全てのプレフィックスを取得
export const getAllPrefixes = () => {
  return axios.get("/prefix/");
};

// 特定のプレフィックスを取得
export const getPrefix = (id) => {
  return axios.get(`/prefix/${id}/`);
};

// 新しいプレフィックスを作成
export const createPrefix = (data) => {
  return axios.post("/prefix/", {
    name: data.name,
    description: data.description,
    code_type: data.code_type
  });
};
/**
 * プレフィックスを更新する
 * @param {number} id - プレフィックスのID
 * @param {Object} data - 更新するプレフィックスのデータ
 * @param {string} data.name - プレフィックス名
 * @param {string} [data.description] - プレフィックスの説明（オプション）
 * @param {('1'|'2'|'3')} data.code_type - コードタイプ（1: 組, 2: 部品, 3: 購入品）
 * @returns {Promise<Object>} 更新されたプレフィックスのデータを含むPromise
 */
export const updatePrefix = (id, data) => {
  return axios.put(`/prefix/${id}/`, {
    name: data.name,
    description: data.description,
    code_type: data.code_type
  });
};

// プレフィックスを削除
export const deletePrefix = (id) => {
  return axios.delete(`/prefix/${id}/`);
};


// プレフィックスを削除
export const generateCode = (prefix_id) => {
  return axios.post(`prefix/${prefix_id}/generate_code/`);
};


// コードタイプの選択肢を取得するための定数
export const CODE_TYPE_CHOICES = [
  { value: '1', label: '組' },
  { value: '2', label: '部品' },
  { value: '3', label: '購入品' }
];