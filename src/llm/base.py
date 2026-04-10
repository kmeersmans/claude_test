"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interface that every LLM backend must implement."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Send a prompt to the LLM and return the raw text response.

        Args:
            system_prompt: The system-level instruction.
            user_prompt: The user-level message containing the text to evaluate.

        Returns:
            The model's response as a string.
        """
