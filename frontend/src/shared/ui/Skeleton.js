import { jsx as _jsx } from "react/jsx-runtime";
export const Skeleton = ({ width = '100%', height = '1rem', count = 1, circle = false, className = '', ...props }) => {
    const skeletons = Array(count).fill(0);
    return (_jsx("div", { className: "flex flex-col gap-2", children: skeletons.map((_, idx) => (_jsx("div", { className: `bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 animate-pulse ${circle ? 'rounded-full' : 'rounded'} ${className}`, style: {
                width: typeof width === 'number' ? `${width}px` : width,
                height: typeof height === 'number' ? `${height}px` : height,
            }, ...props }, idx))) }));
};
//# sourceMappingURL=Skeleton.js.map