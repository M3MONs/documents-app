import { memo, type RefObject } from "react";
import SearchBar from "@/components/atoms/SearchBar";
import CategoryBreadcrumb from "./CategoryBreadcrumb";
import type { BreadcrumbItemData } from "@/types/categoryContent";
import { Button } from "@/components/ui/button";

interface CategoryHeaderProps {
  folderHistory: BreadcrumbItemData[];
  searchQuery: string;
  isFocused: boolean;
  canAddDocument?: boolean;
  onAddDocument?: () => void;
  onSearchChange: (query: string) => void;
  onFocusChange: (focused: boolean) => void;
  onBreadcrumbClick: (index: number) => void;
  inputRef: RefObject<HTMLInputElement | null>;
}

const CategoryHeader = memo(
  ({
    folderHistory,
    searchQuery,
    canAddDocument,
    onAddDocument,
    onSearchChange,
    onFocusChange,
    onBreadcrumbClick,
    inputRef,
  }: CategoryHeaderProps) => {
    return (
      <div className="flex flex-col gap-4">
        <CategoryBreadcrumb folderHistory={folderHistory} handleBreadcrumbClick={onBreadcrumbClick} />
        <div className="flex gap-4">
          <SearchBar
            searchQuery={searchQuery}
            setSearchQuery={onSearchChange}
            setIsFocused={onFocusChange}
            inputRef={inputRef}
          />
          {canAddDocument && <Button onClick={onAddDocument}>Add Document</Button>}
        </div>
      </div>
    );
  }
);

CategoryHeader.displayName = "CategoryHeader";

export default CategoryHeader;
