import type { ContentItem } from "@/types/categoryContent";
import { useState, useRef, useCallback, useMemo } from "react";
import { useSearchParams } from "react-router";

const useCategoryPageState = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const searchQuery = searchParams.get("q") || "";
  const page = parseInt(searchParams.get("page") || "1", 10);

  const currentFolderId = searchParams.get("path") || null;

  const [folderHistory, setFolderHistory] = useState<Array<{ id: string | null; name: string }>>([
    { id: null, name: "Root" },
  ]);

  useMemo(() => {
    if (!currentFolderId) {
      setFolderHistory([{ id: null, name: "Root" }]);
    } else {
      if (folderHistory[folderHistory.length - 1]?.id !== currentFolderId) {
        const existingIndex = folderHistory.findIndex((f) => f.id === currentFolderId);
        if (existingIndex !== -1) {
          setFolderHistory(folderHistory.slice(0, existingIndex + 1));
        } else {
          setFolderHistory([...folderHistory, { id: currentFolderId, name: currentFolderId }]);
        }
      }
    }
  }, [currentFolderId]);

  const navigateToFolder = useCallback(
    (folderId: string, folderName: string) => {
      setSearchParams((prev: URLSearchParams) => {
        const newParams = new URLSearchParams(prev);
        newParams.set("path", folderId);
        newParams.set("page", "1");
        newParams.delete("q");
        return newParams;
      });

      setFolderHistory((prev) => [...prev, { id: folderId, name: folderName }]);
    },
    [setSearchParams]
  );

  const navigateToBreadcrumb = useCallback(
    (index: number) => {
      if (index === 0) {
        setSearchParams((prev: URLSearchParams) => {
          const newParams = new URLSearchParams(prev);
          newParams.delete("path");
          newParams.set("page", "1");
          newParams.delete("q");
          return newParams;
        });
      } else {
        const targetFolder = folderHistory[index];
        if (targetFolder && targetFolder.id) {
          setSearchParams((prev: URLSearchParams) => {
            const newParams = new URLSearchParams(prev);
            newParams.set("path", targetFolder.id!);
            newParams.set("page", "1");
            newParams.delete("q");
            return newParams;
          });
        }
      }
    },
    [folderHistory, setSearchParams]
  );

  const navigateBack = useCallback(() => {
    if (folderHistory.length <= 1) return; // Jesteśmy w root

    const previousFolder = folderHistory[folderHistory.length - 2]; // Folder poprzedni

    if (previousFolder.id === null) {
      setSearchParams((prev: URLSearchParams) => {
        const newParams = new URLSearchParams(prev);
        newParams.delete("path");
        newParams.set("page", "1");
        newParams.delete("q");
        return newParams;
      });
    } else {
      setSearchParams((prev: URLSearchParams) => {
        const newParams = new URLSearchParams(prev);
        newParams.set("path", previousFolder.id!);
        newParams.set("page", "1");
        newParams.delete("q");
        return newParams;
      });
    }

    setFolderHistory((prev) => prev.slice(0, -1));
  }, [folderHistory, setSearchParams]);

  const setSearchQuery = useCallback(
    (q: string) => {
      setSearchParams((prev: URLSearchParams) => {
        const newParams = new URLSearchParams(prev);

        if (q) {
          newParams.set("q", q);
        } else {
          newParams.delete("q");
        }

        newParams.set("page", "1");
        return newParams;
      });
    },
    [setSearchParams]
  );

  const setPage = useCallback(
    (p: number | ((prev: number) => number)) => {
      setSearchParams((prev: URLSearchParams) => {
        const newParams = new URLSearchParams(prev);
        const currentPage = parseInt(newParams.get("page") || "1", 10);

        const nextPage = typeof p === "function" ? p(currentPage) : p;

        if (nextPage > 1) {
          newParams.set("page", String(nextPage));
        } else {
          newParams.delete("page");
        }
        return newParams;
      });
    },
    [setSearchParams]
  );

  const [isFocused, setIsFocused] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<ContentItem | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  return {
    currentFolderId,
    folderHistory,
    searchQuery,
    page,

    navigateToFolder,
    navigateToBreadcrumb,
    navigateBack,
    setSearchQuery,
    setPage,

    isFocused,
    setIsFocused,
    selectedDocument,
    setSelectedDocument,
    inputRef,
  };
};

export default useCategoryPageState;
