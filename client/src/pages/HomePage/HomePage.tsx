import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import SelectOrganizationInfo from "@/components/atoms/SelectOrganizationInfo";
import DashboardLayout from "@/components/layouts/DashboardLayout";
import { useAuth } from "@/context/AuthContext";
import CategoryService from "@/services/categoryService";
import { handleApiError } from "@/utils/errorHandler";
import { FolderOpen, Loader2 } from "lucide-react";

const HomePage = () => {
    const { selectedOrganization } = useAuth();

    if (!selectedOrganization) {
        return <SelectOrganizationInfo />;
    }

    const { data: categories, isLoading, error } = useQuery({
        queryKey: ["categories", selectedOrganization.id],
        queryFn: () => CategoryService.getCategories(selectedOrganization.id),
        enabled: !!selectedOrganization.id,
    });

    if (error) {
        handleApiError(error);
        return (
            <DashboardLayout>
                <div className="flex items-center justify-center min-h-[400px]">
                    <p className="text-destructive">Failed to load categories.</p>
                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <div className="p-6">
                <h1 className="text-2xl font-bold mb-6">Categories</h1>
                {isLoading ? (
                    <div className="flex items-center justify-center min-h-[200px]">
                        <Loader2 className="h-8 w-8 animate-spin" />
                    </div>
                ) : categories && categories.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {categories.map((category: any) => (
                            <Card key={category.id} className="hover:shadow-md transition-shadow">
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <FolderOpen className="h-5 w-5" />
                                        {category.name}
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm text-muted-foreground mb-4">
                                        {category.description || "No description available."}
                                    </p>
                                    <Button asChild variant="outline" className="w-full">
                                        <Link to={`/categories/${category.id}`}>Open Category</Link>
                                    </Button>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center min-h-[400px] p-4">
                        <div className="flex items-center gap-3 p-6 bg-muted/50 border border-border rounded-lg text-muted-foreground max-w-md w-full">
                            <FolderOpen className="h-6 w-6 flex-shrink-0" />
                            <div>
                                <h3 className="font-medium text-foreground">No categories available</h3>
                                <p className="text-sm">You don't have access to any categories in this organization.</p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
};

export default HomePage;
