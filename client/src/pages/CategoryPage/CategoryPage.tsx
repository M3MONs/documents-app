import { useCallback, useMemo, useEffect, useState } from "react";
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
import FolderManageDialog from "./components/Manager/FolderManageDialog";
import { useAuth } from "@/context/AuthContext";
import { StaticRoles } from "@/constants/roles";
import AddDocumentDialog from "./components/Document/AddDocumentDialog";
import DocumentManageDialog from "./components/Manager/DocumentManageDialog";
import DeleteDialog from "./components/Manager/DeleteDialog";

const CategoryPage = () => {
    const { categoryId } = useParams<{ categoryId: string }>();
    const { user } = useAuth();
    const [selectedItem, setSelectedItem] = useState<ContentItem | null>(null);
    const [isManageDialogOpen, setIsManageDialogOpen] = useState(false);
    const [isAddDocumentDialogOpen, setIsAddDocumentDialogOpen] = useState(false);
    const [isDeleteFolderDialogOpen, setIsDeleteFolderDialogOpen] = useState(false);

    const {
        currentFolderId,
        folderHistory,
        searchQuery,
        page,
        navigateToFolder,
        navigateToBreadcrumb,
        navigateBack,
        setSearchQuery,
        setPage,
        isFocused,
        setIsFocused,
        selectedDocument,
        setSelectedDocument,
        inputRef,
    } = useCategoryPageState(categoryId);

    const debouncedSearchQuery = useDebounce(searchQuery, 300);

    useEffect(() => {
        if (isFocused && inputRef.current && document.activeElement !== inputRef.current) {
            inputRef.current.focus();
        }
    }, [isFocused]);

    const { data, isLoading, error } = useCategoryContent({
        categoryId: categoryId || "",
        folderId: currentFolderId,
        searchQuery: debouncedSearchQuery.trim() || undefined,
        page,
    });

    const canManageCategory = useMemo(() => {
        if (user?.is_superuser) return true;
        if (!categoryId) return false;
        return !!user?.organization_roles?.[categoryId]?.includes(StaticRoles.CATEGORIES_MANAGER.name);
    }, [user, categoryId]);

    const combinedContent = useMemo(() => {
        if (!data) return [];

        const items: ContentItem[] = [];

        if (data.folders) {
            items.push(
                ...data.folders.map((folder: any) => ({
                    id: folder.id,
                    name: folder.name,
                    is_private: folder.is_private,
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

    const handleAddDocument = useCallback(() => {
        setIsAddDocumentDialogOpen(true);
    }, []);

    const handleItemClick = useCallback(
        (item: ContentItem) => {
            if (item.type === "folder") {
                navigateToFolder(item.id, item.name);
            } else if (item.type === "document") {
                setSelectedDocument(item);
            }
        },
        [navigateToFolder, setSelectedDocument]
    );

    const handleBreadcrumbClick = useCallback(
        (index: number) => {
            navigateToBreadcrumb(index);
        },
        [navigateToBreadcrumb]
    );

    const handleNavigateBack = useCallback(() => {
        navigateBack();
    }, [navigateBack]);

    const handleManageClick = useCallback(
        (item: ContentItem) => {
            setSelectedItem(item);
            setIsManageDialogOpen(true);
        },
        [setSelectedItem]
    );

    const handleDeleteClick = useCallback((item: ContentItem) => {
        setSelectedItem(item);
        setIsDeleteFolderDialogOpen(true);
    }, []);

    const handleDeleteItem = useCallback(() => {
        // Implement deletion logic here
    }, [selectedItem]);

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
                    canAddDocument={canManageCategory}
                    onAddDocument={handleAddDocument}
                    onSearchChange={setSearchQuery}
                    onFocusChange={setIsFocused}
                    onBreadcrumbClick={handleBreadcrumbClick}
                    inputRef={inputRef}
                />

                {error && <ErrorAlert error={error} />}

                <ContentList
                    items={combinedContent}
                    isLoading={isLoading}
                    canManageCategory={canManageCategory || false}
                    searchQuery={searchQuery}
                    currentPage={page}
                    pagination={data?.pagination}
                    showBackButton={!!currentFolderId}
                    onItemClick={handleItemClick}
                    onManageClick={handleManageClick}
                    onDeleteClick={handleDeleteClick}
                    onBackClick={handleNavigateBack}
                    onPreviousPage={() => setPage(Math.max(1, page - 1))}
                    onNextPage={() => setPage(page + 1)}
                />

                <DocumentDialog selectedDocument={selectedDocument} setSelectedDocument={setSelectedDocument} />

                {selectedItem && selectedItem.type === "folder" && (
                    <FolderManageDialog
                        isOpen={isManageDialogOpen}
                        selectedFolder={selectedItem}
                        onClose={() => {
                            setSelectedItem(null);
                            setIsManageDialogOpen;
                        }}
                    />
                )}

                {selectedItem && selectedItem.type === "document" && (
                    <DocumentManageDialog
                        isOpen={isManageDialogOpen}
                        selectedDocument={selectedItem}
                        onClose={() => {
                            setSelectedItem(null);
                            setIsManageDialogOpen(false);
                        }}
                    />
                )}

                <AddDocumentDialog
                    isOpen={isAddDocumentDialogOpen}
                    onClose={() => setIsAddDocumentDialogOpen(false)}
                    currentFolderId={currentFolderId || undefined}
                    categoryId={categoryId}
                />

                <DeleteDialog
                    isOpen={isDeleteFolderDialogOpen}
                    selectedItem={selectedItem}
                    onClose={() => setIsDeleteFolderDialogOpen(false)}
                    onDelete={handleDeleteItem}
                />
            </div>
        </DashboardLayout>
    );
};

export default CategoryPage;
