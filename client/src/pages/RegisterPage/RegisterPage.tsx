import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import AuthService from "@/services/authService";
import { useAuth } from "@/context/AuthContext";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import z from "zod";
import { useNavigate } from "react-router";
import { handleApiFormError } from "@/utils/errorHandler";
import { useEffect } from "react";

const registerSchema = z
    .object({
        username: z
            .string()
            .min(3, "Username must be at least 3 characters")
            .max(50, "Username must be at most 50 characters"),
        email: z.email("Invalid email address").optional().or(z.literal("")),
        password: z
            .string()
            .min(8, "Password must be at least 8 characters")
            .max(100, "Password must be at most 100 characters"),
        confirmPassword: z
            .string()
            .min(8, "Confirm Password must be at least 8 characters")
            .max(100, "Confirm Password must be at most 100 characters"),
    })
    .refine((data) => data.password === data.confirmPassword, {
        message: "Passwords do not match",
    });

type RegisterFormData = z.infer<typeof registerSchema>;

const RegisterPage = () => {
    const { token, isLoading, setToken, setUser } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (token && !isLoading) {
            navigate("/");
        }
    }, [token, isLoading, navigate]);

    const form = useForm<RegisterFormData>({
        resolver: zodResolver(registerSchema),
        defaultValues: {
            username: "",
            email: "",
            password: "",
            confirmPassword: "",
        },
    });

    const onSubmit = async (data: RegisterFormData) => {
        try {
            const response = await AuthService.register(data);
            setToken(response.access_token);
            setUser(response.user);
            navigate("/");
        } catch (err: any) {
            handleApiFormError(err, form);
        }
    };

    const handleLoginRedirect = () => {
        navigate("/login");
    };

    return (
        <div className="flex items-center flex-col justify-center min-h-screen">
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 w-full max-w-md">
                    <h1 className="text-2xl font-bold">Create an account</h1>
                    <FormField
                        control={form.control}
                        name="username"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Username</FormLabel>
                                <FormControl>
                                    <Input placeholder="Enter username" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="email"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Email (optional)</FormLabel>
                                <FormControl>
                                    <Input placeholder="Enter email" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="password"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Password</FormLabel>
                                <FormControl>
                                    <Input type="password" placeholder="Enter password" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    <FormField
                        control={form.control}
                        name="confirmPassword"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Confirm Password</FormLabel>
                                <FormControl>
                                    <Input type="password" placeholder="Confirm password" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    {form.formState.errors.root && (
                        <div className="text-destructive text-sm">{form.formState.errors.root.message}</div>
                    )}

                    <Button type="submit" className="w-full">
                        Register
                    </Button>
                </form>
            </Form>
            <div>
                <p className="mt-4 text-sm text-muted-foreground">
                    Already have an account?{" "}
                    <Button variant="link" className="p-0" onClick={handleLoginRedirect}>
                        Login here
                    </Button>
                </p>
            </div>
        </div>
    );
};

export default RegisterPage;
