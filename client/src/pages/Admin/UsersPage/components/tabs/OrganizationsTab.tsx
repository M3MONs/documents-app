import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { TabsContent } from "@/components/ui/tabs";
import type { User } from "@/types/user";
import type { Organization } from "@/types/organization";
import { useForm } from "react-hook-form";
import z from "zod";
import { forwardRef, useImperativeHandle, useEffect, useState, useMemo } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import AdminService from "@/services/adminService";
import { toast } from "sonner";
import { handleApiFormError } from "@/utils/errorHandler";
import { Trash2, Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

const organizationSchema = z.object({
    primary_organization_id: z.string().nullable(),
    additional_organization_ids: z.array(z.string()),
});

type OrganizationFormData = z.infer<typeof organizationSchema>;

const NONE_VALUE = "none";

interface OrganizationsTabProps {
    user: User;
}

const OrganizationsTab = forwardRef<any, OrganizationsTabProps>(({ user }, ref) => {
    const { user: loggedUser } = useAuth();
    const [organizations, setOrganizations] = useState<Organization[]>([]);
    const [isLoadingOrganizations, setIsLoadingOrganizations] = useState(true);
    const [selectedToAdd, setSelectedToAdd] = useState<string>("");

    useEffect(() => {
        const fetchOrganizations = async () => {
            try {
                setIsLoadingOrganizations(true);
                const response = await AdminService.getOrganizations({ page: 1, pageSize: 100 });
                setOrganizations(response.items);
            } catch (err) {
                toast.error("Failed to load organizations");
            } finally {
                setIsLoadingOrganizations(false);
            }
        };
        fetchOrganizations();
    }, []);

    const form = useForm<OrganizationFormData>({
        resolver: zodResolver(organizationSchema),
        defaultValues: {
            primary_organization_id: user.primary_organization?.id || null,
            additional_organization_ids: user.additional_organizations?.map((o) => o.id) || [],
        },
    });

    const resetValues = useMemo(
        () => ({
            primary_organization_id: user.primary_organization?.id || null,
            additional_organization_ids: user.additional_organizations?.map((o) => o.id) || [],
        }),
        [user.primary_organization?.id, user.additional_organizations]
    );

    useEffect(() => {
        form.reset(resetValues);
    }, [resetValues]);

    const currentAdditionalIds = form.watch("additional_organization_ids");

    const availableOrganizations = useMemo(() => {
        return organizations.filter((org) => !currentAdditionalIds.includes(org.id));
    }, [organizations, currentAdditionalIds]);

    const handleAddOrganization = (field: any) => {
        if (selectedToAdd && !currentAdditionalIds.includes(selectedToAdd)) {
            field.onChange([...currentAdditionalIds, selectedToAdd]);
            setSelectedToAdd("");
        }
    };

    const handleRemoveOrganization = (field: any, id: string) => {
        field.onChange(currentAdditionalIds.filter((i) => i !== id));
    };

    const handlePrimaryChange = (value: string) => {
        form.setValue("primary_organization_id", value === NONE_VALUE ? null : value);
    };

    const onSubmit = async (data: OrganizationFormData) => {
        try {
            const currentPrimary = user.primary_organization?.id;
            const currentAdditional = user.additional_organizations?.map((o) => o.id) || [];

            if (data.primary_organization_id !== currentPrimary) {
                if (currentPrimary) {
                    await AdminService.unassignUserFromOrganization(user.id, currentPrimary);
                }
                if (data.primary_organization_id) {
                    await AdminService.assignUserToOrganization(user.id, data.primary_organization_id, {
                        set_primary: true,
                    });
                }
            }

            const toAdd = data.additional_organization_ids.filter((id) => !currentAdditional.includes(id));
            const toRemove = currentAdditional.filter((id) => !data.additional_organization_ids.includes(id));

            await Promise.all([
                ...toRemove.map((id) => AdminService.unassignUserFromOrganization(user.id, id)),
                ...toAdd.map((id) => AdminService.assignUserToOrganization(user.id, id, { set_primary: false })),
            ]);

            toast.success("Organizations updated successfully");
        } catch (err: any) {
            handleApiFormError(err, form);
        }
    };

    useImperativeHandle(ref, () => ({
        submit: () => form.handleSubmit(onSubmit)(),
    }));

    if (isLoadingOrganizations) {
        return (
            <TabsContent value="organization" className="space-y-4 flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
                <span className="ml-2">Loading organizations...</span>
            </TabsContent>
        );
    }

    const renderPrimaryOrganizationSelect = () => {
        return (
            <FormField
                control={form.control}
                name="primary_organization_id"
                render={({ field }) => (
                    <FormItem>
                        <FormLabel>Primary Organization</FormLabel>
                        <Select
                            onValueChange={handlePrimaryChange}
                            value={field.value === null ? NONE_VALUE : field.value}
                        >
                            <FormControl>
                                <SelectTrigger className="w-full">
                                    <SelectValue placeholder="Select primary organization" />
                                </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                                <SelectItem value={NONE_VALUE}>None</SelectItem>
                                {organizations.map((org) => (
                                    <SelectItem key={org.id} value={org.id}>
                                        {org.name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <FormMessage />
                    </FormItem>
                )}
            />
        );
    };

    const AddOrganizationSection = ({ field }: { field: any }) => (
        <div className="flex gap-2">
            <Select value={selectedToAdd} onValueChange={setSelectedToAdd}>
                <SelectTrigger className="flex-1" disabled={availableOrganizations.length === 0}>
                    <SelectValue placeholder="Select organization to add" />
                </SelectTrigger>
                <SelectContent>
                    {availableOrganizations.map((org) => (
                        <SelectItem key={org.id} value={org.id}>
                            {org.name}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
            <Button type="button" onClick={() => handleAddOrganization(field)} disabled={!selectedToAdd}>
                Add
            </Button>
        </div>
    );

    const AdditionalOrganizationsTable = ({ field }: { field: any }) =>
        currentAdditionalIds.length > 0 ? (
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Organization</TableHead>
                        <TableHead className="w-20">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {currentAdditionalIds.map((id) => {
                        const org = organizations.find((o) => o.id === id);
                        if(!org) return null;
                        return (
                            <TableRow key={id}>
                                <TableCell>{org?.name || id}</TableCell>
                                <TableCell>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => handleRemoveOrganization(field, id)}
                                        aria-label={`Remove ${org?.name || id}`}
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </TableCell>
                            </TableRow>
                        );
                    })}
                </TableBody>
            </Table>
        ) : (
            <p className="text-sm text-muted-foreground">No additional organizations assigned.</p>
        );

    const renderAdditionalOrganizationsSelect = () => {
        return (
            <FormField
                control={form.control}
                name="additional_organization_ids"
                render={({ field }) => (
                    <FormItem>
                        <FormLabel>Additional Organizations</FormLabel>
                        <div className="space-y-4">
                            <AddOrganizationSection field={field} />
                            <AdditionalOrganizationsTable field={field} />
                        </div>
                        <FormMessage />
                    </FormItem>
                )}
            />
        );
    };

    return (
        <TabsContent value="organization" className="space-y-4">
            <Form {...form}>
                {loggedUser?.is_superuser && renderPrimaryOrganizationSelect()}
                {renderAdditionalOrganizationsSelect()}
            </Form>
        </TabsContent>
    );
});

OrganizationsTab.displayName = "OrganizationsTab";

export default OrganizationsTab;
