import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/context/AuthContext";
import CategoryService from "@/services/categoryService";
import type { PaginationParams } from "@/types/pagination";

interface UseCategoryContentParams {
  categoryId: string;
  folderId?: string | null;
  page?: number;
  pageSize?: number;
  searchQuery?: string;
}

export const useCategoryContent = ({
  categoryId,
  folderId,
  page = 1,
  pageSize = 20,
  searchQuery,
}: UseCategoryContentParams) => {
  const { selectedOrganization } = useAuth();

  return useQuery({
    queryKey: ["categoryContent", categoryId, folderId, page, pageSize, searchQuery],
    queryFn: async () => {
      const paginationParams: PaginationParams = {
        page,
        pageSize,
        organization_id: selectedOrganization?.id,
      };

      return CategoryService.getCategoryContent(
        categoryId,
        folderId || null,
        paginationParams,
        searchQuery
      );
    },
    enabled: !!categoryId && !!selectedOrganization,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  });
};
