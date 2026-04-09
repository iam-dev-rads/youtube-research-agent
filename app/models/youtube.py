from pydantic import BaseModel, HttpUrl


class YouTubeChannel(BaseModel):
    channel_id: str
    name: str
    url: str
    subscriber_count: int | None = None
    video_count: int | None = None
    view_count: int | None = None
    description: str | None = None
    country: str | None = None


class YouTubeVideo(BaseModel):
    video_id: str
    title: str
    url: str
    view_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None
    published_at: str | None = None
    description: str | None = None
    duration: str | None = None
    tags: list[str] = []