import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"; // Dodaj import Tabs
import type { User } from "@/types/user";
import ChangePasswordTab from "./tabs/ChangePasswordTab";
import EditUserTab from "./tabs/EditUserTab";
import OrganizationsTab from "./tabs/OrganizationsTab";
import { useRef, useState } from "react";
import { useAuth } from "@/context/AuthContext";

interface EditUserProps {
    user?: User;
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
}

const EditUser = ({ user, isOpen, onClose, onConfirm }: EditUserProps) => {
    if (!user) return null;
    const {user: loggedUser } = useAuth();

    const [activeTab, setActiveTab] = useState("details");
    const editUserRef = useRef<any>(null);
    const changePasswordRef = useRef<any>(null);
    const organizationRef = useRef<any>(null);

    const handleSave = async () => {
        if (activeTab === "details") {
            await editUserRef.current?.submit();
        } else if (activeTab === "password") {
            await changePasswordRef.current?.submit();
        } else if (activeTab === "organization") {
            await organizationRef.current?.submit();
        }
        onConfirm();
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent
                aria-describedby={undefined}
                className="max-w-[95vw] md:max-w-2xl lg:max-w-3xl px-4 flex flex-col"
            >
                <DialogHeader>
                    <DialogTitle>Edit User</DialogTitle>
                </DialogHeader>
                <div>
                    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                        <TabsList className={"grid w-full grid-cols-1 h-auto gap-2 mb-4" + (loggedUser?.is_superuser ? " sm:grid-cols-3" : " sm:grid-cols-2")}>
                            <TabsTrigger value="details">User Details</TabsTrigger>
                            {loggedUser?.is_superuser && <TabsTrigger value="password">Change Password</TabsTrigger>}
                            <TabsTrigger value="organization">Organizations</TabsTrigger>
                        </TabsList>

                        <EditUserTab ref={editUserRef} user={user} />
                        {loggedUser?.is_superuser && <ChangePasswordTab ref={changePasswordRef} user={user} />}
                        <OrganizationsTab ref={organizationRef} user={user} />
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
