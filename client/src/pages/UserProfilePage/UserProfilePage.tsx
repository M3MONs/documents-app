import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import AuthService from "@/services/authService";
import { useAuth } from "@/context/AuthContext";
import { handleApiFormError } from "@/utils/errorHandler";
import DashboardLayout from "@/components/layouts/DashboardLayout";
import { toast } from "sonner";
import { useState } from "react";
import { Mail, Lock } from "lucide-react";
import { UserInfoCard } from "./components/UserInfoCard";
import { OrganizationsCard } from "./components/OrganizationsCard";
import { DepartmentsCard } from "./components/DepartmentsCard";
import { ChangeEmailDialog } from "./components/ChangeEmailDialog";
import { ChangePasswordDialog } from "./components/ChangePasswordDialog";

const updateEmailSchema = z.object({
    email: z.string().email("Invalid email address"),
});

const changePasswordSchema = z
    .object({
        currentPassword: z.string().min(1, "Current password is required"),
        newPassword: z
            .string()
            .min(8, "Password must be at least 8 characters")
            .max(100, "Password must be at most 100 characters"),
        confirmPassword: z.string(),
    })
    .refine((data) => data.newPassword === data.confirmPassword, {
        message: "Passwords must match",
        path: ["confirmPassword"],
    });

type UpdateEmailFormData = z.infer<typeof updateEmailSchema>;
type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

const UserProfilePage = () => {
    const { user, setUser } = useAuth();
    const [isEmailDialogOpen, setIsEmailDialogOpen] = useState(false);
    const [isPasswordDialogOpen, setIsPasswordDialogOpen] = useState(false);

    const emailForm = useForm<UpdateEmailFormData>({
        resolver: zodResolver(updateEmailSchema),
        defaultValues: {
            email: user?.email || "",
        },
    });

    const passwordForm = useForm<ChangePasswordFormData>({
        resolver: zodResolver(changePasswordSchema),
        defaultValues: {
            currentPassword: "",
            newPassword: "",
            confirmPassword: "",
        },
    });

    const onEmailSubmit = async (data: UpdateEmailFormData) => {
        try {
            await AuthService.updateEmail(data);
            setUser({ ...user!, email: data.email });
            toast.success("Email updated successfully");
            emailForm.reset({ email: data.email });
            setIsEmailDialogOpen(false);
        } catch (err: unknown) {
            handleApiFormError(err, emailForm);
        }
    };

    const onPasswordSubmit = async (data: ChangePasswordFormData) => {
        try {
            await AuthService.changePassword({
                current_password: data.currentPassword,
                new_password: data.newPassword,
            });
            toast.success("Password changed successfully");
            passwordForm.reset();
            setIsPasswordDialogOpen(false);
        } catch (err: unknown) {
            handleApiFormError(err, passwordForm);
        }
    };

    return (
        <DashboardLayout>
            <div className="p-6 space-y-6">
                <h1 className="text-2xl font-bold">User Profile</h1>

                <UserInfoCard user={user} />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Mail className="h-5 w-5" />
                                Change Email
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground mb-4">
                                Update your email address.
                            </p>
                            <Button onClick={() => setIsEmailDialogOpen(true)}>
                                Change Email
                            </Button>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Lock className="h-5 w-5" />
                                Change Password
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-muted-foreground mb-4">
                                Update your password to keep your account secure.
                            </p>
                            <Button onClick={() => setIsPasswordDialogOpen(true)}>
                                Change Password
                            </Button>
                        </CardContent>
                    </Card>
                </div>

                <OrganizationsCard user={user} />

                <DepartmentsCard user={user} />

                <ChangeEmailDialog
                    isOpen={isEmailDialogOpen}
                    onOpenChange={setIsEmailDialogOpen}
                    form={emailForm}
                    onSubmit={onEmailSubmit}
                />

                <ChangePasswordDialog
                    isOpen={isPasswordDialogOpen}
                    onOpenChange={setIsPasswordDialogOpen}
                    form={passwordForm}
                    onSubmit={onPasswordSubmit}
                />
            </div>
        </DashboardLayout>
    );
};

export default UserProfilePage;