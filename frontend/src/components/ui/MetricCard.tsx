import type { HTMLAttributes } from 'react'

function joinClasses(...classes: Array<string | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export interface MetricCardProps extends HTMLAttributes<HTMLElement> {
  label: string
  value: string
  supportingText?: string
}

export function MetricCard({ label, value, supportingText, className, ...props }: MetricCardProps) {
  return (
    <article
      className={joinClasses('flex min-h-[120px] w-full flex-col gap-2 rounded-card bg-background-surface p-5 shadow-card', className)}
      {...props}
    >
      <p className="type-caption text-text-secondary">{label}</p>
      <p className="type-number text-text-primary">{value}</p>
      {supportingText && <p className="type-body text-text-secondary">{supportingText}</p>}
    </article>
  )
}
