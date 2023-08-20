"""
Queue of Players. If it's after 4am, all items from before 4am are removed.
There will only be one item in this collection, being the queue itself.
"""
from pymongo import MongoClient
from pydantic import BaseModel

from datetime import datetime

from keys import KEYS


# Create a connection to the database queue collection
QUEUE_COLL = MongoClient(KEYS.MongoDB.connect_str).PoolQueue.queue


# Ensure there is only one item in the queue collection
if QUEUE_COLL.count_documents({}) == 0:
    QUEUE_COLL.insert_one({"players": []})
elif QUEUE_COLL.count_documents({}) > 1:
    raise RuntimeError("There should only be one item in the queue collection.")


class QueueItem(BaseModel):
    """Item in the queue."""
    player_phone: str
    datetime_added: datetime


class PlayerQueue(BaseModel):
    """Queue of players."""

    def add(self, player_phone: str) -> None:
        """Add a player to the queue."""
        item = QueueItem(player_phone=player_phone, datetime_added=datetime.now())
        QUEUE_COLL.update_one(
            {},
            {"$push": {"players": item.model_dump()}}
        )

    def find_next_player(self) -> str:
        """Find the next player in the queue."""
        return QUEUE_COLL.find_one({})["players"][0]["player_phone"]

    def remove(self, player_phone: str) -> None:
        """Remove a player from the queue."""
        QUEUE_COLL.update_one(
            {},
            {"$pull": {"players": {"player_phone": player_phone}}}
        )

    def daily_clear(cls) -> None:
        """Clear the queue of all players added before 4am."""
        QUEUE_COLL.update_one(
            {},
            {"$pull": {"players": {"datetime_added": {"$lt": datetime.now().replace(hour=4)}}}}
        )
