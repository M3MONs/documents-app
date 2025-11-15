import type { Organization } from "./organization";

export interface Department {
    id: string;
    name: string;
    organization: Organization;
    is_assigned?: boolean;
}

export interface DepartmentCreatePayload {
    name: string;
    organization_id: string;
}