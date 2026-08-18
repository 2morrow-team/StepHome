import { describe, expect, it } from 'vitest'
import { getSimulatedReadinessScore } from './App'

describe('frontend test setup', () => {
  it('runs with Vitest', () => {
    expect(true).toBe(true)
  })
})

describe('getSimulatedReadinessScore', () => {
  it('reaches 100 when every roadmap action is complete even from a high base score', () => {
    expect(getSimulatedReadinessScore(98, 6, 6)).toBe(100)
  })

  it('uses completion ratio instead of rounding each action down to zero', () => {
    expect(getSimulatedReadinessScore(98, 6, 3)).toBe(99)
  })
})
