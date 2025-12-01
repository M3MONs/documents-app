import apiClient from "./apiClient";
import type { PaginationParams } from "@/types/pagination";

const URL = "/categories";

export default class CategoryService {
    static getCategories = async (organizationId: string) => {
        const response = await apiClient.get(`${URL}/`, {
            params: { organization_id: organizationId },
        });
        return response.data;
    };

    static getCategory = async (categoryId: string) => {
        const response = await apiClient.get(`${URL}/${categoryId}`);
        return response.data;
    };

    static getCategoryContent = async (
        categoryId: string,
        folderId: string | null,
        pagination: PaginationParams,
        search?: string
    ) => {
        const params = {
            page: pagination.page,
            page_size: pagination.pageSize,
            folder_id: folderId || undefined,
            ...(search && { search }),
            ...(pagination.organization_id && { organization_id: pagination.organization_id }),
            ...(pagination.ordering && { ordering: pagination.ordering }),
            ...(pagination.ordering_desc !== undefined && { ordering_desc: pagination.ordering_desc }),
            ...(pagination.filter_field && { filter_field: pagination.filter_field }),
            ...(pagination.filter_value && { filter_value: pagination.filter_value }),
        };

        const response = await apiClient.get(`${URL}/${categoryId}/content`, {
            params,
        });
        return response.data;
    };

    static getFolderBreadcrumb = async (categoryId: string, folderId: string) => {
        const response = await apiClient.get(`${URL}/${categoryId}/folder-breadcrumb`, {
            params: { folder_id: folderId },
        });
        return response.data;
    };
}
