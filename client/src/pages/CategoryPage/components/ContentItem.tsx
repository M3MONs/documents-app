import { memo } from "react";
import { Folder, Lock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import type { ContentItem as ContentItemType } from "@/types/categoryContent";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuGroup,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import FileIcon from "./FileIcon";

interface ContentItemProps {
    item: ContentItemType;
    canManageCategory: boolean;
    onItemClick: (item: ContentItemType) => void;
    onManageClick: (item: ContentItemType) => void;
}

const ContentItem = memo(({ item, canManageCategory, onItemClick, onManageClick }: ContentItemProps) => {
    const isFolder = item.type === "folder";

    const handleCardClick = () => {
        onItemClick(item);
    };

    const handleDropdownClick = (e: React.MouseEvent) => {
        e.stopPropagation();
    };

    return (
        <Card
            className={`cursor-pointer transition-all hover:shadow-sm hover:border-primary group ${
                isFolder ? "hover:bg-accent/50" : "hover:bg-muted/30"
            }`}
            onClick={handleCardClick}
        >
            <CardContent className="flex items-center justify-between py-3 px-4">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                    {isFolder ? (
                        <>
                            {item.is_private && <Lock className="h-5 w-5 text-muted-foreground flex-shrink-0" />}
                            <Folder className="h-5 w-5 text-blue-500 flex-shrink-0" />
                        </>
                    ) : (
                        <FileIcon mimeType={item.mime_type} />
                    )}
                    <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate">{item.name}</p>
                        {!isFolder && item.mime_type && (
                            <p className="text-xs text-muted-foreground">{item.mime_type}</p>
                        )}
                    </div>
                </div>
                {isFolder && canManageCategory && (
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm" className="ml-2" onClick={handleDropdownClick}>
                                ...
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent className="w-56" align="start">
                            <DropdownMenuGroup>
                                <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onManageClick(item); }}>Manage</DropdownMenuItem>
                            </DropdownMenuGroup>
                        </DropdownMenuContent>
                    </DropdownMenu>
                )}
            </CardContent>
        </Card>
    );
});

ContentItem.displayName = "ContentItem";

export default ContentItem;
