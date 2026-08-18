import { useState } from 'react'
import {
  ActionItem,
  AiScenarioCard,
  Button,
  ContentSection,
  GlobalNav,
  Input,
  MetricCard,
  PageContainer,
  PolicyCard,
  SelectChip,
  StatusBadge,
} from '../components'

export default function UiPreview() {
  const [isPrimaryChipSelected, setIsPrimaryChipSelected] = useState(true)

  return (
    <>
      <GlobalNav />
      <PageContainer className="min-h-screen bg-background-page py-8 text-text-primary sm:py-10">
        <ContentSection className="space-y-8" aria-labelledby="ui-preview-title">
        <header className="space-y-2">
          <p className="type-label text-action-primary">StepHome · 2morrow</p>
          <h1 id="ui-preview-title" className="type-display text-text-primary">
            공통 UI Preview
          </h1>
          <p className="type-body text-text-secondary">디자인 시스템의 공통 컴포넌트 상태를 확인합니다.</p>
        </header>

        <ContentSection aria-labelledby="control-title" className="rounded-card bg-background-surface p-5 shadow-card">
          <h2 id="control-title" className="type-title text-text-primary">
            Controls
          </h2>
          <div className="flex flex-wrap gap-2">
            <Button>Primary Button</Button>
            <Button variant="secondary">Secondary Button</Button>
            <Button disabled>Disabled Button</Button>
          </div>
          <div className="grid gap-4">
            <Input label="Default Input" placeholder="내용을 입력하세요" helperText="입력값을 확인할 수 있습니다." />
            <Input label="Error Input" id="preview-error-input" defaultValue="잘못된 값" errorMessage="입력값을 다시 확인해 주세요." />
            <Input label="Disabled Input" id="preview-disabled-input" defaultValue="수정할 수 없습니다" disabled helperText="현재 비활성 상태입니다." />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <SelectChip
              selected={isPrimaryChipSelected}
              onClick={() => setIsPrimaryChipSelected((selected) => !selected)}
            >
              선택 Chip
            </SelectChip>
            <SelectChip
              selected={!isPrimaryChipSelected}
              onClick={() => setIsPrimaryChipSelected((selected) => !selected)}
            >
              선택 해제 Chip
            </SelectChip>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status="available" />
            <StatusBadge status="conditional" />
            <StatusBadge status="review" />
            <StatusBadge status="unavailable" />
            <StatusBadge status="available" label="맞춤 라벨" />
          </div>
        </ContentSection>

        <ContentSection aria-labelledby="metric-title" className="rounded-card bg-background-surface p-5 shadow-card">
          <h2 id="metric-title" className="type-title text-text-primary">
            MetricCard
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <MetricCard label="독립 준비도" value="72점" supportingText="목표까지 차근차근 준비하고 있어요." />
            <MetricCard label="예상 준비기간" value="8개월" />
          </div>
        </ContentSection>

        <ContentSection aria-labelledby="policy-title" className="rounded-card bg-background-surface p-5 shadow-card">
          <h2 id="policy-title" className="type-title text-text-primary">
            PolicyCard
          </h2>
          <div className="grid gap-4">
            <PolicyCard
              title="청년 월세 한시 특별지원"
              status="available"
              description="월 최대 20만원까지 지원받을 수 있어요."
            />
            <PolicyCard
              title="추가 확인이 필요한 주거 지원 정책"
              status="conditional"
              description="소득 및 거주 요건을 충족하면 신청할 수 있어요."
            />
            <PolicyCard
              title="현재 조건과 맞지 않는 정책"
              status="unavailable"
              description="현재 조건에서는 소득 기준을 충족하지 못했어요."
            />
            <PolicyCard
              title="추가 확인이 필요한 정책 카드"
              status="review"
              description="신청 전 세부 조건을 한 번 더 확인해야 해요."
            />
          </div>
        </ContentSection>

        <ContentSection aria-labelledby="scenario-title" className="rounded-card bg-background-surface p-5 shadow-card">
          <h2 id="scenario-title" className="type-title text-text-primary">
            AiScenarioCard
          </h2>
          <div className="grid gap-4 lg:grid-cols-3">
            <AiScenarioCard
              title="보증금을 낮추면?"
              changedConditionLabel="보증금"
              beforeValue="9,000만원"
              afterValue="7,000만원"
              metrics={[{ label: '독립 시점', value: '2027.06 → 2027.02' }]}
              details={[{ label: '필요 월 저축액', value: '월 130만원' }]}
              aiReason={(
                <>
                  초기 보증금 부담을 낮춰
                  <br />
                  저축 부담 없이 시점을 앞당겨요.
                </>
              )}
              tradeoff="월세가 월 12만원 늘 수 있어요."
            />
            <AiScenarioCard
              title="저축액을 늘리면?"
              changedConditionLabel="월 저축액"
              beforeValue="50만원"
              afterValue="80만원"
              metrics={[{ label: '준비도', value: '72점 → 81점' }]}
              details={[{ label: '정책 변화', value: '추가 확인 필요 → 신청 가능' }]}
              aiReason="월별 준비 속도가 빨라져 목표 시점의 자금 부족분을 줄일 수 있어요."
              tradeoff="생활비 여유가 줄어들 수 있어요."
            />
          </div>
        </ContentSection>

        <ContentSection aria-labelledby="action-title" className="rounded-card bg-background-surface p-5 shadow-card">
          <h2 id="action-title" className="type-title text-text-primary">
            ActionItem
          </h2>
          <div className="grid gap-4">
            <ActionItem
              status="incomplete"
              step={1}
              actionName="월 저축 목표를 정하고 자동이체를 설정하세요"
              description="매월 정해진 금액을 먼저 저축하면 준비 기간을 안정적으로 관리할 수 있습니다."
              reason="자금 부족분을 일정하게 줄일 수 있어요."
            />
            <ActionItem
              status="complete"
              actionName="지원 정책의 신청 자격을 확인했어요"
              description="현재 조건에서 신청 가능한 정책을 우선 확인했습니다."
              reason="정책 활용 가능성을 먼저 확정하면 계획 변경 폭이 줄어듭니다."
            />
          </div>
        </ContentSection>
        </ContentSection>
      </PageContainer>
    </>
  )
}
