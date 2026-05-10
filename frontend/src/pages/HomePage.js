import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Link } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/useAuth';
const features = [
    {
        title: 'Comida fresca',
        desc: 'Ingredientes de la mejor calidad, preparados al momento.',
        icon: '🥗',
    },
    {
        title: 'Pedidos online',
        desc: 'Hacé tu pedido desde cualquier lugar y pasá a retirar.',
        icon: '📱',
    },
    {
        title: 'Personalizá tu plato',
        desc: 'Elegí ingredientes, ajustá porciones, sin límites.',
        icon: '🎨',
    },
    {
        title: 'Entrega rápida',
        desc: 'En menos de 30 minutos tu pedido está listo.',
        icon: '⚡',
    },
];
export const HomePage = () => {
    const { isAuthenticated } = useAuth();
    return (_jsxs("div", { className: "space-y-16", children: [_jsxs("section", { className: "relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary-600 via-primary-500 to-primary-400 dark:from-primary-800 dark:via-primary-700 dark:to-primary-600 text-white", children: [_jsx("div", { className: "absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" }), _jsx("div", { className: "relative px-8 py-16 md:py-24 md:px-12", children: _jsxs("div", { className: "max-w-2xl", children: [_jsx("h1", { className: "text-4xl md:text-5xl font-bold mb-4", children: "Bienvenido a Food Store" }), _jsx("p", { className: "text-lg md:text-xl text-primary-100 mb-8", children: "La mejor comida, al mejor precio. Ped\u00ED online y retir\u00E1 cuando quieras." }), _jsxs("div", { className: "flex flex-wrap gap-4", children: [_jsx(Link, { to: "/productos", className: "inline-flex items-center px-6 py-3 bg-white text-primary-600 font-semibold rounded-lg hover:bg-primary-50 transition-colors shadow-lg", children: "Ver Cat\u00E1logo" }), !isAuthenticated && (_jsx(Link, { to: "/auth/register", className: "inline-flex items-center px-6 py-3 bg-white/20 text-white font-semibold rounded-lg hover:bg-white/30 transition-colors backdrop-blur-sm", children: "Registrarse" }))] })] }) })] }), _jsxs("section", { children: [_jsx("h2", { className: "text-2xl font-bold text-gray-900 dark:text-gray-50 mb-8 text-center", children: "\u00BFPor qu\u00E9 elegirnos?" }), _jsx("div", { className: "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6", children: features.map((feature) => (_jsxs("div", { className: "card-base p-6 hover:shadow-md transition-shadow", children: [_jsx("span", { className: "text-4xl block mb-4", children: feature.icon }), _jsx("h3", { className: "text-lg font-semibold text-gray-900 dark:text-gray-50 mb-2", children: feature.title }), _jsx("p", { className: "text-sm text-gray-600 dark:text-gray-400", children: feature.desc })] }, feature.title))) })] }), isAuthenticated && (_jsxs("section", { className: "text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-2xl", children: [_jsx("h2", { className: "text-2xl font-bold text-gray-900 dark:text-gray-50 mb-4", children: "\u00BFListo para pedir?" }), _jsx("p", { className: "text-gray-600 dark:text-gray-400 mb-6", children: "Explor\u00E1 nuestro cat\u00E1logo y arm\u00E1 tu pedido." }), _jsx(Link, { to: "/productos", className: "inline-flex items-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors", children: "Ir al Cat\u00E1logo" })] }))] }));
};
export default HomePage;
//# sourceMappingURL=HomePage.js.map