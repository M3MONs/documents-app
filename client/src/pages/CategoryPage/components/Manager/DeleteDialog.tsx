import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import type { ContentItem } from "@/types/categoryContent";
import { File, Folder } from "lucide-react";
import { useState } from "react";

interface DeleteDialogProps {
    isOpen: boolean;
    selectedItem: ContentItem | null;
    onClose: () => void;
    onDelete?: () => void;
}

const DeleteDialog = ({ isOpen, selectedItem, onClose, onDelete }: DeleteDialogProps) => {
    const [confirmationText, setConfirmationText] = useState("");

    const handleDeleteBtnClick = () => {
        if (!onDelete || confirmationText !== selectedItem?.name) return;

        onDelete();
        setConfirmationText("");
        onClose();
    };

    return (
        <Dialog
            open={isOpen}
            onOpenChange={(open) => {
                if (!open) onClose();
            }}
        >
            <DialogContent
                aria-describedby="Delete Item"
                className="sm:max-w-none sm:w-screen sm:h-screen md:max-w-[600px] md:max-h-[500px] overflow-hidden flex flex-col"
            >
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        {selectedItem?.type === "folder" ? (
                            <Folder className="h-5 w-5 text-primary" />
                        ) : (
                            <File className="h-5 w-5 text-primary" />
                        )}
                        Delete {selectedItem?.name}
                    </DialogTitle>
                </DialogHeader>

                <div className="flex-1 overflow-y-auto mt-4">
                    <div>
                        <p>Are you sure you want to delete this {selectedItem?.type}?</p>
                        <Input
                            type="text"
                            className="mt-4"
                            defaultValue={confirmationText}
                            onChange={(e) => setConfirmationText(e.target.value)}
                            placeholder={`Type ${selectedItem?.name} to confirm`}
                        />
                    </div>
                </div>

                <div className="mt-4 flex justify-between gap-2">
                    <Button onClick={onClose}>Cancel</Button>

                    <Button
                        onClick={handleDeleteBtnClick}
                        variant="destructive"
                        disabled={confirmationText !== selectedItem?.name}
                    >
                        Delete
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default DeleteDialog;
