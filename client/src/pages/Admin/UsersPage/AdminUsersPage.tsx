import { type SortingState, type ColumnFiltersState, type RowData, type Updater } from "@tanstack/react-table";

import AdminService from "@/services/adminService";

import { useState } from "react";
import { columns } from "./columns";
import { usePaginationQuery } from "@/hooks/usePaginationQuery";
import TableLayout from "@/components/layouts/TableLayout";
import type { User } from "@/types/user";
import DeactivateDialog from "@/components/molecules/DeactivateDialog";
import { handleApiError } from "@/utils/errorHandler";
import { useQueryClient } from "@tanstack/react-query";
import ActivateDialog from "@/components/molecules/ActivateDialog";
import EditUser from "./components/EditUser";
import { useAuth } from "@/context/AuthContext";

declare module "@tanstack/react-table" {
  interface ColumnMeta<TData extends RowData, TValue> {
    filterable?: boolean;
  }
}

const AdminUsersPage = () => {
  const queryClient = useQueryClient();
  const { user: loggedUser } = useAuth();
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isDeactivateDialogOpen, setIsDeactivateDialogOpen] = useState(false);
  const [isActivateDialogOpen, setIsActivateDialogOpen] = useState(false);
  const [isEditUserOpen, setIsEditUserOpen] = useState(false);
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [{ pageIndex, pageSize }, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  const refreshData = async () => {
    await queryClient.invalidateQueries({ queryKey: ["admin/users"] });

    try {
      if (selectedUser) {
        const updatedUser = await AdminService.getUserById(selectedUser.id);
        setSelectedUser(updatedUser);
      }
    } catch (err: any) {
      handleApiError(err);
    }
  };

  const handleEditAction = (user: User) => {
    setSelectedUser(user);
    setIsEditUserOpen(true);
  };

  const handleDeactivateAction = (user: User) => {
    setSelectedUser(user);

    if (user.is_active) {
      setIsDeactivateDialogOpen(true);
    } else {
      setIsActivateDialogOpen(true);
    }
  };

  const handleDeactivateConfirm = async () => {
    if (!selectedUser) return;

    try {
      await AdminService.deactivateUser(selectedUser.id);
      setIsDeactivateDialogOpen(false);
    } catch (err: any) {
      handleApiError(err);
    } finally {
      setIsDeactivateDialogOpen(false);
      setSelectedUser(null);
      refreshData();
    }
  };

  const handleActivateConfirm = async () => {
    if (!selectedUser) return;

    try {
      await AdminService.activateUser(selectedUser.id);
      setIsActivateDialogOpen(false);
    } catch (err: any) {
      handleApiError(err);
    } finally {
      setIsActivateDialogOpen(false);
      setSelectedUser(null);
      refreshData();
    }
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
    setPagination((prev) => (typeof updaterOrValue === "function" ? updaterOrValue(prev) : updaterOrValue));
  };

  return (
    <div className="p-4">
      <TableLayout
        data={data}
        columns={columns(handleEditAction, handleDeactivateAction, loggedUser?.is_superuser || false)}
        isLoading={isLoading}
        sorting={sorting}
        columnFilters={columnFilters}
        pageIndex={pageIndex}
        pageSize={pageSize}
        setSorting={setSorting}
        setColumnFilters={setColumnFilters}
        setPagination={handlePaginationChange}
      />

      <DeactivateDialog
        isOpen={isDeactivateDialogOpen}
        onClose={() => setIsDeactivateDialogOpen(false)}
        onConfirm={handleDeactivateConfirm}
        text={selectedUser?.username}
      />

      <ActivateDialog
        isOpen={isActivateDialogOpen}
        onClose={() => setIsActivateDialogOpen(false)}
        onConfirm={handleActivateConfirm}
        text={selectedUser?.username}
      />

      <EditUser
        user={selectedUser!}
        isOpen={isEditUserOpen}
        onClose={() => setIsEditUserOpen(false)}
        onConfirm={() => {
          setIsEditUserOpen(false);
          refreshData();
        }}
      />
    </div>
  );
};

export default AdminUsersPage;
