import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users } from "lucide-react";
import type { User as UserType } from "@/types/user";

interface DepartmentsCardProps {
    user: UserType | null;
}

export const DepartmentsCard = ({ user }: DepartmentsCardProps) => {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Departments
                </CardTitle>
            </CardHeader>
            <CardContent>
                {user?.departments && user.departments.length > 0 ? (
                    <div className="space-y-2">
                        {user.departments.map((dept) => (
                            <div key={dept.id} className="flex items-center gap-2 p-2 border rounded">
                                <Users className="h-4 w-4" />
                                <div>
                                    <span className="text-sm font-medium">{dept.name}</span>
                                    <span className="text-xs text-muted-foreground ml-2">({dept.organization.name})</span>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <p className="text-sm text-muted-foreground">No departments assigned.</p>
                )}
            </CardContent>
        </Card>
    );
};