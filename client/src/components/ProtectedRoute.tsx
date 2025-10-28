import { Navigate, Outlet } from "react-router";
import { useAuth } from "../context/AuthContext";

const ProtectedRoute = () => {
    const { token, user, isLoading } = useAuth();

    if (isLoading) return <div>Loading...</div>;

    if (!token || !user?.id) return <Navigate to="/login" replace />;

    return <Outlet />;
};

export default ProtectedRoute;
