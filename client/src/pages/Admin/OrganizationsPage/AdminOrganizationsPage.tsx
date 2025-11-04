import { type SortingState, type ColumnFiltersState, type RowData, type Updater } from "@tanstack/react-table";

import AdminService from "@/services/adminService";

import { useState } from "react";
import { columns } from "./columns";
import { usePaginationQuery } from "@/hooks/usePaginationQuery";
import TableLayout from "@/components/layouts/TableLayout";
import DeactivateDialog from "@/components/molecules/DeactivateDialog";
import { handleApiError } from "@/utils/errorHandler";
import { useQueryClient } from "@tanstack/react-query";
import CreateEditOrganization from "./components/CreateEditOrganization";
import type { Organization } from "@/types/organization";

declare module "@tanstack/react-table" {
    interface ColumnMeta<TData extends RowData, TValue> {
        filterable?: boolean;
    }
}

const AdminOrganizationsPage = () => {
    const queryClient = useQueryClient();
    const [selectedOrganization, setSelectedOrganization] = useState<Organization | null>(null);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [isEditOrganizationOpen, setIsEditOrganizationOpen] = useState(false);
    const [isCreateOrganizationOpen, setIsCreateOrganizationOpen] = useState(false);
    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [{ pageIndex, pageSize }, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const refreshData = () => {
        queryClient.invalidateQueries({ queryKey: ["admin/organizations"] });
    };

    const handleAddButtonClick = () => {
        setIsCreateOrganizationOpen(true);
    };

    const handleEditAction = (organization: Organization) => {
        setSelectedOrganization(organization);
        setIsEditOrganizationOpen(true);
    };

    const handleDeleteAction = (organization: Organization) => {
        setSelectedOrganization(organization);
        setIsDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!selectedOrganization) return;

        try {
            await AdminService.deleteOrganization(selectedOrganization.id);
            setIsDeleteDialogOpen(false);
        } catch (err: any) {
            handleApiError(err);
        } finally {
            setIsDeleteDialogOpen(false);
            setSelectedOrganization(null);
            refreshData();
        }
    };

    const { data, isLoading, error } = usePaginationQuery(
        ["admin/organizations"],
        pageIndex,
        pageSize,
        sorting,
        columnFilters,
        AdminService.getOrganizations
    );

    if (error) {
        console.error("Error fetching organizations:", error);
    }

    const handlePaginationChange = (updaterOrValue: Updater<{ pageIndex: number; pageSize: number }>) => {
        setPagination((prev) => (typeof updaterOrValue === "function" ? updaterOrValue(prev) : updaterOrValue));
    };

    return (
        <>
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
                onAddButtonClick={handleAddButtonClick}
            />

            <DeactivateDialog
                isOpen={isDeleteDialogOpen}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={handleDeleteConfirm}
                text={selectedOrganization?.name}
                title="Delete"
                description={`This action will permanently delete the organization "${selectedOrganization?.name}". This action cannot be undone. Are you sure you want to proceed?`}
            />

            <CreateEditOrganization
                isOpen={isCreateOrganizationOpen}
                onClose={() => setIsCreateOrganizationOpen(false)}
                onConfirm={() => refreshData()}
            />

            <CreateEditOrganization
                isOpen={isEditOrganizationOpen}
                onClose={() => setIsEditOrganizationOpen(false)}
                onConfirm={() => refreshData()}
                organization={selectedOrganization || undefined}
            />
        </>
    );
};

export default AdminOrganizationsPage;
