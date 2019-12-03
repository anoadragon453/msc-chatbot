import requests
import json
from errors import BotException
import logging

logger = logging.getLogger(__name__)


class Github(object):
    def __init__(self, repo_slug: str):
        """

        Args:
            repo_slug: The slug (user/repo_name) of the github repository
        """
        # TODO: Add support for custom token
        self.repo_slug = repo_slug

        self.api_base = "https://api.github.com"

    def get_info_for_issue_pr(self, num: int) -> dict:
        """Get the metadata of a github issue/PR

        Args:
            num: The issue/PR number
        Returns:
            dict[str, str]: Metadata about the issue/PR
        Raises:
            FileNotFoundError: The issue/PR was not found
        """
        # Assume it's a PR. Query github's API
        resp = requests.get(self.api_base + f"/repos/{self.repo_slug}/pulls/{num}")
        if resp.status_code == 404 or not resp.content:
            raise FileNotFoundError

        # Load JSON
        body = json.loads(resp.content)
        if resp.status_code == 403:
            # Check if this is a rate limit hit or an invalid token
            if "message" in body:
                logger.error(f"Rate-limit hit on {resp.url}. Consider using your own Github token.")
                raise PermissionError("rate-limit hit")

            logger.error(f"Forbidden on contacting {resp.url}. Check your access token.")
            raise PermissionError("forbidden")

        if resp.status_code != 200:
            raise BotException(f"HTTP error ({resp.status_code})")

        return body
