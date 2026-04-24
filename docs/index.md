# 울산항 3D 관제 시스템

<div style="text-align: center; margin: 2rem 0;">
  <strong>2026 스마트해운물류 × ICT 멘토링 공모전 제출 프로젝트</strong>
</div>

---

## 프로젝트 한눈에 보기

울산항 공공데이터(선박 위치, 선석 현황, 기상, 화물 통계 등)를 **온톨로지 기반 지식 그래프**로 통합하고, **3D WebGL 관제 화면**으로 실시간 시각화하는 풀스택 웹 애플리케이션입니다.

### 핵심 키워드

| | |
|---|---|
| :material-ship-wheel: **3D 실시간 관제** | 울산만 실제 지형 위에 선박·부두를 3D 렌더링 |
| :material-graph-outline: **온톨로지 그래프** | 25개 클래스, 20개 관계로 항만 도메인 모델링 |
| :material-lightning-bolt: **실시간 스트리밍** | WebSocket + Redis Pub/Sub로 초 단위 업데이트 |
| :material-robot: **AI 인사이트** | 규칙 엔진 + LLM 기반 상황 분석·요약 |

### 라이브 데모

> :material-open-in-new: [**울산항 3D 관제 데모 바로가기**](https://yeongseon.github.io/ulsan-port-3d/)
>
> Mock 데이터(선박 15척, 선석 12개)로 전체 UI를 체험할 수 있습니다.

---

## 문서 안내

### 한글 문서

| 문서 | 설명 |
|------|------|
| [**프로젝트 소개서**](project-overview-ko.md) | 동기, 솔루션, 차별점, 기대 효과 — 공모전 심사위원용 |
| [**시스템 아키텍처**](architecture-ko.md) | 기술 스택, 데이터 파이프라인, 온톨로지, 3D 렌더링 상세 |

### 영문 문서 (English)

| Document | Description |
|----------|-------------|
| [Product Requirements](prd.md) | Full PRD with user stories and functional requirements |
| [Ontology Reference](ontology.md) | Entity classes, relationships, and graph semantics |
| [API Specification](api-spec.md) | 24 REST + WebSocket endpoints |

---

## 프로젝트 규모

| 항목 | 수치 |
|------|------|
| 소스 파일 | 115개 |
| 코드 라인 | ~9,500줄 |
| 백엔드 API | 24개 엔드포인트 |
| ETL 수집기 | 8개 |
| 온톨로지 | 25 클래스 · 20 관계 |
| 3D 씬 컴포넌트 | 7개 |

---

## 기술 스택

```
프론트엔드:  React 19 · TypeScript 5 · THREE.js · Zustand · Tailwind · Vite
백엔드:      FastAPI · SQLAlchemy 2.0 · PostgreSQL + PostGIS · Redis
ETL:        Python · httpx · APScheduler
인프라:      Docker Compose · GitHub Actions · GitHub Pages
```

---

## 소스 코드

:material-github: [github.com/yeongseon/ulsan-port-3d](https://github.com/yeongseon/ulsan-port-3d)
