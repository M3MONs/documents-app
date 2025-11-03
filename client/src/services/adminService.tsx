import apiClient from "@/services/apiClient";
import type { PaginationParams } from "@/types/pagination";

const URL = "/admin";

export default class AdminService {
    static getUsers = async (pagination: PaginationParams) => {
        const response = await apiClient.get(`${URL}/users`, {
            params: { ...pagination },
        });
        return response.data;
    };

    static deactivateUser = async (userId: string) => {
        await apiClient.delete(`${URL}/users/${userId}`);
    }

    static activateUser = async (userId: string) => {
        await apiClient.post(`${URL}/users/${userId}/activate`);
    }

    static resetUserPassword = async (userId: string, newPassword: string) => {
        await apiClient.post(`${URL}/users/${userId}/reset-password`, { new_password: newPassword });
    }
}