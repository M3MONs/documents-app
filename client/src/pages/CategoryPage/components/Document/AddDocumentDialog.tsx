import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { FileText } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import AdminService from "@/services/adminService";
import { toast } from "sonner";
import { handleApiError } from "@/utils/errorHandler";
import { useMutation, useQueryClient } from "@tanstack/react-query";

const formSchema = z.object({
  name: z.string().min(1, "Name is required"),
  file: z.instanceof(File).refine((file) => file.size > 0, "File is required"),
});

type DocumentFormData = z.infer<typeof formSchema>;

interface AddDocumentDialogProps {
  isOpen: boolean;
  onClose: () => void;
  currentFolderId?: string;
  categoryId?: string;
}

const AddDocumentDialog = ({
  isOpen,
  onClose,
  currentFolderId: _currentFolderId,
  categoryId: _categoryId,
}: AddDocumentDialogProps) => {
  const queryClient = useQueryClient();

  const form = useForm<DocumentFormData>({
    resolver: zodResolver(formSchema),
  });

  const addMutation = useMutation({
    mutationFn: (data: FormData) => AdminService.addDocument(data),
    onSuccess: () => {
      toast.success("Document added successfully");
      queryClient.invalidateQueries({ queryKey: ["categoryContent"] });
    },
    onError: (error) => {
      handleApiError(error);
    },
  });

  const onSubmit = async (data: DocumentFormData) => {
    if (!_categoryId) return toast.error("Category ID is missing.");

    try {
      const formData = new FormData();
      formData.append("name", data.name);
      formData.append("file", data.file);
      formData.append("category_id", _categoryId);

      if (_currentFolderId) {
        formData.append("folder_id", _currentFolderId);
      }

      await addMutation.mutateAsync(formData);
      form.reset();
      onClose();
    } catch (err) {
      handleApiError(err);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-none sm:w-screen sm:h-screen md:max-w-[600px] md:max-h-[600px] md:w-[100%] md:h-[100%] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            Add Document
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 p-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Document name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="file"
                render={({ field: { value, onChange, ...field } }) => (
                  <FormItem>
                    <FormLabel>File</FormLabel>
                    <FormControl>
                      <Input type="file" accept="*/*" onChange={(e) => onChange(e.target.files?.[0])} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="mt-2 ">
                Add Document
              </Button>
            </form>
          </Form>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AddDocumentDialog;
