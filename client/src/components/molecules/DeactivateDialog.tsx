import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "../ui/button";

interface DeactivateDialogProps {
    isOpen: boolean;
    text?: string;
    onClose: () => void;
    onConfirm: () => void;
}

const DeactivateDialog = ({ isOpen, text, onClose, onConfirm }: DeactivateDialogProps) => {
    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Deactivate</DialogTitle>
                    <DialogDescription>
                        This action will change the status of the {text ? text : "item"} to inactive. Are you sure you
                        want to proceed?
                    </DialogDescription>
                </DialogHeader>
                <div className="mt-4 flex justify-end gap-2">
                    <Button variant="outline" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button variant="destructive" onClick={onConfirm}>
                        Deactivate
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default DeactivateDialog;
