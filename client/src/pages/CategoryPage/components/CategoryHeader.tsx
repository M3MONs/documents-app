import { memo, type RefObject } from "react";
import SearchBar from "@/components/atoms/SearchBar";
import CategoryBreadcrumb from "./CategoryBreadcrumb";
import type { BreadcrumbItemData } from "@/types/categoryContent";

interface CategoryHeaderProps {
    folderHistory: BreadcrumbItemData[];
    searchQuery: string;
    isFocused: boolean;
    onSearchChange: (query: string) => void;
    onFocusChange: (focused: boolean) => void;
    onBreadcrumbClick: (index: number) => void;
    inputRef: RefObject<HTMLInputElement | null>;
}

const CategoryHeader = memo(
    ({
        folderHistory,
        searchQuery,
        onSearchChange,
        onFocusChange,
        onBreadcrumbClick,
        inputRef,
    }: CategoryHeaderProps) => {
        return (
            <div className="flex flex-col gap-4">
                <CategoryBreadcrumb
                    folderHistory={folderHistory}
                    handleBreadcrumbClick={onBreadcrumbClick}
                />
                <SearchBar
                    searchQuery={searchQuery}
                    setSearchQuery={onSearchChange}
                    setIsFocused={onFocusChange}
                    inputRef={inputRef}
                />
            </div>
        );
    }
);

CategoryHeader.displayName = "CategoryHeader";

export default CategoryHeader;
