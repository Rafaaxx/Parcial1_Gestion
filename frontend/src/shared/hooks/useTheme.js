/**
 * useTheme hook for accessing and toggling theme from UI store
 */
import { useUIStore } from '@/features/ui/store';
export function useTheme() {
    const theme = useUIStore((state) => state.theme);
    const toggleTheme = useUIStore((state) => state.toggleTheme);
    // Apply theme to document
    const applyTheme = (newTheme) => {
        if (typeof document !== 'undefined') {
            if (newTheme === 'dark') {
                document.documentElement.classList.add('dark');
            }
            else {
                document.documentElement.classList.remove('dark');
            }
        }
    };
    // Toggle and apply
    const handleToggleTheme = () => {
        toggleTheme();
        const newTheme = theme === 'light' ? 'dark' : 'light';
        applyTheme(newTheme);
    };
    return {
        theme,
        toggleTheme: handleToggleTheme,
        applyTheme,
    };
}
//# sourceMappingURL=useTheme.js.map