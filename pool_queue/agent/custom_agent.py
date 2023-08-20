"""Custom agent."""
from langchain.agents import ZeroShotAgent


class InternalThoughtZeroShotAgent(ZeroShotAgent):
    """
    A normal ZeroShotAgent but doesn't inject "Thought:" before the LLM. After testing
    and heavy prompt engineering, I've found a better sucess rate with having the LLM
    create its own "Thought" label. This is because it knows that each Thought must
    also have either an Action/Action Input or a Final Answer.
    """
    @property
    def llm_prefix(self) -> str:
        """Prefix to append the llm call with."""
        return ""
