import {
    Breadcrumb,
    BreadcrumbList,
    BreadcrumbSeparator,
    BreadcrumbItem,
    BreadcrumbPage,
    BreadcrumbLink,
} from "@/components/ui/breadcrumb";
import { capitalize } from "@/utils/helpers";

interface CategoryBreadcrumbProps {
    folderHistory: { id: string | null; name: string }[];
    handleBreadcrumbClick: (index: number) => void;
}

const CategoryBreadcrumb = ({ folderHistory, handleBreadcrumbClick }: CategoryBreadcrumbProps) => {
    return (
        <Breadcrumb>
            <BreadcrumbList>
                {folderHistory.map((item, index) => (
                    <div key={`${item.id}-${index}`} className="flex items-center gap-2">
                        {index > 0 && <BreadcrumbSeparator />}
                        <BreadcrumbItem>
                            {index === folderHistory.length - 1 ? (
                                <BreadcrumbPage>{index === 0 ? capitalize(item.name) : item.name}</BreadcrumbPage>
                            ) : (
                                <BreadcrumbLink asChild>
                                    <button
                                        onClick={() => handleBreadcrumbClick(index)}
                                        className="cursor-pointer hover:text-foreground transition-colors"
                                    >
                                        {index === 0 ? capitalize(item.name) : item.name}
                                    </button>
                                </BreadcrumbLink>
                            )}
                        </BreadcrumbItem>
                    </div>
                ))}
            </BreadcrumbList>
        </Breadcrumb>
    );
};

export default CategoryBreadcrumb;
