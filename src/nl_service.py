from typing import List

from iem_model import AbstractAppConfig, App, AppModel
from llm_service import GPT4o
from history import History


class NLService:

    def __init__(self, data_obj: AppModel, llm=GPT4o()):
        self.model = data_obj
        self.client = llm

    def retrieve_model(self, history: History) -> str:
        return self.client.prompt(history)
