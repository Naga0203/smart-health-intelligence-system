import os
from common.gemini_client import LangChainGeminiClient
from common.openai_client import LangChainOpenAIClient


class LLMFactory:

    @staticmethod
    def get_llm():
        provider = os.getenv("LLM_PROVIDER", "gemini").lower()

        if provider == "openai":
            return LangChainOpenAIClient().llm
        return LangChainGeminiClient().llm
