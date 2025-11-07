import React, { useState } from "react";
import { type SortingState, type ColumnFiltersState, type Updater } from "@tanstack/react-table";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import AdminService from "@/services/adminService";
import TableLayout from "@/components/layouts/TableLayout";
import type { User } from "@/types/user";
import { handleApiError } from "@/utils/errorHandler";
import type { Department } from "@/types/department";
import type { PaginationParams } from "@/types/pagination";
import { getUsersColumns } from "../usersColumns";

interface UsersTabProps {
    selectedDepartment: Department | null;
}

const UsersTab: React.FC<UsersTabProps> = ({ selectedDepartment }) => {
    const queryClient = useQueryClient();
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [{ pageIndex, pageSize }, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const refreshData = () => {
        queryClient.invalidateQueries({ queryKey: ["admin/department-users"] });
    };

    const { data: usersData, isLoading: usersLoading } = useQuery({
        queryKey: ["admin/department-users", selectedDepartment?.id || "", pageIndex, pageSize, sorting, columnFilters],
        queryFn: () => {
            if (!selectedDepartment?.id) return { items: [], total: 0 };
            const pagination: PaginationParams = {
                page: pageIndex + 1,
                pageSize,
                ordering: sorting.length > 0 ? sorting[0].id : undefined,
                ordering_desc: sorting.length > 0 ? sorting[0].desc : false,
                filters: columnFilters.map((filter: any) => [filter.id, filter.value as string]),
            };
            return AdminService.getDepartmentUsers(pagination, selectedDepartment.id);
        },
        enabled: !!selectedDepartment?.id,
    });

    const handleAssignAction = async (user: User) => {
        if (!selectedDepartment) return;

        try {
            await AdminService.assignUserToDepartment(user.id, selectedDepartment.id);
        } catch (err: any) {
            handleApiError(err);
        } finally {
            refreshData();
        }
    };

    const handleUnassignAction = async (user: User) => {
        if (!selectedDepartment) return;

        try {
            await AdminService.unassignUserFromDepartment(user.id, selectedDepartment.id);
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