import { memo, useCallback } from "react";
import { Button } from "@/components/ui/button";
import ContentItem from "./ContentItem";
import ContentEmpty from "./ContentEmpty";
import ContentLoading from "./ContentLoading";
import PaginationControls from "./PaginationControls";
import type { ContentItem as ContentItemType } from "@/types/categoryContent";

interface ContentListProps {
  items: ContentItemType[];
  isLoading: boolean;
  canManageCategory: boolean;
  searchQuery: string;
  currentPage: number;
  pagination?: {
    page: number;
    total_pages: number;
    total: number;
  };
  showBackButton: boolean;
  onItemClick: (item: ContentItemType) => void;
  onManageClick: (item: ContentItemType) => void;
  onDeleteClick: (item: ContentItemType) => void;
  onBackClick: () => void;
  onPreviousPage: () => void;
  onNextPage: () => void;
}

const ContentList = memo(
  ({
    items,
    isLoading,
    canManageCategory,
    searchQuery,
    currentPage,
    pagination,
    showBackButton,
    onItemClick,
    onManageClick,
    onDeleteClick,
    onBackClick,
    onPreviousPage,
    onNextPage,
  }: ContentListProps) => {
    const handleItemClick = useCallback(
      (item: ContentItemType) => {
        onItemClick(item);
      },
      [onItemClick]
    );

    if (isLoading) {
      return <ContentLoading />;
    }

    return (
      <div className="space-y-2">
        {items.length > 0 ? (
          <>
            {items.map((item) => (
              <ContentItem
                key={`${item.type}-${item.id}`}
                item={item}
                canManageCategory={canManageCategory || false}
                onItemClick={handleItemClick}
                onManageClick={onManageClick}
                onDeleteClick={onDeleteClick}
              />
            ))}
          </>
        ) : (
          <ContentEmpty searchQuery={searchQuery} />
        )}

        {showBackButton && (
          <div className="flex gap-2 pt-4">
            <Button variant="outline" onClick={onBackClick}>
              ← Back
            </Button>
          </div>
        )}

        {pagination && (
          <PaginationControls
            pagination={pagination}
            currentPage={currentPage}
            isLoading={isLoading}
            onPreviousPage={onPreviousPage}
            onNextPage={onNextPage}
          />
        )}
      </div>
    );
  }
);

ContentList.displayName = "ContentList";

export default ContentList;
