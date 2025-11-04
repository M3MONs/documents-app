import React, { useCallback, useState } from "react";
import { debounce } from "lodash";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "../ui/button";

interface TableControlsProps {
    selectedColumn: string;
    searchValue: string;
    isAddButtonVisible?: boolean;
    handleColumnChange: (value: string) => void;
    handleSearchChange: (value: string) => void;
    getFilterableColumns: () => Array<{ id: string; name: string }>;
    onAddButtonClick?: () => void;
}

const TableControls = ({
    selectedColumn,
    searchValue,
    isAddButtonVisible = false,
    handleColumnChange,
    handleSearchChange,
    getFilterableColumns,
    onAddButtonClick,
}: TableControlsProps) => {
    const [localSearchValue, setLocalSearchValue] = useState(searchValue);

    const debouncedHandleSearchChange = useCallback(
        debounce((value: string) => {
            handleSearchChange(value);
        }, 300),
        [handleSearchChange]
    );

    const handleInputChange = (value: string) => {
        setLocalSearchValue(value);
        debouncedHandleSearchChange(value);
    };

    return (
        <div className="flex gap-4 mb-4 sm:flex-row flex-col">
            <Select onValueChange={handleColumnChange}>
                <SelectTrigger className="sm:w-[200px] w-full">
                    <SelectValue placeholder="Select column" />
                </SelectTrigger>
                <SelectContent>
                    {getFilterableColumns().map((col: any) => (
                        <SelectItem key={col.id} value={col.id}>
                            {col.name}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
            <Input
                placeholder={selectedColumn ? "Search..." : "Select a column first"}
                value={localSearchValue}
                disabled={!selectedColumn}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleInputChange(e.target.value)}
                className="flex-1"
            />
            {isAddButtonVisible && (
                <Button onClick={onAddButtonClick} className="min-w-[100px]">
                    Add
                </Button>
            )}
        </div>
    );
};

export default TableControls;
