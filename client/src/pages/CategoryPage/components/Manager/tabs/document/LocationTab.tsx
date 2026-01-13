import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ChevronDown, ChevronRight, Folder } from "lucide-react";
import CategoryService from "@/services/categoryService";
import AdminService from "@/services/adminService";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

interface FolderTreeNode {
    id: string;
    name: string;
    children: FolderTreeNode[];
}

interface LocationTabProps {
    selectedDocument: any | null;
    categoryId: string;
}

interface ExpandedState {
    [folderId: string]: boolean;
}

const FolderTreeItem: React.FC<{
    node: FolderTreeNode;
    expanded: ExpandedState;
    onToggleExpand: (folderId: string) => void;
    selectedFolderId: string | null;
    onSelectFolder: (folderId: string) => void;
    level?: number;
}> = ({ node, expanded, onToggleExpand, selectedFolderId, onSelectFolder, level = 0 }) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expanded[node.id];
    const isSelected = selectedFolderId === node.id;

    return (
        <div key={node.id}>
            <div
                className={`flex items-center gap-2 py-2 px-2 rounded-md transition-colors ${
                    isSelected ? "bg-blue-100 dark:bg-blue-900" : "hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
                style={{ paddingLeft: `${level * 1.5}rem` }}
            >
                {hasChildren ? (
                    <button
                        onClick={() => onToggleExpand(node.id)}
                        className="flex-shrink-0 p-0 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
                    >
                        {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                    </button>
                ) : (
                    <div className="w-[18px]" />
                )}

                <RadioGroupItem value={node.id} id={`folder-${node.id}`} />

                <Folder size={16} className="flex-shrink-0 text-amber-600" />

                <Label
                    htmlFor={`folder-${node.id}`}
                    className="flex-1 text-sm font-medium cursor-pointer hover:underline"
                >
                    {node.name}
                </Label>
            </div>

            {hasChildren && isExpanded && (
                <div>
                    {node.children.map((child) => (
                        <FolderTreeItem
                            key={child.id}
                            node={child}
                            expanded={expanded}
                            onToggleExpand={onToggleExpand}
                            selectedFolderId={selectedFolderId}
                            onSelectFolder={onSelectFolder}
                            level={level + 1}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

const LocationTab: React.FC<LocationTabProps> = ({ selectedDocument, categoryId }) => {
    const [expanded, setExpanded] = useState<ExpandedState>({});
    const [selectedFolderId, setSelectedFolderId] = useState<string | null>(selectedDocument?.folder_id || null);
    const queryClient = useQueryClient();

    const {
        data: folderTree,
        isLoading,
        error,
    } = useQuery({
        queryKey: ["categoryFolderTree", categoryId],
        queryFn: () => CategoryService.getCategoryFolderTree(categoryId),
        enabled: !!categoryId,
    });

    const moveMutation = useMutation({
        mutationFn: (folderId: string | null) => AdminService.moveDocument(selectedDocument.id, folderId),
        onSuccess: () => {
            toast.success("Document moved successfully");
            queryClient.invalidateQueries({ queryKey: ["categoryContent"] });
        },
        onError: (error: any) => {
            const message = error.response?.data?.detail || "Failed to move document";
            toast.error(message);
        },
    });

    const handleToggleExpand = (folderId: string) => {
        setExpanded((prev) => ({
            ...prev,
            [folderId]: !prev[folderId],
        }));
    };

    const handleMove = () => {
        if (!selectedDocument) {
            toast.error("No document selected");
            return;
        }

        moveMutation.mutate(selectedFolderId);
    };

    if (!selectedDocument) {
        return <div className="py-4 px-4 text-center text-gray-500">Please select a document first</div>;
    }

    if (isLoading) {
        return (
            <div className="py-4 space-y-2">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
            </div>
        );
    }

    if (error) {
        return <div className="py-4 px-4 text-center text-red-500">Failed to load folder structure</div>;
    }

    return (
        <div className="py-4 space-y-4 h-full flex flex-col">
            <div className="px-4 pb-4 border-b">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Document: <span className="text-blue-600 dark:text-blue-400">{selectedDocument.name}</span>
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Select a folder to move this document</p>
            </div>

            <div className="flex-1 overflow-y-auto px-2">
                <RadioGroup
                    value={selectedFolderId || ""}
                    onValueChange={(value) => setSelectedFolderId(value || null)}
                >
                    <div
                        className={`flex items-center gap-2 py-2 px-2 rounded-md transition-colors cursor-pointer ${
                            selectedFolderId === null
                                ? "bg-blue-100 dark:bg-blue-900"
                                : "hover:bg-gray-100 dark:hover:bg-gray-800"
                        }`}
                    >
                        <div className="w-[18px]" />
                        <RadioGroupItem value="" id="folder-root" />
                        <Folder size={16} className="flex-shrink-0 text-amber-600" />
                        <Label
                            htmlFor="folder-root"
                            className="flex-1 text-sm font-medium cursor-pointer hover:underline"
                        >
                            Category Root
                        </Label>
                    </div>

                    {folderTree && folderTree.length > 0 ? (
                        folderTree.map((node: any) => (
                            <FolderTreeItem
                                key={node.id}
                                node={node}
                                expanded={expanded}
                                onToggleExpand={handleToggleExpand}
                                selectedFolderId={selectedFolderId}
                                onSelectFolder={setSelectedFolderId}
                            />
                        ))
                    ) : (
                        <div className="px-4 py-8 text-center text-gray-500 text-sm">
                            No folders in this category yet
                        </div>
                    )}
                </RadioGroup>
            </div>

            <div className="flex gap-2 px-4 py-4 border-t">
                <Button
                    onClick={handleMove}
                    disabled={selectedFolderId === selectedDocument.folder_id || moveMutation.isPending}
                    size="sm"
                >
                    Move Document
                </Button>
            </div>
        </div>
    );
};

export default LocationTab;
