import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import RolesTab from "./tabs/RolesTab";
import OrganizationRolesTab from "./tabs/OrganizationRolesTab";

const AdminRolesPage = () => {
    const [activeTab, setActiveTab] = useState("roles");

    return (
        <div className="p-4">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid w-full grid-cols-1 sm:grid-cols-2 h-auto gap-2 mb-4">
                    <TabsTrigger value="roles">Roles</TabsTrigger>
                    <TabsTrigger value="organization-roles">Organization Roles</TabsTrigger>
                </TabsList>

                <TabsContent value="roles">
                    <RolesTab />
                </TabsContent>

                <TabsContent value="organization-roles">
                    <OrganizationRolesTab />
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default AdminRolesPage;
