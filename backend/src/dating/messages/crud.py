from dataclasses import asdict

from .schema import Message, MessageIn


MESSAGES_DB: list[Message] = []


class RAMMessageCrud:
    def get_by_id(self, chat_id: int) -> Message | None:
        for chat in MESSAGES_DB:
            if chat.id == chat_id:
                return chat

        return None

    def get_user_messages(self, user_id: int) -> list[Message]:
        user_messages: list[Message] = []
        for message in MESSAGES_DB:
            if message.owner_id == user_id:
                user_messages.append(message)

        return user_messages

    def create(self, message_in: MessageIn, owner_id: int) -> Message:
        message_id = max(MESSAGES_DB, key=lambda x: x.id).id + 1 if MESSAGES_DB else 1
        message = Message(id=message_id, owner_id=owner_id, **asdict(message_in))
        MESSAGES_DB.append(message)
        return message

    def delete(self, message_id: int) -> Message | None:
        message = self.get_by_id(message_id)

        if message:
            MESSAGES_DB.remove(message)

        return message