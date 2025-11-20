import { useCallback, useMemo, useEffect } from "react";
import { useParams } from "react-router";
import SelectCategoryInfo from "@/components/atoms/SelectCategoryInfo";
import DashboardLayout from "@/components/layouts/DashboardLayout";
import { useCategoryContent } from "@/hooks/useCategoryContent";
import { useDebounce } from "@/hooks/useDebounce";
import type { ContentItem } from "@/types/categoryContent";
import DocumentDialog from "./components/Document/DocumentDialog";
import CategoryHeader from "./components/CategoryHeader";
import ContentList from "./components/ContentList";
import ErrorAlert from "../../components/atoms/ErrorAlert";
import useCategoryPageState from "@/hooks/useCategoryPageState";

const CategoryPage = () => {
    const { categoryId } = useParams<{ categoryId: string }>();
    const {
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
    } = useCategoryPageState();

    const debouncedSearchQuery = useDebounce(searchQuery, 300);

    useEffect(() => {
        if (isFocused && inputRef.current && document.activeElement !== inputRef.current) {
            inputRef.current.focus();
        }
    }, [isFocused]);

    useEffect(() => {
        setPage(1);
    }, [debouncedSearchQuery, currentFolderId, setPage]);

    const { data, isLoading, error } = useCategoryContent({
        categoryId: categoryId || "",
        folderId: currentFolderId,
        searchQuery: debouncedSearchQuery.trim() || undefined,
        page,
    });

    const combinedContent = useMemo(() => {
        if (!data) return [];

        const items: ContentItem[] = [];

        if (data.folders) {
            items.push(
                ...data.folders.map((folder: any) => ({
                    id: folder.id,
                    name: folder.name,
                    type: "folder" as const,
                }))
            );
        }

        if (data.documents) {
            items.push(
                ...data.documents.map((doc: any) => ({
                    id: doc.id,
                    name: doc.name,
                    type: "document" as const,
                    mime_type: doc.mime_type,
                }))
            );
        }

        return items;
    }, [data]);

    const handleItemClick = useCallback(
        (item: ContentItem) => {
            if (item.type === "folder") {
                setCurrentFolderId(item.id);
                setFolderHistory((prev) => [
                    ...prev,
                    {
                        id: item.id,
                        name: item.name,
                    },
                ]);
            } else if (item.type === "document") {
                setSelectedDocument(item);
            }
        },
        [setCurrentFolderId, setFolderHistory, setSelectedDocument]
    );

    const handleBreadcrumbClick = useCallback(
        (index: number) => {
            const targetFolder = folderHistory[index];
            setCurrentFolderId(targetFolder.id);
            setFolderHistory((prev) => prev.slice(0, index + 1));
            setSearchQuery("");
        },
        [folderHistory, setCurrentFolderId, setFolderHistory, setSearchQuery]
    );

    const handleNavigateBack = useCallback(() => {
        if (folderHistory.length > 1) {
            const newHistory = folderHistory.slice(0, -1);
            const prevFolder = newHistory[newHistory.length - 1];
            setCurrentFolderId(prevFolder.id);
            setFolderHistory(newHistory);
            setSearchQuery("");
        }
    }, [folderHistory, setCurrentFolderId, setFolderHistory, setSearchQuery]);

    if (!categoryId) {
        return <SelectCategoryInfo />;
    }

    return (
        <DashboardLayout>
            <div className="flex flex-col gap-6 p-6">
                <CategoryHeader
                    folderHistory={folderHistory}
                    searchQuery={searchQuery}
                    isFocused={isFocused}
                    onSearchChange={setSearchQuery}
                    onFocusChange={setIsFocused}
                    onBreadcrumbClick={handleBreadcrumbClick}
                    inputRef={inputRef}
                />

                {error && <ErrorAlert error={error} />}

                <ContentList
                    items={combinedContent}
                    isLoading={isLoading}
                    searchQuery={searchQuery}
                    currentPage={page}
                    pagination={data?.pagination}
                    showBackButton={!!currentFolderId}
                    onItemClick={handleItemClick}
                    onBackClick={handleNavigateBack}
                    onPreviousPage={() => setPage((p) => Math.max(1, p - 1))}
                    onNextPage={() => setPage((p) => p + 1)}
                />

                <DocumentDialog selectedDocument={selectedDocument} setSelectedDocument={setSelectedDocument} />
            </div>
        </DashboardLayout>
    );
};

export default CategoryPage;
