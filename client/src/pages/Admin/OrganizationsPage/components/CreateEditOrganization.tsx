import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { handleApiFormError } from "@/utils/errorHandler";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import z from "zod";
import AdminService from "@/services/adminService";
import type { Organization } from "@/types/organization";
import { toast } from "sonner";
import { useEffect } from "react";

const createOrganizationSchema = z.object({
    name: z
        .string()
        .min(3, "Organization name must be at least 3 characters")
        .max(100, "Organization name must be at most 100 characters"),
    domain: z.string().optional(),
    is_active: z.boolean(),
});

type CreateEditOrganizationFormData = z.infer<typeof createOrganizationSchema>;

interface CreateEditOrganizationProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    organization?: Organization;
}

const CreateEditOrganization = ({ isOpen, onClose, onConfirm, organization }: CreateEditOrganizationProps) => {
    const form = useForm<CreateEditOrganizationFormData>({
        resolver: zodResolver(createOrganizationSchema),
        defaultValues: {
            name: organization?.name || "",
            domain: organization?.domain || "",
            is_active: organization?.is_active ?? true,
        },
    });

    useEffect(() => {
        form.reset({
            name: organization?.name || "",
            domain: organization?.domain || "",
            is_active: organization?.is_active ?? true,
        });
    }, [organization?.id]);

    const onSubmit = async (data: CreateEditOrganizationFormData) => {
        try {
            if (organization) {
                await AdminService.updateOrganization(organization.id, data);
                toast.success("Organization updated successfully");
            } else {
                await AdminService.createOrganization(data);
                form.reset();
                toast.success("Organization created successfully");
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
                    <DialogTitle>{organization ? "Edit Organization" : "Create Organization"}</DialogTitle>
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
                            name="domain"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Domain</FormLabel>
                                    <FormControl>
                                        <Input placeholder="Enter domain" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="is_active"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Active</FormLabel>
                                    <FormControl>
                                        <Switch checked={field.value} onCheckedChange={field.onChange} />
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
                            <Button type="submit">{organization ? "Update Organization" : "Create Organization"}</Button>
                        </div>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
};

export default CreateEditOrganization;
