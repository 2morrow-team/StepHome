import { act, type ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, beforeAll, describe, expect, it } from 'vitest'
import { Button, Input, SelectChip, StatusBadge } from './index'

type RenderedView = {
  container: HTMLDivElement
  rerender: (element: ReactNode) => void
}

const renderedRoots: Array<ReturnType<typeof createRoot>> = []

beforeAll(() => {
  const reactGlobal = globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT?: boolean }
  reactGlobal.IS_REACT_ACT_ENVIRONMENT = true
})

afterEach(() => {
  act(() => {
    renderedRoots.splice(0).forEach((root) => root.unmount())
  })
  document.body.innerHTML = ''
})

function render(element: ReactNode): RenderedView {
  const container = document.createElement('div')
  document.body.appendChild(container)
  const root = createRoot(container)
  renderedRoots.push(root)

  act(() => {
    root.render(element)
  })

  return {
    container,
    rerender: (nextElement) => {
      act(() => {
        root.render(nextElement)
      })
    },
  }
}

describe('Input', () => {
  it('connects a generated input id to its label and helper text', () => {
    const { container } = render(<Input label="이름" helperText="실명을 입력해 주세요." />)
    const input = container.querySelector<HTMLInputElement>('input')!
    const label = container.querySelector<HTMLLabelElement>('label')!
    const describedBy = input.getAttribute('aria-describedby')!

    expect(input.id).not.toBe('')
    expect(label.htmlFor).toBe(input.id)
    expect(input.getAttribute('aria-invalid')).toBeNull()
    expect(describedBy.split(' ')).toContain(`${input.id}-message`)
    expect(container.querySelector(`#${CSS.escape(`${input.id}-message`)}`)?.textContent).toBe('실명을 입력해 주세요.')
  })

  it('prioritizes an error message and connects its ARIA description', () => {
    const { container } = render(
      <Input
        id="email-input"
        label="이메일"
        helperText="이메일 형식을 사용해 주세요."
        errorMessage="이메일 주소를 확인해 주세요."
        aria-describedby="external-description"
      />,
    )
    const input = container.querySelector<HTMLInputElement>('input')!
    const describedBy = input.getAttribute('aria-describedby')!.split(' ')

    expect(input.getAttribute('aria-invalid')).toBe('true')
    expect(describedBy).toEqual(['external-description', 'email-input-message'])
    expect(container.textContent).toContain('이메일 주소를 확인해 주세요.')
    expect(container.textContent).not.toContain('이메일 형식을 사용해 주세요.')
  })
})

describe('Button', () => {
  it('uses button as the default type and preserves native attributes when disabled', () => {
    const { container } = render(<Button name="submit-plan" disabled aria-label="계획 생성">생성</Button>)
    const button = container.querySelector<HTMLButtonElement>('button')!

    expect(button.type).toBe('button')
    expect(button.disabled).toBe(true)
    expect(button.name).toBe('submit-plan')
    expect(button.getAttribute('aria-label')).toBe('계획 생성')
  })
})

describe('SelectChip', () => {
  it('exposes controlled selection through aria-pressed and a visible check', () => {
    const { container, rerender } = render(<SelectChip selected>서울</SelectChip>)
    const button = () => container.querySelector<HTMLButtonElement>('button')!

    expect(button().getAttribute('aria-pressed')).toBe('true')
    expect(container.querySelector('[aria-hidden="true"]')?.textContent).toBe('✓')

    rerender(<SelectChip selected={false}>서울</SelectChip>)

    expect(button().getAttribute('aria-pressed')).toBe('false')
    expect(container.querySelector('[aria-hidden="true"]')).toBeNull()
    expect(button().textContent).toBe('서울')
  })
})

describe('StatusBadge', () => {
  it('renders the default label for each status and accepts an override', () => {
    const { container, rerender } = render(<StatusBadge status="available" />)

    expect(container.textContent).toBe('이용 가능')

    rerender(<StatusBadge status="review" />)
    expect(container.textContent).toBe('추가 확인')

    rerender(<StatusBadge status="unavailable" />)
    expect(container.textContent).toBe('이용 불가')

    rerender(<StatusBadge status="available" label="신청 가능" />)
    expect(container.textContent).toBe('신청 가능')
  })
})
