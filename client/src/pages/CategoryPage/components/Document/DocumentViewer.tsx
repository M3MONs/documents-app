import { memo, useEffect, useState } from "react";
import { FileText, Download, ExternalLink, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import documentService from "@/services/documentService";
import type { ContentItem } from "@/types/categoryContent";
import type { DocumentMetadata } from "@/types/document";

interface DocumentViewerProps {
    document: ContentItem;
}

const DocumentViewer = memo(({ document }: DocumentViewerProps) => {
    const [metadata, setMetadata] = useState<DocumentMetadata | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [blobUrl, setBlobUrl] = useState<string | null>(null);

    useEffect(() => {
        const loadDocument = async () => {
            try {
                setIsLoading(true);
                setError(null);

                const meta = await documentService.getDocumentMetadata(document.id);
                setMetadata(meta);

                if (meta.viewable) {
                    const blob = await documentService.getDocumentContent(document.id);
                    const url = URL.createObjectURL(blob);
                    setBlobUrl(url);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load document");
            } finally {
                setIsLoading(false);
            }
        };

        loadDocument();

        return () => {
            if (blobUrl) {
                URL.revokeObjectURL(blobUrl);
            }
        };
    }, [document.id]);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-96 gap-2">
                <Loader2 className="h-5 w-5 animate-spin" />
                <p className="text-muted-foreground">Loading document...</p>
            </div>
        );
    }

    if (error || !metadata) {
        return (
            <div className="flex flex-col items-center justify-center h-96 gap-4 bg-destructive/5 rounded-lg border border-destructive">
                <AlertCircle className="h-12 w-12 text-destructive" />
                <p className="text-destructive font-medium">Failed to load document</p>
                <p className="text-sm text-muted-foreground">{error}</p>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col gap-4">
            {metadata.viewable ? (
                <div className="flex-1 rounded-lg border overflow-hidden bg-black/5">
                    {metadata.mime_type?.startsWith("image/") ? (
                        <img
                            src={blobUrl || documentService.getDocumentViewUrl(document.id)}
                            alt={metadata.name}
                            className="w-full h-full object-contain"
                        />
                    ) : metadata.mime_type === "application/pdf" ? (
                        <iframe
                            src={blobUrl || documentService.getDocumentViewUrl(document.id)}
                            className="w-full h-full"
                            title={metadata.name}
                        />
                    ) : metadata.mime_type?.startsWith("text/") ? (
                        <div className="p-4 h-full overflow-auto">
                            {blobUrl ? (
                                <TextPreview url={blobUrl} />
                            ) : (
                                <p className="text-sm text-muted-foreground">Loading text preview...</p>
                            )}
                        </div>
                    ) : null}
                </div>
            ) : (
                <div className="flex-1 p-8 bg-muted rounded-lg border border-dashed flex flex-col items-center gap-3">
                    <FileText className="h-12 w-12 text-muted-foreground/50" />
                    <p className="text-sm font-medium">Preview not available</p>
                    <p className="text-xs text-muted-foreground text-center">
                        This file type cannot be previewed. Download the file to view it.
                    </p>
                </div>
            )}

            <div className="grid grid-cols-4 gap-4 text-sm">
                <div>
                    <p className="text-muted-foreground">Created</p>
                    <p className="font-medium">{new Date(metadata.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                    <p className="text-muted-foreground">Size</p>
                    <p className="font-medium">
                        {metadata.file_size ? `${(metadata.file_size / 1024).toFixed(2)} KB` : "Unknown"}
                    </p>
                </div>
                <Button
                    variant="outline"
                    size="sm"
                    className="cursor-pointer"
                    onClick={() => documentService.downloadDocument(document.id, metadata.name)}
                >
                    <Download className="h-4 w-4 mr-1" />
                    Download
                </Button>
                {metadata.viewable && blobUrl && (
                    <Button
                        variant="outline"
                        className="cursor-pointer"
                        size="sm"
                        onClick={() => window.open(blobUrl, "_blank")}
                    >
                        <ExternalLink className="h-4 w-4 mr-1" />
                        Open
                    </Button>
                )}
            </div>
        </div>
    );
});

DocumentViewer.displayName = "DocumentViewer";

const TextPreview = memo(({ url }: { url: string }) => {
    const [text, setText] = useState<string>("");

    useEffect(() => {
        const fetchText = async () => {
            const response = await fetch(url);
            const content = await response.text();
            setText(content.substring(0, 5000));
        };

        fetchText();
    }, [url]);

    return <pre className="text-xs font-mono whitespace-pre-wrap break-words">{text}</pre>;
});

TextPreview.displayName = "TextPreview";

export default DocumentViewer;
