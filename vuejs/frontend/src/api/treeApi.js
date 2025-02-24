import apiClient from "@/api/setting";

export default {
  getAllTrees() {
    return apiClient.get("/tree/"); // 全てのツリーを取得
  },
  getTree(id) {
    return apiClient.get(`/tree/${id}/`); // 特定のツリーを取得
  },
  createTree(data) {
    return apiClient.post("/tree/", data); // 新しいツリーを作成
  },
  updateTree(id, data) {
    return apiClient.put(`/tree/${id}/`, data); // 特定のツリーを更新
  },
  deleteTree(id) {
    return apiClient.delete(`/tree/${id}/`); // 特定のツリーを削除
  },
};
