"""All tools for the users to use with the agent."""
from langchain.tools import BaseTool

from threading import Thread

from pool_queue.player import Player, PlayerNotFoundError
from pool_queue.game import Game, GameNotFoundError, GameStatus
from pool_queue.player_queue import PlayerQueue


def create_registration_tool(player_phone: str) -> BaseTool:
    """Create the registration tool for the agent to use."""

    class RegisterPlayerTool(BaseTool):
        """Register a player with the agent."""
        name = "Register Player"
        description = (
            "Register a new player with the system. Input must be simply the full name of "
            "the player. If the full name is not provided, ask the user for the full name. "
            "Provide the full name with proper capitalization, even if it wasn't provided "
            "that way. Ex. if user provides 'john doe', you should register 'John Doe'."
        )

        def _run(self, name: str):
            Player.register(name=name, phone_number=player_phone)
            return "Player has been registered."

    return RegisterPlayerTool()


# Necessary tools:
# - join queue
# - leave queue
# - check position in queue
# - see full queue
# - start game
# - end game
# - confirm inbound challenger


def create_tools(player: Player) -> list[BaseTool]:
    """
    Create the tools for the agent to use. Returns a list of tools.

    The player queue can be daily cleared here because tools are built for every
    inbound request.
    """
    player_queue = PlayerQueue()
    player_queue.daily_clear()

    class JoinQueueTool(BaseTool):
        """Join the queue."""
        name = "Join Queue"
        description = "Join the queue to play a game. Takes no input, so input n/a."

        def _run(self, query: str):
            if not player_queue.add(player):
                return (
                    "Player is already in the queue, position "
                    f"{player_queue.get_position(player)}"
                )
            
            return f"Player added to queue, position {player_queue.get_position(player)}."

    class LeaveQueueTool(BaseTool):
        """Leave the queue."""
        name = "Leave Queue"
        description = "Leave the queue. Takes no input, so input n/a."

        def _run(self, query: str):
            if not player_queue.remove(player):
                return "Player was not in the queue."

            return "Player removed from queue."

    class CheckPositionTool(BaseTool):
        """Check position in queue."""
        name = "Check Position"
        description = "Check position in queue. Takes no input, so input n/a."

        def _run(self, query: str):
            position = player_queue.get_position(player)
            if position == -1:
                return "Player is not in the queue."

            return f"Player is in position {position}."
        
    class SeeFullQueueTool(BaseTool):
        """See the full queue."""
        name = "See Full Queue"
        description = (
            "See the names of all players in order in the queue. "
            "Takes no input, so input n/a."
        )

        def _run(self, query: str):
            queue: list[Player] = player_queue.get_queue()
            queue_str = "\n".join([f"{i}. {p.name}" for i, p in enumerate(queue, 1)])
            return f"Queue:\n{queue_str}"

    class StartGameTool(BaseTool):
        """Start a game when none exist."""
        name = "Start Game"
        description = (
            "Create the first game of the day, when none exist. Input must the phone "
            "number of the user's opponent. If the phone number is not provided, ask the "
            "user for the phone number."
        )

        def _run(self, opponent_phone: str):
            try:
                Game.from_only_active()
                return (
                    "Game already exists, cannot use this tool. "
                    "End the last active game by having the loser declare themselves."
                )
            except GameNotFoundError:
                try:
                    opponent = Player.from_phone(opponent_phone)
                except PlayerNotFoundError:
                    return "Opponent has not registered. Have them text me to register first."
                game = Game.create(king=player, challenger=opponent)
                return (
                    f"Game created. King: {game.king.name}, Challenger: "
                    f"{game.challenger.name}"
                )

    class LostMatchEndGameTool(BaseTool):
        """End the game when the king loses."""
        name = "Lost Match, End Game"
        description = (
            "The loser of the active match will use this tool to specify that they lost "
            "the match. The game will then be ended and a new game will be started with "
            "the next player in the queue to challenge the winner of the last match. "
            "Takes no input, as the loser is the one to use this tool, so input n/a."
        )

        def _run(self, query: str):
            try:
                game = Game.from_only_active()
            except GameNotFoundError:
                return (
                    "No game exists. Use the 'Start Game' tool to start a new game."
                )

            # Determine winner and loser
            winner = game.challenger if game.king == player else game.king

            # Mark game as finshed
            game.update_status(GameStatus.FINISHED)

            # Start next game
            next_challenger = player_queue.find_next_player()
            if not next_challenger:
                return (
                    "Game ended. No players in queue to challenge the winner, "
                    "feel free to play again."
                )

            next_game = Game.create(king=winner, challenger=next_challenger)
            print("awaiting confirmation")

            return (
                f"Game ended. The next player in the queue, {next_challenger.name}, "
                f"has two minutes to come to the table and be confirmed by "
                f"{winner.name}. They can say '{next_challenger.name} is here' or "
                "'next player is here' etc."
            )

    class ConfirmInboundChallengerTool(BaseTool):
        """Confirm the inbound challenger."""
        name = "Confirm Inbound Challenger"
        description = (
            "The winner of the last match will use this tool to confirm the next player "
            "in the queue as the challenger. This tool will only work if the next player "
            "in the queue has used the 'Start Game' tool and is waiting to be confirmed. "
            "Takes no input, as the winner is the one to use this tool, so input n/a."
        )

        def _run(self, query: str):
            try:
                game = Game.from_only_pending()
            except GameNotFoundError:
                return (
                    "No game exists. Use the 'Start Game' tool to start a new game."
                )

            # Make sure user is the king
            if game.king != player:
                return "Only the king can confirm the inbound challenger."

            # Mark game as finshed
            game.update_status(GameStatus.IN_PROGRESS)

            return (
                f"Confirmed. The game has begun between {game.king.name} and "
                f"{game.challenger.name}. Good luck."
            )

    return [
        JoinQueueTool(),
        LeaveQueueTool(),
        CheckPositionTool(),
        SeeFullQueueTool(),
        StartGameTool(),
        LostMatchEndGameTool(),
        ConfirmInboundChallengerTool()
    ]
