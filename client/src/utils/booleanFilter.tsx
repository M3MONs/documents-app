export const booleanFilter = (value: boolean | undefined, filterValue: string): boolean => {
    const lowerFilter = filterValue.toLowerCase();
    if (lowerFilter === "") return true;

    if (lowerFilter === "yes" || lowerFilter === "1") return value === true;

    if (lowerFilter === "no" || lowerFilter === "0") return value === false;

    return false;
};
