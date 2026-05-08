/**
 * Skeleton loader component for loading states
 */

import React from 'react'

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  width?: string | number
  height?: string | number
  count?: number
  circle?: boolean
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '1rem',
  count = 1,
  circle = false,
  className = '',
  ...props
}) => {
  const skeletons = Array(count).fill(0)

  return (
    <div className="flex flex-col gap-2">
      {skeletons.map((_, idx) => (
        <div
          key={idx}
          className={`bg-gradient-to-r from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800 animate-pulse ${
            circle ? 'rounded-full' : 'rounded'
          } ${className}`}
          style={{
            width: typeof width === 'number' ? `${width}px` : width,
            height: typeof height === 'number' ? `${height}px` : height,
          }}
          {...props}
        />
      ))}
    </div>
  )
}
