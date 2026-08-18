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
  href?: string
  benefitLabel?: string
  benefitValue?: string
  supportingText?: string
}

export function PolicyCard({
  title,
  status,
  statusLabel,
  description,
  href,
  benefitLabel,
  benefitValue,
  supportingText,
  className,
  ...props
}: PolicyCardProps) {
  void benefitLabel
  void benefitValue
  void supportingText

  return (
    <article
      className={joinClasses('flex min-h-[116px] w-full flex-col gap-3 rounded-card bg-background-surface p-5 shadow-card', className)}
      {...props}
    >
      <div className="flex min-w-0 items-start justify-between gap-4">
        <h3 className="min-w-0 break-words type-heading text-text-primary">{title}</h3>
        <StatusBadge status={status} label={statusLabel} className="shrink-0" />
      </div>
      <div className="flex min-w-0 items-center justify-between gap-4">
        <p className="min-w-0 truncate type-body text-text-secondary">{description}</p>
        {href && (
          <a
            href={href}
            target="_blank"
            rel="noreferrer"
            className="shrink-0 type-caption text-action-primary hover:text-action-hover"
            onClick={(event) => event.stopPropagation()}
          >
            바로가기 ↗
          </a>
        )}
      </div>
    </article>
  )
}
