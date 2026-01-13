import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Department } from "@/types/department";
import React, { useState } from "react";
import UsersTab from "./tabs/UsersTab";

interface DepartmentAssignmentsProps {
    isOpen: boolean;
    selectedDepartment: Department | null;
    onClose: () => void;
}

const DepartmentAssignments = ({ isOpen, selectedDepartment, onClose }: DepartmentAssignmentsProps) => {
    const [activeTab, setActiveTab] = useState("details");

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent
                aria-describedby={undefined}
                className="max-w-[95vw] md:max-w-2xl lg:max-w-5xl xl:max-w-6xl min-h-[90vh] px-4 flex flex-col"
            >
                <DialogHeader>
                    <DialogTitle>Department Assignments</DialogTitle>
                </DialogHeader>
                <div className="flex-1 overflow-hidden flex flex-col">
                    <Tabs
                        value={activeTab}
                        onValueChange={setActiveTab}
                        className="w-full flex flex-col flex-1 overflow-hidden"
                    >
                        <TabsList className="grid w-full grid-cols-1">
                            <TabsTrigger value="users">Users</TabsTrigger>
                        </TabsList>

                        <TabsContent value="users">
                            <UsersTab selectedDepartment={selectedDepartment} />
                        </TabsContent>
                    </Tabs>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default React.memo(DepartmentAssignments);