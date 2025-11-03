import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"; // Dodaj import Tabs
import type { User } from "@/types/user";
import ChangePasswordTab from "./tabs/ChangePasswordTab";
import EditUserTab from "./tabs/EditUserTab";
import { useRef, useState } from "react";

interface EditUserProps {
    user?: User;
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
}

const EditUser = ({ user, isOpen, onClose, onConfirm }: EditUserProps) => {
    if (!user) return null;

    const [activeTab, setActiveTab] = useState("details");
    const editUserRef = useRef<any>(null);
    const changePasswordRef = useRef<any>(null);

    const handleSave = async () => {
        if (activeTab === "details") {
            await editUserRef.current?.submit();
        } else if (activeTab === "password") {
            await changePasswordRef.current?.submit();
        }
        onConfirm();
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent aria-describedby={undefined}>
                <DialogHeader>
                    <DialogTitle>Edit User</DialogTitle>
                </DialogHeader>
                <div>
                    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                        <TabsList className="grid w-full grid-cols-2">
                            <TabsTrigger value="details">User Details</TabsTrigger>
                            <TabsTrigger value="password">Change Password</TabsTrigger>
                        </TabsList>

                        <EditUserTab ref={editUserRef} user={user} />
                        <ChangePasswordTab ref={changePasswordRef} user={user} />
                    </Tabs>

                    <div className="mt-4 flex justify-between gap-2">
                        <DialogClose asChild>
                            <Button type="button" variant="secondary">
                                Cancel
                            </Button>
                        </DialogClose>
                        <Button onClick={handleSave} type="button">
                            Save Changes
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default EditUser;
