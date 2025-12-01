import type { Folder } from "./folder";
import type { Document } from "./document";

export interface PaginationInfo {
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}

export interface CategoryContentResponse {
    folders: Folder[];
    documents: Document[];
    pagination: PaginationInfo;
}

export interface BreadcrumbItemData {
    id: string | null;
    name: string;
}

export interface ContentItem {
    id: string;
    name: string;
    type: "folder" | "document";
    mime_type?: string;
    is_private?: boolean;
}