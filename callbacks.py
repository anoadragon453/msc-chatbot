from chat_functions import (
    send_text_to_room,
)
from bot_commands import Command
from message_responder import Message
from nio import (
    JoinError,
)

import re
import logging
logger = logging.getLogger(__name__)


class Callbacks(object):

    def __init__(self, client, store, config):
        """
        Args:
            client (nio.AsyncClient): nio client used to interact with matrix

            store (Storage): Bot storage

            config (Config): Bot configuration parameters
        """
        self.client = client
        self.store = store
        self.config = config
        self.command_prefix = config.command_prefix

        self.reply_regex = re.compile("<mx-reply>.*</mx-reply>")

    async def message(self, room, event):
        """Callback for when a message event is received

        Args:
            room (nio.rooms.MatrixRoom): The room the event came from

            event (nio.events.room_events.RoomMessageText): The event defining the message
        """
        if event.body.startswith(" * "):
            # This is likely an edit, ignore
            return

        # Extract the message text
        msg = event.formatted_body or event.body

        # Discard reply blocks
        msg = self.reply_regex.sub('', msg)

        # Ignore messages from ourselves
        if event.sender == self.client.user:
            return

        logger.debug(
            f"Bot message received for room {room.display_name} | "
            f"{room.user_name(event.sender)}: {msg}"
        )

        # Is this a command?
        has_command_prefix = msg.startswith(self.command_prefix)
        if has_command_prefix:
            # Remove the command prefix
            msg = msg[len(self.command_prefix):]

            command = Command(self.client, self.store, msg, room, event)
            await command.process()
            return

        # General message listener
        message = Message(self.client, self.store, self.config, msg, room, event)
        await message.process()

    async def invite(self, room, event):
        """Callback for when an invite is received. Join the room specified in the invite"""
        logger.debug(f"Got invite to {room.room_id} from {event.sender}.")

        # Attempt to join 3 times before giving up
        for attempt in range(3):
            result = await self.client.join(room.room_id)
            if type(result) == JoinError:
                logger.error(
                    f"Error joining room {room.room_id} (attempt %d): %s",
                    attempt, result.message,
                )
            else:
                logger.info(f"Joined {room.room_id}")
                break

