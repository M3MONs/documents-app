import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "../ui/button";

interface ActivateDialogProps {
    isOpen: boolean;
    text?: string;
    onClose: () => void;
    onConfirm: () => void;
}

const ActivateDialog = ({ isOpen, text, onClose, onConfirm }: ActivateDialogProps) => {
    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Activate</DialogTitle>
                    <DialogDescription>
                        This action will change the status of the {text ? text : "item"} to active. Are you sure you
                        want to proceed?
                    </DialogDescription>
                </DialogHeader>
                <div className="mt-4 flex justify-end gap-2">
                    <Button variant="outline" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button variant="default" className="bg-green-600" onClick={onConfirm}>
                        Activate
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default ActivateDialog;
