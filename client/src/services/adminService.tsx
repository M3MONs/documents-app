import apiClient from "@/services/apiClient";
import type { OrganizationCreatePayload } from "@/types/organization";
import type { PaginationParams } from "@/types/pagination";
import type { UserAssignOrganizationPayload, UserEditPayload, UserPasswordResetPayload } from "@/types/user";

const URL = "/admin";

export default class AdminService {
    static getUsers = async (pagination: PaginationParams, organizationId?: string) => {
        const params = { ...pagination };
        if (organizationId) {
            params.organization_id = organizationId;
        }

        if (params.filters && Array.isArray(params.filters) && params.filters.length > 0) {
            const filter = params.filters[0];
            params.filter_field = filter[0];
            params.filter_value = filter[1];
        }
        delete params.filters;
        const response = await apiClient.get(`${URL}/users`, {
            params,
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

    static getOrganizations = async (pagination: PaginationParams) => {
        const params = { ...pagination };

        if (params.filters && Array.isArray(params.filters) && params.filters.length > 0) {
            const filter = params.filters[0];
            params.filter_field = filter[0];
            params.filter_value = filter[1];
        }

        delete params.filters;
        const response = await apiClient.get(`${URL}/organizations`, {
            params,
        });
        
        return response.data;
    };

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
    };

    static assignUserToOrganization = async (
        userId: string,
        organizationId: string,
        payload: UserAssignOrganizationPayload
    ) => {
        await apiClient.post(`${URL}/organizations/${organizationId}/users/${userId}/assign`, payload);
    };

    static unassignUserFromOrganization = async (userId: string, organizationId: string) => {
        await apiClient.post(`${URL}/organizations/${organizationId}/users/${userId}/unassign`);
    }
}
