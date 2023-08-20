"""Game class, interfaces with the database."""
from pydantic import BaseModel, ConfigDict
from bson.objectid import ObjectId
from pymongo import MongoClient

from enum import Enum

from keys import KEYS
from pool_queue.player import Player


# Create a connection to the database players collection
PLAYER_COLL = MongoClient(KEYS.MongoDB.connect_str).PoolQueue.games


class GameNotFoundError(Exception):
    """Raised when a game is not found in the database."""
    def __init__(self, lookup_method: str, value: str):
        super().__init__(f"Game with {lookup_method} {value} not found.")


class GameStatus(Enum):
    """
    The status of a game.

    PENDING_CHALLENGER: The game is waiting for a challenger to arrive, triggering
        the king (last match winner) to confirm their arrival and therefore the start
        of the new game.
    """
    PENDING_CHALLENGER = "pending_challenger"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Game(BaseModel):
    """A pool player in or out of the queue."""
    game_id: ObjectId
    king: Player
    challenger: Player
    status: GameStatus

    # Model config
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_game_id(cls, object_id: str | ObjectId):
        """
        Get a game from it's database ID. If no player is found, raise
        PlayerNotFoundError.
        """
        if isinstance(object_id, str):
            object_id = ObjectId(object_id)

        game = PLAYER_COLL.find_one({"_id": object_id})

        if game is None:
            raise GameNotFoundError("game ID", object_id)

        # Parse
        return cls(
            game_id=game["_id"],
            king=Player.from_phone(game["king"]),
            challenger=Player.from_phone(game["challenger"]),
            status=GameStatus(game["status"])
        )
        

    @classmethod
    def create(cls, king: Player, challenger: Player):
        """
        Create a new pending game. This should happen when a game has just finished 
        and a new game needs to be created, involving the winner of the last 
        match and the next person in the queue.
        """
        res = PLAYER_COLL.insert_one(
            {
                "king": king.phone_number,
                "challenger": challenger.phone_number,
                "status": GameStatus.PENDING_CHALLENGER.value
            }
        )

        return cls.from_game_id(res.inserted_id)