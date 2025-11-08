import TableLayout from "@/components/layouts/TableLayout";
import { usePaginationQuery } from "@/hooks/usePaginationQuery";
import AdminService from "@/services/adminService";
import { handleApiError } from "@/utils/errorHandler";
import { useQueryClient } from "@tanstack/react-query";
import type { ColumnFiltersState, SortingState, Updater } from "@tanstack/react-table";
import { useState } from "react";
import type { Role } from "@/types/role";
import DeactivateDialog from "@/components/molecules/DeactivateDialog";
import CreateEditRole from "../components/CreateEditRole";
import { columns } from "../columns";

const RolesTab = () => {
    const queryClient = useQueryClient();
    const [selectedRole, setSelectedRole] = useState<Role | null>(null);

    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [isEditRoleOpen, setIsEditRoleOpen] = useState(false);
    const [isCreateRoleOpen, setIsCreateRoleOpen] = useState(false);

    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [{ pageIndex, pageSize }, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const refreshData = () => {
        queryClient.invalidateQueries({ queryKey: ["admin/roles"] });
    };

    const handleAddAction = () => {
        setIsCreateRoleOpen(true);
    };

    const handleEditAction = (role: Role) => {
        setSelectedRole(role);
        setIsEditRoleOpen(true);
    };

    const handleDeleteAction = (role: Role) => {
        setSelectedRole(role);
        setIsDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!selectedRole) return;

        try {
            await AdminService.deleteRole(selectedRole.id);
            setIsDeleteDialogOpen(false);
        } catch (err: any) {
            handleApiError(err);
        } finally {
            setIsDeleteDialogOpen(false);
            setSelectedRole(null);
            refreshData();
        }
    };

    const handleCreateEditClose = () => {
        setIsEditRoleOpen(false);
        setIsCreateRoleOpen(false);
        setSelectedRole(null);
    };

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
                onAddButtonClick={handleAddAction}
            />

            <DeactivateDialog
                isOpen={isDeleteDialogOpen}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={handleDeleteConfirm}
                text={selectedRole?.name}
                title="Delete"
                confirmText="Delete"
                description={`This action will permanently delete the role "${selectedRole?.name}". This action cannot be undone. Are you sure you want to proceed?`}
            />

            <CreateEditRole
                isOpen={isEditRoleOpen || isCreateRoleOpen}
                onClose={handleCreateEditClose}
                onConfirm={refreshData}
                role={selectedRole}
            />
        </div>
    );
};

export default RolesTab;
