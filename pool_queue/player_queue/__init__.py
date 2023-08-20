"""
Queue of Players. If it's after 4am, all items from before 4am are removed.
There will only be one item in this collection, being the queue itself.
"""
from pymongo import MongoClient
from pydantic import BaseModel

from datetime import datetime

from keys import KEYS
from pool_queue.player import Player


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

    def player_in_queue(self, player: Player | str) -> bool:
        """
        Check if a player is in the queue. `player` can be a Player object or a phone
        number.
        """
        player_phone = player.phone_number if isinstance(player, Player) else player
        return bool(QUEUE_COLL.find_one({"players.player_phone": player_phone}))

    def get_queue(self) -> list[Player]:
        """Get the queue."""
        players: list[dict] = QUEUE_COLL.find_one({})["players"]
        return [Player.from_phone(p["player_phone"]) for p in players]

    def add(self, player: Player | str) -> bool:
        """
        Add a player to the queue. `player` can be a Player object or a phone number.
        Returns True if the player was added, False if the player was already in the
        queue.
        """
        player_phone = player.phone_number if isinstance(player, Player) else player

        # Check if the player is already in the queue
        if self.player_in_queue(player_phone):
            return False

        item = QueueItem(player_phone=player_phone, datetime_added=datetime.now())
        QUEUE_COLL.update_one(
            {},
            {"$push": {"players": item.model_dump()}}
        )

        return True

    def get_position(self, player: Player | str) -> int:
        """
        Get the position of a player in the queue. `player` can be a Player object or a
        phone number. Returns -1 if the player is not in the queue.
        """
        # Check if the player is in the queue
        if not self.player_in_queue(player_phone):
            return -1

        player_phone = player.phone_number if isinstance(player, Player) else player
        players: list[dict] = QUEUE_COLL.find_one({})["players"]
        player: dict = next(filter(lambda p: p["player_phone"] == player_phone, players))
        return players.index(player) + 1

    def find_next_player(self) -> Player | None:
        """Find the next player in the queue. Returns None if the queue is empty."""
        if len(queue := self.get_queue()) == 0:
            return None

        return queue[0]

    def remove(self, player: Player | str) -> bool:
        """
        Remove a player from the queue. Returns True if the player was removed, 
        False if the player was not in the queue.
        """
        # Check if the player is in the queue
        if not self.player_in_queue(player):
            return False

        player_phone = player.phone_number if isinstance(player, Player) else player
        QUEUE_COLL.update_one(
            {},
            {"$pull": {"players": {"player_phone": player_phone}}}
        )

        return True

    def daily_clear(cls) -> None:
        """Clear the queue of all players added before 4am."""
        QUEUE_COLL.update_one(
            {},
            {"$pull": {"players": {"datetime_added": {"$lt": datetime.now().replace(hour=4)}}}}
        )
