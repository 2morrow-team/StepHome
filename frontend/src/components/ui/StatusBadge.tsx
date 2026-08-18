import type { HTMLAttributes } from 'react'

function joinClasses(...classes: Array<string | undefined>) {
  return classes.filter(Boolean).join(' ')
}

const statusConfig = {
  available: {
    defaultLabel: '이용 가능',
    className: 'bg-status-success-background text-status-success',
  },
  conditional: {
    defaultLabel: '조건 충족 후 가능',
    className: 'bg-status-caution-background text-status-caution',
  },
  review: {
    defaultLabel: '추가 확인 필요',
    className: 'bg-background-surface-subtle text-text-secondary',
  },
  unavailable: {
    defaultLabel: '현재 대상 아님',
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
    <span
      className={joinClasses('inline-flex min-h-9 items-center justify-center rounded-pill px-3 py-2 type-label', config.className, className)}
      {...props}
    >
      {label ?? config.defaultLabel}
    </span>
  )
}
