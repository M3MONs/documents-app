import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { TabsContent } from "@/components/ui/tabs";
import type { User } from "@/types/user";
import { useForm } from "react-hook-form";
import z from "zod";
import { forwardRef, useImperativeHandle } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import AdminService from "@/services/adminService";
import { toast } from "sonner";
import { handleApiFormError } from "@/utils/errorHandler";

const editUserSchema = z.object({
    username: z
        .string()
        .min(3, "Username must be at least 3 characters")
        .max(50, "Username must be at most 50 characters"),
    email: z.email("Invalid email address").optional().or(z.literal("")),
});

type EditUserFormData = z.infer<typeof editUserSchema>;

interface EditUserTabProps {
    user: User;
}

const EditUserTab = forwardRef<any, EditUserTabProps>(({ user }, ref) => {
    const form = useForm<EditUserFormData>({
        resolver: zodResolver(editUserSchema),
        defaultValues: {
            username: user.username,
            email: user.email || "",
        },
    });

    const onSubmit = async (data: EditUserFormData) => {
        try {
            await AdminService.updateUser(user.id, { email: data.email });
            toast.success("User updated successfully");
        } catch (err: any) {
            handleApiFormError(err, form);
        }
    };

    useImperativeHandle(ref, () => ({
        submit: () => form.handleSubmit(onSubmit)(),
    }));

    return (
        <TabsContent value="details" className="space-y-4">
            <Form {...form}>
                <form className="space-y-4 w-full max-w-md">
                    <FormField
                        control={form.control}
                        name="username"
                        disabled={true}
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Username</FormLabel>
                                <FormControl>
                                    <Input placeholder="Enter username" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="email"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Email</FormLabel>
                                <FormControl>
                                    <Input placeholder="Email" {...field} />
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

EditUserTab.displayName = "EditUserTab";

export default EditUserTab;
