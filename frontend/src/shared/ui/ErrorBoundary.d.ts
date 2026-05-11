/**
 * ErrorBoundary component to catch and display React errors gracefully
 */
import React from 'react';
interface ErrorBoundaryProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
}
interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
}
export declare class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps);
    static getDerivedStateFromError(error: Error): ErrorBoundaryState;
    componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void;
    handleRetry: () => void;
    render(): React.ReactNode;
}
export default ErrorBoundary;
//# sourceMappingURL=ErrorBoundary.d.ts.map