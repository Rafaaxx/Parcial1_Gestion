import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * RegisterPage — User registration form
 */
import { useState } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useAuthStore } from '@/features/auth/store';
import { apiClient } from '@/shared/http/client';
import { Input } from '@/shared/ui/Input';
import { Button } from '@/shared/ui/Button';
export const RegisterPage = () => {
    const navigate = useNavigate();
    const { isAuthenticated, rehydrated, setTokens, setUser } = useAuthStore();
    const [nombre, setNombre] = useState('');
    const [apellido, setApellido] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState(null);
    const [fieldErrors, setFieldErrors] = useState({});
    // If already authenticated, redirect (use Navigate component, not navigate() side-effect)
    if (rehydrated && isAuthenticated) {
        return _jsx(Navigate, { to: "/", replace: true });
    }
    const registerMutation = useMutation({
        mutationFn: async (data) => {
            const tokenResp = await apiClient.post('/auth/register', data);
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
            navigate('/', { replace: true });
        },
        onError: (err) => {
            const axiosError = err;
            const detail = axiosError?.response?.data?.detail;
            if (typeof detail === 'object' && detail !== null) {
                setFieldErrors(detail);
                setError('Por favor, corregí los errores del formulario.');
            }
            else if (typeof detail === 'string') {
                setError(detail);
            }
            else {
                setError('Ocurrió un error al registrarse. Intentá de nuevo.');
            }
        },
    });
    const handleSubmit = (e) => {
        e.preventDefault();
        setError(null);
        setFieldErrors({});
        // Client-side validation
        if (password !== confirmPassword) {
            setError('Las contraseñas no coinciden.');
            return;
        }
        if (nombre.trim().length < 2) {
            setFieldErrors({ nombre: 'El nombre debe tener al menos 2 caracteres.' });
            return;
        }
        registerMutation.mutate({
            nombre: nombre.trim(),
            apellido: apellido.trim(),
            email: email.trim(),
            password,
        });
    };
    return (_jsx("div", { className: "min-h-[80vh] flex items-center justify-center px-4", children: _jsx("div", { className: "w-full max-w-md", children: _jsxs("div", { className: "card-base p-8", children: [_jsxs("div", { className: "text-center mb-8", children: [_jsx("h1", { className: "text-2xl font-bold text-gray-900 dark:text-gray-50 mb-2", children: "Crear Cuenta" }), _jsx("p", { className: "text-sm text-gray-600 dark:text-gray-400", children: "Complet\u00E1 tus datos para registrarte" })] }), error && (_jsx("div", { className: "mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-700 dark:text-red-300", children: error })), _jsxs("form", { onSubmit: handleSubmit, className: "space-y-4", children: [_jsxs("div", { className: "grid grid-cols-2 gap-4", children: [_jsxs("div", { children: [_jsx("label", { htmlFor: "nombre", className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Nombre" }), _jsx(Input, { id: "nombre", type: "text", value: nombre, onChange: (e) => setNombre(e.target.value), placeholder: "Juan", required: true, autoComplete: "given-name" }), fieldErrors.nombre && (_jsx("p", { className: "mt-1 text-xs text-red-500", children: fieldErrors.nombre }))] }), _jsxs("div", { children: [_jsx("label", { htmlFor: "apellido", className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Apellido" }), _jsx(Input, { id: "apellido", type: "text", value: apellido, onChange: (e) => setApellido(e.target.value), placeholder: "P\u00E9rez", required: true, autoComplete: "family-name" }), fieldErrors.apellido && (_jsx("p", { className: "mt-1 text-xs text-red-500", children: fieldErrors.apellido }))] })] }), _jsxs("div", { children: [_jsx("label", { htmlFor: "email", className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Email" }), _jsx(Input, { id: "email", type: "email", value: email, onChange: (e) => setEmail(e.target.value), placeholder: "tu@email.com", required: true, autoComplete: "email" }), fieldErrors.email && (_jsx("p", { className: "mt-1 text-xs text-red-500", children: fieldErrors.email }))] }), _jsxs("div", { children: [_jsx("label", { htmlFor: "password", className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Contrase\u00F1a" }), _jsx(Input, { id: "password", type: "password", value: password, onChange: (e) => setPassword(e.target.value), placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", required: true, autoComplete: "new-password", minLength: 6 }), fieldErrors.password && (_jsx("p", { className: "mt-1 text-xs text-red-500", children: fieldErrors.password }))] }), _jsxs("div", { children: [_jsx("label", { htmlFor: "confirmPassword", className: "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1", children: "Confirmar Contrase\u00F1a" }), _jsx(Input, { id: "confirmPassword", type: "password", value: confirmPassword, onChange: (e) => setConfirmPassword(e.target.value), placeholder: "\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022", required: true, autoComplete: "new-password" })] }), _jsx(Button, { type: "submit", className: "w-full", disabled: registerMutation.isPending, children: registerMutation.isPending ? 'Registrando...' : 'Crear Cuenta' })] }), _jsxs("p", { className: "mt-6 text-center text-sm text-gray-600 dark:text-gray-400", children: ["\u00BFYa ten\u00E9s cuenta?", ' ', _jsx(Link, { to: "/auth/login", className: "text-primary-600 dark:text-primary-400 hover:underline font-medium", children: "Iniciar Sesi\u00F3n" })] })] }) }) }));
};
export default RegisterPage;
//# sourceMappingURL=RegisterPage.js.map