import {
    SidebarGroup,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar";
import { useAuth } from "@/context/AuthContext";
import CategoryService from "@/services/categoryService";
import { handleApiError } from "@/utils/errorHandler";
import { useEffect, useState } from "react";
import { NavLink } from "react-router";

export function NavMain() {
    const { user, selectedOrganization } = useAuth();
    const [categories, setCategories] = useState<Array<any>>([]);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const data = await CategoryService.getCategories(selectedOrganization!.id);
                setCategories(data);
            } catch (err: any) {
                handleApiError(err);
            }
        };

        if (!user?.id || !selectedOrganization?.id) return;
        fetchCategories();
    }, [user?.id, selectedOrganization?.id]);

    return (
        <SidebarGroup>
            <SidebarGroupLabel>Categories</SidebarGroupLabel>
            <SidebarMenu>
                {categories.map((category) => (
                    <SidebarMenuItem key={category.id}>
                        <SidebarMenuButton asChild>
                            <NavLink to={`/categories/${category.id}`}>{category.name}</NavLink>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                ))}
            </SidebarMenu>
        </SidebarGroup>
    );
}
