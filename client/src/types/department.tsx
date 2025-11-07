import type { Organization } from "./organization";

export interface Department {
    id: string;
    name: string;
    organization: Organization;
}

export interface DepartmentCreatePayload {
    name: string;
    organization_id: string;
}