import type { Organization } from "./organization";
import type { Role } from "./role";

export interface User {
    id: string;
    username: string;
    email?: string | null;
    is_active: boolean;
    is_superuser?: boolean | null;
    role?: Role | null;
    primary_organization?: Organization | null;
    additional_organizations?: Organization[] | null;
    is_assigned?: boolean | null;
}

export interface UserEditPayload {
    email?: string;
}

export interface UserPasswordResetPayload {
    new_password: string;
}

export interface UserAssignOrganizationPayload {
    set_primary?: boolean;
}