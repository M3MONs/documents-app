import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { TabsContent } from "@/components/ui/tabs";
import type { User } from "@/types/user";
import { useForm } from "react-hook-form";
import z from "zod";
import { forwardRef, useImperativeHandle } from "react";
import AdminService from "@/services/adminService";
import { handleApiFormError } from "@/utils/errorHandler";
import { toast } from "sonner";
import { zodResolver } from "@hookform/resolvers/zod";

const changePasswordSchema = z
    .object({
        password: z
            .string()
            .min(8, "Password must be at least 8 characters")
            .max(100, "Password must be at most 100 characters"),
        confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
        message: "Passwords must match and both fields must be filled if changing password",
        path: ["confirmPassword"],
    });

type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

interface ChangePasswordTabProps {
    user: User;
}

const ChangePasswordTab = forwardRef<any, ChangePasswordTabProps>(({ user }, ref) => {
    const form = useForm<ChangePasswordFormData>({
        resolver: zodResolver(changePasswordSchema),
        defaultValues: {
            password: "",
            confirmPassword: "",
        },
    });

    const onSubmit = async (data: ChangePasswordFormData) => {
        try {
            await AdminService.resetUserPassword(user.id, { new_password: data.password });
            toast.success("Password changed successfully");
            form.reset();
        } catch (err: any) {
            handleApiFormError(err, form);
        }
    };

    useImperativeHandle(ref, () => ({
        submit: () => form.handleSubmit(onSubmit)(),
    }));

    return (
        <TabsContent value="password" className="space-y-4">
            <Form {...form}>
                <form className="space-y-4 w-full max-w-md">
                    <FormField
                        control={form.control}
                        name="password"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Password</FormLabel>
                                <FormControl>
                                    <Input type="password" placeholder="Password" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="confirmPassword"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Confirm Password</FormLabel>
                                <FormControl>
                                    <Input type="password" placeholder="Confirm Password" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    {form.formState.errors.root && (
                        <div className="text-destructive text-sm">{form.formState.errors.root.message}</div>
                    )}
                </form>
            </Form>
        </TabsContent>
    );
});

ChangePasswordTab.displayName = "ChangePasswordTab";

export default ChangePasswordTab;
