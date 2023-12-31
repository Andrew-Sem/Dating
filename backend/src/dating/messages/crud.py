from dataclasses import asdict
from typing import Iterable

from .exceptions import MessageNotFound
from .schema import Message, MessageIn, MessageHide


MESSAGES_DB: list[Message] = []
MESSAGES_HIDES_DB: list[MessageHide] = []


class RAMMessageCrud:
    def get_by_id(self, message_id: int) -> Message | None:
        for message in MESSAGES_DB:
            if message.id == message_id:
                return message

        return None

    def get_messages_by_ids(self, messages_ids: Iterable[int]) -> list[Message]:
        matched_messages: list[Message] = []
        for message_id in messages_ids:
            message = self.get_by_id(message_id)
            if message:
                matched_messages.append(message)
            else:
                raise MessageNotFound

        return matched_messages

    def get_user_messages(self, user_id: int, offset: int, limit: int) -> list[Message]:
        user_messages: list[Message] = []
        for message in MESSAGES_DB:
            if message.owner_id == user_id:
                user_messages.append(message)

        return user_messages[offset:offset + limit]

    def get_user_messages_hides_for_chat(self, user_id: int, chat_id: int) -> list[MessageHide]:
        hides: list[MessageHide] = []
        for hide in MESSAGES_HIDES_DB:
            if hide.user_id == user_id and hide.chat_id == chat_id:
                hides.append(hide)

        return hides

    def create(self, message_in: MessageIn, owner_id: int) -> Message:
        message_id = max(MESSAGES_DB, key=lambda x: x.id).id + 1 if MESSAGES_DB else 1
        message = Message(id=message_id, owner_id=owner_id, **asdict(message_in))
        MESSAGES_DB.append(message)
        return message

    def delete(self, message_id: int) -> Message:
        message = self.get_by_id(message_id)

        if not message:
            raise MessageNotFound

        MESSAGES_DB.remove(message)

        return message

    def hide_message(self, message_id: int, chat_id: int, user_id: int) -> MessageHide:
        hide = MessageHide(message_id, chat_id, user_id)
        MESSAGES_HIDES_DB.append(hide)
        return hide
