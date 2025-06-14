import apiClient from "@/api/setting";

export default {
  getAllPrefixes() {
    return apiClient.get("/prefix/");
  },
  getPrefix(id) {
    return apiClient.get(`/prefix/${id}/`);
  },
  createPrefix(data) {
    return apiClient.post("/prefix/", data);
  },
  updatePrefix(id, data) {
    return apiClient.put(`/prefix/${id}/`, data);
  },
  deletePrefix(id) {
    return apiClient.delete(`/prefix/${id}/`);
  },
};