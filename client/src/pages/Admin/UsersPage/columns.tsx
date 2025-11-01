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
import type { User } from "@/types/user";

export const columns = (onEdit?: (user: User) => void, onDelete?: (user: User) => void): ColumnDef<User>[] => [
    {
        accessorKey: "username",
        header: ({ column }) => {
            return (
                <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
                    Username
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            );
        },
        meta: { filterable: true },
    },
    {
        accessorKey: "is_active",
        header: "Active",
        cell: ({ row }) => (row.getValue("is_active") ? "Yes" : "No"),
        filterFn: (row, columnId, filterValue) => {
            const cellValue = row.getValue(columnId) ? "Yes" : "No";
            return cellValue.toLowerCase().includes(filterValue.toLowerCase());
        },
        meta: { filterable: true },
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const user = row.original;
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
                        <DropdownMenuItem onClick={() => onEdit?.(user)}>Edit</DropdownMenuItem>
                        {user.is_active ? (
                            <DropdownMenuItem className="text-red-600" onClick={() => onDelete?.(user)}>
                                Deactivate
                            </DropdownMenuItem>
                        ) : (
                            <DropdownMenuItem className="text-green-600" onClick={() => onDelete?.(user)}>
                                Activate
                            </DropdownMenuItem>
                        )}
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        },
    },
];
