import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Plus, Trash2 } from "lucide-react";
import { Combobox } from "@/components/ui/combobox";
import AdminService from "@/services/adminService";
import { handleApiError } from "@/utils/errorHandler";
import { toast } from "sonner";
import type { User } from "@/types/user";
import type { Organization } from "@/types/organization";
import type { Role } from "@/types/role";
import type { UserOrganizationRole } from "@/types/userOrganizationRole";

const OrganizationRolesTab = () => {
    const [selectedUserId, setSelectedUserId] = useState<string>("");
    const [selectedOrganizationId, setSelectedOrganizationId] = useState<string>("");
    const [selectedRoleId, setSelectedRoleId] = useState<string>("");

    const { data: users } = useQuery({
        queryKey: ["admin/users"],
        queryFn: () => AdminService.getUsers({ page: 1, pageSize: 1000 }),
    });

    const { data: organizations } = useQuery({
        queryKey: ["admin/organizations"],
        queryFn: () => AdminService.getOrganizations({ page: 1, pageSize: 1000 }),
    });

    const { data: roles } = useQuery({
        queryKey: ["admin/roles"],
        queryFn: () => AdminService.getRoles({ page: 1, pageSize: 1000 }),
    });

    const { data: userOrganizationRoles, isLoading: uorLoading, refetch: refetchUOR } = useQuery({
        queryKey: ["admin/user-organization-roles", selectedUserId],
        queryFn: () => AdminService.getUserOrganizationRoles(selectedUserId),
        enabled: !!selectedUserId,
    });

    const userOptions = useMemo(() => {
        if (!users?.items) return [];
        return users.items.map((user: User) => ({
            value: user.id,
            label: user.username,
        }));
    }, [users?.items]);

    const handleAssignRole = async () => {
        if (!selectedUserId || !selectedOrganizationId || !selectedRoleId) {
            return;
        }

        try {
            await AdminService.assignRoleToUserInOrganization({
                user_id: selectedUserId,
                organization_id: selectedOrganizationId,
                role_id: selectedRoleId,
                is_primary: false,
            });
            refetchUOR();
            setSelectedRoleId("");
            toast.success("Role assigned successfully!");
        } catch (error) {
            handleApiError(error);
        }
    };

    const handleRemoveRole = async (uorId: string) => {
        try {
            await AdminService.removeRoleFromUserInOrganization(uorId);
            refetchUOR();
            toast.success("Role removed successfully!");
        } catch (error) {
            handleApiError(error);
        }
    };

    const handleUserChange = (userId: string) => {
        setSelectedUserId(userId);
        setSelectedOrganizationId("");
        setSelectedRoleId("");
    };

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Assign Roles to Users in Organizations</CardTitle>
                    <CardDescription>
                        Select a user and organization, then choose a role to assign.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="user-select">User</Label>
                            <Combobox
                                options={userOptions}
                                value={selectedUserId}
                                onValueChange={handleUserChange}
                                placeholder="Select a user..."
                                searchPlaceholder="Search users..."
                                emptyMessage="No users found."
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="organization-select">Organization</Label>
                            <Select
                                value={selectedOrganizationId}
                                onValueChange={setSelectedOrganizationId}
                                disabled={!selectedUserId}
                            >
                                <SelectTrigger className="w-[100%]">
                                    <SelectValue placeholder={selectedUserId ? "Select an organization" : "Select a user first"} />
                                </SelectTrigger>
                                <SelectContent>
                                    {organizations?.items?.map((org: Organization) => (
                                        <SelectItem key={org.id} value={org.id}>
                                            {org.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="role-select">Role</Label>
                            <Select
                                value={selectedRoleId}
                                onValueChange={setSelectedRoleId}
                                disabled={!selectedOrganizationId}
                            >
                                <SelectTrigger className="w-[100%]">
                                    <SelectValue placeholder={selectedOrganizationId ? "Select a role" : "Select an organization first"} />
                                </SelectTrigger>
                                <SelectContent>
                                    {roles?.items?.map((role: Role) => (
                                        <SelectItem key={role.id} value={role.id}>
                                            {role.name}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <Button
                            onClick={handleAssignRole}
                            disabled={!selectedUserId || !selectedOrganizationId || !selectedRoleId}
                            className="w-full"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Assign Role
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {selectedUserId && (
                <Card>
                    <CardHeader>
                        <CardTitle>User Organization Roles</CardTitle>
                        <CardDescription>
                            Roles assigned to the selected user across organizations.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {uorLoading ? (
                            <div>Loading...</div>
                        ) : userOrganizationRoles?.length > 0 ? (
                            <div className="space-y-2">
                                {userOrganizationRoles.map((uor: UserOrganizationRole) => (
                                    <div key={uor.id} className="flex items-center justify-between p-3 border rounded-lg">
                                        <div className="flex items-center space-x-2">
                                            <span className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs font-medium text-secondary-foreground">
                                                {uor.role?.name}
                                            </span>
                                            <span>in</span>
                                            <span className="inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium">
                                                {uor.organization?.name}
                                            </span>
                                            {uor.is_primary && (
                                                <span className="inline-flex items-center rounded-md bg-primary px-2 py-1 text-xs font-medium text-primary-foreground">
                                                    Primary
                                                </span>
                                            )}
                                        </div>
                                        <Button
                                            variant="destructive"
                                            size="sm"
                                            onClick={() => handleRemoveRole(uor.id)}
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center text-muted-foreground py-8">
                                No roles assigned to this user.
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default OrganizationRolesTab;
