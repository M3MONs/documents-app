import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import type { ContentItem } from "@/types/categoryContent";
import { FileText } from "lucide-react";
import React from "react";

interface DocumentDialogProps {
    selectedDocument: ContentItem | null;
    setSelectedDocument: (document: ContentItem | null) => void;
}

const DocumentDialog: React.FC<DocumentDialogProps> = ({ selectedDocument, setSelectedDocument }) => {
    return (
        <Dialog open={!!selectedDocument} onOpenChange={(open) => !open && setSelectedDocument(null)}>
            <DialogContent className="max-w-4xl w-full max-h-screen overflow-y-auto">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5 text-primary" />
                        {selectedDocument?.name}
                    </DialogTitle>
                </DialogHeader>

            </DialogContent>
        </Dialog>
    );
};

export default DocumentDialog;
