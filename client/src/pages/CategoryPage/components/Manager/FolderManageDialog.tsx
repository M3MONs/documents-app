import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Folder } from "lucide-react";
import { useState } from "react";
import DepartmentsTab from "./tabs/DepartmentsTab.tsx";

interface FolderManageDialogProps {
    selectedFolder: any | null;
    setSelectedFolder: (folder: any | null) => void;
}

const FolderManageDialog = ({ selectedFolder, setSelectedFolder }: FolderManageDialogProps) => {
    const [activeTab, setActiveTab] = useState("departments");

    return (
        <Dialog
            open={!!selectedFolder}
            onOpenChange={(open) => {
                if (!open) setSelectedFolder(null);
            }}
        >
            <DialogContent
                aria-describedby="Manage Folder"
                className="sm:max-w-none sm:w-screen sm:h-screen md:max-w-[80vw] md:max-h-[90vh] md:w-[80vw] md:h-[90vh] overflow-hidden flex flex-col"
            >
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <Folder className="h-5 w-5 text-primary" />
                        {selectedFolder?.name}
                    </DialogTitle>
                </DialogHeader>

                <div className="flex-1 overflow-y-auto">
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
                            <DepartmentsTab selectedFolder={selectedFolder} />
                        </TabsContent>
                        <TabsContent value="users">
                            <div className="p-4">Users management coming soon...</div>
                        </TabsContent>
                    </Tabs>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default FolderManageDialog;
