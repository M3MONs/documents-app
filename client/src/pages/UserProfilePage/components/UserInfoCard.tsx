import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { User } from "lucide-react";
import type { User as UserType } from "@/types/user";

interface UserInfoCardProps {
    user: UserType | null;
}

export const UserInfoCard = ({ user }: UserInfoCardProps) => {
    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    User Information
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="text-sm font-medium">Username</label>
                        <p className="text-sm text-muted-foreground">{user?.username}</p>
                    </div>
                    <div>
                        <label className="text-sm font-medium">Email</label>
                        <p className="text-sm text-muted-foreground">{user?.email}</p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};