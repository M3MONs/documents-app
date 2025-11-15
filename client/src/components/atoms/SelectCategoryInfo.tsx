import React from "react";
import { AlertCircle } from "lucide-react";
import DashboardLayout from "../layouts/DashboardLayout";

const SelectCategoryInfo: React.FC = () => {
    return (
        <DashboardLayout>
            <div className="flex flex-col items-center justify-center min-h-[400px] p-4">
                <div className="flex items-center gap-3 p-6 bg-muted/50 border border-border rounded-lg text-muted-foreground max-w-md w-full">
                    <AlertCircle className="h-6 w-6 flex-shrink-0" />
                    <div>
                        <h3 className="font-medium text-foreground">Select a category</h3>
                        <p className="text-sm">To continue, select a category from the menu on the left.</p>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
};

export default SelectCategoryInfo;
