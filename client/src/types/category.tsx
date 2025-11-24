import type { Organization } from "./organization";

export interface Category {
    id: string;
    name: string;
    description?: string | null;
    organization: Organization
    is_active: boolean;
    is_public: boolean;
}

export interface CategoryCreatePayload {
    name: string;
    description?: string | null;
    organization_id: string;
    is_active: boolean;
    is_public: boolean;
}