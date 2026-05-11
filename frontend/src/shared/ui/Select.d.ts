/**
 * Select component
 */
import React from 'react';
export interface SelectOption {
  label: string;
  value: string | number;
}
export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: SelectOption[];
}
export declare const Select: React.ForwardRefExoticComponent<
  SelectProps & React.RefAttributes<HTMLSelectElement>
>;
//# sourceMappingURL=Select.d.ts.map
