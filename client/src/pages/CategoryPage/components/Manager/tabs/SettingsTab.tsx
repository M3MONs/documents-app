import React, { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import AdminService from "@/services/adminService";
import { handleApiError } from "@/utils/errorHandler";
import { toast } from "sonner";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  is_private: z.boolean(),
  apply_to_children: z.boolean().optional(),
});

type FormData = z.infer<typeof schema>;

interface SettingsTabProps {
  selectedFolder: any | null;
}

const HELPER_TEXT_PRIVATE =
  "When enabled, the folder and all its subfolders will be set to private. Only assigned users and departments can access them.";
const HELPER_TEXT_PUBLIC =
  "When disabled, only this folder will be set to public. Subfolders will remain in their current state.";

const SettingsTab: React.FC<SettingsTabProps> = ({ selectedFolder }) => {
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: selectedFolder?.name || "",
      is_private: selectedFolder?.is_private || false,
      apply_to_children: false,
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: FormData) => AdminService.updateFolder(selectedFolder.id, data),
    onSuccess: () => {
      toast.success("Folder updated successfully");
      queryClient.invalidateQueries({ queryKey: ["categoryContent"] });
    },
    onError: (error) => {
      handleApiError(error);
    },
  });

  useEffect(() => {
    reset({
      name: selectedFolder?.name || "",
      is_private: selectedFolder?.is_private || false,
      apply_to_children: false,
    });
  }, [selectedFolder, reset]);

  const onSubmit = (data: FormData) => {
    updateMutation.mutate(data);
  };

  const isPrivate = watch("is_private");
  const applyToChildren = watch("apply_to_children");

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="p-4 space-y-4">
      <div>
        <Label htmlFor="name" className="mb-2">
          Folder Name
        </Label>
        <Input id="name" {...register("name")} />
        {errors.name && <p className="text-sm text-red-500">{errors.name.message}</p>}
      </div>
      <div className="flex items-center space-x-2">
        <Switch
          id="private-mode"
          checked={isPrivate}
          onCheckedChange={(checked) => setValue("is_private", checked === true)}
          disabled={updateMutation.isPending}
        />
        <Label htmlFor="private-mode">Private Folder</Label>
      </div>
      <p className="text-sm text-muted-foreground">{isPrivate ? HELPER_TEXT_PRIVATE : HELPER_TEXT_PUBLIC}</p>
      {!isPrivate && (
        <div className="flex items-center space-x-2">
          <Checkbox
            id="apply-to-children"
            checked={applyToChildren}
            onCheckedChange={(checked) => setValue("apply_to_children", checked === true)}
            disabled={updateMutation.isPending}
          />
          <Label htmlFor="apply-to-children">Apply to all subfolders as well</Label>
        </div>
      )}
      <Button type="submit" disabled={updateMutation.isPending}>
        {updateMutation.isPending ? "Saving..." : "Save"}
      </Button>
    </form>
  );
};

export default React.memo(SettingsTab);
