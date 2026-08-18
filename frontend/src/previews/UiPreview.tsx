import { useState } from 'react'
import {
  ActionItem,
  Button,
  ContentSection,
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
              description="현재 조건에서 신청 가능한 정책입니다."
              benefitLabel="예상 지원"
              benefitValue="월 20만원"
              supportingText="신청 전 소득 및 거주 요건을 확인하세요."
            />
            <PolicyCard
              title="추가 확인이 필요한 주거 지원 정책"
              status="review"
              statusLabel="확인 필요"
              description="일부 조건을 확인한 뒤 이용 가능 여부를 판단할 수 있습니다."
              supportingText="신청 전 추가 조건을 확인하세요."
            />
            <PolicyCard
              title="현재 조건과 맞지 않는 정책"
              status="unavailable"
              description="현재 조건에서는 이용할 수 없습니다."
              benefitLabel="예상 지원"
              benefitValue="조건 미충족"
            />
            <PolicyCard
              title="선택 정보가 없는 정책 카드"
              status="review"
              description="선택적인 혜택과 보조 설명 없이 기본 정보만 보여줍니다."
            />
          </div>
        </ContentSection>

        <ContentSection aria-labelledby="action-title" className="rounded-card bg-background-surface p-5 shadow-card">
          <h2 id="action-title" className="type-title text-text-primary">
            ActionItem
          </h2>
          <div className="grid gap-4">
            <ActionItem
              status="pending"
              step={1}
              title="월 저축 목표를 정하고 자동이체를 설정하세요"
              detail="매월 정해진 금액을 먼저 저축하면 준비 기간을 안정적으로 관리할 수 있습니다."
            />
            <ActionItem status="complete" step={2} title="지원 정책의 신청 자격을 확인했어요" />
          </div>
        </ContentSection>
      </ContentSection>
    </PageContainer>
  )
}
