import apiClient from "@/services/apiClient";
import type { OrganizationCreatePayload } from "@/types/organization";
import type { PaginationParams } from "@/types/pagination";
import type { UserEditPayload, UserPasswordResetPayload } from "@/types/user";

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
    };

    static activateUser = async (userId: string) => {
        await apiClient.post(`${URL}/users/${userId}/activate`);
    };

    static resetUserPassword = async (userId: string, payload: UserPasswordResetPayload) => {
        await apiClient.post(`${URL}/users/${userId}/reset-password`, payload);
    };

    static updateUser = async (userId: string, payload: UserEditPayload) => {
        await apiClient.put(`${URL}/users/${userId}`, payload);
    };

    static getOrganizations = async () => {
        const response = await apiClient.get(`${URL}/organizations`);
        return response.data;
    }

    static createOrganization = async (payload: OrganizationCreatePayload) => {
        const response = await apiClient.post(`${URL}/organizations`, payload);
        return response.data;
    };

    static updateOrganization = async (organizationId: string, payload: OrganizationCreatePayload) => {
        const response = await apiClient.put(`${URL}/organizations/${organizationId}`, payload);
        return response.data;
    };

    static deleteOrganization = async (organizationId: string) => {
        await apiClient.delete(`${URL}/organizations/${organizationId}`);
    }
}
