import { type ColumnDef } from "@tanstack/react-table";

import { Button } from "@/components/ui/button";

import { ArrowUpDown, CheckCircle, MoreHorizontal, XCircle } from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Organization } from "@/types/organization";

export const columns = (
    onEdit?: (organization: Organization) => void,
    onDelete?: (organization: Organization) => void,
    onAssignments?: (organization: Organization) => void
): ColumnDef<Organization>[] => [
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
        accessorKey: "domain",
        header: ({ column }) => {
            return (
                <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
                    Domain
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            );
        },
        cell: ({ row }) => row.getValue("domain"),
        filterFn: (row, columnId, filterValue) => {
            const cellValue = row.getValue(columnId) as string;
            return cellValue.toLowerCase().includes(filterValue.toLowerCase());
        },
        meta: { filterable: true },
    },
    {
        accessorKey: "is_active",
        header: ({ column }) => {
            return (
                <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
                    Active
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            );
        },
        cell: ({ row }) => {
            const isActive = row.getValue("is_active");
            return isActive ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
                <XCircle className="h-4 w-4 text-red-500" />
            );
        },
        filterFn: (row, columnId, filterValue) => {
            const value = row.getValue(columnId) as boolean;
            const lowerFilter = filterValue.toLowerCase();
            if (lowerFilter === "") return true;

            if (lowerFilter === "yes" || lowerFilter === "1" || lowerFilter === "true") {
                return value === true;
            }
            if (lowerFilter === "no" || lowerFilter === "0") {
                return value === false;
            }
            return false;
        },
        meta: { filterable: true },
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const organization = row.original;
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
                        <DropdownMenuItem onClick={() => onAssignments?.(organization)}>
                            Manage Assignments
                        </DropdownMenuItem>

                        <DropdownMenuItem onClick={() => onEdit?.(organization)}>Edit</DropdownMenuItem>

                        <DropdownMenuItem className="text-red-600" onClick={() => onDelete?.(organization)}>
                            Delete
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        },
    },
];
