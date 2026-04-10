"""Ollama LLM provider — calls a locally-running Ollama instance."""

import ollama as ollama_client

from src.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str = "llama3.1:8b",
        base_url: str = "http://localhost:11434",
        temperature: float = 0.1,
        num_ctx: int = 8192,
    ):
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx
        self.client = ollama_client.Client(host=base_url)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={
                "temperature": self.temperature,
                "num_ctx": self.num_ctx,
            },
        )
        return response["message"]["content"]
