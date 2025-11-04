import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import type { User } from "@/types/user";
import type { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown, CheckCircle, XCircle } from "lucide-react";

export const getUsersColumns = (handleAssignAction: (user: User, setPrimary: boolean) => void): ColumnDef<User>[] => [
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
            accessorKey: "is_active",
            header: "Active",
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

                if (lowerFilter === "yes" || lowerFilter === "1") return value === true;

                if (lowerFilter === "no" || lowerFilter === "0") return value === false;

                return false;
            },
            meta: { filterable: true },
        },
        {
            id: "assigned",
            header: "Assigned",
            cell: ({ row }) => {
                const user = row.original;
                return user.is_assigned ? "Yes" : "No";
            },
        },
        {
            id: "assign",
            header: "Assign",
            cell: ({ row }) => {
                const user = row.original;
                if (user.is_assigned) {
                    return <span className="text-green-600">Assigned</span>;
                }
                return (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" size="sm">
                                Assign
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                            <DropdownMenuItem onClick={() => handleAssignAction(user, false)}>
                                Assign as Additional
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleAssignAction(user, true)}>
                                Assign as Primary
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                );
            },
        },
    ];