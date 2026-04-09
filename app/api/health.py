import asyncio
import google.generativeai as genai
from fastapi import APIRouter
from app.core.config import settings
from app.core.logger import logger
from app.tools.youtube import search_channels

router = APIRouter()


async def _check_youtube() -> dict:
    try:
        results = await search_channels(query="python", max_results=1)
        return {"status": "ok", "reachable": True}
    except Exception as e:
        logger.warning("health_youtube_failed", error=str(e)[:100])
        return {"status": "error", "reachable": False, "detail": str(e)[:100]}


async def _check_gemini() -> dict:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        await asyncio.to_thread(
            model.generate_content,
            "Reply with one word: OK",
        )
        return {"status": "ok", "reachable": True}
    except Exception as e:
        error_str = str(e)
        # Quota exceeded = reachable but limited, not a config failure
        if "429" in error_str or "quota" in error_str.lower():
            logger.warning("health_gemini_quota", error=error_str[:100])
            return {"status": "quota_exceeded", "reachable": True, "detail": "Rate limited"}
        logger.warning("health_gemini_failed", error=error_str[:100])
        return {"status": "error", "reachable": False, "detail": error_str[:100]}


@router.get("/health")
async def health():
    youtube, gemini = await asyncio.gather(
        _check_youtube(),
        _check_gemini(),
    )

    overall = (
        "ok"
        if youtube["status"] == "ok" and gemini["status"] == "ok"
        else "degraded"
    )

    logger.info("health_checked", overall=overall)

    return {
        "status": overall,
        "version": "0.1.0",
        "dependencies": {
            "youtube": youtube,
            "gemini": gemini,
        },
    }