import React, { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import AdminService from "@/services/adminService";
import { handleApiError } from "@/utils/errorHandler";
import { toast } from "sonner";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

interface SettingsTabProps {
    selectedFolder: any | null;
}

const SettingsTab: React.FC<SettingsTabProps> = ({ selectedFolder }) => {
    const queryClient = useQueryClient();
    const [isPrivate, setIsPrivate] = useState(selectedFolder?.is_private || false);

    useEffect(() => {
        setIsPrivate(selectedFolder?.is_private || false);
    }, [selectedFolder]);

    const setPrivacyMutation = useMutation({
        mutationFn: (isPrivate: boolean) => AdminService.setFolderPrivacy(selectedFolder.id, isPrivate),
        onSuccess: () => {
            toast.success("Folder privacy updated successfully");
            queryClient.invalidateQueries({ queryKey: ["category-content"] });
        },
        onError: (error) => {
            handleApiError(error);
        },
    });

    const handlePrivacyChange = (checked: boolean) => {
        setIsPrivate(checked);
        setPrivacyMutation.mutate(checked);
    };

    return (
        <div className="p-4 space-y-4">
            <div className="flex items-center space-x-2">
                <Switch
                    id="private-mode"
                    checked={isPrivate}
                    onCheckedChange={handlePrivacyChange}
                    disabled={setPrivacyMutation.isPending}
                />
                <Label htmlFor="private-mode">Private Folder</Label>
            </div>
            <p className="text-sm text-muted-foreground">
                When enabled, only assigned users and departments can access this folder.
            </p>
        </div>
    );
};

export default React.memo(SettingsTab);