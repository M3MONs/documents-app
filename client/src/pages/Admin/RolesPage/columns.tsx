import { type ColumnDef } from "@tanstack/react-table";

import { Button } from "@/components/ui/button";

import { ArrowUpDown } from "lucide-react";
import type { Role } from "@/types/role";

export const columns = (): ColumnDef<Role>[] => [
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
        accessorKey: "description",
        header: ({ column }) => {
            return (
                <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
                    Description
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
];
