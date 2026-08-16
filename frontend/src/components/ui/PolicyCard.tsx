import type { HTMLAttributes } from 'react'
import { StatusBadge } from './StatusBadge'
import type { StatusBadgeProps } from './StatusBadge'

function joinClasses(...classes: Array<string | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export interface PolicyCardProps extends HTMLAttributes<HTMLElement> {
  title: string
  status: StatusBadgeProps['status']
  statusLabel?: string
  description: string
  benefitLabel?: string
  benefitValue?: string
  supportingText?: string
}

export function PolicyCard({
  title,
  status,
  statusLabel,
  description,
  benefitLabel,
  benefitValue,
  supportingText,
  className,
  ...props
}: PolicyCardProps) {
  const hasBenefit = Boolean(benefitLabel && benefitValue)

  return (
    <article
      className={joinClasses('flex min-h-[252px] w-full max-w-[584px] flex-col gap-4 rounded-card bg-background-surface px-5 py-policy-card-y shadow-card', className)}
      {...props}
    >
      <div className="flex min-w-0 items-start justify-between gap-4">
        <h3 className="min-w-0 break-words type-heading text-text-primary">{title}</h3>
        <StatusBadge status={status} label={statusLabel} className="shrink-0" />
      </div>
      <p className="type-body text-text-primary">{description}</p>
      {hasBenefit && (
        <dl className="flex flex-col gap-2">
          <dt className="type-caption text-text-secondary">{benefitLabel}</dt>
          <dd className="type-number text-text-primary">{benefitValue}</dd>
        </dl>
      )}
      {supportingText && <p className="type-body text-text-secondary">{supportingText}</p>}
    </article>
  )
}
