import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { User } from "@/types/user";
import { booleanFilter } from "@/utils/booleanFilter";
import type { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown, CheckCircle, XCircle } from "lucide-react";

export const getUsersColumns = (
    handleAssignAction: (user: User) => void,
    handleUnassignAction: (user: User) => void
): ColumnDef<User>[] => [
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
        accessorKey: "email",
        header: ({ column }) => {
            return (
                <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
                    Email
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            );
        },
        meta: { filterable: true },
    },
    {
        accessorKey: "is_assigned",
        header: ({ column }) => {
            return (
                <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
                    Assigned
                    <ArrowUpDown className="ml-2 h-4 w-4" />
                </Button>
            );
        },
        cell: ({ row }) => {
            const user = row.original;
            return user.is_assigned ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
                <XCircle className="h-4 w-4 text-red-500" />
            );
        },
        filterFn: (row, columnId, filterValue) => {
            const value = row.getValue(columnId) as boolean;
            return booleanFilter(value, filterValue);
        },
        meta: { filterable: true },
    },
    {
        id: "assign",
        header: "Assign",
        cell: ({ row }) => {
            const user = row.original;
            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="outline" size="sm">
                            Assign
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                        {!user.is_assigned && (
                            <DropdownMenuItem onClick={() => handleAssignAction(user)}>
                                Assign to Department
                            </DropdownMenuItem>
                        )}

                        {user.is_assigned && (
                            <DropdownMenuItem
                                onClick={() => handleUnassignAction(user)}
                                className="text-red-600 hover:bg-red-600/10"
                            >
                                Unassign
                            </DropdownMenuItem>
                        )}
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        },
    },
];