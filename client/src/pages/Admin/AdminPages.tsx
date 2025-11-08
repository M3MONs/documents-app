import { Route, Routes } from "react-router";
import DashboardLayout from "@/components/layouts/DashboardLayout"
import ProtectedRoute from "@/components/ProtectedRoute";
import AdminUsersPage from "@/pages/Admin/UsersPage/AdminUsersPage";
import AdminDepartmentsPage from "@/pages/Admin/DepartmentsPage/AdminDepartmentsPage";
import AdminOrganizationsPage from "@/pages/Admin/OrganizationsPage/AdminOrganizationsPage";
import AdminRolesPage from "./RolesPage/AdminRolesPage";

const AdminPages = () => {
    return (
        <DashboardLayout>
            <Routes>
                <Route element={<ProtectedRoute isSuperuser={true} />}>
                    <Route path="users" element={<AdminUsersPage />} />
                    <Route path="organizations" element={<AdminOrganizationsPage />} />
                    <Route path="departments" element={<AdminDepartmentsPage />} />
                    <Route path="roles" element={<AdminRolesPage />} />
                </Route>
            </Routes>
        </DashboardLayout>
    );
};

export default AdminPages;
