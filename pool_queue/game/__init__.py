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
    def _from_game_id(cls, object_id: str | ObjectId) -> "Game":
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
    def from_only_active(cls) -> "Game":
        """
        Get the only active game. If no game is found, raise GameNotFoundError.
        """
        game = PLAYER_COLL.find_one({"status": GameStatus.IN_PROGRESS.value})

        if game is None:
            raise GameNotFoundError("status", GameStatus.IN_PROGRESS.value)
        
        return cls._from_game_id(game["_id"])

    @classmethod
    def from_only_pending(cls) -> "Game":
        """
        Get the only pending game. If no game is found, raise GameNotFoundError.
        """
        game = PLAYER_COLL.find_one({"status": GameStatus.PENDING_CHALLENGER.value})

        if game is None:
            raise GameNotFoundError("status", GameStatus.PENDING_CHALLENGER.value)
        
        return cls._from_game_id(game["_id"])

    @classmethod
    def create(cls, king: Player, challenger: Player, force_active: bool = False) -> "Game":
        """
        Create a new pending game. This should happen when a game has just finished 
        and a new game needs to be created, involving the winner of the last 
        match and the next person in the queue.

        If force_active is True, the game will be created as active, rather than
        pending. This should only be used when a game is being created for the first
        time.
        """
        res = PLAYER_COLL.insert_one(
            {
                "king": king.phone_number,
                "challenger": challenger.phone_number,
                "status": GameStatus.PENDING_CHALLENGER.value
            }
        )

        return cls._from_game_id(res.inserted_id)
    
    def check_status(self) -> GameStatus:
        """Check the status of the game."""
        return GameStatus(PLAYER_COLL.find_one({"_id": self.game_id})["status"])

    def update_status(self, status: GameStatus):
        """Update the status of the game."""
        self.status = status
        PLAYER_COLL.update_one(
            {"_id": self.game_id},
            {"$set": {"status": status.value}}
        )
