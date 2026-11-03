import json
import logging

logger = logging.getLogger(__name__)


def attach_api_response(url: str, data: dict) -> None:
    """Log and attach an API response to both pytest-html (via logging) and Allure."""
    logger.info("API URL: %s", url)
    logger.info("API Response:\n%s", json.dumps(data, indent=2))

    try:
        import allure  # type: ignore[import-untyped]

        allure.attach(
            json.dumps(data, indent=2),
            name=f"Response: {url}",
            attachment_type=allure.attachment_type.JSON,
        )
    except ImportError:
        pass
