import { memo } from "react";
import { FileText, Folder, ChevronRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { ContentItem as ContentItemType } from "@/types/categoryContent";

interface ContentItemProps {
    item: ContentItemType;
    onItemClick: (item: ContentItemType) => void;
}

const ContentItem = memo(({ item, onItemClick }: ContentItemProps) => {
    const isFolder = item.type === "folder";

    return (
        <Card
            className={`cursor-pointer transition-all hover:shadow-sm hover:border-primary group ${
                isFolder ? "hover:bg-accent/50" : "hover:bg-muted/30"
            }`}
            onClick={() => onItemClick(item)}
        >
            <CardContent className="flex items-center justify-between py-3 px-4">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                    {isFolder ? (
                        <Folder className="h-5 w-5 text-blue-500 flex-shrink-0" />
                    ) : (
                        <FileText className="h-5 w-5 text-gray-500 flex-shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate">{item.name}</p>
                        {!isFolder && item.mime_type && (
                            <p className="text-xs text-muted-foreground">{item.mime_type}</p>
                        )}
                    </div>
                </div>
                {isFolder && (
                    <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary flex-shrink-0 ml-2" />
                )}
                {!isFolder && (
                    <Button variant="ghost" size="sm" className="ml-2">
                        Open
                    </Button>
                )}
            </CardContent>
        </Card>
    );
});

ContentItem.displayName = "ContentItem";

export default ContentItem;
