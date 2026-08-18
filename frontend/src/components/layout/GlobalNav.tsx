import { NavLink } from 'react-router-dom'
import logo from '../../assets/logo.webp'

function joinClasses(...classes: Array<string | false | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export type GlobalNavItemKey = 'plan' | 'simulator' | 'replan'

export interface GlobalNavItem {
  key: GlobalNavItemKey
  label: string
  to: string
}

export interface GlobalNavProps {
  items?: GlobalNavItem[]
  className?: string
}

const defaultItems: GlobalNavItem[] = [
  { key: 'plan', label: '내 독립 플랜', to: '/' },
  { key: 'simulator', label: 'AI 시뮬레이터', to: '/simulator' },
  { key: 'replan', label: '플랜 수정', to: '/replan' },
]

export function GlobalNav({ items = defaultItems, className }: GlobalNavProps) {
  return (
    <header className={joinClasses('border-b border-border-subtle bg-background-surface', className)}>
      <nav
        className="mx-auto flex min-h-20 w-full max-w-7xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:gap-6 sm:px-6 sm:py-0 lg:px-8"
        aria-label="주요 메뉴"
      >
        <NavLink to="/" className="flex h-[46px] w-[110px] shrink-0 items-center overflow-hidden" aria-label="StepHome 홈">
          <img src={logo} alt="StepHome" className="h-full w-full object-cover" />
        </NavLink>

        <div className="flex min-w-0 flex-1 items-center gap-2 overflow-x-auto">
          {items.map((item) => (
            <NavLink
              key={item.key}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                joinClasses(
                  'flex min-h-9 shrink-0 items-center justify-center rounded-subtle px-3 py-2 type-label transition-colors',
                  isActive ? 'bg-action-subtle text-action-primary' : 'text-text-secondary hover:bg-background-surface-subtle hover:text-text-primary',
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </header>
  )
}
