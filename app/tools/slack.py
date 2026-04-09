import httpx
from app.core.config import settings
from app.core.logger import logger


async def send_slack_notification(message: str) -> bool:
    if settings.SLACK_WEBHOOK_URL == "placeholder":
        logger.info("slack_skipped", reason="no webhook configured")
        return False

    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.SLACK_WEBHOOK_URL,
            json={"text": message},
        )

    success = response.status_code == 200
    logger.info("slack_notification_sent", success=success)
    return success