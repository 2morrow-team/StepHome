import type { HTMLAttributes } from 'react'

function joinClasses(...classes: Array<string | undefined>) {
  return classes.filter(Boolean).join(' ')
}

const statusConfig = {
  available: {
    defaultLabel: '이용 가능',
    className: 'bg-status-success-background text-status-success',
  },
  review: {
    defaultLabel: '추가 확인',
    className: 'bg-status-caution-background text-status-caution',
  },
  unavailable: {
    defaultLabel: '이용 불가',
    className: 'bg-status-danger-background text-status-danger',
  },
} as const

export interface StatusBadgeProps extends HTMLAttributes<HTMLSpanElement> {
  status: keyof typeof statusConfig
  label?: string
}

export function StatusBadge({ status, label, className, ...props }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <span className={joinClasses('inline-flex min-h-7 items-center rounded-pill px-2.5 py-1.5 type-caption', config.className, className)} {...props}>
      {label ?? config.defaultLabel}
    </span>
  )
}
