import { useEffect, useState } from "react";
import { ChevronsUpDown } from "lucide-react";

import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuShortcut,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem, useSidebar } from "@/components/ui/sidebar";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { useAuth } from "@/context/AuthContext";
import type { Organization } from "@/types/organization";

export function OrganizationSwitcher() {
    const { isMobile } = useSidebar();
    const { user, setSelectedOrganizationId } = useAuth();
    const [organizations, setOrganizations] = useState<Organization[] | null>(null);
    const [activeOrganization, setActiveOrganization] = useState<Organization | null>(null);

    useEffect(() => {
        if (user) {
            setOrganizations(user.additional_organizations || []);
            setActiveOrganization(user.primary_organization || null);
            setSelectedOrganizationId(user.primary_organization ? user.primary_organization.id : null);
        }
    }, [user]);

    const handleOrganizationChange = (organization: Organization | null) => {
        setActiveOrganization(organization);
        setSelectedOrganizationId(organization ? organization.id : null);
    };

    return (
        <SidebarMenu>
            <SidebarMenuItem>
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <SidebarMenuButton
                            size="lg"
                            className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                            disabled={!organizations}
                        >
                            <Avatar className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                                <AvatarImage src={""} alt={activeOrganization?.name} />
                                <AvatarFallback className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                                    {activeOrganization ? activeOrganization?.name.charAt(0) : "N"}
                                </AvatarFallback>
                            </Avatar>

                            <div className="grid flex-1 text-left text-sm leading-tight">
                                <span className="truncate font-medium">
                                    {activeOrganization ? activeOrganization?.name : "No organization"}
                                </span>
                            </div>
                            <ChevronsUpDown className="ml-auto" />
                        </SidebarMenuButton>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent
                        className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
                        align="start"
                        side={isMobile ? "bottom" : "right"}
                        sideOffset={4}
                    >
                        <DropdownMenuLabel className="text-muted-foreground text-xs">Organizations</DropdownMenuLabel>
                        {organizations?.map((organization, index) => (
                            <DropdownMenuItem
                                key={organization.name}
                                onClick={() => handleOrganizationChange(organization)}
                                className="gap-2 p-2"
                            >
                                <div className="flex size-6 items-center justify-center rounded-md border">
                                    <Avatar>
                                        <AvatarImage src={""} alt={organization.name} />
                                        <AvatarFallback>{organization.name.charAt(0)}</AvatarFallback>
                                    </Avatar>
                                </div>
                                {organization.name}
                                <DropdownMenuShortcut>⌘{index + 1}</DropdownMenuShortcut>
                            </DropdownMenuItem>
                        ))}
                    </DropdownMenuContent>
                </DropdownMenu>
            </SidebarMenuItem>
        </SidebarMenu>
    );
}
