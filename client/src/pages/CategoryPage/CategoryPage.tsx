import SelectCategoryInfo from "@/components/atoms/SelectCategoryInfo";
import DashboardLayout from "@/components/layouts/DashboardLayout";
import { useParams } from "react-router";

const CategoryPage = () => {
    const { categoryId } = useParams<{ categoryId: string }>();

    if (!categoryId) {
        return <SelectCategoryInfo />;
    }

    return <DashboardLayout>CategoryPage</DashboardLayout>;
};

export default CategoryPage;
