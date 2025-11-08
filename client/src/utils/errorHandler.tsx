import { AxiosError } from "axios";
import type { FieldPath, UseFormReturn } from "react-hook-form";
import { toast } from "sonner";

interface FastAPIValidationError {
    loc: (string | number)[];
    msg: string;
    ctx?: {
        reason?: string;
    };
}

interface ErrorResponse {
    detail: string | FastAPIValidationError[];
}

export const handleApiFormError = <T extends Record<string, any>>(error: unknown, form: UseFormReturn<T>) => {
    if (error instanceof AxiosError && error.response?.data) {
        const errorData = error.response.data as ErrorResponse;

        if (Array.isArray(errorData.detail)) {
            errorData.detail.forEach((err) => {
                const message = err.ctx?.reason || err.msg;
                const fieldName = err.loc[err.loc.length - 1] as FieldPath<T>;

                if (fieldName && form.getValues(fieldName) !== undefined) {
                    form.setError(fieldName, { type: "server", message });
                } else {
                    form.setError("root", { type: "server", message });
                }
            });
        } else if (typeof errorData.detail === "string") {
            form.setError("root", {
                type: "server",
                message: errorData.detail,
            });
        } else {
            form.setError("root", {
                type: "server",
                message: "An unexpected error occurred.",
            });
        }

        console.error("API Error:", errorData);
    } else {
        form.setError("root", {
            type: "manual",
            message: "An unexpected error occurred. Please try again.",
        });
        console.error("An unexpected error occurred:", error);
    }
};


export const handleApiError = (error: unknown) => {
    if (error instanceof AxiosError && error.response?.data) {
        const errorData = error.response.data as ErrorResponse;

        if (Array.isArray(errorData.detail)) {
            errorData.detail.forEach((err) => {
                const message = err.ctx?.reason || err.msg;
                console.error("API Validation Error:", message);
            });
        } else if (typeof errorData.detail === "string") {
            console.error("API Error:", errorData.detail);
            toast.error(errorData.detail);
        } else {
            console.error("An unexpected error occurred:", errorData);
        }
    } else {
        console.error("An unexpected error occurred:", error);
    }
};