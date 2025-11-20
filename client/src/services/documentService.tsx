import type { DocumentMetadata } from "@/types/document";
import apiClient from "./apiClient";

const URL = "/documents";

class DocumentService {
    async getDocumentContent(documentId: string): Promise<Blob> {
        const response = await apiClient.get(`${URL}/${documentId}/content`, {
            responseType: "blob",
        });
        return response.data;
    }

    async getDocumentMetadata(documentId: string): Promise<DocumentMetadata> {
        const response = await apiClient.get(`${URL}/${documentId}/metadata`);
        return response.data;
    }

    async downloadDocument(documentId: string, fileName?: string): Promise<void> {
        const response = await apiClient.get(`${URL}/${documentId}/download`, {
            responseType: "blob",
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", fileName || "document");

        document.body.appendChild(link);
        link.click();

        link.parentNode?.removeChild(link);
        window.URL.revokeObjectURL(url);
    }

    getDocumentViewUrl(documentId: string): string {
        return `${apiClient.defaults.baseURL}${URL}/${documentId}/content`;
    }
}

export default new DocumentService();
