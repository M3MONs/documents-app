import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Department } from "@/types/department";
import type { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown, CheckCircle, XCircle, MoreHorizontal } from "lucide-react";
import { booleanFilter } from "@/utils/booleanFilter";

export const getUsersColumns = (
  handleAssignAction: (department: Department) => void,
  handleUnassignAction: (department: Department) => void
): ColumnDef<Department>[] => [
  {
    accessorKey: "username",
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
      const department = row.original;
      return department.is_assigned ? (
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
            {!department.is_assigned && (
              <DropdownMenuItem onClick={() => handleAssignAction(department)}>
                <CheckCircle className="mr-2 h-4 w-4" />
                Assign
              </DropdownMenuItem>
            )}
            {department.is_assigned && (
              <DropdownMenuItem onClick={() => handleUnassignAction(department)}>
                <XCircle className="mr-2 h-4 w-4" />
                Unassign
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];
