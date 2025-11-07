import { type ColumnDef } from "@tanstack/react-table";

import { Button } from "@/components/ui/button";

import { ArrowUpDown, MoreHorizontal } from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Department } from "@/types/department";

export const columns = (
    onEdit?: (department: Department) => void,
    onDelete?: (department: Department) => void,
    onAssignments?: (department: Department) => void
): ColumnDef<Department>[] => [
    {
        accessorKey: "name",
        header: ({ column }) => {
            return (
                <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
                    Name
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            );
        },
        meta: { filterable: true },
    },
    {
        accessorKey: "organization.name",
        header: ({ column }) => {
            return (
                <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
                    Organization
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            );
        },
        filterFn: (row, columnId, filterValue) => {
            const cellValue = row.getValue(columnId) as string;
            return cellValue.toLowerCase().includes(filterValue.toLowerCase());
        },
        meta: { filterable: true },
    },
    {
        id: "actions",
        header: "Actions",
        cell: ({ row }) => {
            const department = row.original;
            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                            <span className="sr-only">Open menu</span>
                            <MoreHorizontal className="h-4 w-4" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuSeparator />

                        <DropdownMenuItem onClick={() => onEdit?.(department)}>Edit</DropdownMenuItem>

                        <DropdownMenuItem onClick={() => onAssignments?.(department)}>Assignments</DropdownMenuItem>

                        <DropdownMenuItem className="text-red-600" onClick={() => onDelete?.(department)}>
                            Delete
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        },
    },
];
