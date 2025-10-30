import type { Organization } from "./organization";
import type { Role } from "./role";

export interface User {
    id: number;
    username: string;
    email?: string | null;
    is_superuser?: boolean | null;
    role?: Role | null;
    primary_organization?: Organization | null;
    additional_organizations?: Organization[] | null;
}