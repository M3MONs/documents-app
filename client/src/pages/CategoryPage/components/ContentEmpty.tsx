import { memo } from "react";
import { Search, Folder } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface ContentEmptyProps {
    searchQuery: string;
}

const ContentEmpty = memo(({ searchQuery }: ContentEmptyProps) => {
    return (
        <Card className="border-dashed">
            <CardContent className="flex flex-col items-center justify-center py-12 gap-3">
                {searchQuery ? (
                    <>
                        <Search className="h-12 w-12 text-muted-foreground/50" />
                        <h3 className="font-semibold text-foreground">No results found</h3>
                        <p className="text-sm text-muted-foreground">Try a different search term</p>
                    </>
                ) : (
                    <>
                        <Folder className="h-12 w-12 text-muted-foreground/50" />
                        <h3 className="font-semibold text-foreground">No Content Found</h3>
                        <p className="text-sm text-muted-foreground">This folder is empty</p>
                    </>
                )}
            </CardContent>
        </Card>
    );
});

ContentEmpty.displayName = "ContentEmpty";

export default ContentEmpty;
