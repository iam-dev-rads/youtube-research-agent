import httpx
from app.core.config import settings
from app.core.logger import logger
from app.models.youtube import YouTubeChannel, YouTubeVideo


BASE_URL = "https://www.googleapis.com/youtube/v3"


async def search_channels(query: str, max_results: int = 5) -> list[YouTubeChannel]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/search",
            params={
                "part": "snippet",
                "type": "channel",
                "q": query,
                "maxResults": max_results,
                "key": settings.YOUTUBE_API_KEY,
            },
        )
        response.raise_for_status()
        data = response.json()

    channels = []
    for item in data.get("items", []):
        channel = YouTubeChannel(
            channel_id=item["id"]["channelId"],
            name=item["snippet"]["title"],
            url=f"https://www.youtube.com/channel/{item['id']['channelId']}",
            description=item["snippet"].get("description"),
        )
        channels.append(channel)
        logger.info("channel_found", name=channel.name)

    return channels


async def get_channel_details(channel_id: str) -> YouTubeChannel | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/channels",
            params={
                "part": "snippet,statistics",
                "id": channel_id,
                "key": settings.YOUTUBE_API_KEY,
            },
        )
        response.raise_for_status()
        data = response.json()

    items = data.get("items", [])
    if not items:
        return None

    item = items[0]
    stats = item.get("statistics", {})

    return YouTubeChannel(
        channel_id=channel_id,
        name=item["snippet"]["title"],
        url=f"https://www.youtube.com/channel/{channel_id}",
        description=item["snippet"].get("description"),
        subscriber_count=int(stats.get("subscriberCount", 0)),
        video_count=int(stats.get("videoCount", 0)),
        view_count=int(stats.get("viewCount", 0)),
        country=item["snippet"].get("country"),
    )

async def get_channel_videos(
    channel_id: str, max_results: int = 10
) -> list[YouTubeVideo]:
    async with httpx.AsyncClient() as client:

        # Step 1 — get uploads playlist id
        channel_response = await client.get(
            f"{BASE_URL}/channels",
            params={
                "part": "contentDetails",
                "id": channel_id,
                "key": settings.YOUTUBE_API_KEY,
            },
        )
        channel_response.raise_for_status()
        channel_data = channel_response.json()

        playlist_id = (
            channel_data["items"][0]
            ["contentDetails"]
            ["relatedPlaylists"]
            ["uploads"]
        )

        # Step 2 — get video IDs from playlist
        videos_response = await client.get(
            f"{BASE_URL}/playlistItems",
            params={
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": max_results,
                "key": settings.YOUTUBE_API_KEY,
            },
        )
        videos_response.raise_for_status()
        videos_data = videos_response.json()

        # ── collect video IDs from playlist ──────────────────────────────
        video_ids = [
            item["snippet"]["resourceId"]["videoId"]
            for item in videos_data.get("items", [])
        ]

        if not video_ids:
            return []

        # Step 3 — fetch statistics + duration for all videos in one call
        stats_response = await client.get(
            f"{BASE_URL}/videos",
            params={
                "part": "statistics,contentDetails",
                "id": ",".join(video_ids),          # batch — 1 API call
                "key": settings.YOUTUBE_API_KEY,
            },
        )
        stats_response.raise_for_status()
        stats_data = stats_response.json()

    # ── build a lookup dict keyed by video_id ─────────────────────────────
    stats_lookup: dict[str, dict] = {
        item["id"]: item
        for item in stats_data.get("items", [])
    }

    # ── build YouTubeVideo objects with full data ─────────────────────────
    videos = []
    for item in videos_data.get("items", []):
        snippet  = item["snippet"]
        video_id = snippet["resourceId"]["videoId"]

        enriched    = stats_lookup.get(video_id, {})
        stats       = enriched.get("statistics", {})
        content     = enriched.get("contentDetails", {})

        video = YouTubeVideo(
            video_id=video_id,
            title=snippet["title"],
            url=f"https://www.youtube.com/watch?v={video_id}",
            published_at=snippet.get("publishedAt"),
            description=snippet.get("description"),
            view_count=int(stats.get("viewCount", 0)),
            like_count=int(stats.get("likeCount", 0)),
            comment_count=int(stats.get("commentCount", 0)),
            duration=content.get("duration"),          # ISO 8601 e.g. PT12M5S
        )
        videos.append(video)

    return videos