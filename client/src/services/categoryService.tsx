import apiClient from "./apiClient";

const URL = "/categories";

export default class CategoryService {
    static getCategories = async (organizationId: string) => {
        const response = await apiClient.get(`${URL}/`, {
            params: { organization_id: organizationId },
        });
        return response.data;
    };
}
