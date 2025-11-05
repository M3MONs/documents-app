import React, { useState } from "react";
import { type SortingState, type ColumnFiltersState, type Updater } from "@tanstack/react-table";
import { useQueryClient } from "@tanstack/react-query";
import AdminService from "@/services/adminService";
import { usePaginationQuery } from "@/hooks/usePaginationQuery";
import TableLayout from "@/components/layouts/TableLayout";
import type { User } from "@/types/user";
import { handleApiError } from "@/utils/errorHandler";
import { getUsersColumns } from "../usersColumns";
import type { Organization } from "@/types/organization";

interface UsersTabProps {
    selectedOrganization: Organization | null;
}

const UsersTab: React.FC<UsersTabProps> = ({ selectedOrganization }) => {
    const queryClient = useQueryClient();
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [{ pageIndex, pageSize }, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const refreshData = () => {
        queryClient.invalidateQueries({ queryKey: ["admin/users"] });
    };

    const { data: usersData, isLoading: usersLoading } = usePaginationQuery(
        ["admin/users"],
        pageIndex,
        pageSize,
        sorting,
        columnFilters,
        AdminService.getUsers,
        selectedOrganization?.id
    );

    const handleAssignAction = async (user: User, setPrimary: boolean) => {
        if (!selectedOrganization) return;

        try {
            await AdminService.assignUserToOrganization(user.id, selectedOrganization.id, {
                set_primary: setPrimary,
            });
        } catch (err: any) {
            handleApiError(err);
        } finally {
            refreshData();
        }
    };

    const handleUnassignAction = async (user: User) => {
        if (!selectedOrganization) return;

        try {
            await AdminService.unassignUserFromOrganization(user.id, selectedOrganization.id);
        } catch (err: any) {
            handleApiError(err);
        } finally {
            refreshData();
        }
    }

    const handlePaginationChange = (updaterOrValue: Updater<{ pageIndex: number; pageSize: number }>) => {
        setPagination((prev) => (typeof updaterOrValue === "function" ? updaterOrValue(prev) : updaterOrValue));
    };

    const columns = getUsersColumns(handleAssignAction, handleUnassignAction);

    return (
        <div className="flex-1 overflow-hidden flex flex-col">
            <div className="flex-1 overflow-auto">
                <TableLayout
                    data={usersData}
                    columns={columns}
                    isLoading={usersLoading}
                    sorting={sorting}
                    columnFilters={columnFilters}
                    pageIndex={pageIndex}
                    pageSize={pageSize}
                    setSorting={setSorting}
                    setColumnFilters={setColumnFilters}
                    setPagination={handlePaginationChange}
                />
            </div>
        </div>
    );
};

export default UsersTab;
