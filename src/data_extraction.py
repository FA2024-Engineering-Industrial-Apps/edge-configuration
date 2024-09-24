from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from iem_model import AbstractAppConfig
import json


class DataExtractor:

    model: AbstractAppConfig
    client: OpenAI

    def __init__(self, data_obj: AbstractAppConfig):
        self.model = data_obj
        load_dotenv()
        self.client = OpenAI()
        tools = self.model.generate_tool_functions()
        self.function_lib = {}

        for item in tools:
            self.function_lib[item.name] = item.fct

        self.tool_descriptions = [i.llm_description for i in tools]

    def update_data(self, messages: List[Dict]):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=self.tool_descriptions,
            tool_choice="auto",
        )  # type: ignore

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = self.function_lib[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_to_call(
                **function_args,
            )
