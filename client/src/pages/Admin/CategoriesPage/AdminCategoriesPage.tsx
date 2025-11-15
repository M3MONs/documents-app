import TableLayout from "@/components/layouts/TableLayout";
import DeactivateDialog from "@/components/molecules/DeactivateDialog";
import { usePaginationQuery } from "@/hooks/usePaginationQuery";
import AdminService from "@/services/adminService";
import type { Category } from "@/types/category";
import { handleApiError } from "@/utils/errorHandler";
import { useQueryClient } from "@tanstack/react-query";
import type { ColumnFiltersState, SortingState, Updater } from "@tanstack/react-table";
import { useState } from "react";
import { columns } from "./columns";
import CreateEditCategory from "./components/CreateEditCategory";

const AdminCategoriesPage = () => {
    const queryClient = useQueryClient();
    const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
    const [isCreateEditDialogOpen, setIsCreateEditDialogOpen] = useState(false);
    const [isCategoryAssignmentsOpen, setIsCategoryAssignmentsOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

    const [sorting, setSorting] = useState<SortingState>([]);
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
    const [{ pageIndex, pageSize }, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const refreshData = () => {
        queryClient.invalidateQueries({ queryKey: ["admin/categories"] });
    };

    const handleDeleteAction = (category: any) => {
        setSelectedCategory(category);
        setIsDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!selectedCategory) return;
        try {
            await AdminService.deleteCategory(selectedCategory.id);
            setIsDeleteDialogOpen(false);
            setSelectedCategory(null);
            refreshData();
        } catch (error) {
            handleApiError(error);
        }
    };

    const handleAssignmentsAction = (category: any) => {
        setSelectedCategory(category);
    };

    const handleEditAction = (category: any) => {
        setSelectedCategory(category);
        setIsCreateEditDialogOpen(true);
    };

    const { data, isLoading, error } = usePaginationQuery(
        ["admin/categories"],
        pageIndex,
        pageSize,
        sorting,
        columnFilters,
        AdminService.getCategories
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
                onAddButtonClick={() => {setSelectedCategory(null);setIsCreateEditDialogOpen(true)}}
            />

            <DeactivateDialog
                isOpen={isDeleteDialogOpen}
                onClose={() => setIsDeleteDialogOpen(false)}
                onConfirm={handleDeleteConfirm}
                text={selectedCategory?.name}
                title="Delete"
                confirmText="Delete"
                description={`This action will permanently delete the category "${selectedCategory?.name}". This action cannot be undone. Are you sure you want to proceed?`}
            />

            <CreateEditCategory
                isOpen={isCreateEditDialogOpen}
                onClose={() => setIsCreateEditDialogOpen(false)}
                onConfirm={() => {
                    setIsCreateEditDialogOpen(false);
                    refreshData();
                }}
                category={selectedCategory || undefined}
            />
        </div>
    );
};

export default AdminCategoriesPage;
