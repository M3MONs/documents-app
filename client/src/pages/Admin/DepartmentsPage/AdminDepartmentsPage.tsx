import TableLayout from "@/components/layouts/TableLayout";
import { usePaginationQuery } from "@/hooks/usePaginationQuery";
import AdminService from "@/services/adminService";
import { handleApiError } from "@/utils/errorHandler";
import { useQueryClient } from "@tanstack/react-query";
import type { ColumnFiltersState, SortingState, Updater } from "@tanstack/react-table";
import { useState } from "react";
import { columns } from "./columns";
import CreateEditDepartment from "./components/CreateEditDepartment";

const AdminDepartmentsPage = () => {
    const queryClient = useQueryClient();
    const [selectedDepartment, setSelectedDepartment] = useState(null);
    const [isCreateEditDialogOpen, setIsCreateEditDialogOpen] = useState(false);

    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [{ pageIndex, pageSize }, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const refreshData = () => {
        queryClient.invalidateQueries({ queryKey: ["admin/departments"] });
    };

    const handleDeleteAction = (department: any) => {
        setSelectedDepartment(department);
    };

    const handleEditAction = (department: any) => {
        setSelectedDepartment(department);
        setIsCreateEditDialogOpen(true);
    };

    const { data, isLoading, error } = usePaginationQuery(
        ["admin/departments"],
        pageIndex,
        pageSize,
        sorting,
        columnFilters,
        AdminService.getDepartments
    );

    if (error) {
        handleApiError(error);
    }

    const handlePaginationChange = (updaterOrValue: Updater<{ pageIndex: number; pageSize: number }>) => {
        setPagination((prev) => (typeof updaterOrValue === "function" ? updaterOrValue(prev) : updaterOrValue));
    };

    return (
        <div className="p-4">
            <TableLayout
                data={data}
                columns={columns(handleEditAction, handleDeleteAction)}
                isLoading={isLoading}
                sorting={sorting}
                columnFilters={columnFilters}
                pageIndex={pageIndex}
                pageSize={pageSize}
                setSorting={setSorting}
                setColumnFilters={setColumnFilters}
                setPagination={handlePaginationChange}
                isAddButtonVisible={true}
                onAddButtonClick={() => setIsCreateEditDialogOpen(true)}
            />

            <CreateEditDepartment
                isOpen={isCreateEditDialogOpen}
                onClose={() => setIsCreateEditDialogOpen(false)}
                onConfirm={refreshData}
                department={selectedDepartment || undefined}
            />
        </div>
    );
};

export default AdminDepartmentsPage;
