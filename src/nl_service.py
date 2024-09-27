from src.models.iem_model import AbstractAppConfig
from llm_service import GPT4o


class NLService:

    def __init__(self, data_obj: AbstractAppConfig, llm=GPT4o()):
        self.model = data_obj
        self.client = llm

    def retrieve_model(self, prompt: str, model: AbstractAppConfig, history: list) -> str:
        return self.client.prompt(prompt, history, model)
