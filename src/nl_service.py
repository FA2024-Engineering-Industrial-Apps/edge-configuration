from typing import List

from models.abstract_config import AbstractAppConfig
from models.app import App, AppModel
from llm_service import GPT4o


class NLService:

    def __init__(self, data_obj: AppModel, llm=GPT4o()):
        self.model = data_obj
        self.client = llm

    def retrieve_model(self, prompt: str, model: AppModel, history: list) -> str:
        return self.client.prompt(prompt, history, model)
