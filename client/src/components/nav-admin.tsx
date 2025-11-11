import {
    SidebarGroup,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar";
import { StaticRoles } from "@/constants/roles";
import { useAuth } from "@/context/AuthContext";
import { Building2, Group, User, Crown } from "lucide-react";
import { NavLink } from "react-router";

const ADMIN_PAGES = [
    { name: "Users", path: "/admin/users", icon: User, role: StaticRoles.USER_MANAGER },
    { name: "Organizations", path: "/admin/organizations", icon: Building2, role: StaticRoles.USER_MANAGER },
    { name: "Departments", path: "/admin/departments", icon: Group, role: StaticRoles.DEPARTMENT_MANAGER },
    { name: "Roles", path: "/admin/roles", icon: Crown, role: null },
];

export function NavAdmin() {
    const { user } = useAuth();

    if (!user?.is_superuser && (!user?.roles || user.roles.length === 0)) {
        return null;
    }

    const hasAccess = (role: { name: string; description: string } | null) => {
        if (user?.is_superuser) return true;
        if (!user?.roles) return false;
        return user?.roles.some((userRole) => userRole === role?.name);
    };

    return (
        <SidebarGroup className="group-data-[collapsible=icon]:hidden">
            <SidebarGroupLabel>Admin</SidebarGroupLabel>
            <SidebarMenu>
                {ADMIN_PAGES.filter(page => hasAccess(page.role)).map((page) => (
                    <SidebarMenuItem key={page.path}>
                        <SidebarMenuButton asChild>
                            <NavLink to={page.path} className="flex items-center gap-2">
                                <page.icon />
                                {page.name}
                            </NavLink>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                ))}
            </SidebarMenu>
        </SidebarGroup>
    );
}
