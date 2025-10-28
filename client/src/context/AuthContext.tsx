import { createContext, useState, useContext, useEffect } from "react";
import { setAuthToken } from "../services/tokenManager";
import AuthService from "@/services/authService";
import type { User } from "@/types/user";

interface AuthContextType {
    token: string | null;
    user: User | null;
    isLoading: boolean;
    setToken: (token: string | null) => void;
    setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: any }) => {
    const [token, setToken] = useState<string | null>(null);
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const handleSetToken = (newToken: string | null) => {
        setToken(newToken);
    };

    const handleSetUser = (newUser: User | null) => {
        setUser(newUser);
    };

    useEffect(() => {
        const refreshAuthToken = async () => {
            try {
                const data = await AuthService.refreshToken();
                setUser(data.user);
                setToken(data.access_token);
            } catch (err: any) {
                console.error("Failed to refresh auth token on app load:", err);
                setToken(null);
            } finally {
                setIsLoading(false);
            }
        };

        refreshAuthToken();
    }, []);

    useEffect(() => {
        setAuthToken(token);
    }, [token]);

    const value = { token, user, isLoading, setToken: handleSetToken, setUser: handleSetUser };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
