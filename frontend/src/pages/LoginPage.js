import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * LoginPage — Authentication form
 */
import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useAuthStore } from '@/features/auth/store';
import { apiClient } from '@/shared/http/client';
import { Input } from '@/shared/ui/Input';
import { Button } from '@/shared/ui/Button';
export const LoginPage = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const redirect = searchParams.get('redirect') || '/';
    const { isAuthenticated, rehydrated, setTokens, setUser } = useAuthStore();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    // If already authenticated, redirect (use Navigate component, not navigate() side-effect)
    if (rehydrated && isAuthenticated) {
        console.log("isAuthenticades: ", isAuthenticated);
        console.log("rehydrated", rehydrated);
        //return <Navigate to="/" replace />
    }
    const loginMutation = useMutation({
        mutationFn: async (data) => {
            const tokenResp = await apiClient.post('/auth/login', data);
            const { access_token, refresh_token } = tokenResp.data;
            // Set tokens immediately so /auth/me can use them
            setTokens(access_token, refresh_token);
            // Fetch user data from /auth/me
            const meResp = await apiClient.get('/auth/me');
            const userData = meResp.data;
            setUser({
                id: String(userData.id),
                email: userData.email,
                name: `${userData.nombre} ${userData.apellido}`,
                roles: userData.roles,
            });
            return tokenResp.data;
        },
        onSuccess: () => {
            navigate(redirect, { replace: true });
        },
        onError: (error) => {
            const axiosError = error;
            setError(axiosError?.response?.data?.detail || 'Credenciales inválidas');
        },
    });
    const handleSubmit = (e) => {
        e.preventDefault();
        setError(null);
        loginMutation.mutate({ email, password });
    };
    return (_jsx("div", { className: "min-h-[80vh] flex items-center justify-center px-4", children: _jsx("div", { className: "w-full max-w-md", children: _jsxs("div", { className: "card-base p-8", children: [_jsxs("div", { className: "text-center mb-8", children: [_jsx("h1", { className: "text-2xl font-bold text-gray-900 dark:text-gray-50 mb-2", children: "Iniciar Sesi\u00F3n" }), _jsx("p", { className: "text-sm text-gray-600 dark:text-gray-400", children: "Ingres\u00E1 tus credenciales para continuar" })] }), error && (_jsx("div", { className: "mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300", children: error })), _jsxs("form", { onSubmit: handleSubmit, className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { htmlFor: "email", className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Email" }), _jsx(Input, { id: "email", type: "email", value: email, onChange: (e) => setEmail(e.target.value), placeholder: "tu@email.com", required: true, autoComplete: "email" })] }), _jsxs("div", { children: [_jsx("label", { htmlFor: "password", className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Contrase\u00F1a" }), _jsx(Input, { id: "password", type: "password", value: password, onChange: (e) => setPassword(e.target.value), placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", required: true, autoComplete: "current-password" })] }), _jsx(Button, { type: "submit", className: "w-full", disabled: loginMutation.isPending, children: loginMutation.isPending ? 'Ingresando...' : 'Iniciar Sesión' })] }), _jsxs("p", { className: "mt-6 text-center text-sm text-gray-600 dark:text-gray-400", children: ["\u00BFNo ten\u00E9s cuenta?", ' ', _jsx(Link, { to: "/auth/register", className: "text-primary-600 dark:text-primary-400 hover:underline font-medium", children: "Registrarse" })] })] }) }) }));
};
export default LoginPage;
//# sourceMappingURL=LoginPage.js.map