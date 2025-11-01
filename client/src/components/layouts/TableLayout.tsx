import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import Pagination from "@/components/atoms/Pagination";
import {
    flexRender,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    getSortedRowModel,
    useReactTable,
    type ColumnFiltersState,
    type OnChangeFn,
    type SortingState,
    type VisibilityState,
} from "@tanstack/react-table";
import { useMemo, useState } from "react";
import { capitalize } from "@/utils/helpers";
import TableControls from "@/components/atoms/TableControls";

interface TableLayoutProps {
    data: any;
    isLoading?: boolean;
    columns: any;
    sorting: SortingState;
    columnFilters: ColumnFiltersState;
    pageIndex: number;
    pageSize: number;
    setSorting: (updater: SortingState | ((old: SortingState) => SortingState)) => void;
    setColumnFilters: (updater: ColumnFiltersState | ((old: ColumnFiltersState) => ColumnFiltersState)) => void;
    setPagination: OnChangeFn<{ pageIndex: number; pageSize: number }>;
}

const TableLayout = ({
    data,
    columns,
    isLoading = false,
    sorting,
    columnFilters,
    pageIndex,
    pageSize,
    setSorting,
    setColumnFilters,
    setPagination,
}: TableLayoutProps) => {
    const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
    const [rowSelection, setRowSelection] = useState({});

    const [selectedColumn, setSelectedColumn] = useState<string>("");
    const [searchValue, setSearchValue] = useState<string>("");

    const pagination = useMemo(
        () => ({
            pageIndex,
            pageSize,
        }),
        [pageIndex, pageSize]
    );

    const table = useReactTable({
        data: data?.items ?? [],
        columns,
        pageCount: data?.total ? Math.ceil(data.total / pageSize) : -1,
        state: {
            sorting,
            columnFilters,
            columnVisibility,
            rowSelection,
            pagination,
        },
        onPaginationChange: setPagination,
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        onColumnVisibilityChange: setColumnVisibility,
        onRowSelectionChange: setRowSelection,
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        manualPagination: true,
    });

    const updateFilters = (columnId: string, value: string) => {
        setColumnFilters([{ id: columnId, value }]);
    };

    const handleColumnChange = (value: string) => {
        setSelectedColumn(value);
        updateFilters(value, searchValue);
    };

    const handleSearchChange = (value: string) => {
        setSearchValue(value);
        if (selectedColumn) {
            updateFilters(selectedColumn, value);
        }
    };

    const getFilterableColumns = () => {
        return columns
            .filter((col: any) => col.meta?.filterable)
            .map((col: any) => ({
                id: (col as any).accessorKey as string,
                name:
                    typeof col.header === "string"
                        ? col.header
                        : capitalize((col as any).accessorKey?.replace(/_/g, " ")),
            }));
    };

    const handleRenderHeader = (headerGroup: any) => {
        return (
            <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header: any) => {
                    return (
                        <TableHead key={header.id}>
                            {header.isPlaceholder
                                ? null
                                : flexRender(header.column.columnDef.header, header.getContext())}
                        </TableHead>
                    );
                })}
            </TableRow>
        );
    };

    const handleRenderBody = (row: any) => {
        return (
            <TableRow key={row.id} data-state={row.getIsSelected() && "selected"}>
                {row.getVisibleCells().map((cell: any) => (
                    <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                ))}
            </TableRow>
        );
    };

    return (
        <div className="w-full h-full flex flex-col p-4">
            <TableControls
                selectedColumn={selectedColumn}
                searchValue={searchValue}
                handleColumnChange={handleColumnChange}
                handleSearchChange={handleSearchChange}
                getFilterableColumns={getFilterableColumns}
            />
            <div className="rounded-md border flex-1 flex flex-col overflow-hidden">
                <Table className="h-full">
                    <TableHeader>
                        {table.getHeaderGroups().map((headerGroup) => handleRenderHeader(headerGroup))}
                    </TableHeader>
                    <TableBody className="overflow-y-auto flex-1">
                        {isLoading ? (
                            <TableRow>
                                <TableCell colSpan={columns.length} className="h-24 text-center">
                                    Loading...
                                </TableCell>
                            </TableRow>
                        ) : table.getRowModel().rows?.length ? (
                            table.getRowModel().rows.map((row) => handleRenderBody(row))
                        ) : (
                            <TableRow>
                                <TableCell colSpan={columns.length} className="h-24 text-center">
                                    No results found.
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>
            <Pagination table={table} data={data} />
        </div>
    );
};

export default TableLayout;
