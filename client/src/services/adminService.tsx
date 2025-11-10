import apiClient from "@/services/apiClient";
import type { DepartmentCreatePayload } from "@/types/department";
import type { OrganizationCreatePayload } from "@/types/organization";
import type { PaginationParams } from "@/types/pagination";
import type { UserAssignOrganizationPayload, UserEditPayload, UserPasswordResetPayload } from "@/types/user";
import type {
    UserOrganizationRoleCreatePayload,
    UserOrganizationRoleUpdatePayload,
} from "@/types/userOrganizationRole";

const URL = "/admin";

const handleFilterParams = (params: PaginationParams) => {
    if (params.filters && Array.isArray(params.filters) && params.filters.length > 0) {
        const filter = params.filters[0];
        params.filter_field = filter[0];
        params.filter_value = filter[1];
    }
    delete params.filters;
};

export default class AdminService {
    // User Management

    static getUsers = async (pagination: PaginationParams, organizationId?: string) => {
        const params = { ...pagination };

        if (organizationId) {
            params.organization_id = organizationId;
        }

        handleFilterParams(params);

        const response = await apiClient.get(`${URL}/users`, {
            params,
        });
        return response.data;
    };

    static getDepartmentUsers = async (pagination: PaginationParams, departmentId: string) => {
        const params = { ...pagination };

        handleFilterParams(params);

        const response = await apiClient.get(`${URL}/departments/${departmentId}/users`, {
            params,
        });
        return response.data;
    };

    static getUserById = async (userId: string) => {
        const response = await apiClient.get(`${URL}/users/${userId}`);
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

    // Organization Management

    static getOrganizations = async (pagination: PaginationParams) => {
        const params = { ...pagination };

        handleFilterParams(params);

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
    };

    // Department Management

    static getDepartments = async (pagination: PaginationParams) => {
        const params = { ...pagination };

        handleFilterParams(params);

        const response = await apiClient.get(`${URL}/departments`, {
            params,
        });

        return response.data;
    };

    static createDepartment = async (payload: DepartmentCreatePayload) => {
        const response = await apiClient.post(`${URL}/departments`, payload);
        return response.data;
    };

    static updateDepartment = async (departmentId: string, payload: DepartmentCreatePayload) => {
        const response = await apiClient.put(`${URL}/departments/${departmentId}`, payload);
        return response.data;
    };

    static deleteDepartment = async (departmentId: string) => {
        await apiClient.delete(`${URL}/departments/${departmentId}`);
    };

    static assignUserToDepartment = async (userId: string, departmentId: string) => {
        await apiClient.post(`${URL}/departments/${departmentId}/users/${userId}/assign`);
    };

    static unassignUserFromDepartment = async (userId: string, departmentId: string) => {
        await apiClient.post(`${URL}/departments/${departmentId}/users/${userId}/unassign`);
    };

    // Role Management

    static getRoles = async (pagination: PaginationParams) => {
        const params = { ...pagination };

        handleFilterParams(params);

        const response = await apiClient.get(`${URL}/roles`, {
            params,
        });

        return response.data;
    };

    // User Organization Roles

    static getUserOrganizationRoles = async (userId: string) => {
        const response = await apiClient.get(`${URL}/user-organization-roles/user/${userId}`);
        return response.data;
    };

    static getUserRolesInOrganization = async (userId: string, organizationId: string) => {
        const response = await apiClient.get(
            `${URL}/user-organization-roles/user/${userId}/organization/${organizationId}`
        );
        return response.data;
    };

    static assignRoleToUserInOrganization = async (payload: UserOrganizationRoleCreatePayload) => {
        const response = await apiClient.post(`${URL}/user-organization-roles`, payload);
        return response.data;
    };

    static updateUserOrganizationRole = async (uorId: string, payload: UserOrganizationRoleUpdatePayload) => {
        const response = await apiClient.put(`${URL}/user-organization-roles/${uorId}`, payload);
        return response.data;
    };

    static removeRoleFromUserInOrganization = async (uorId: string) => {
        await apiClient.delete(`${URL}/user-organization-roles/${uorId}`);
    };
}
