import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
const footerLinks = [
    { label: 'Inicio', href: '/' },
    { label: 'Catálogo', href: '/productos' },
    { label: 'Contacto', href: '#' },
];
export const Footer = () => {
    return (_jsx("footer", { className: "bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800", children: _jsx("div", { className: "container mx-auto px-4 py-8", children: _jsxs("div", { className: "flex flex-col md:flex-row items-center justify-between gap-4", children: [_jsx("p", { className: "text-sm text-gray-600 dark:text-gray-400", children: "\u00A9 2026 Food Store. Todos los derechos reservados." }), _jsx("nav", { className: "flex items-center gap-6", children: footerLinks.map((link) => (_jsx("a", { href: link.href, className: "text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-50 transition-colors", children: link.label }, link.label))) })] }) }) }));
};
export default Footer;
//# sourceMappingURL=Footer.js.map