import { createContext, useState, useContext, useEffect } from "react";
import { setAuthToken } from "../services/tokenManager";
import AuthService from "@/services/authService";
import type { User } from "@/types/user";
import type { Organization } from "@/types/organization";
import { getFromLocalStorage, removeFromLocalStorage, saveToLocalStorage } from "@/utils/localStorage";
import OrganizationService from "@/services/organizationService";

interface AuthContextType {
    token: string | null;
    user: User | null;
    selectedOrganization: Organization | null;
    isLoading: boolean;
    setToken: (token: string | null) => void;
    setUser: (user: User | null) => void;
    setSelectedOrganization: (organization: Organization | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: any }) => {
    const [token, setToken] = useState<string | null>(null);
    const [user, setUser] = useState<User | null>(null);
    const [selectedOrganization, setSelectedOrganization] = useState<Organization | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const handleSetToken = (newToken: string | null) => {
        setToken(newToken);
        setAuthToken(newToken);
    };

    const handleSetUser = (newUser: User | null) => {
        setUser(newUser);
    };

    const handleSetSelectedOrganization = (newOrganization: Organization | null) => {
        setSelectedOrganization(newOrganization);

        if (newOrganization) saveToLocalStorage("selectedOrganization", JSON.stringify(newOrganization));
        else removeFromLocalStorage("selectedOrganization");
    };

    useEffect(() => {
        const refreshAuthToken = async () => {
            try {
                const data = await AuthService.refreshToken();

                if (!data || !data.access_token) {
                    throw new Error("Invalid refresh response");
                }

                setUser(data.user);
                handleSetToken(data.access_token);
            } catch (err: any) {
                console.error("Failed to refresh auth token on app load:", err);
                handleSetToken(null);
            } finally {
                setIsLoading(false);
            }
        };

        const validateOrganization = async (storedOrganization: string) => {
            try {
                await OrganizationService.validateOrganizationAccess(JSON.parse(storedOrganization).id);
                setSelectedOrganization(JSON.parse(storedOrganization));
            } catch (err: any) {
                console.error("Failed to validate stored organization:", err);
                removeFromLocalStorage("selectedOrganization");
            }
        };

        const init = async () => {
            await refreshAuthToken();
            const storedOrganization = getFromLocalStorage("selectedOrganization");
            if (storedOrganization) await validateOrganization(storedOrganization);
        };

        init();
    }, []);

    const value = {
        token,
        user,
        selectedOrganization,
        isLoading,
        setToken: handleSetToken,
        setUser: handleSetUser,
        setSelectedOrganization: handleSetSelectedOrganization,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
