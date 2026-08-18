import type { ButtonHTMLAttributes } from 'react'

function joinClasses(...classes: Array<string | false | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
}

export function Button({ variant = 'primary', className, type = 'button', ...props }: ButtonProps) {
  const variantClassName =
    variant === 'primary'
      ? 'border border-transparent bg-action-primary text-action-on-primary hover:bg-action-hover disabled:border-disabled-border disabled:bg-disabled-background disabled:text-disabled-text'
      : 'border border-border-default bg-background-surface-subtle text-text-primary hover:border-border-focus hover:bg-action-subtle disabled:border-disabled-border disabled:bg-disabled-background disabled:text-disabled-text'

  return (
    <button
      type={type}
      className={joinClasses(
        'inline-flex min-h-12 items-center justify-center rounded-control px-4 py-3 type-label',
        variantClassName,
        className,
      )}
      {...props}
    />
  )
}
