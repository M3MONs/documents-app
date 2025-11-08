import SelectOrganizationInfo from "@/components/atoms/SelectOrganizationInfo";
import DashboardLayout from "@/components/layouts/DashboardLayout";
import { useAuth } from "@/context/AuthContext";

const HomePage = () => {
    const { selectedOrganization } = useAuth();

    if (!selectedOrganization) {
        return <SelectOrganizationInfo />;
    }

    return (
        <DashboardLayout>
            <h1>HomePage</h1>
        </DashboardLayout>
    );
};

export default HomePage;
