/**
 * Formatting utility functions
 */
/**
 * Format price to currency format (e.g., $100.00)
 */
export function formatPrice(price, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(price);
}
/**
 * Format date to readable string
 */
export function formatDate(date) {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
}
/**
 * Format datetime to readable string
 */
export function formatDateTime(date) {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}
/**
 * Truncate text to specified length with ellipsis
 */
export function truncateText(text, length) {
    if (text.length <= length)
        return text;
    return `${text.substring(0, length)}...`;
}
/**
 * Capitalize first letter of a string
 */
export function capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}
//# sourceMappingURL=formatters.js.map