import apiClient from "@/services/apiClient";

const URL = "/auth";

export default class AuthService {
    static refreshToken = async () => {
        const response = await apiClient.get(`${URL}/refresh`);
        return response.data;
    };

    static logout = async () => {
        const response = await apiClient.post(`${URL}/logout`);
        return response.data;
    };

    static login = async (data: any) => {
        const response = await apiClient.post(`${URL}/login`, data);
        return response.data;
    }

    static register = async (data: any) => {
        const response = await apiClient.post(`${URL}/register`, data);
        return response.data;
    }
}
