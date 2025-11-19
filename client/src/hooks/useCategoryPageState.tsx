import type { BreadcrumbItemData, ContentItem } from "@/types/categoryContent";
import { useState, useRef } from "react";

const useCategoryPageState = () => {
    const [currentFolderId, setCurrentFolderId] = useState<string | null>(null);
    const [folderHistory, setFolderHistory] = useState<BreadcrumbItemData[]>([{ id: null, name: "Category Root" }]);
    const [searchQuery, setSearchQuery] = useState("");
    const [isFocused, setIsFocused] = useState(false);
    const [selectedDocument, setSelectedDocument] = useState<ContentItem | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const [page, setPage] = useState(1);

    return {
        currentFolderId,
        setCurrentFolderId,
        folderHistory,
        setFolderHistory,
        searchQuery,
        setSearchQuery,
        isFocused,
        setIsFocused,
        selectedDocument,
        setSelectedDocument,
        inputRef,
        page,
        setPage,
    };
};

export default useCategoryPageState;
