import { memo } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface PaginationData {
    page: number;
    total_pages: number;
    total: number;
}

interface PaginationControlsProps {
    pagination: PaginationData;
    currentPage: number;
    isLoading: boolean;
    onPreviousPage: () => void;
    onNextPage: () => void;
}

const PaginationControls = memo(
    ({ pagination, currentPage, isLoading, onPreviousPage, onNextPage }: PaginationControlsProps) => {
        const itemsPerPage = 20;
        const startItem = (pagination.page - 1) * itemsPerPage + 1;
        const endItem = Math.min(pagination.page * itemsPerPage, pagination.total);

        return (
            <div className="flex items-center justify-between pt-4 border-t">
                <div className="text-sm text-muted-foreground">
                    Showing {startItem} to {endItem} of {pagination.total} items
                </div>
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={onPreviousPage}
                        disabled={currentPage === 1 || isLoading}
                    >
                        <ChevronLeft className="h-4 w-4 mr-1" />
                        Previous
                    </Button>
                    <div className="text-sm font-medium min-w-[3rem] text-center">
                        Page {pagination.page} / {pagination.total_pages}
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={onNextPage}
                        disabled={currentPage >= pagination.total_pages || isLoading}
                    >
                        Next
                        <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                </div>
            </div>
        );
    }
);

PaginationControls.displayName = "PaginationControls";

export default PaginationControls;
