import apiClient from "@/services/apiClient";
import axios from "axios";

const URL = "/auth";

export default class AuthService {
    static refreshToken = async () => {
        const response = await axios.get(`/api${URL}/refresh`, {
            withCredentials: true,
            timeout: 10000,
        });
        return response.data;
    };

    static logout = async () => {
        const response = await apiClient.post(`${URL}/logout`);
        return response.data;
    };

    static login = async (data: any) => {
        const response = await apiClient.post(`${URL}/login`, data);
        return response.data;
    };

    static register = async (data: any) => {
        const response = await apiClient.post(`${URL}/register`, data);
        return response.data;
    };
}
