import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Organization } from "@/types/organization";
import React, { useState } from "react";
import UsersTab from "./tabs/UsersTab";

interface OrganizationAssignmentsProps {
    isOpen: boolean;
    selectedOrganization: Organization | null;
    onClose: () => void;
}

const OrganizationAssignments = ({ isOpen, selectedOrganization, onClose }: OrganizationAssignmentsProps) => {
    const [activeTab, setActiveTab] = useState("details");

    // console.log("Selected Organization:", selectedOrganization);

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent
                aria-describedby={undefined}
                className="max-w-[95vw] md:max-w-2xl lg:max-w-5xl xl:max-w-6xl min-h-[90vh] px-4 flex flex-col"
            >
                <DialogHeader>
                    <DialogTitle>Organization Assignments</DialogTitle>
                </DialogHeader>
                <div className="flex-1 overflow-hidden flex flex-col">
                    <Tabs
                        value={activeTab}
                        onValueChange={setActiveTab}
                        className="w-full flex flex-col flex-1 overflow-hidden"
                    >
                        <TabsList className="grid w-full grid-cols-2">
                            <TabsTrigger value="departments">Departments</TabsTrigger>
                            <TabsTrigger value="users">Users</TabsTrigger>
                        </TabsList>

                        <TabsContent value="departments">
                            <div className="p-4">Manage Departments for {selectedOrganization?.name}</div>
                        </TabsContent>

                        <TabsContent value="users">
                            <UsersTab selectedOrganization={selectedOrganization} />
                        </TabsContent>
                    </Tabs>

                    <div className="mt-4 flex justify-between gap-2 pb-6 border-t pt-4">
                        <DialogClose asChild>
                            <Button type="button" variant="secondary">
                                Cancel
                            </Button>
                        </DialogClose>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default React.memo(OrganizationAssignments);
