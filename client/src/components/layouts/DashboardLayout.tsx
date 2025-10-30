import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { Separator } from "@/components/ui/separator";
import NavBreadcrumb from "@/components/nav-breadcrumb";

type DashboardLayoutProps = {
    children: React.ReactNode;
};

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }: DashboardLayoutProps) => {
    return (
        <SidebarProvider>
            <AppSidebar />
            <SidebarInset>
                <header className="flex h-16 shrink-0 items-center gap-2 border-b">
                    <div className="flex items-center gap-2 px-3">
                        <SidebarTrigger className="-ml-1" />
                        <Separator orientation="vertical" className="mr-2 data-[orientation=vertical]:h-4" />
                        <NavBreadcrumb />
                    </div>
                </header>
                <main className="flex-1 overflow-y-auto">{children}</main>
            </SidebarInset>
        </SidebarProvider>
    );
};

export default DashboardLayout;
