import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router";
import "@/index.css";
import HomePage from "@/pages/HomePage/HomePage.tsx";
import LoginPage from "@/pages/LoginPage/LoginPage.tsx";
import RegisterPage from "@/pages/RegisterPage/RegisterPage.tsx";
import { AuthProvider } from "@/context/AuthContext.tsx";
import ProtectedRoute from "./components/ProtectedRoute";
import NotFoundPage from "./pages/NotFoundPage/NotFoundPage";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <AuthProvider>
            <BrowserRouter>
                <Routes>
                    <Route element={<ProtectedRoute />}>
                        <Route path="/" element={<HomePage />} />
                    </Route>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="*" element={<NotFoundPage />} />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    </StrictMode>
);
