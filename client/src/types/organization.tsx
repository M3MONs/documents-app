export interface Organization {
    id: string;
    name: string;
    domain?: string | null;
    is_active: boolean;    
}

export interface OrganizationCreatePayload {
    name: string;
    domain?: string | null;
    is_active: boolean;
}