import { Button } from "@/components/ui/button";
import { Dialog, DialogClose, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { handleApiError, handleApiFormError } from "@/utils/errorHandler";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import z from "zod";
import AdminService from "@/services/adminService";
import { toast } from "sonner";
import { useEffect, useState } from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Category } from "@/types/category";
import type { Organization } from "@/types/organization";

const createCategorySchema = z.object({
    name: z
        .string()
        .min(3, "Category name must be at least 3 characters")
        .max(100, "Category name must be at most 100 characters"),
    description: z.string().max(255, "Description must be at most 255 characters").optional(),
    organization_id: z.string("Organization ID must be a valid UUID"),
});

type CreateEditCategoryFormData = z.infer<typeof createCategorySchema>;

interface CreateEditCategoryProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    category?: Category;
}

const CreateEditCategory = ({ isOpen, onClose, onConfirm, category }: CreateEditCategoryProps) => {
    const [organizations, setOrganizations] = useState<Organization[]>([]);

    const form = useForm<CreateEditCategoryFormData>({
        resolver: zodResolver(createCategorySchema),
        defaultValues: {
            name: category?.name || "",
            description: category?.description || "",
            organization_id: category?.organization?.id || "",
        },
    });

    useEffect(() => {
        form.reset({
            name: category?.name || "",
            description: category?.description || "",
            organization_id: category?.organization?.id || "",
        });
    }, [category?.id]);

    useEffect(() => {
        const fetchOrganizations = async () => {
            try {
                const data = await AdminService.getOrganizations({ page: 1, pageSize: 100 });
                setOrganizations(data.items);
            } catch (err: any) {
                handleApiError(err);
            }
        };

        fetchOrganizations();
    }, []);

    const handleOrganizationChange = (value: string) => {
        form.setValue("organization_id", value);
    };

    const onSubmit = async (data: CreateEditCategoryFormData) => {
        try {
            if (category) {
                await AdminService.updateCategory(category.id, data);
                toast.success("Category updated successfully");
            } else {
                await AdminService.createCategory(data);
                form.reset();
                toast.success("Category created successfully");
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
                    <DialogTitle>{category ? "Edit Category" : "Create Category"}</DialogTitle>
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
                            name="organization_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Organization</FormLabel>
                                    <FormControl>
                                        <Select {...field} onValueChange={handleOrganizationChange} value={field.value}>
                                            <SelectTrigger className="w-full">
                                                <SelectValue placeholder="Select organization" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {organizations.map((org) => (
                                                    <SelectItem key={org.id} value={org.id}>
                                                        {org.name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
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
                            <Button type="submit">{category ? "Update Category" : "Create Category"}</Button>
                        </div>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
};

export default CreateEditCategory;
