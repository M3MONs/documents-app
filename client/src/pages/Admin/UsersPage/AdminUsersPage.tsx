import { type SortingState, type ColumnFiltersState, type RowData, type Updater } from "@tanstack/react-table";

import AdminService from "@/services/adminService";

import { useState } from "react";
import { columns } from "./columns";
import { usePaginationQuery } from "@/hooks/usePaginationQuery";
import TableLayout from "@/components/layouts/TableLayout";
import type { User } from "@/types/user";

declare module "@tanstack/react-table" {
    interface ColumnMeta<TData extends RowData, TValue> {
        filterable?: boolean;
    }
}

const AdminUsersPage = () => {
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [{ pageIndex, pageSize }, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const handleEdit = (user: User) => {
        console.log("Edit user", user);
    };

    const handleDelete = (user: User) => {
        console.log("Delete user", user);
    };

    const { data, isLoading, error } = usePaginationQuery(
        ["admin/users"],
        pageIndex,
        pageSize,
        sorting,
        columnFilters,
        AdminService.getUsers
    );

    if (error) {
        console.error("Error fetching users:", error);
    }

    const handlePaginationChange = (updaterOrValue: Updater<{ pageIndex: number; pageSize: number }>) => {
        setPagination(prev => typeof updaterOrValue === 'function' ? updaterOrValue(prev) : updaterOrValue);
    };

    return (
        <TableLayout
            data={data}
            columns={columns(handleEdit, handleDelete)}
            isLoading={isLoading}
            sorting={sorting}
            columnFilters={columnFilters}
            pageIndex={pageIndex}
            pageSize={pageSize}
            setSorting={setSorting}
            setColumnFilters={setColumnFilters}
            setPagination={handlePaginationChange}
        />
    );
};

export default AdminUsersPage;
