import type { ComponentPropsWithoutRef, PropsWithChildren } from 'react'

function joinClasses(...classes: Array<string | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export type PageContainerProps = PropsWithChildren<ComponentPropsWithoutRef<'main'>>

export function PageContainer({ className, children, ...props }: PageContainerProps) {
  return (
    <main className={joinClasses('mx-auto w-full max-w-[640px] px-4 sm:px-6', className)} {...props}>
      {children}
    </main>
  )
}
