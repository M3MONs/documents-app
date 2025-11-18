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
