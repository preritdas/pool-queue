"""All tools for the users to use with the agent."""
from langchain.tools import BaseTool

from pool_queue.player import Player


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



def create_tools(player: Player) -> list[type[BaseTool]]:
    """Create the tools for the agent to use. Returns a list of tool classes."""
