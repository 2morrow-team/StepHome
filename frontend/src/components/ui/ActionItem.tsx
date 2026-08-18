import { useEffect, useState } from 'react'
import type { ButtonHTMLAttributes, MouseEvent } from 'react'

function joinClasses(...classes: Array<string | false | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export type ActionItemStatus = 'incomplete' | 'complete' | 'pending'

export interface ActionItemProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  status?: ActionItemStatus
  actionName?: string
  description?: string
  reason?: string
  title?: string
  detail?: string
  step?: string | number
  onStatusChange?: (status: Exclude<ActionItemStatus, 'pending'>) => void
}

function normalizeStatus(status: ActionItemStatus | undefined): Exclude<ActionItemStatus, 'pending'> {
  return status === 'complete' ? 'complete' : 'incomplete'
}

export function ActionItem({
  status = 'incomplete',
  actionName,
  description,
  reason,
  title,
  detail,
  step,
  className,
  onClick,
  onStatusChange,
  type = 'button',
  ...props
}: ActionItemProps) {
  const [currentStatus, setCurrentStatus] = useState(normalizeStatus(status))
  const isComplete = currentStatus === 'complete'
  const displayTitle = actionName ?? title
  const displayDescription = description ?? detail

  useEffect(() => {
    setCurrentStatus(normalizeStatus(status))
  }, [status])

  const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
    onClick?.(event)
    if (event.defaultPrevented) return

    const nextStatus = isComplete ? 'incomplete' : 'complete'
    setCurrentStatus(nextStatus)
    onStatusChange?.(nextStatus)
  }

  return (
    <button
      type={type}
      className={joinClasses(
        'flex min-h-[112px] w-full items-start gap-3.5 rounded-control border border-border-default bg-background-surface p-4 text-left transition-colors hover:border-border-interactive hover:bg-background-control',
        className,
      )}
      aria-pressed={isComplete}
      onClick={handleClick}
      {...props}
    >
      <span
        className={joinClasses(
          'inline-flex size-8 shrink-0 items-center justify-center rounded-pill type-label',
          isComplete
            ? 'border border-status-success bg-status-success-background text-status-success'
            : 'border border-disabled-border bg-disabled-background text-disabled-text',
        )}
      >
        <span aria-hidden="true">{isComplete ? '✓' : '−'}</span>
        <span className="sr-only">{isComplete ? '완료' : '미완료'}</span>
      </span>
      <div className="min-w-0 flex-1 space-y-2">
        {displayTitle && <h3 className="type-heading text-text-primary">{displayTitle}</h3>}
        {displayDescription && <p className="type-body text-text-primary">{displayDescription}</p>}
        {reason && <p className="type-caption text-text-secondary">추천 이유: {reason}</p>}
      </div>
    </button>
  )
}
