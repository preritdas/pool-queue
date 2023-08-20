"""Player class, interfaces with the database."""
from pydantic import BaseModel, field_validator
from pymongo import MongoClient

from keys import KEYS
from pool_queue.utils import validate_phone_number


# Create a connection to the database players collection
PLAYER_COLL = MongoClient(KEYS.MongoDB.connect_str).PoolQueue.players


class PlayerNotFoundError(Exception):
    """Raised when a player is not found in the database."""
    def __init__(self, lookup_method: str, value: str):
        super().__init__(f"Player with {lookup_method} {value} not found.")


class Player(BaseModel):
    """A pool player in or out of the queue."""
    name: str
    phone_number: str
    in_queue: bool = False
    in_game: bool = False

    @field_validator("phone_number")
    def validate_phone_number(cls, phone):
        """Ensure phone number is in 12223334455 format."""
        return validate_phone_number(phone)

    @classmethod
    def from_phone(cls, phone_number: str):
        """
        Get a player from their phone number. If no player is found, raise
        PlayerNotFoundError.
        """
        player = PLAYER_COLL.find_one({"phone_number": phone_number})

        if player is None:
            raise PlayerNotFoundError("phone number", phone_number)

        return cls(**player)

    @classmethod
    def register(cls, name: str, phone_number: str):
        """Register a new player. Phone number must be in 12223334455 format."""
        player = cls(name=name, phone_number=phone_number)
        PLAYER_COLL.insert_one(player.model_dump())
        return player
