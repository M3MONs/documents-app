import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Building } from "lucide-react";
import type { User as UserType } from "@/types/user";

interface OrganizationsCardProps {
    user: UserType | null;
}

export const OrganizationsCard = ({ user }: OrganizationsCardProps) => {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Building className="h-5 w-5" />
                    Organizations
                </CardTitle>
            </CardHeader>
            <CardContent>
                {user?.primary_organization && (
                    <div className="mb-4">
                        <h4 className="font-medium">Primary Organization</h4>
                        <p className="text-sm text-muted-foreground">{user.primary_organization.name}</p>
                    </div>
                )}
                {user?.additional_organizations && user.additional_organizations.length > 0 && (
                    <div>
                        <h4 className="font-medium mb-2">Additional Organizations</h4>
                        <div className="space-y-2">
                            {user.additional_organizations.map((org) => (
                                <div key={org.id} className="flex items-center gap-2 p-2 border rounded">
                                    <Building className="h-4 w-4" />
                                    <span className="text-sm">{org.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                {!user?.primary_organization && (!user?.additional_organizations || user.additional_organizations.length === 0) && (
                    <p className="text-sm text-muted-foreground">No organizations assigned.</p>
                )}
            </CardContent>
        </Card>
    );
};