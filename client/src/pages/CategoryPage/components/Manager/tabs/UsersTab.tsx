import React, { useState } from "react";
import { type SortingState, type ColumnFiltersState, type Updater } from "@tanstack/react-table";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import AdminService from "@/services/adminService";
import TableLayout from "@/components/layouts/TableLayout";
import type { Department } from "@/types/department";
import { handleApiError } from "@/utils/errorHandler";
import type { PaginationParams } from "@/types/pagination";
import { toast } from "sonner";
import { getUsersColumns } from "./usersColumns.tsx";

interface UsersTabProps {
  selectedFolder: any | null;
}

const UsersTab: React.FC<UsersTabProps> = ({ selectedFolder }) => {
  const queryClient = useQueryClient();
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [{ pageIndex, pageSize }, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
  });

  const refreshData = () => {
    queryClient.invalidateQueries({ queryKey: ["admin/folder-users"] });
  };

  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ["admin/folder-users", selectedFolder?.id || "", pageIndex, pageSize, sorting, columnFilters],
    queryFn: () => {
      if (!selectedFolder?.id) return { items: [], total: 0 };
      const pagination: PaginationParams = {
        page: pageIndex + 1,
        pageSize,
        ordering: sorting.length > 0 ? sorting[0].id : undefined,
        ordering_desc: sorting.length > 0 ? sorting[0].desc : false,
        filters: columnFilters.map((filter: any) => [filter.id, filter.value as string]),
      };
      return AdminService.getFolderUsers(selectedFolder.id, pagination);
    },
    enabled: !!selectedFolder?.id,
  });

  const handleAssignAction = async (department: Department) => {
    if (!selectedFolder) return;
    try {
      await AdminService.assignUserToFolder(selectedFolder.id, department.id);
      toast.success("Department assigned successfully");
    } catch (err: any) {
      handleApiError(err);
    } finally {
      refreshData();
    }
  };

  const handleUnassignAction = async (department: Department) => {
    if (!selectedFolder) return;
    try {
      await AdminService.unassignUserFromFolder(selectedFolder.id, department.id);
      toast.success("Department unassigned successfully");
    } catch (err: any) {
      handleApiError(err);
    } finally {
      refreshData();
    }
  };

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
          isAddButtonVisible={false}
        />
      </div>
    </div>
  );
};

export default UsersTab;
