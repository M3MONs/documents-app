import { memo } from "react";
import { Skeleton } from "@/components/ui/skeleton";

const SKELETON_COUNT = 5;

const ContentLoading = memo(() => (
    <div className="space-y-3">
        {Array.from({ length: SKELETON_COUNT }).map((_, i) => (
            <Skeleton key={`item-skeleton-${i}`} className="h-16 rounded-lg" />
        ))}
    </div>
));

ContentLoading.displayName = "ContentLoading";

export default ContentLoading;
