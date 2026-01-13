import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import AdminService from "@/services/adminService";
import { toast } from "sonner";
import { handleApiFormError } from "@/utils/errorHandler";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const schema = z.object({
    name: z.string().min(1, "Name is required"),
});

type FormData = z.infer<typeof schema>;

interface SettingsTabProps {
    selectedDocument: any | null;
}

const SettingsTab: React.FC<SettingsTabProps> = ({ selectedDocument }) => {
    const queryClient = useQueryClient();

    const form = useForm<FormData>({
        resolver: zodResolver(schema),
        defaultValues: {
            name: selectedDocument?.name || "",
        },
    });

    const updateMutation = useMutation({
        mutationFn: (data: FormData) => AdminService.updateDocument(selectedDocument.id, data),
        onSuccess: () => {
            toast.success("Document updated successfully");
            queryClient.invalidateQueries({ queryKey: ["categoryContent"] });
        },
        onError: (error) => {
            handleApiFormError(error, form);
        },
    });

    const onSubmit = (data: FormData) => {
        updateMutation.mutate(data);
    };

    return (
        <form onSubmit={form.handleSubmit(onSubmit)} className="py-4 space-y-4 h-full flex flex-col justify-between">
            <div>
                <div>
                    <Label htmlFor="name" className="mb-3">
                        Document Name
                    </Label>
                    <Input id="name" {...form.register("name")} />
                </div>

                {form.formState.errors.root && (
                    <div className="text-destructive text-sm">{form.formState.errors.root.message}</div>
                )}
            </div>

            <Button type="submit" disabled={updateMutation.isPending}>
                {updateMutation.isPending ? "Saving..." : "Save"}
            </Button>
        </form>
    );
};

export default SettingsTab;
