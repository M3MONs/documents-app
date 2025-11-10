import TableLayout from "@/components/layouts/TableLayout";
import { usePaginationQuery } from "@/hooks/usePaginationQuery";
import AdminService from "@/services/adminService";
import { handleApiError } from "@/utils/errorHandler";
import type { ColumnFiltersState, SortingState, Updater } from "@tanstack/react-table";
import { useState } from "react";
import { columns } from "../columns";

const RolesTab = () => {
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [{ pageIndex, pageSize }, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const { data, isLoading, error } = usePaginationQuery(
        ["admin/roles"],
        pageIndex,
        pageSize,
        sorting,
        columnFilters,
        AdminService.getRoles
    );

    if (error) {
        handleApiError(error);
    }

    const handlePaginationChange = (updaterOrValue: Updater<{ pageIndex: number; pageSize: number }>) => {
        setPagination((prev: any) => (typeof updaterOrValue === "function" ? updaterOrValue(prev) : updaterOrValue));
    };

    return (
        <div>
            <TableLayout
                data={data}
                columns={columns()}
                isLoading={isLoading}
                sorting={sorting}
                columnFilters={columnFilters}
                pageIndex={pageIndex}
                pageSize={pageSize}
                setSorting={setSorting}
                setColumnFilters={setColumnFilters}
                setPagination={handlePaginationChange}
            />
        </div>
    );
};

export default RolesTab;
