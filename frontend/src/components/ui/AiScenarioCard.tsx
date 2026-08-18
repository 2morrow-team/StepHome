import type { ButtonHTMLAttributes, HTMLAttributes, ReactNode } from 'react'

function joinClasses(...classes: Array<string | false | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export interface AiScenarioMetric {
  label: string
  value: string
}

export interface AiScenarioDetail {
  label: string
  value: string
}

export interface AiScenarioCardProps extends HTMLAttributes<HTMLElement> {
  title: string
  changedConditionLabel: string
  beforeValue: string
  afterValue: string
  metrics: AiScenarioMetric[]
  details?: AiScenarioDetail[]
  aiReason: ReactNode
  tradeoff: string
  ctaLabel?: string
  ctaProps?: ButtonHTMLAttributes<HTMLButtonElement>
}

export function AiScenarioCard({
  title,
  changedConditionLabel,
  beforeValue,
  afterValue,
  metrics,
  details = [],
  aiReason,
  tradeoff,
  ctaLabel = '이 조건으로 계획 변경하기',
  ctaProps,
  className,
  ...props
}: AiScenarioCardProps) {
  const { className: ctaClassName, type = 'button', ...buttonProps } = ctaProps ?? {}

  return (
    <article
      className={joinClasses(
        'flex w-full flex-col gap-4 rounded-card border border-border-default bg-background-surface p-6 transition-[border-color,box-shadow]',
        'hover:border-border-interactive hover:ring-1 hover:ring-border-interactive hover:shadow-card',
        className,
      )}
      {...props}
    >
      <h3 className="type-heading text-text-primary">{title}</h3>

      <div className="grid gap-2">
        <p className="type-label text-text-secondary">{changedConditionLabel}</p>
        <div className="flex flex-wrap items-center gap-3 type-heading">
          <span className="text-text-secondary">{beforeValue}</span>
          <span className="text-action-primary" aria-hidden="true">→</span>
          <span className="text-text-primary">{afterValue}</span>
        </div>
      </div>

      <div className="grid gap-3">
        {metrics.map((metric) => (
          <div key={`${metric.label}-${metric.value}`} className="rounded-control bg-background-surface-subtle p-3">
            <p className="type-caption text-text-secondary">{metric.label}</p>
            <p className="mt-2 type-label text-text-primary">{metric.value}</p>
          </div>
        ))}
      </div>

      {details.length > 0 && (
        <dl className="grid gap-2">
          {details.map((detail) => (
            <div key={`${detail.label}-${detail.value}`} className="flex items-start justify-between gap-4">
              <dt className="type-caption text-text-secondary">{detail.label}</dt>
              <dd className="text-right type-label text-text-primary">{detail.value}</dd>
            </div>
          ))}
        </dl>
      )}

      <div className="rounded-control bg-action-subtle p-4">
        <p className="type-label text-action-primary">AI 추천 이유</p>
        <div className="mt-2 type-body text-text-primary">{aiReason}</div>
      </div>

      <div className="rounded-control bg-status-caution-background p-3">
        <p className="type-caption text-status-caution">주의 · {tradeoff}</p>
      </div>

      <button
        type={type}
        className={joinClasses(
          'mt-auto flex min-h-12 w-full items-center justify-center rounded-control bg-action-primary px-4 py-3 type-label text-text-inverse hover:bg-action-hover disabled:bg-disabled-background disabled:text-disabled-text',
          ctaClassName,
        )}
        {...buttonProps}
      >
        {ctaLabel}
      </button>
    </article>
  )
}
