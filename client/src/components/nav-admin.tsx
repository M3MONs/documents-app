import {
    SidebarGroup,
    SidebarGroupLabel,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar";
import { Building2, Group, User, Crown } from "lucide-react";
import { NavLink } from "react-router";

const ADMIN_PAGES = [
    { name: "Users", path: "/admin/users", icon: User },
    { name: "Organizations", path: "/admin/organizations", icon: Building2 },
    { name: "Departments", path: "/admin/departments", icon: Group },
    { name: "Roles", path: "/admin/roles", icon: Crown },
];

export function NavAdmin() {
    return (
        <SidebarGroup className="group-data-[collapsible=icon]:hidden">
            <SidebarGroupLabel>Admin</SidebarGroupLabel>
            <SidebarMenu>
                {ADMIN_PAGES.map((page) => (
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
