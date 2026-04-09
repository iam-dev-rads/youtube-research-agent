from enum import Enum

from pydantic import BaseModel

from app.models.youtube import YouTubeChannel, YouTubeVideo


class ResearchStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    query: str
    max_channels: int = 5
    max_videos_per_channel: int = 10
    notify_slack: bool = True


class ChannelAnalysis(BaseModel):
    channel: YouTubeChannel
    top_videos: list[YouTubeVideo] = []
    content_themes: list[str] = []
    posting_frequency: str | None = None
    engagement_rate: float | None = None
    summary: str | None = None


class ResearchResult(BaseModel):
    query: str
    status: ResearchStatus = ResearchStatus.PENDING
    channels: list[ChannelAnalysis] = []
    overall_insights: str | None = None
    recommendations: list[str] = []
    error: str | None = None