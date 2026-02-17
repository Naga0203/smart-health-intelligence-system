from langchain_openai import ChatOpenAI
import os


class LangChainOpenAIClient:

    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def get_client_status(self):
        return {"provider": "openai"}
