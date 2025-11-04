import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface DeactivateDialogProps {
    isOpen: boolean;
    text?: string;
    title?: string;
    description?: string;
    onClose: () => void;
    onConfirm: () => void;
}

const DeactivateDialog = ({ isOpen, text, title, description, onClose, onConfirm }: DeactivateDialogProps) => {
    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>{title ? title : "Deactivate"}</DialogTitle>
                    <DialogDescription>
                        {description ? description : `This action will change the status of the ${text ? text : "item"} to inactive. Are you sure you want to proceed?`}
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter className="mt-4 flex justify-end gap-2">
                    <Button variant="outline" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button variant="destructive" onClick={onConfirm}>
                        Deactivate
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};

export default DeactivateDialog;
