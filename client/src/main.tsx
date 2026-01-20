import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router";
import "@/index.css";
import HomePage from "@/pages/HomePage/HomePage.tsx";
import LoginPage from "@/pages/LoginPage/LoginPage.tsx";
import RegisterPage from "@/pages/RegisterPage/RegisterPage.tsx";
import { AuthProvider } from "@/context/AuthContext.tsx";
import ProtectedRoute from "@/components/ProtectedRoute";
import NotFoundPage from "@/pages/NotFoundPage/NotFoundPage";
import { ThemeProvider } from "@/components/theme-provider";
import AdminPages from "@/pages/Admin/AdminPages";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";
import CategoryPage from "@/pages/CategoryPage/CategoryPage";
import UserProfilePage from "@/pages/UserProfilePage/UserProfilePage";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <ThemeProvider>
            <QueryClientProvider client={new QueryClient()}>
                <AuthProvider>
                    <BrowserRouter>
                        <Routes>
                             <Route element={<ProtectedRoute />}>
                                 <Route path="/" element={<HomePage />} />
                                 <Route path="/categories/:categoryId" element={<CategoryPage />} />
                                 <Route path="/profile" element={<UserProfilePage />} />
                             </Route>

                            <Route path="/admin/*" element={<AdminPages />} />

                            <Route path="/login" element={<LoginPage />} />
                            <Route path="/register" element={<RegisterPage />} />
                            <Route path="*" element={<NotFoundPage />} />
                        </Routes>
                    </BrowserRouter>
                </AuthProvider>
            </QueryClientProvider>
            <Toaster />
        </ThemeProvider>
    </StrictMode>
);
