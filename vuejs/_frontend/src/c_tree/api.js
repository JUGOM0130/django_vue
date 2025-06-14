import apiClient from "@/api/setting";

export default {
  getAllTree() {
    return apiClient.get("/tree/");
  },
  getTree(id) {
    return apiClient.get(`/tree/${id}/`);
  },
  createTree(data) {
    return apiClient.post("/tree/", data);
  },
  updateTree(id, data) {
    return apiClient.put(`/tree/${id}/`, data);
  },
  deleteTree(id) {
    return apiClient.delete(`/tree/${id}/`);
  },
};