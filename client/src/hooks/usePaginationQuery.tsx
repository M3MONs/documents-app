import { useQuery } from "@tanstack/react-query";
import type { PaginationParams } from "@/types/pagination";
import type { ColumnFiltersState, SortingState } from "@tanstack/react-table";

export const usePaginationQuery = (
    queryKey: string[],
    pageIndex: number,
    pageSize: number,
    sorting: SortingState,
    columnFilters: ColumnFiltersState,
    service: (pagination: PaginationParams) => Promise<any>
) => {
    return useQuery({
        queryKey: [...queryKey, pageIndex, pageSize, sorting, columnFilters],
        queryFn: () => {
            const pagination: PaginationParams = {
                page: pageIndex + 1,
                pageSize,
                ordering: sorting.length > 0 ? sorting[0].id : undefined,
                orderingDesc: sorting.length > 0 ? sorting[0].desc : false,
                filters: columnFilters.map((filter: any) => [filter.id, filter.value as string]),
            };
            return service(pagination);
        },
    });
};
