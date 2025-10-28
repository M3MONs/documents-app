import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { useNavigate } from "react-router";

const NotFoundPage = () => {
    const navigate = useNavigate();

    const handleGoHome = () => {
        navigate("/");
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background text-foreground p-4">
            <Card className="w-full max-w-md shadow-lg">
                <CardHeader className="text-center">
                    <h1 className="text-8xl font-bold tracking-tighter pt-8">404</h1>
                </CardHeader>

                <CardContent className="text-center pb-6">
                    <h2 className="text-3xl font-semibold tracking-tight">Page Not Found</h2>

                    <p className="mt-3 text-muted-foreground">
                        It looks like the page you're looking for doesn't exist or has been moved.
                    </p>
                </CardContent>

                <CardFooter>
                    <Button className="w-full" onClick={handleGoHome}>
                        Go back home
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
};

export default NotFoundPage;
