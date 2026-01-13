import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { File } from "lucide-react";
import { useState } from "react";
import SettingsTab from "./tabs/document/SettingsTab";

interface DocumentManageDialogProps {
    isOpen: boolean;
    selectedDocument: any | null;
    onClose: () => void;
}

const DocumentManageDialog = ({ isOpen, selectedDocument, onClose }: DocumentManageDialogProps) => {
    const [activeTab, setActiveTab] = useState("settings");

    return (
        <Dialog
            open={isOpen}
            onOpenChange={(open) => {
                if (!open) onClose();
            }}
        >
            <DialogContent
                aria-describedby="Manage Document"
                className="sm:max-w-none sm:w-screen sm:h-screen md:max-w-[600px] md:max-h-[500px] overflow-hidden flex flex-col"
            >
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <File className="h-5 w-5 text-primary" />
                        {selectedDocument?.name}
                    </DialogTitle>
                </DialogHeader>

                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full h-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="settings">Document Settings</TabsTrigger>
                        <TabsTrigger value="location">Location</TabsTrigger>
                    </TabsList>
                    <TabsContent value="settings" className="">
                        <SettingsTab selectedDocument={selectedDocument} />
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    );
};

export default DocumentManageDialog;
