export const capitalize = (str: string) => {
    if (!str || typeof str !== "string" || str.length === 0) {
        return "";
    }

    const restOfString = str.slice(1).toLowerCase();
    return str.charAt(0).toUpperCase() + restOfString;
};
