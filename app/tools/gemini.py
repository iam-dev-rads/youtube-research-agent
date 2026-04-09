import asyncio
import json
import google.generativeai as genai
from app.core.config import settings
from app.core.logger import logger

genai.configure(api_key=settings.GEMINI_API_KEY)

_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-lite",
    generation_config={"response_mime_type": "application/json"},
)


def _build_channel_prompt(analysis) -> str:
    channel = analysis.channel
    video_lines = "\n".join([
        f"- {v.title} | Views: {v.view_count} | Likes: {v.like_count}"
        for v in analysis.top_videos
    ])

    return f"""Analyse this YouTube channel. Return JSON with exactly these fields:
{{
  "summary": "2-3 sentence description of what this channel covers",
  "content_themes": ["tag1", "tag2", "tag3"],
  "engagement_rate": 0.00,
  "posting_frequency": "Weekly"
}}

Channel:
Name: {channel.name}
Subscribers: {channel.subscriber_count:,}
Total Videos: {channel.video_count}
Total Views: {channel.view_count:,}
Country: {channel.country or "Unknown"}
Description: {(channel.description or "")[:300]}

Recent Videos:
{video_lines}

Rules:
- engagement_rate = average (likes / views * 100) across videos, rounded to 2dp
- posting_frequency: one of Daily / Several times a week / Weekly / Monthly
- Return ONLY valid JSON. No markdown. No explanation."""


def _build_insights_prompt(query: str, channels) -> str:
    summaries = "\n".join([
        f"- {a.channel.name} ({a.channel.subscriber_count:,} subs): "
        f"{a.summary} Themes: {', '.join(a.content_themes)}"
        for a in channels
    ])

    return f"""Given these YouTube channels found for the query "{query}", return JSON with:
{{
  "overall_insights": "2-3 sentence summary of the content landscape",
  "recommendations": [
    "actionable recommendation 1",
    "actionable recommendation 2",
    "actionable recommendation 3"
  ]
}}

Channels:
{summaries}

Return ONLY valid JSON. No markdown. No explanation."""


async def analyse_channel_with_llm(analysis) -> dict:
    prompt = _build_channel_prompt(analysis)
    try:
        response = await asyncio.to_thread(_model.generate_content, prompt)
        result = json.loads(response.text)
        logger.info(
            "gemini_channel_analysed",
            channel=analysis.channel.name,
            themes=result.get("content_themes", []),
        )
        return result
    except Exception as e:
        logger.error(
            "gemini_channel_failed",
            channel=analysis.channel.name,
            error=str(e),
        )
        return {}


async def generate_overall_insights(query: str, channels) -> dict:
    prompt = _build_insights_prompt(query, channels)
    try:
        response = await asyncio.to_thread(_model.generate_content, prompt)
        result = json.loads(response.text)
        logger.info("gemini_insights_generated", query=query)
        return result
    except Exception as e:
        logger.error("gemini_insights_failed", query=query, error=str(e))
        return {}