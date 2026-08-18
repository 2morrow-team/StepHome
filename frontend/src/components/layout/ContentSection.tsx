import type { ComponentPropsWithoutRef, PropsWithChildren } from 'react'

function joinClasses(...classes: Array<string | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export type ContentSectionProps = PropsWithChildren<ComponentPropsWithoutRef<'section'>>

export function ContentSection({ className, children, ...props }: ContentSectionProps) {
  return (
    <section className={joinClasses('w-full space-y-4', className)} {...props}>
      {children}
    </section>
  )
}
