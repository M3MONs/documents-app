import type { Organization } from "./organization";

export interface Category {
    id: string;
    name: string;
    description?: string | null;
    organization: Organization
}

export interface CategoryCreatePayload {
    name: string;
    description?: string | null;
    organization_id: string;
}