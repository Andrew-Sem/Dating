from typing import Iterable, Container

from .exceptions import ChatNotFound, ChatUnavailableForUser
from .schema import Chat
from ..messages.crud import RAMMessageCrud
from ..messages.exceptions import MessageNotFound
from ..messages.schema import Message

CHATS_DB: list[Chat] = []


class RAMChatCrud:
    def __init__(self, message_crud: RAMMessageCrud) -> None:  # Shit code bcs of bad design
        self.message_crud = message_crud

    def get_by_id(self, chat_id: int) -> Chat | None:
        for chat in CHATS_DB:
            if chat.id == chat_id:
                return chat

        return None

    def get_user_chats(self, user_id: int, offset: int, limit: int) -> list[Chat]:
        chats: list[Chat] = []
        for chat in CHATS_DB:
            if user_id in chat.users_ids:
                chats.append(chat)
        return chats[offset:limit + offset]

    def get_all_user_chats(self, user_id: int) -> list[Chat]:
        chats: list[Chat] = []
        for chat in CHATS_DB:
            if user_id in chat.users_ids:
                chats.append(chat)
        return chats

    def get_chat_messages_ids(self, chat_id: int, offset: int, limit: int, except_: Container[int]) -> list[int]:
        chat = self.get_by_id(chat_id)

        if not chat:
            raise ChatNotFound

        messages_ids: list[int] = []
        for message_id in chat.messages_story[offset:]:
            if len(messages_ids):
                break

            if message_id not in except_:
                messages_ids.append(message_id)

        return messages_ids

    def create_chat(self, users_ids: Iterable[int]) -> Chat:
        chat_id = max(CHATS_DB, key=lambda x: x.id).id + 1 if CHATS_DB else 1
        chat = Chat(id=chat_id, users_ids=list(users_ids))
        CHATS_DB.append(chat)
        return chat

    def add_message_to_chat(self, chat_id: int, message_id: int) -> Message:
        chat = self.get_by_id(chat_id)

        if not chat:
            raise ChatNotFound

        chat.messages_story.insert(0, message_id)

        message = self.message_crud.get_by_id(message_id)

        if not message:
            raise MessageNotFound

        return message

    def delete_message_from_chat(self, chat_id: int, message_id: int) -> Message:
        chat = self.get_by_id(chat_id)

        if not chat:
            raise ChatNotFound

        if message_id not in chat.messages_story:
            raise MessageNotFound

        chat.messages_story.remove(message_id)

        message = self.message_crud.get_by_id(message_id)

        if not message:
            raise MessageNotFound

        return message

    def delete_chat(self, chat_id: int) -> Chat:
        chat = self.get_by_id(chat_id)

        if not chat:
            raise ChatNotFound

        CHATS_DB.remove(chat)
        return chat

    def delete_chat_for_user(self, chat_id: int, user_id: int) -> Chat:
        chat = self.get_by_id(chat_id)

        if not chat:
            raise ChatNotFound

        if user_id not in chat.users_ids:
            raise ChatUnavailableForUser

        chat.users_ids.remove(user_id)
        return chat
