import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Link } from 'react-router-dom';
export const ForbiddenPage = () => {
    return (_jsxs("div", { className: "flex flex-col items-center justify-center min-h-[60vh] text-center px-4", children: [_jsx("span", { className: "text-6xl mb-4", children: "\uD83D\uDEAB" }), _jsx("h1", { className: "text-2xl font-bold text-gray-900 dark:text-gray-50 mb-2", children: "Acceso denegado" }), _jsx("p", { className: "text-gray-600 dark:text-gray-400 mb-6 max-w-md", children: "No ten\u00E9s permisos para acceder a esta p\u00E1gina." }), _jsx(Link, { to: "/", className: "px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors", children: "Volver al inicio" })] }));
};
export default ForbiddenPage;
//# sourceMappingURL=ForbiddenPage.js.map