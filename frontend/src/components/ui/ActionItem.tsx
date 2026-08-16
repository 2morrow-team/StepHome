import type { HTMLAttributes } from 'react'

function joinClasses(...classes: Array<string | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export interface ActionItemProps extends HTMLAttributes<HTMLElement> {
  status: 'pending' | 'complete'
  step: string | number
  title: string
  detail?: string
}

export function ActionItem({ status, step, title, detail, className, ...props }: ActionItemProps) {
  const isComplete = status === 'complete'

  return (
    <article
      className={joinClasses('flex min-h-[88px] w-full max-w-[584px] items-center gap-3.5 rounded-control border border-border-default bg-background-surface p-4', className)}
      {...props}
    >
      <span
        className={joinClasses(
          'inline-flex size-8 shrink-0 items-center justify-center rounded-pill type-label',
          isComplete
            ? 'border border-status-success bg-status-success-background text-status-success'
            : 'border border-border-default bg-action-subtle text-action-primary',
        )}
      >
        <span aria-hidden="true">{isComplete ? '✓' : step}</span>
        <span className="sr-only">{isComplete ? `${step}단계 완료` : `${step}단계 진행 중`}</span>
      </span>
      <div className="min-w-0 flex-1">
        <h3 className="type-heading text-text-primary">{title}</h3>
        {detail && <p className="mt-1 type-body text-text-secondary">{detail}</p>}
      </div>
    </article>
  )
}
