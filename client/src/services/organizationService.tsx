import apiClient from "./apiClient";

const URL = "/organizations";

export default class OrganizationService {
    static validateOrganizationAccess = async (organizationId: string) => {
        const response = await apiClient.get(`${URL}/validate/${organizationId}`);
        return response.data;
    };
}
