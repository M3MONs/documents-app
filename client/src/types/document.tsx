export interface Document {
    id: string;
    name: string;
    mime_type: string;
}

export interface DocumentMetadata {
    id: string;
    name: string;
    mime_type: string | null;
    file_size: number | null;
    created_at: string;
    updated_at: string;
    file_exists: boolean;
    viewable: boolean;
}