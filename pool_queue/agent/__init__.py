"""The agent to serve as the interface between users and the pool-queue system."""
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import AgentExecutor

from pool_queue.agent.custom_agent import InternalThoughtZeroShotAgent
from pool_queue.agent.prompts import AgentPrompts
from pool_queue.agent.tools import create_registration_tool, create_tools
from pool_queue.player import Player, PlayerNotFoundError

from keys import KEYS


llm = ChatOpenAI(model_name="gpt-4", openai_api_key=KEYS.OpenAI.api_key, temperature=0)


def create_agent_executor(
    toolkit: list[Tool],
    player: Player | None
) -> AgentExecutor:
    """Create the agent given authenticated tools."""
    agent_prompts = AgentPrompts.build(player)
    agent = InternalThoughtZeroShotAgent.from_llm_and_tools(
        llm=llm,
        tools=toolkit,
        prefix=agent_prompts.prefix,
        format_instructions=agent_prompts.format_instructions,
        suffix=agent_prompts.suffix
    )
    return AgentExecutor(
        agent=agent,
        tools=toolkit,
        max_iterations=3,
        verbose=True
    )


def run_agent(player_phone: str) -> str:
    """Run the agent."""
    try:
        player = Player.from_phone(player_phone)
        tools = create_tools(player)
    except PlayerNotFoundError:
        tools = [create_registration_tool(player_phone)]

    agent_executor = create_agent_executor(tools, player)
