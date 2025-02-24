import apiClient from "@/api/setting";

export default {
  getAllNodes() {
    return apiClient.get("/nodes/");
  },
  getNode(id) {
    return apiClient.get(`/nodes/${id}/`);
  },
  createNode(data) {
    return apiClient.post("/nodes/", data);
  },
  updateNode(id, data) {
    return apiClient.put(`/nodes/${id}/`, data);
  },
  deleteNode(id) {
    return apiClient.delete(`/nodes/${id}/`);
  },
};
