import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AdminService from "@/services/adminService";
import { handleApiFormError } from "@/utils/errorHandler";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { File } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
});

type FormData = z.infer<typeof schema>;

interface DocumentManageDialogProps {
  selectedDocument: any | null;
  setSelectedDocument: (document: any | null) => void;
}

const DocumentManageDialog = ({ selectedDocument, setSelectedDocument }: DocumentManageDialogProps) => {
  const [activeTab, setActiveTab] = useState("settings");
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
      setSelectedDocument(null);
    },
    onError: (error) => {
      handleApiFormError(error, form);
    },
  });

  const onSubmit = (data: FormData) => {
    updateMutation.mutate(data);
  };

  return (
    <Dialog
      open={!!selectedDocument}
      onOpenChange={(open) => {
        if (!open) setSelectedDocument(null);
      }}
    >
      <DialogContent
        aria-describedby="Manage Document"
        className="sm:max-w-none sm:w-screen sm:h-screen md:max-w-[600px] md:max-h-[500px] overflow-hidden flex flex-col"
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <File className="h-5 w-5 text-primary" />
            {selectedDocument?.name}
          </DialogTitle>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full h-full">
          <TabsList className="grid w-full grid-cols-1">
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>
          <TabsContent value="settings" className="">
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className="py-4 space-y-4 h-full flex flex-col justify-between"
            >
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
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default DocumentManageDialog;
