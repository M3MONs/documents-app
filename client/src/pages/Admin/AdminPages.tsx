import { Route, Routes } from "react-router";
import DashboardLayout from "@/components/layouts/DashboardLayout"
import ProtectedRoute from "@/components/ProtectedRoute";
import AdminUsersPage from "@/pages/Admin/UsersPage/AdminUsersPage";
import AdminDepartmentsPage from "@/pages/Admin/DepartmentsPage/AdminDepartmentsPage";
import AdminOrganizationsPage from "@/pages/Admin/OrganizationsPage/AdminOrganizationsPage";
import AdminRolesPage from "./RolesPage/AdminRolesPage";
import { StaticRoles } from "@/constants/roles";

const AdminPages = () => {
    return (
        <DashboardLayout>
            <Routes>
                <Route element={<ProtectedRoute requiredRoles={[StaticRoles.USER_MANAGER.name]} />}>
                    <Route path="users" element={<AdminUsersPage />} />
                </Route>
                <Route element={<ProtectedRoute requiredRoles={[StaticRoles.USER_MANAGER.name]} />}>
                    <Route path="organizations" element={<AdminOrganizationsPage />} />
                </Route>
                <Route element={<ProtectedRoute requiredRoles={[StaticRoles.DEPARTMENT_MANAGER.name]} />}>
                    <Route path="departments" element={<AdminDepartmentsPage />} />
                </Route>
                <Route element={<ProtectedRoute isSuperuser />}>
                    <Route path="roles" element={<AdminRolesPage />} />
                </Route>
            </Routes>
        </DashboardLayout>
    );
};

export default AdminPages;
