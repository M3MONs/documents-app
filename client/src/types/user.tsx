import type { Organization } from "./organization";

export interface User {
    id: string;
    username: string;
    email?: string | null;
    is_active: boolean;
    is_superuser?: boolean | null;
    roles?: string[] | null;
    primary_organization?: Organization | null;
    additional_organizations?: Organization[] | null;
    is_assigned?: boolean | null;
    is_primary?: boolean | null;
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