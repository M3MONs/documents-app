import { Dialog, DialogClose, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Category } from "@/types/category";
import React, { useState } from "react";
import DepartmentsTab from "./tabs/DepartmentsTab";

interface CategoryAssignmentsProps {
    isOpen: boolean;
    selectedCategory: Category | null;
    onClose: () => void;
}

const CategoryAssignments = ({ isOpen, selectedCategory, onClose }: CategoryAssignmentsProps) => {
    const [activeTab, setActiveTab] = useState("departments");

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent
                aria-describedby={undefined}
                className="max-w-[95vw] md:max-w-2xl lg:max-w-5xl xl:max-w-6xl min-h-[90vh] px-4 flex flex-col"
            >
                <DialogHeader>
                    <DialogTitle>Category Assignments</DialogTitle>
                </DialogHeader>
                <div className="flex-1 overflow-hidden flex flex-col">
                    <Tabs
                        value={activeTab}
                        onValueChange={setActiveTab}
                        className="w-full flex flex-col flex-1 overflow-hidden"
                    >
                        <TabsList className="grid w-full grid-cols-1">
                            <TabsTrigger value="departments">Departments</TabsTrigger>
                        </TabsList>
                        <TabsContent value="departments">
                            <DepartmentsTab selectedCategory={selectedCategory} />
                        </TabsContent>
                    </Tabs>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default React.memo(CategoryAssignments);