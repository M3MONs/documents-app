import { SidebarGroup, SidebarGroupLabel, SidebarMenu } from "@/components/ui/sidebar";

export function NavAdmin() {
    return (
        <SidebarGroup className="group-data-[collapsible=icon]:hidden">
            <SidebarGroupLabel>Admin</SidebarGroupLabel>
            <SidebarMenu>{/* TODO: List of admin pages */}</SidebarMenu>
        </SidebarGroup>
    );
}
