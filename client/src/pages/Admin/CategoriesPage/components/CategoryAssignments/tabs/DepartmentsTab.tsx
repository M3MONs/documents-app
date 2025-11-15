import React, { useState } from "react";
import { type SortingState, type ColumnFiltersState, type Updater } from "@tanstack/react-table";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import AdminService from "@/services/adminService";
import TableLayout from "@/components/layouts/TableLayout";
import type { Department } from "@/types/department";
import { handleApiError } from "@/utils/errorHandler";
import type { Category } from "@/types/category";
import type { PaginationParams } from "@/types/pagination";
import { getDepartmentsColumns } from "../departmentsColumns";

interface DepartmentsTabProps {
    selectedCategory: Category | null;
}

const DepartmentsTab: React.FC<DepartmentsTabProps> = ({ selectedCategory }) => {
    const queryClient = useQueryClient();
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [{ pageIndex, pageSize }, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const refreshData = () => {
        queryClient.invalidateQueries({ queryKey: ["admin/category-departments"] });
    };

    const { data: departmentsData, isLoading: departmentsLoading } = useQuery({
        queryKey: ["admin/category-departments", selectedCategory?.id || "", pageIndex, pageSize, sorting, columnFilters],
        queryFn: () => {
            if (!selectedCategory?.id) return { items: [], total: 0 };
            const pagination: PaginationParams = {
                page: pageIndex + 1,
                pageSize,
                ordering: sorting.length > 0 ? sorting[0].id : undefined,
                ordering_desc: sorting.length > 0 ? sorting[0].desc : false,
                filters: columnFilters.map((filter: any) => [filter.id, filter.value as string]),
            };
            return AdminService.getCategoryDepartments(selectedCategory.id, pagination);
        },
        enabled: !!selectedCategory?.id,
    });

    const handleAssignAction = async (department: Department) => {
        if (!selectedCategory) return;
        try {
            await AdminService.assignDepartmentToCategory(selectedCategory.id, department.id);
        } catch (err: any) {
            handleApiError(err);
        } finally {
            refreshData();
        }
    };

    const handleUnassignAction = async (department: Department) => {
        if (!selectedCategory) return;
        try {
            await AdminService.unassignDepartmentFromCategory(selectedCategory.id, department.id);
        } catch (err: any) {
            handleApiError(err);
        } finally {
            refreshData();
        }
    };

    const handlePaginationChange = (updaterOrValue: Updater<{ pageIndex: number; pageSize: number }>) => {
        setPagination((prev) => (typeof updaterOrValue === "function" ? updaterOrValue(prev) : updaterOrValue));
    };

    const columns = getDepartmentsColumns(handleAssignAction, handleUnassignAction);

    return (
        <div className="flex-1 overflow-hidden flex flex-col">
            <div className="flex-1 overflow-auto">
                <TableLayout
                    data={departmentsData}
                    columns={columns}
                    isLoading={departmentsLoading}
                    sorting={sorting}
                    columnFilters={columnFilters}
                    pageIndex={pageIndex}
                    pageSize={pageSize}
                    setSorting={setSorting}
                    setColumnFilters={setColumnFilters}
                    setPagination={handlePaginationChange}
                    isAddButtonVisible={false}
                />
            </div>
        </div>
    );
};

export default DepartmentsTab;