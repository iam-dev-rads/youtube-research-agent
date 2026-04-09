from fastapi import APIRouter, HTTPException
from app.agents import agent
from app.core.logger import logger
from app.models.research import ResearchRequest, ResearchResult, ResearchStatus
from app.models.agent import AgentState

router = APIRouter()


@router.post("/research", response_model=ResearchResult)
async def run_research(request: ResearchRequest):
    logger.info("research_request_received", query=request.query)

    # Build initial state
    initial_state = AgentState(
        request=request,
        result=ResearchResult(query=request.query),
    )

    try:
        final_state = await agent.ainvoke(initial_state)
    except Exception as e:
        logger.error("research_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

    result = final_state["result"]

    if result.status == ResearchStatus.FAILED:
        raise HTTPException(status_code=500, detail=result.error)

    logger.info(
        "research_completed",
        query=request.query,
        channels_found=len(result.channels),
    )

    return result