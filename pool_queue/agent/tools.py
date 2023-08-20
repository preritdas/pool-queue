"""All tools for the users to use with the agent."""
from langchain.tools import BaseTool

from pool_queue.player import Player
from pool_queue.player_queue import PlayerQueue


def create_registration_tool(player_phone: str) -> type[BaseTool]:
    """Create the registration tool for the agent to use."""

    class RegisterPlayerTool(BaseTool):
        """Register a player with the agent."""
        name = "Register Player"
        description = (
            "Register a new player with the system. Input must be simply the full name of "
            "the player. If the full name is not provided, ask the user for the full name."
        )

        def _run(self, name: str):
            Player.register(name=name, phone_number=player_phone)

    return RegisterPlayerTool


# Necessary tools:
# - join queue
# - leave queue
# - check position in queue
# - see full queue
# - start game
# - end game
# - confirm inbound challenger


def create_tools(player: Player) -> list[type[BaseTool]]:
    """
    Create the tools for the agent to use. Returns a list of tool classes.

    The player queue can be daily cleared here because tools are built for every
    inbound request.
    """
    player_queue = PlayerQueue()
    player_queue.daily_clear()

    class JoinQueueTool(BaseTool):
        """Join the queue."""
        name = "Join Queue"
        description = "Join the queue to play a game."

        def _run(self):
            if not player_queue.add(player):
                return (
                    "Player is already in the queue, position "
                    f"{player_queue.get_position(player)}"
                )
            
            return f"Player added to queue, position {player_queue.get_position(player)}."

    class LeaveQueueTool(BaseTool):
        """Leave the queue."""
        name = "Leave Queue"
        description = "Leave the queue."

        def _run(self):
            if not player_queue.remove(player):
                return "Player was not in the queue."

            return "Player removed from queue."

    class CheckPositionTool(BaseTool):
        """Check position in queue."""
        name = "Check Position"
        description = "Check position in queue."

        def _run(self):
            position = player_queue.get_position(player)
            if position == -1:
                return "Player is not in the queue."

            return f"Player is in position {position}."
        
    class SeeFullQueueTool(BaseTool):
        """See the full queue."""
        name = "See Full Queue"
        description = "See the names of all players in order in the queue."

        def _run(self):
            queue: list[Player] = player_queue.get_queue()
            queue_str = "\n".join([f"{i}. {p.name}" for i, p in enumerate(queue, 1)])
            return f"Queue:\n{queue_str}"
