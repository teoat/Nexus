/**
 * 🃏 Card Component
 * Flexible card component for content organization
 */

import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils/cn';

const cardVariants = cva(
  // Base styles
  'rounded-lg border bg-card text-card-foreground shadow-sm',
  {
    variants: {
      variant: {
        default: 'border-neutral-200 bg-white',
        elevated: 'border-neutral-200 bg-white shadow-md',
        outlined: 'border-neutral-300 bg-white',
        filled: 'border-transparent bg-neutral-50',
        ghost: 'border-transparent bg-transparent shadow-none',
        success: 'border-success-200 bg-success-50',
        warning: 'border-warning-200 bg-warning-50',
        error: 'border-error-200 bg-error-50',
        info: 'border-primary-200 bg-primary-50',
      },
      size: {
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
        xl: 'p-10',
      },
      interactive: {
        true: 'cursor-pointer transition-all duration-200 hover:shadow-md hover:scale-[1.02] active:scale-[0.98]',
        false: '',
      },
      loading: {
        true: 'animate-pulse',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
      interactive: false,
      loading: false,
    },
  }
);

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  /**
   * Card content
   */
  children: React.ReactNode;
  
  /**
   * Card title
   */
  title?: string;
  
  /**
   * Card description
   */
  description?: string;
  
  /**
   * Card actions (buttons, etc.)
   */
  actions?: React.ReactNode;
  
  /**
   * Card header content
   */
  header?: React.ReactNode;
  
  /**
   * Card footer content
   */
  footer?: React.ReactNode;
  
  /**
   * Loading state
   */
  loading?: boolean;
  
  /**
   * Click handler (makes card interactive)
   */
  onClick?: () => void;
  
  /**
   * Card status
   */
  status?: 'default' | 'success' | 'warning' | 'error' | 'info';
  
  /**
   * Card badge
   */
  badge?: React.ReactNode;
  
  /**
   * Card icon
   */
  icon?: React.ReactNode;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      className,
      variant,
      size,
      interactive,
      loading,
      title,
      description,
      actions,
      header,
      footer,
      onClick,
      status,
      badge,
      icon,
      children,
      ...props
    },
    ref
  ) => {
    const isInteractive = interactive || !!onClick;
    const cardVariant = status ? status : variant;

    return (
      <div
        ref={ref}
        className={cn(
          cardVariants({ 
            variant: cardVariant, 
            size, 
            interactive: isInteractive, 
            loading 
          }),
          className
        )}
        onClick={onClick}
        role={isInteractive ? 'button' : undefined}
        tabIndex={isInteractive ? 0 : undefined}
        onKeyDown={isInteractive ? (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onClick?.();
          }
        } : undefined}
        {...props}
      >
        {/* Header */}
        {(header || title || description || icon || badge) && (
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-start space-x-3">
              {icon && (
                <div className="flex-shrink-0">
                  {icon}
                </div>
              )}
              <div className="flex-1 min-w-0">
                {title && (
                  <h3 className="text-lg font-semibold text-neutral-900 truncate">
                    {title}
                  </h3>
                )}
                {description && (
                  <p className="mt-1 text-sm text-neutral-600 line-clamp-2">
                    {description}
                  </p>
                )}
              </div>
            </div>
            {badge && (
              <div className="flex-shrink-0 ml-2">
                {badge}
              </div>
            )}
          </div>
        )}

        {/* Custom Header */}
        {header && !title && !description && (
          <div className="mb-4">
            {header}
          </div>
        )}

        {/* Content */}
        <div className="flex-1">
          {children}
        </div>

        {/* Actions */}
        {actions && (
          <div className="mt-4 flex items-center justify-end space-x-2">
            {actions}
          </div>
        )}

        {/* Footer */}
        {footer && (
          <div className="mt-4 pt-4 border-t border-neutral-200">
            {footer}
          </div>
        )}
      </div>
    );
  }
);

Card.displayName = 'Card';

// Card Header Component
export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex flex-col space-y-1.5 p-6', className)}
      {...props}
    >
      {children}
    </div>
  )
);

CardHeader.displayName = 'CardHeader';

// Card Title Component
export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}

const CardTitle = React.forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ className, children, as: Component = 'h3', ...props }, ref) => (
    <Component
      ref={ref}
      className={cn('text-2xl font-semibold leading-none tracking-tight', className)}
      {...props}
    >
      {children}
    </Component>
  )
);

CardTitle.displayName = 'CardTitle';

// Card Description Component
export interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

const CardDescription = React.forwardRef<HTMLParagraphElement, CardDescriptionProps>(
  ({ className, children, ...props }, ref) => (
    <p
      ref={ref}
      className={cn('text-sm text-neutral-600', className)}
      {...props}
    >
      {children}
    </p>
  )
);

CardDescription.displayName = 'CardDescription';

// Card Content Component
export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('p-6 pt-0', className)}
      {...props}
    >
      {children}
    </div>
  )
);

CardContent.displayName = 'CardContent';

// Card Footer Component
export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex items-center p-6 pt-0', className)}
      {...props}
    >
      {children}
    </div>
  )
);

CardFooter.displayName = 'CardFooter';

// Card Actions Component
export interface CardActionsProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  align?: 'left' | 'center' | 'right' | 'between';
}

const CardActions = React.forwardRef<HTMLDivElement, CardActionsProps>(
  ({ className, children, align = 'right', ...props }, ref) => {
    const alignClasses = {
      left: 'justify-start',
      center: 'justify-center',
      right: 'justify-end',
      between: 'justify-between',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'flex items-center space-x-2',
          alignClasses[align],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardActions.displayName = 'CardActions';

export { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardDescription, 
  CardContent, 
  CardFooter, 
  CardActions,
  cardVariants 
};
export type { 
  CardProps, 
  CardHeaderProps, 
  CardTitleProps, 
  CardDescriptionProps, 
  CardContentProps, 
  CardFooterProps, 
  CardActionsProps 
};
