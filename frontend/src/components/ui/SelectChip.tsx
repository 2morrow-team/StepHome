import type { ButtonHTMLAttributes } from 'react'

function joinClasses(...classes: Array<string | false | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export interface SelectChipProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  selected: boolean
}

export function SelectChip({ selected, disabled, className, type = 'button', children, ...props }: SelectChipProps) {
  const chipClassName = selected
    ? 'bg-action-primary text-action-on-primary'
    : 'border border-border-interactive bg-background-surface text-text-primary'
  const disabledClassName = disabled
    ? 'border border-disabled-border bg-disabled-background text-disabled-text'
    : undefined

  return (
    <button
      type={type}
      className={joinClasses('inline-flex min-h-12 items-center justify-center rounded-pill p-1', className)}
      disabled={disabled}
      {...props}
      aria-pressed={selected}
    >
      <span className={joinClasses('inline-flex h-10 items-center justify-center gap-2 rounded-pill px-4 py-2 type-label', chipClassName, disabledClassName)}>
        {selected && <span aria-hidden="true">✓</span>}
        <span>{children}</span>
      </span>
    </button>
  )
}
