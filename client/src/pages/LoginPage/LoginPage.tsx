import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import AuthService from "@/services/authService";
import { useAuth } from "@/context/AuthContext";
import { handleApiFormError } from "@/utils/errorHandler";
import { useNavigate } from "react-router";
import { useEffect } from "react";

const loginSchema = z.object({
    username: z
        .string()
        .min(3, "Username must be at least 3 characters")
        .max(50, "Username must be at most 50 characters"),
    password: z
        .string()
        .min(8, "Password must be at least 8 characters")
        .max(100, "Password must be at most 100 characters"),
});

type LoginFormData = z.infer<typeof loginSchema>;

const LoginPage = () => {
    const { token, isLoading, setToken, setUser } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (token && !isLoading) {
            navigate("/");
        }
    }, [token, isLoading, navigate]);

    const form = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
        defaultValues: {
            username: "",
            password: "",
        },
    });

    const onSubmit = async (data: LoginFormData) => {
        try {
            const response = await AuthService.login(data);
            setToken(response.access_token);
            setUser(response.user);
            navigate("/");
        } catch (err: any) {
            handleApiFormError(err, form);
        }
    };

    const handleRegisterRedirect = () => {
        navigate("/register");
    };

    return (
        <div className="flex items-center flex-col justify-center min-h-screen">
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 w-full max-w-md">
                    <h1 className="text-2xl font-bold">Login</h1>
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

                    {form.formState.errors.root && (
                        <div className="text-destructive text-sm">{form.formState.errors.root.message}</div>
                    )}

                    <Button type="submit" className="w-full">
                        Login
                    </Button>
                </form>
            </Form>
            <div>
                <p className="mt-4 text-sm text-muted-foreground">
                    Don't have an account?{" "}
                    <Button variant="link" className="p-0" onClick={handleRegisterRedirect}>
                        Register here
                    </Button>
                </p>
            </div>
        </div>
    );
};

export default LoginPage;
