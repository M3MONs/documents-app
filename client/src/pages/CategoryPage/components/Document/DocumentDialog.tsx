import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import type { ContentItem } from "@/types/categoryContent";
import { FileText } from "lucide-react";
import React from "react";
import DocumentViewer from "./DocumentViewer";

interface DocumentDialogProps {
    selectedDocument: ContentItem | null;
    setSelectedDocument: (document: ContentItem | null) => void;
}

const DocumentDialog: React.FC<DocumentDialogProps> = ({ selectedDocument, setSelectedDocument }) => {
    return (
        <Dialog open={!!selectedDocument} onOpenChange={(open) => !open && setSelectedDocument(null)}>
            <DialogContent className="sm:max-w-none sm:w-screen sm:h-screen md:max-w-[80vw] md:max-h-[90vh] md:w-[80vw] md:h-[90vh] overflow-hidden flex flex-col">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <FileText className="h-5 w-5 text-primary" />
                        {selectedDocument?.name}
                    </DialogTitle>
                </DialogHeader>

                <div className="flex-1 overflow-y-auto">{selectedDocument && <DocumentViewer document={selectedDocument} />}</div>
            </DialogContent>
        </Dialog>
    );
};

export default DocumentDialog;
