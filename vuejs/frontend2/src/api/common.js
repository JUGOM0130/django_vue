// node.js
import axios from "./settings";

/**
 * コード生成APIを呼び出す
 * @param {string} prefixId - プレフィックスID
 * @returns {Promise} - APIレスポンスのPromise
 */
export const generateCode = (prefixId) => {
  return axios.post("/generate-code/", { prefix: prefixId });
};

/**
 * コード更新APIを呼び出す
 * @param {string} codeId - コードID
 * @param {Object} newData - 更新するデータ
 * @returns {Promise} - APIレスポンスのPromise
 */
export const updateCode = (codeId, newData) => {
  return axios.put(`/update-code/${codeId}/`, newData);
};

/**
 * 特定のコードのバージョン履歴を取得するAPIを呼び出す
 * @param {string} code - コード
 * @returns {Promise} - APIレスポンスのPromise
 */
export const getCodeHistory = (code) => {
  return axios.get(`/code-history/${code}/`);
};

/**
 * 全てのコードのバージョン履歴を取得するAPIを呼び出す
 * @returns {Promise} - APIレスポンスのPromise
 */
export const getAllCodeHistory = () => {
  return axios.get("/all-code-history/");
};