import { Button } from "@/components/ui/button";
import type { Table } from "@tanstack/react-table";

type PaginationProps = {
    table: Table<any>;
    data?: {
        total: number;
    };
};

const Pagination = ({ table, data }: PaginationProps) => {
    return (
        <div className="flex items-center justify-end space-x-2 py-4">
            <div className="flex-1 text-sm text-muted-foreground">Total {data?.total ?? 0} rows</div>
            <Button
                variant="outline"
                size="sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
            >
                Previous
            </Button>
            <Button variant="outline" size="sm" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
                Next
            </Button>
        </div>
    );
};

export default Pagination;
