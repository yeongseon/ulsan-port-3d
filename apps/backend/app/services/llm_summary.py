import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

LLM_SYSTEM_PROMPT = """당신은 울산항 항만 관제 전문 AI 어시스턴트입니다.
주어진 항만 운영 데이터를 분석하여 한국어로 간결하고 정확한 상황 요약을 제공합니다.
- 현재 기상, 선석 상태, 체선 현황을 종합적으로 판단합니다.
- 위험 요소가 있으면 명확히 경고합니다.
- 불필요한 수식어 없이 핵심만 전달합니다.
- 데이터에 근거한 설명만 합니다."""


async def generate_llm_summary(context: dict) -> str | None:
    llm_api_key = getattr(settings, "llm_api_key", None)
    if not llm_api_key:
        return None

    prompt = _build_prompt(context)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {llm_api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": LLM_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 300,
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception:
        logger.warning("LLM summary generation failed, falling back to rule-based")
        return None


def _build_prompt(context: dict) -> str:
    lines = ["현재 울산항 상태를 요약해주세요. 데이터:"]

    if "wind_speed" in context:
        lines.append(f"- 풍속: {context['wind_speed']}m/s, 풍향: {context.get('wind_dir', 'N/A')}°")
    if "wave_height" in context:
        lines.append(f"- 파고: {context['wave_height']}m")
    if "temperature" in context:
        lines.append(f"- 기온: {context['temperature']}°C")
    if "visibility" in context:
        lines.append(f"- 시정: {context['visibility']}km")
    if "precipitation" in context:
        lines.append(f"- 강수량: {context['precipitation']}mm")
    if "unavailable_berth_count" in context:
        lines.append(f"- 사용불가 선석: {context['unavailable_berth_count']}개")
    if "waiting_count" in context:
        lines.append(f"- 체선 선박: {context['waiting_count']}척")

    lines.append(
        "\n위 데이터를 종합하여 2-3문장으로 현재 상황을 요약하고, 주의사항이 있으면 알려주세요."
    )
    return "\n".join(lines)
