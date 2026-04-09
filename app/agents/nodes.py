from app.core.logger import logger
from app.models.agent import AgentState
from app.models.research import ChannelAnalysis, ResearchResult, ResearchStatus
from app.tools.youtube import get_channel_details, get_channel_videos, search_channels
from app.tools.slack import send_slack_notification
from app.tools.gemini import analyse_channel_with_llm, generate_overall_insights


async def search_node(state: AgentState) -> AgentState:
    logger.info("agent_step", step="search", query=state.request.query)
    state.current_step = "search"

    try:
        channels = await search_channels(
            query=state.request.query,
            max_results=state.request.max_channels,
        )
        state.result.channels = [
            ChannelAnalysis(channel=channel) for channel in channels
        ]
        state.result.status = ResearchStatus.IN_PROGRESS
    except Exception as e:
        state.error = str(e)
        state.result.status = ResearchStatus.FAILED
        logger.error("search_node_failed", error=str(e))

    return state


async def enrich_node(state: AgentState) -> AgentState:
    logger.info("agent_step", step="enrich")
    state.current_step = "enrich"

    if state.result.status == ResearchStatus.FAILED:
        return state

    try:
        enriched = []
        for analysis in state.result.channels:
            channel_id = analysis.channel.channel_id

            # Get full channel details
            details = await get_channel_details(channel_id)
            if details:
                analysis.channel = details

            # Get top videos
            videos = await get_channel_videos(
                channel_id=channel_id,
                max_results=state.request.max_videos_per_channel,
            )
            analysis.top_videos = videos
            enriched.append(analysis)
            logger.info("channel_enriched", channel=analysis.channel.name)

        state.result.channels = enriched
    except Exception as e:
        state.error = str(e)
        state.result.status = ResearchStatus.FAILED
        logger.error("enrich_node_failed", error=str(e))

    return state




async def summarise_node(state: AgentState) -> AgentState:
    logger.info("agent_step", step="summarise")
    state.current_step = "summarise"

    if state.result.status == ResearchStatus.FAILED:
        return state

    try:
        # Per-channel LLM analysis
        for analysis in state.result.channels:
            llm_result = await analyse_channel_with_llm(analysis)

            # Graceful fallback if Gemini fails
            analysis.summary = llm_result.get(
                "summary",
                f"{analysis.channel.name} has "
                f"{analysis.channel.subscriber_count:,} subscribers.",
            )
            analysis.content_themes = llm_result.get("content_themes", [])
            analysis.engagement_rate = llm_result.get("engagement_rate")
            analysis.posting_frequency = llm_result.get("posting_frequency")

        # Overall insights across all channels
        insights = await generate_overall_insights(
            state.request.query,
            state.result.channels,
        )
        state.result.overall_insights = insights.get(
            "overall_insights",
            f"Found {len(state.result.channels)} channels for '{state.request.query}'",
        )
        state.result.recommendations = insights.get("recommendations", [])
        state.result.status = ResearchStatus.COMPLETED

    except Exception as e:
        state.error = str(e)
        state.result.status = ResearchStatus.FAILED
        logger.error("summarise_node_failed", error=str(e))

    return state

async def notify_node(state: AgentState) -> AgentState:
    logger.info("agent_step", step="notify")
    state.current_step = "notify"

    if not state.request.notify_slack:
        return state

    message = (
        f"✅ Research complete for: *{state.request.query}*\n"
        f"{state.result.overall_insights}\n"
        f"Channels: {', '.join(a.channel.name for a in state.result.channels)}"
    )

    await send_slack_notification(message)
    return state