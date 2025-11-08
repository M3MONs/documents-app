import type { User } from "./user";
import type { Organization } from "./organization";
import type { Role } from "./role";

export interface UserOrganizationRole {
    id: string;
    user_id: string;
    organization_id: string;
    role_id: string;
    is_primary: boolean;
    created_at?: string;
    user?: User;
    organization?: Organization;
    role?: Role;
}

export interface UserOrganizationRoleCreatePayload {
    user_id: string;
    organization_id: string;
    role_id: string;
    is_primary?: boolean;
}

export interface UserOrganizationRoleUpdatePayload {
    is_primary: boolean;
}