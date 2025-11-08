export interface Role {
    id: string;
    name: string;
    description?: string | null;
}

export interface RoleCreatePayload {
    name: string;
    description?: string;
}