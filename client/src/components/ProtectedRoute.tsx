import { Navigate, Outlet } from "react-router";
import { useAuth } from "../context/AuthContext";

type ProtectedRouteProps = {
    isSuperuser?: boolean;
};

const ProtectedRoute = ({ isSuperuser = false }: ProtectedRouteProps) => {
    const { token, user, isLoading } = useAuth();

    if (isLoading) return <div>Loading...</div>;

    if (!token || !user?.id) return <Navigate to="/login" replace />;

    if (!isSuperuser && user?.is_superuser !== true) return <Navigate to="/" replace />;

    return <Outlet />;
};

export default ProtectedRoute;
