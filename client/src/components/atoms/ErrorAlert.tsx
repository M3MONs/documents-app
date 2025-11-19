import { memo } from "react";
import { AlertCircle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface ErrorAlertProps {
    error: Error | string;
}

const ErrorAlert = memo(({ error }: ErrorAlertProps) => {
    const message =
        error instanceof Error
            ? error.message
            : "An error occurred while loading folder content";

    return (
        <Card className="border-destructive bg-destructive/5">
            <CardContent className="flex gap-4 pt-6">
                <AlertCircle className="h-5 w-5 text-destructive shrink-0 mt-0.5" />
                <div className="flex-1">
                    <h3 className="font-semibold text-destructive mb-1">Failed to Load Content</h3>
                    <p className="text-sm text-muted-foreground">{message}</p>
                </div>
            </CardContent>
        </Card>
    );
});

ErrorAlert.displayName = "ErrorAlert";

export default ErrorAlert;
