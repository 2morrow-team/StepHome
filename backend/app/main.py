# FastAPI 애플리케이션 진입점

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from app.routers.plan import router as plan_router
from app.routers.replan import router as replan_router
from app.routers.scenario import router as scenario_router
from app.ai.planner import AIPlannerError
from app.schemas.schemas import HealthResponse


app = FastAPI(
    title="StepHome API",
    description="StepHome Backend API",
    version="1.0.0",
)


# Frontend 개발 서버와의 로컬 통신 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Router 등록
app.include_router(plan_router)
app.include_router(replan_router)
app.include_router(scenario_router)


@app.exception_handler(AIPlannerError)
async def ai_planner_error_handler(
    _,
    _exc: AIPlannerError,
) -> JSONResponse:
    """AI와 안전 fallback이 모두 실패한 경우 공통 오류 형식으로 응답한다."""

    return JSONResponse(
        status_code=503,
        content={
            "error": {
                "code": "AI_TEMPORARILY_UNAVAILABLE",
                "message": "맞춤 계획 생성이 지연되고 있습니다. 잠시 후 다시 시도해주세요.",
            }
        },
    )


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> dict[str, str]:
    """Backend 서버 상태 확인."""
    return {"status": "OK"}


@app.get("/test", response_class=HTMLResponse)
def test_ui() -> str:
    return """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StepHome API 테스트</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f5f7; color: #1d1d1f; }
  .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
  h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
  .subtitle { color: #6e6e73; margin-bottom: 32px; }
  .card { background: white; border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
  .card h2 { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #1d1d1f; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  label { display: block; font-size: 12px; color: #6e6e73; margin-bottom: 4px; }
  input, select { width: 100%; padding: 8px 12px; border: 1px solid #d2d2d7; border-radius: 8px; font-size: 14px; }
  input:focus, select:focus { outline: none; border-color: #0071e3; }
  .btn { width: 100%; padding: 14px; background: #0071e3; color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 8px; }
  .btn:hover { background: #0077ed; }
  .btn:disabled { background: #a1a1a6; cursor: not-allowed; }
  .spinner { display: none; text-align: center; padding: 20px; color: #6e6e73; }
  .summary-box { background: #f5f5f7; border-radius: 12px; padding: 16px; margin-bottom: 20px; font-size: 14px; line-height: 1.6; }
  .phase-header { display: flex; align-items: center; gap: 10px; margin: 20px 0 12px; }
  .phase-badge { background: #0071e3; color: white; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px; }
  .phase-date { font-size: 13px; color: #6e6e73; }
  .action-card { border: 1px solid #e8e8ed; border-radius: 12px; padding: 16px; margin-bottom: 10px; }
  .action-top { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
  .type-badge { font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 6px; }
  .SAVING { background: #e8f4fd; color: #0071e3; }
  .POLICY { background: #e8fdf0; color: #1d7a40; }
  .HOUSING { background: #fdf4e8; color: #b45309; }
  .CONTRACT { background: #fde8e8; color: #b42020; }
  .action-title { font-weight: 600; font-size: 15px; }
  .action-due { font-size: 12px; color: #6e6e73; margin-left: auto; }
  .action-desc { font-size: 13px; color: #3a3a3c; line-height: 1.6; margin-bottom: 8px; }
  .action-reason { font-size: 12px; color: #6e6e73; background: #f5f5f7; padding: 8px 10px; border-radius: 8px; line-height: 1.5; }
  .action-reason::before { content: "💡 추천 이유: "; font-weight: 600; }
  .error { background: #fde8e8; color: #b42020; padding: 16px; border-radius: 12px; font-size: 14px; }
  .tabs { display: flex; gap: 8px; margin-bottom: 20px; }
  .tab { padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; border: 1px solid #d2d2d7; background: white; }
  .tab.active { background: #0071e3; color: white; border-color: #0071e3; }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
</style>
</head>
<body>
<div class="container">
  <h1>StepHome API 테스트</h1>
  <p class="subtitle">AI 액션 플랜 생성 결과를 직접 확인해보세요</p>

  <div class="tabs">
    <div class="tab active" onclick="switchTab('plan')">액션 플랜</div>
    <div class="tab" onclick="switchTab('replan')">리플랜</div>
  </div>

  <!-- 액션 플랜 탭 -->
  <div id="tab-plan" class="tab-content active">
    <div class="card">
      <h2>👤 사용자 정보</h2>
      <div class="grid">
        <div><label>나이</label><input id="age" type="number" value="25"></div>
        <div><label>고용형태</label>
          <select id="employment_status">
            <option value="EMPLOYED">재직중</option>
            <option value="JOB_SEEKER">구직중</option>
            <option value="STUDENT">학생</option>
          </select>
        </div>
        <div><label>현재 지역</label>
          <select id="current_region">
            <option value="SEOUL">서울</option>
            <option value="GYEONGGI">경기</option>
            <option value="BUSAN">부산</option>
          </select>
        </div>
        <div><label>혼인 상태</label>
          <select id="marital_status">
            <option value="UNMARRIED">미혼</option>
            <option value="MARRIED">기혼</option>
          </select>
        </div>
        <div><label>월 소득 (원)</label><input id="income" type="number" value="2500000"></div>
        <div><label>총 자산 (원)</label><input id="assets" type="number" value="30000000"></div>
        <div><label>월 저축액 (원)</label><input id="savings" type="number" value="500000"></div>
        <div><label>주거 형태</label>
          <select id="housing_status">
            <option value="NO_HOME">무주택</option>
            <option value="HAS_HOME">유주택</option>
          </select>
        </div>
        <div><label>가구 월소득 (원)</label><input id="household_income" type="number" value="2500000"></div>
        <div><label>가구원 수</label><input id="household_size" type="number" value="1"></div>
      </div>
    </div>
    <div class="card">
      <h2>🏠 독립 목표</h2>
      <div class="grid">
        <div><label>입주 예정일</label><input id="move_in" type="date" value="2026-11-19"></div>
        <div><label>희망 지역</label>
          <select id="desired_region">
            <option value="SEOUL">서울</option>
            <option value="GYEONGGI">경기</option>
            <option value="BUSAN">부산</option>
          </select>
        </div>
        <div><label>희망 보증금 (원)</label><input id="deposit" type="number" value="90000000"></div>
        <div><label>희망 월세 (원)</label><input id="monthly_rent" type="number" value="500000"></div>
        <div><label>주거 유형</label>
          <select id="housing_type">
            <option value="MONTHLY_RENT">월세</option>
            <option value="JEONSE">전세</option>
          </select>
        </div>
      </div>
    </div>
    <button class="btn" onclick="createPlan()">🤖 AI 액션 플랜 생성</button>
    <div class="spinner" id="plan-spinner">AI가 플랜을 생성하고 있습니다...</div>
    <div id="plan-result"></div>
  </div>

  <!-- 리플랜 탭 -->
  <div id="tab-replan" class="tab-content">
    <div class="card">
      <h2>🔄 리플랜 (이전 플랜 기반)</h2>
      <div class="grid">
        <div><label>user_id</label><input id="r_user_id" type="number" value="1"></div>
        <div><label>target_id</label><input id="r_target_id" type="number" value="1"></div>
        <div><label>previous_diagnosis_id</label><input id="r_diag_id" type="number" value="1"></div>
        <div><label>previous_plan_id</label><input id="r_plan_id" type="number" value="1"></div>
      </div>
      <div style="margin-top:16px">
        <h2 style="margin-bottom:12px">변경할 조건 (바꾸고 싶은 것만 입력)</h2>
        <div class="grid">
          <div><label>희망 보증금 (원)</label><input id="r_deposit" type="number" placeholder="비워두면 변경 안함"></div>
          <div><label>희망 월세 (원)</label><input id="r_rent" type="number" placeholder="비워두면 변경 안함"></div>
          <div><label>입주 예정일</label><input id="r_move_in" type="date" placeholder="비워두면 변경 안함"></div>
          <div><label>월 저축액 (원)</label><input id="r_savings" type="number" placeholder="비워두면 변경 안함"></div>
        </div>
      </div>
    </div>
    <button class="btn" onclick="replan()">🔄 리플랜 실행</button>
    <div class="spinner" id="replan-spinner">AI가 새 플랜을 생성하고 있습니다...</div>
    <div id="replan-result"></div>
  </div>
</div>

<script>
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('tab-' + name).classList.add('active');
}

function renderPlan(data) {
  const plan = data.action_plan || data.current?.action_plan;
  if (!plan) return '<div class="error">액션 플랜 데이터가 없습니다.</div>';

  const changedFields = data.changed_fields;
  let html = '';

  if (changedFields) {
    html += '<div class="card" style="margin-top:20px"><h2>✏️ 변경된 조건</h2>';
    for (const [field, val] of Object.entries(changedFields)) {
      const labels = { desired_deposit:'보증금', desired_monthly_rent:'월세', planned_move_in_date:'입주예정일', monthly_savings:'월 저축액' };
      html += `<div style="font-size:14px;padding:8px 0;border-bottom:1px solid #f0f0f0">
        <span style="color:#6e6e73">${labels[field] || field}</span>
        <strong style="margin-left:8px">${val.before?.toLocaleString?.() ?? val.before}</strong>
        <span style="margin:0 8px">→</span>
        <strong style="color:#0071e3">${val.after?.toLocaleString?.() ?? val.after}</strong>
      </div>`;
    }
    html += '</div>';
  }

  html += `<div class="card" style="margin-top:20px">
    <h2>📋 요약</h2>
    <div class="summary-box">${plan.summary}</div>`;

  const byPhase = {};
  for (const a of plan.actions) {
    const p = a.phase || 0;
    if (!byPhase[p]) byPhase[p] = [];
    byPhase[p].push(a);
  }

  const phaseLabels = { 1:'즉시 실행', 2:'단기 준비', 3:'중기 준비', 4:'입주 직전' };
  for (const [phase, actions] of Object.entries(byPhase)) {
    const dueDate = actions[0].due_date || '';
    html += `<div class="phase-header">
      <span class="phase-badge">Phase ${phase} · ${phaseLabels[phase] || ''}</span>
      <span class="phase-date">~ ${dueDate}</span>
    </div>`;
    for (const a of actions) {
      html += `<div class="action-card">
        <div class="action-top">
          <span class="type-badge ${a.action_type}">${a.action_type}</span>
          <span class="action-title">${a.title}</span>
          <span class="action-due">마감 ${a.due_date || '-'}</span>
        </div>
        <div class="action-desc">${a.description}</div>
        <div class="action-reason">${a.reason}</div>
      </div>`;
    }
  }
  html += '</div>';
  return html;
}

async function createPlan() {
  const btn = event.target;
  btn.disabled = true;
  document.getElementById('plan-spinner').style.display = 'block';
  document.getElementById('plan-result').innerHTML = '';

  const body = {
    user: {
      age: +document.getElementById('age').value,
      employment_status: document.getElementById('employment_status').value,
      current_region: document.getElementById('current_region').value,
      marital_status: document.getElementById('marital_status').value,
      personal_monthly_income: +document.getElementById('income').value,
      total_assets: +document.getElementById('assets').value,
      monthly_savings: +document.getElementById('savings').value,
      housing_status: document.getElementById('housing_status').value,
      youth_household_monthly_income: +document.getElementById('household_income').value,
      youth_household_size: +document.getElementById('household_size').value,
    },
    target: {
      planned_move_in_date: document.getElementById('move_in').value,
      desired_region: document.getElementById('desired_region').value,
      desired_deposit: +document.getElementById('deposit').value,
      desired_monthly_rent: +document.getElementById('monthly_rent').value,
      desired_housing_type: document.getElementById('housing_type').value,
    }
  };

  try {
    const res = await fetch('/api/v1/plan', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
    const data = await res.json();
    if (!res.ok) { document.getElementById('plan-result').innerHTML = `<div class="error">${JSON.stringify(data, null, 2)}</div>`; return; }
    document.getElementById('plan-result').innerHTML = renderPlan(data);
    document.getElementById('r_user_id').value = data.user_id;
    document.getElementById('r_target_id').value = data.target_id;
    document.getElementById('r_diag_id').value = data.diagnosis_id;
    document.getElementById('r_plan_id').value = data.plan_id;
  } catch(e) {
    document.getElementById('plan-result').innerHTML = `<div class="error">${e.message}</div>`;
  } finally {
    btn.disabled = false;
    document.getElementById('plan-spinner').style.display = 'none';
  }
}

async function replan() {
  const btn = event.target;
  btn.disabled = true;
  document.getElementById('replan-spinner').style.display = 'block';
  document.getElementById('replan-result').innerHTML = '';

  const changes = {};
  const d = document.getElementById('r_deposit').value;
  const r = document.getElementById('r_rent').value;
  const m = document.getElementById('r_move_in').value;
  const s = document.getElementById('r_savings').value;
  if (d) changes.desired_deposit = +d;
  if (r) changes.desired_monthly_rent = +r;
  if (m) changes.planned_move_in_date = m;
  if (s) changes.monthly_savings = +s;

  const body = {
    user_id: +document.getElementById('r_user_id').value,
    target_id: +document.getElementById('r_target_id').value,
    previous_diagnosis_id: +document.getElementById('r_diag_id').value,
    previous_plan_id: +document.getElementById('r_plan_id').value,
    changes,
  };

  try {
    const res = await fetch('/api/v1/replan', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
    const data = await res.json();
    if (!res.ok) { document.getElementById('replan-result').innerHTML = `<div class="error">${JSON.stringify(data, null, 2)}</div>`; return; }
    document.getElementById('replan-result').innerHTML = renderPlan(data.current) + renderChangedSummary(data);
  } catch(e) {
    document.getElementById('replan-result').innerHTML = `<div class="error">${e.message}</div>`;
  } finally {
    btn.disabled = false;
    document.getElementById('replan-spinner').style.display = 'none';
  }
}

function renderChangedSummary(data) {
  if (!data.changed_fields) return '';
  let html = '<div class="card"><h2>✏️ 변경된 조건</h2>';
  const labels = { desired_deposit:'보증금', desired_monthly_rent:'월세', planned_move_in_date:'입주예정일', monthly_savings:'월 저축액' };
  for (const [field, val] of Object.entries(data.changed_fields)) {
    html += `<div style="font-size:14px;padding:8px 0;border-bottom:1px solid #f0f0f0">
      <span style="color:#6e6e73">${labels[field] || field}</span>
      <strong style="margin-left:8px">${val.before?.toLocaleString?.() ?? val.before}</strong>
      <span style="margin:0 8px">→</span>
      <strong style="color:#0071e3">${val.after?.toLocaleString?.() ?? val.after}</strong>
    </div>`;
  }
  return html + '</div>';
}
</script>
</body>
</html>"""


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Pydantic / FastAPI Request Validation 오류를
    Frontend 공통 Error Contract로 변환한다.

    FastAPI 내부 경로의 `body` prefix는 제거한다.

    예:
    body.user.age
    -> user.age
    """

    details = []

    for error in exc.errors():
        location = list(error.get("loc", []))

        # FastAPI 내부 prefix 제거
        if location and location[0] == "body":
            location = location[1:]

        field = ".".join(
            str(item)
            for item in location
        )

        details.append(
            {
                "field": field,
                "reason": error.get(
                    "msg",
                    "입력값이 올바르지 않습니다.",
                ),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "INVALID_INPUT",
                "message": "입력값을 확인해주세요.",
                "details": details,
            }
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(
    _,
    exc: ValueError,
) -> JSONResponse:
    """
    서비스/Diagnosis 등에서 발생한
    사용자 입력 관련 ValueError 처리.
    """

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "INVALID_INPUT",
                "message": str(exc),
            }
        },
    )


@app.exception_handler(LookupError)
async def lookup_error_handler(
    _,
    exc: LookupError,
) -> JSONResponse:
    """기존 Plan / User / Target 등을 찾지 못한 경우."""

    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "PLAN_NOT_FOUND",
                "message": str(exc),
            }
        },
    )
