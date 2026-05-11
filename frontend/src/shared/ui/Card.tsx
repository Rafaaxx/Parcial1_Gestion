/**
 * Card component for content containers
 */

import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  interactive?: boolean;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className = '', interactive = false, children, ...props }, ref) => {
    const hoverStyles = interactive ? 'hover:shadow-lg transition-shadow' : '';

    return (
      <div ref={ref} className={`card-base p-4 ${hoverStyles} ${className}`} {...props}>
        {children}
      </div>
    );
  }
);

Card.displayName = 'Card';
