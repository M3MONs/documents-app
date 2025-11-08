import TableLayout from "@/components/layouts/TableLayout";
import { usePaginationQuery } from "@/hooks/usePaginationQuery";
import AdminService from "@/services/adminService";
import { handleApiError } from "@/utils/errorHandler";
import { useQueryClient } from "@tanstack/react-query";
import type { ColumnFiltersState, SortingState, Updater } from "@tanstack/react-table";
import { useState } from "react";
import { columns } from "./columns";
import CreateEditDepartment from "./components/CreateEditDepartment";
import type { Department } from "@/types/department";
import DepartmentAssignments from "./components/DepartmentAssignments/DepartmentAssignments";
import DeactivateDialog from "@/components/molecules/DeactivateDialog";

const AdminDepartmentsPage = () => {
    const queryClient = useQueryClient();
    const [selectedDepartment, setSelectedDepartment] = useState<Department | null>(null);
    const [isCreateEditDialogOpen, setIsCreateEditDialogOpen] = useState(false);
    const [isDepartmentAssignmentsOpen, setIsDepartmentAssignmentsOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

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
        setIsDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!selectedDepartment) return;
        try {
            await AdminService.deleteDepartment(selectedDepartment.id);
            setIsDeleteDialogOpen(false);
            setSelectedDepartment(null);
            refreshData();
        } catch (error) {
            handleApiError(error);
        }
    }

    const handleAssignmentsAction = (department: any) => {
        setSelectedDepartment(department);
        setIsDepartmentAssignmentsOpen(true);
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
                columns={columns(handleEditAction, handleDeleteAction, handleAssignmentsAction)}
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

            <DeactivateDialog
                isOpen={isDeleteDialogOpen}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={handleDeleteConfirm}
                text={selectedDepartment?.name}
                title="Delete"
                confirmText="Delete"
                description={`This action will permanently delete the department "${selectedDepartment?.name}". This action cannot be undone. Are you sure you want to proceed?`}
            />

            <CreateEditDepartment
                isOpen={isCreateEditDialogOpen}
                onClose={() => setIsCreateEditDialogOpen(false)}
                onConfirm={refreshData}
                department={selectedDepartment || undefined}
            />

            <DepartmentAssignments
                isOpen={isDepartmentAssignmentsOpen}
                selectedDepartment={selectedDepartment}
                onClose={() => {setIsDepartmentAssignmentsOpen(false); setSelectedDepartment(null)}}
            />
        </div>
    );
};

export default AdminDepartmentsPage;
