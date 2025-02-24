import apiClient from "@/api/setting";

export default {
    // Node 関連の API 呼び出し
    getNodes() {
        return apiClient.get('/node/');
    },
    getNodeById(id) {
        return apiClient.get(`/node/${id}/`);
    },
    createNode(data) {
        return apiClient.post('/node/', data);
    },
    updateNode(id, data) {
        return apiClient.put(`/node/${id}/`, data);
    },
    deleteNode(id) {
        return apiClient.delete(`/node/${id}/`);
    },

    // Code Generation API 呼び出し
    generateCode(data) {
        return apiClient.post('/generate-code/', data);
    },
}