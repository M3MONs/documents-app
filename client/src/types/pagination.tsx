export interface PaginationParams {
    page: number;
    pageSize: number;
    ordering?: string;
    orderingDesc?: boolean;
    filters?: Array<[string, string]>;
}

export class PaginationParamsImpl implements PaginationParams {
    page: number = 1;
    pageSize: number = 10;
    ordering?: string;
    orderingDesc: boolean = false;
    filters?: Array<[string, string]>;

    get offset(): number {
        return (this.page - 1) * this.pageSize;
    }
}

export interface PaginationResponse<T> {
    total: number;
    items: T[];
}
