import re
import logging
from errors import BotException
from chat_functions import send_text_to_room
from github import Github

logger = logging.getLogger(__name__)


class Message(object):

    def __init__(self, client, store, config, message_content, room, event):
        """Initialize a new Message

        Args:
            client:
            store:
            config:
            message_content:
            room:
            event:
        """
        self.client = client
        self.store = store
        self.config = config
        self.message_content = message_content
        self.room = room
        self.event = event

        # MSC#### regex
        self.msc_number_regex = re.compile(r"(^| |\()MSC(\d+)(\)| |$)", flags=re.IGNORECASE)

        # Initialize Github object
        self.github = Github(self.config.repo_slug)

    async def process(self):
        """Process and possibly respond to the message"""
        # Link all mentioned MSCs
        await self._link_mscs()

    async def _link_mscs(self):
        """Post a link to any mentioned MSCs"""
        links = []
        for match in self.msc_number_regex.finditer(self.message_content):
            # Extract issue number from MSC ID
            logger.debug("Got match: %s", match.group(2))
            match_text = match.group(2)
            msc_num = int(match_text[3:])

            try:
                metadata = self.github.get_info_for_issue_pr(msc_num)
            except FileNotFoundError:
                # Unknown MSC, no match
                return
            except PermissionError:
                # Forbidden from accessing the API
                return
            except BotException as e:
                await send_text_to_room(self.client, self.room.room_id, f"Error: {e.msg}")
                return

            keys = ['title', 'user', 'html_url']
            for key in keys:
                if key not in metadata:
                    logger.error("MSC metadata does not contain required key '%s': %s", key, metadata)
                    await send_text_to_room(self.client, self.room, "Error (missing metadata)")
                    return

            link = (
                f"[{metadata['title']}]({metadata['html_url']})"
                f" by [{metadata['user']['login']}]({metadata['user']['html_url']})"
            )
            if link not in links:
                links.append(link)

        if links:
            response_content = "\n\n".join(links)
            await send_text_to_room(self.client, self.room.room_id, response_content,
                                    notice=True)

