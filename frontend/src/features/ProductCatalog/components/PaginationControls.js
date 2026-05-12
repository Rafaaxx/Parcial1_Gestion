import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export function PaginationControls({ currentPage, totalItems, itemsPerPage, onPageChange, isLoading, }) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const hasNextPage = currentPage < totalPages;
    const hasPrevPage = currentPage > 1;
    const startItem = (currentPage - 1) * itemsPerPage + 1;
    const endItem = Math.min(currentPage * itemsPerPage, totalItems);
    return (_jsxs("div", { className: "flex flex-col sm:flex-row items-center justify-between gap-4 py-6 border-t border-gray-200", children: [_jsxs("div", { className: "text-sm text-gray-600", children: ["Showing", ' ', _jsx("span", { className: "font-semibold text-gray-900", children: startItem }), " to", ' ', _jsx("span", { className: "font-semibold text-gray-900", children: endItem }), " of", ' ', _jsx("span", { className: "font-semibold text-gray-900", children: totalItems }), " products"] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { onClick: () => onPageChange(currentPage - 1), disabled: !hasPrevPage || isLoading, className: "px-4 py-2 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors", "aria-label": "Previous page", children: "\u2190 Previous" }), _jsxs("div", { className: "flex items-center gap-1", children: [_jsx(PageButton, { pageNumber: 1, isActive: currentPage === 1, onClick: () => onPageChange(1), isLoading: isLoading }), currentPage > 3 && _jsx("span", { className: "px-2 py-1 text-gray-600", children: "..." }), totalPages > 2 &&
                                Array.from({ length: Math.min(3, totalPages - 1) }, (_, i) => {
                                    const pageNum = Math.max(2, currentPage - 1) + i;
                                    if (pageNum >= totalPages)
                                        return null;
                                    return (_jsx(PageButton, { pageNumber: pageNum, isActive: currentPage === pageNum, onClick: () => onPageChange(pageNum), isLoading: isLoading }, pageNum));
                                }), currentPage < totalPages - 2 && (_jsx("span", { className: "px-2 py-1 text-gray-600", children: "..." })), totalPages > 1 && (_jsx(PageButton, { pageNumber: totalPages, isActive: currentPage === totalPages, onClick: () => onPageChange(totalPages), isLoading: isLoading }))] }), _jsx("button", { onClick: () => onPageChange(currentPage + 1), disabled: !hasNextPage || isLoading, className: "px-4 py-2 border border-gray-300 text-gray-700 rounded-md font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors", "aria-label": "Next page", children: "Next \u2192" })] }), _jsxs("div", { className: "text-sm text-gray-600", children: ["Page ", _jsx("span", { className: "font-semibold text-gray-900", children: currentPage }), " of", ' ', _jsx("span", { className: "font-semibold text-gray-900", children: totalPages })] })] }));
}
function PageButton({ pageNumber, isActive, onClick, isLoading }) {
    return (_jsx("button", { onClick: onClick, disabled: isLoading, className: `px-3 py-2 rounded-md font-medium transition-colors ${isActive
            ? 'bg-blue-600 text-white'
            : 'border border-gray-300 text-gray-700 hover:bg-gray-50'} disabled:opacity-50 disabled:cursor-not-allowed`, "aria-label": `Go to page ${pageNumber}`, "aria-current": isActive ? 'page' : undefined, children: pageNumber }));
}
//# sourceMappingURL=PaginationControls.js.map