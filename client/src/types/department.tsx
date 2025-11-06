export interface Department {
    id: string;
    name: string;
    organization_id: string;
}

export interface DepartmentCreatePayload {
    name: string;
    organization_id: string;
}