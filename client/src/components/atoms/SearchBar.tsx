import { Search } from "lucide-react";
import React from "react";
import { Input } from "../ui/input";

interface SearchBarProps {
    searchQuery: string;
    placeholder?: string;
    setSearchQuery: (query: string) => void;
    setIsFocused: (focused: boolean) => void;
    inputRef: React.RefObject<HTMLInputElement | null>;
}

const SearchBar = ({ searchQuery, placeholder, setSearchQuery, setIsFocused, inputRef }: SearchBarProps) => {
    return (
        <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
                ref={inputRef}
                placeholder={placeholder || "Search folders and documents..."}
                value={searchQuery}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                className="pl-10"
            />
        </div>
    );
};

export default SearchBar;
