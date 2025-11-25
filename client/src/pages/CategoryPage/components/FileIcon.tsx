import { FileText, FileImage, FileVideo, FileAudio, FileArchive, File } from "lucide-react";

interface FileIconProps {
    mimeType?: string;
}

const FileIcon = ({ mimeType }: FileIconProps) => {
    if (!mimeType) {
        return <File className="h-5 w-5 text-gray-500 flex-shrink-0" />;
    }
    if (mimeType.startsWith('image/')) {
        return <FileImage className="h-5 w-5 text-green-500 flex-shrink-0" />;
    }
    if (mimeType === 'application/pdf') {
        return <FileText className="h-5 w-5 text-red-500 flex-shrink-0" />;
    }
    if (mimeType.startsWith('video/')) {
        return <FileVideo className="h-5 w-5 text-purple-500 flex-shrink-0" />;
    }
    if (mimeType.startsWith('audio/')) {
        return <FileAudio className="h-5 w-5 text-yellow-500 flex-shrink-0" />;
    }
    if (mimeType.includes('zip') || mimeType.includes('rar') || mimeType.includes('tar')) {
        return <FileArchive className="h-5 w-5 text-orange-500 flex-shrink-0" />;
    }
    if (mimeType.startsWith('text/') || mimeType === 'application/json' || mimeType === 'application/xml') {
        return <FileText className="h-5 w-5 text-blue-500 flex-shrink-0" />;
    }

    return <File className="h-5 w-5 text-gray-500 flex-shrink-0" />;
};

export default FileIcon;