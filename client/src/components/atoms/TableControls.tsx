import React from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";

interface TableControlsProps {
    selectedColumn: string;
    searchValue: string;
    handleColumnChange: (value: string) => void;
    handleSearchChange: (value: string) => void;
    getFilterableColumns: () => Array<{ id: string; name: string }>;
}

const TableControls = ({
    selectedColumn,
    searchValue,
    handleColumnChange,
    handleSearchChange,
    getFilterableColumns,
}: TableControlsProps) => {
    return (
        <div className="flex gap-4 mb-4">
            <Select onValueChange={handleColumnChange}>
                <SelectTrigger className="w-[200px]">
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
                value={searchValue}
                disabled={!selectedColumn}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleSearchChange(e.target.value)}
                className="flex-1"
            />
        </div>
    );
};

export default TableControls;
