import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { handleApiFormError } from "@/utils/errorHandler";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import z from "zod";
import AdminService from "@/services/adminService";
import { toast } from "sonner";
import { useEffect } from "react";
import type { Role } from "@/types/role";

const createRoleSchema = z.object({
    name: z
        .string()
        .min(3, "Role name must be at least 3 characters")
        .max(100, "Role name must be at most 100 characters"),
    description: z.string().optional(),
});

type CreateEditRoleFormData = z.infer<typeof createRoleSchema>;

interface CreateEditRoleProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    role?: Role | null;
}

const CreateEditRole = ({ isOpen, onClose, onConfirm, role }: CreateEditRoleProps) => {
    const form = useForm<CreateEditRoleFormData>({
        resolver: zodResolver(createRoleSchema),
        defaultValues: {
            name: role?.name || "",
            description: role?.description || "",
        },
    });

    useEffect(() => {
        form.reset({
            name: role?.name || "",
            description: role?.description || "",
        });
    }, [role?.id]);

    const onSubmit = async (data: CreateEditRoleFormData) => {
        try {
            if (role) {
                await AdminService.updateRole(role.id, data);
                toast.success("Role updated successfully");
            } else {
                await AdminService.createRole(data);
                form.reset();
                toast.success("Role created successfully");
            }
            onConfirm();
        } catch (err: any) {
            handleApiFormError(err, form);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent aria-describedby={undefined}>
                <DialogHeader>
                    <DialogTitle>{role ? "Edit Role" : "Create Role"}</DialogTitle>
                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 w-full max-w-md">
                        <FormField
                            control={form.control}
                            name="name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Name</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Enter name" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="description"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Description</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Enter description" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        {form.formState.errors.root && (
                            <div className="text-destructive text-sm">{form.formState.errors.root.message}</div>
                        )}

                        <div className="mt-4 flex justify-between gap-2">
                            <DialogClose asChild>
                                <Button type="button" variant="secondary">
                                    Cancel
                                </Button>
                            </DialogClose>
                            <Button type="submit">{role ? "Update Role" : "Create Role"}</Button>
                        </div>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
};

export default CreateEditRole;
