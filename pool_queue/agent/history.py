"""User chat history."""
from pydantic import BaseModel
from pymongo import MongoClient

from typing import Literal

from keys import KEYS


# Create a connection to the database history collection
HISTORY_COLL = MongoClient(KEYS.MongoDB.connect_str).PoolQueue.chat_history


class Message(BaseModel):
    """A message in the chat history."""
    phone_number: str
    content: str
    sender: Literal["user", "agent"]


class ChatHistory(BaseModel):
    """Chat history for a user."""
    phone_number: str
    messages: list[Message]

    @classmethod
    def from_phone(cls, phone_number: str) -> "ChatHistory":
        """Get the chat history for a user."""
        # Empty list if user has no history
        if not HISTORY_COLL.find_one({"phone_number": phone_number}): 
            return cls(phone_number, messages=[])

        res = HISTORY_COLL.find_one({"phone_number": phone_number})
        return cls(
            phone_number=phone_number,
            messages=[Message(**message) for message in res["messages"]]
        )

    def add(self, message: Message) -> None:
        """Add a query and response to the chat history."""
        self.update()
        self.messages.append(message)
        HISTORY_COLL.update_one(
            {"phone_number": self.phone_number},
            {"$set": {"messages": [message.model_dump() for message in self.messages]}},
            upsert=True  # create if user doesn't have chat history yet
        )

    def update(self) -> "ChatHistory":
        """Get the chat history."""
        self = ChatHistory.from_phone(self.phone_number)
        return self

    def as_string(self) -> str:
        """Get the chat history as a string."""
        self.update()
        return "\n".join(
            f"{message.sender}: {message.content}" for message in self.messages
        )
