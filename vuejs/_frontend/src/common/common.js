import apiClient from "@/api/setting";

export const generateCode = async (prefix) => {
    try {
        const response = await apiClient.post('/generate-code/', { prefix });
        return response.data.code;
    } catch (error) {
        throw new Error(`Failed to generate code: ${error.message}`);
    }
};