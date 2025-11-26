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

const CategoryPage = () => {
  const { categoryId } = useParams<{ categoryId: string }>();
  const [selectedFolder, setSelectedFolder] = useState<ContentItem | null>(null);

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
  } = useCategoryPageState();

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

  const handleManageFolder = useCallback(
    (item: ContentItem) => {
      setSelectedFolder(item);
    },
    [setSelectedFolder]
  );

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
          onManageClick={handleManageFolder}
          onBackClick={handleNavigateBack}
          onPreviousPage={() => setPage(Math.max(1, page - 1))}
          onNextPage={() => setPage(page + 1)}
        />

        <DocumentDialog selectedDocument={selectedDocument} setSelectedDocument={setSelectedDocument} />

        <FolderManageDialog selectedFolder={selectedFolder} setSelectedFolder={setSelectedFolder} />
      </div>
    </DashboardLayout>
  );
};

export default CategoryPage;
