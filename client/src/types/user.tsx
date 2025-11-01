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
}