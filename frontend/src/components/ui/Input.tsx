import { useId } from 'react'
import type { InputHTMLAttributes } from 'react'

function joinClasses(...classes: Array<string | false | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  helperText?: string
  errorMessage?: string
}

export function Input({
  id,
  label,
  helperText,
  errorMessage,
  className,
  disabled,
  'aria-describedby': ariaDescribedBy,
  ...props
}: InputProps) {
  const generatedId = useId()
  const inputId = id ?? `input-${generatedId}`
  const hasError = Boolean(errorMessage)
  const message = hasError ? errorMessage : helperText
  const messageId = `${inputId}-message`
  const describedBy = [ariaDescribedBy, message ? messageId : undefined].filter(Boolean).join(' ') || undefined

  return (
    <div className="flex w-full flex-col gap-2">
      <label htmlFor={inputId} className="type-label text-text-primary">
        {label}
      </label>
      <input
        id={inputId}
        className={joinClasses(
          'min-h-12 w-full rounded-control border bg-background-control px-3.5 py-3 type-body text-text-primary',
          hasError ? 'border-status-danger' : 'border-border-interactive',
          'disabled:border-disabled-border disabled:bg-disabled-background disabled:text-disabled-text',
          className,
        )}
        disabled={disabled}
        {...props}
        aria-invalid={hasError ? true : undefined}
        aria-describedby={describedBy}
      />
      {message && (
        <p id={messageId} className={joinClasses('type-caption', hasError ? 'text-status-danger' : 'text-text-secondary')}>
          {message}
        </p>
      )}
    </div>
  )
}
