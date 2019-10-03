import re
import logging
from chat_functions import send_text_to_room

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
        self.msc_number_regex = re.compile(r"MSC\d+", flags=re.IGNORECASE)

    async def process(self):
        """Process and possibly respond to the message"""
        # Link all mentioned MSCs
        await self._link_mscs()

    async def _link_mscs(self):
        """Post a link to any mentioned MSCs"""
        links = []
        for match in self.msc_number_regex.finditer(self.message_content):
            # Extract issue number from MSC ID
            logger.debug("Got match: %s", match.group())
            match_text = match.group()
            msc_num = match_text[3:]

            links.append(f"{self.config.project_url}/issues/{msc_num}")

        if links:
            response_content = "\n\n".join(links)
            await send_text_to_room(self.client, self.room.room_id, response_content,
                                    markdown_convert=False)

