/**
 * 🔘 Button Component
 * Comprehensive button component with multiple variants and states
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils/cn';

const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        // Primary variants
        primary: 'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800',
        'primary-ghost': 'bg-primary-50 text-primary-700 hover:bg-primary-100 active:bg-primary-200',
        'primary-outline': 'border border-primary-600 text-primary-700 hover:bg-primary-50 active:bg-primary-100',
        
        // Secondary variants
        secondary: 'bg-secondary-600 text-white hover:bg-secondary-700 active:bg-secondary-800',
        'secondary-ghost': 'bg-secondary-50 text-secondary-700 hover:bg-secondary-100 active:bg-secondary-200',
        'secondary-outline': 'border border-secondary-600 text-secondary-700 hover:bg-secondary-50 active:bg-secondary-100',
        
        // Neutral variants
        neutral: 'bg-neutral-600 text-white hover:bg-neutral-700 active:bg-neutral-800',
        'neutral-ghost': 'bg-neutral-50 text-neutral-700 hover:bg-neutral-100 active:bg-neutral-200',
        'neutral-outline': 'border border-neutral-300 text-neutral-700 hover:bg-neutral-50 active:bg-neutral-100',
        
        // Status variants
        success: 'bg-success-600 text-white hover:bg-success-700 active:bg-success-800',
        warning: 'bg-warning-600 text-white hover:bg-warning-700 active:bg-warning-800',
        error: 'bg-error-600 text-white hover:bg-error-700 active:bg-error-800',
        
        // Ghost variants
        ghost: 'hover:bg-neutral-100 active:bg-neutral-200',
        'ghost-success': 'hover:bg-success-50 active:bg-success-100 text-success-700',
        'ghost-warning': 'hover:bg-warning-50 active:bg-warning-100 text-warning-700',
        'ghost-error': 'hover:bg-error-50 active:bg-error-100 text-error-700',
        
        // Link variant
        link: 'text-primary-600 underline-offset-4 hover:underline active:text-primary-800',
        
        // Destructive variant
        destructive: 'bg-error-600 text-white hover:bg-error-700 active:bg-error-800',
        'destructive-ghost': 'bg-error-50 text-error-700 hover:bg-error-100 active:bg-error-200',
        'destructive-outline': 'border border-error-600 text-error-700 hover:bg-error-50 active:bg-error-100',
      },
      size: {
        xs: 'h-7 px-2 text-xs',
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-11 px-6 text-base',
        xl: 'h-12 px-8 text-base',
        '2xl': 'h-14 px-10 text-lg',
      },
      width: {
        auto: 'w-auto',
        full: 'w-full',
        fit: 'w-fit',
      },
      loading: {
        true: 'cursor-not-allowed',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      width: 'auto',
      loading: false,
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /**
   * Button content
   */
  children: React.ReactNode;
  
  /**
   * Loading state
   */
  loading?: boolean;
  
  /**
   * Loading text (shown when loading is true)
   */
  loadingText?: string;
  
  /**
   * Left icon
   */
  leftIcon?: React.ReactNode;
  
  /**
   * Right icon
   */
  rightIcon?: React.ReactNode;
  
  /**
   * Icon only (for icon buttons)
   */
  iconOnly?: boolean;
  
  /**
   * Tooltip text
   */
  tooltip?: string;
  
  /**
   * Button group position
   */
  groupPosition?: 'first' | 'middle' | 'last' | 'only';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      width,
      loading = false,
      loadingText,
      leftIcon,
      rightIcon,
      iconOnly = false,
      tooltip,
      groupPosition,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;
    
    // Loading icon component
    const LoadingIcon = () => (
      <svg
        className="animate-spin -ml-1 mr-2 h-4 w-4"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    );

    // Group position styles
    const getGroupStyles = () => {
      if (!groupPosition) return '';
      
      const baseStyles = 'relative';
      switch (groupPosition) {
        case 'first':
          return `${baseStyles} rounded-r-none`;
        case 'middle':
          return `${baseStyles} rounded-none -ml-px`;
        case 'last':
          return `${baseStyles} rounded-l-none -ml-px`;
        case 'only':
          return baseStyles;
        default:
          return baseStyles;
      }
    };

    return (
      <button
        className={cn(
          buttonVariants({ variant, size, width, loading }),
          getGroupStyles(),
          className
        )}
        disabled={isDisabled}
        ref={ref}
        title={tooltip}
        {...props}
      >
        {loading && <LoadingIcon />}
        {!loading && leftIcon && <span className="mr-2">{leftIcon}</span>}
        
        {loading ? (
          <span>{loadingText || 'Loading...'}</span>
        ) : iconOnly ? (
          <span className="flex items-center justify-center">
            {leftIcon || rightIcon}
          </span>
        ) : (
          <span className="flex items-center">
            {children}
            {rightIcon && <span className="ml-2">{rightIcon}</span>}
          </span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

// Button Group Component
export interface ButtonGroupProps {
  children: React.ReactNode;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  variant?: 'primary' | 'secondary' | 'neutral' | 'outline' | 'ghost';
}

const ButtonGroup = React.forwardRef<HTMLDivElement, ButtonGroupProps>(
  ({ children, className, orientation = 'horizontal', size = 'md', variant = 'primary' }, ref) => {
    const childrenArray = React.Children.toArray(children);
    const totalChildren = childrenArray.length;

    return (
      <div
        ref={ref}
        className={cn(
          'inline-flex',
          orientation === 'vertical' ? 'flex-col' : 'flex-row',
          className
        )}
        role="group"
      >
        {React.Children.map(childrenArray, (child, index) => {
          if (React.isValidElement(child)) {
            const position = totalChildren === 1 ? 'only' :
                           index === 0 ? 'first' :
                           index === totalChildren - 1 ? 'last' : 'middle';
            
            return React.cloneElement(child, {
              ...child.props,
              groupPosition: position,
              size: child.props.size || size,
              variant: child.props.variant || variant,
            });
          }
          return child;
        })}
      </div>
    );
  }
);

ButtonGroup.displayName = 'ButtonGroup';

export { Button, ButtonGroup, buttonVariants };
export type { ButtonProps, ButtonGroupProps };
