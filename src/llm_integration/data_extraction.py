from typing import List, Dict
from model.app_model import AppModel
import json
from llm_integration.llm_service import LLM, GPT4o
from error_handling import ValidationException


class DataExtractor:

    model: AppModel
    client: LLM

    def __init__(self, data_obj: AppModel, llm=GPT4o()):
        self.model = data_obj
        self.client = llm
        self._refresh_tools()

    def _refresh_tools(self):

        tools = self.model.generate_tool_functions()
        self.function_lib = {}

        # creating a dictionary function_lib containing all functions i.e. their name as key and the function as value
        for item in tools:
            self.function_lib[item.name] = item.fct

        self.tool_descriptions = [i.llm_description for i in tools]

    def update_data(self, messages: List[Dict]):
        self._refresh_tools()

        response_pair = self.client.prompt_tool(messages, self.tool_descriptions)
        # response_message = response_pair.response
        tool_calls = response_pair.tool_calls
        extractor_message = response_pair.response
        print(f"The extractor message is:\n{extractor_message}\n\n")
        print(f"tool_calls:\n {tool_calls}\n\n")
        if not tool_calls:
            return

        # Execute all function calls given by GPT
        print("Just before function calling loop")
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = self.function_lib[function_name]
            function_args = json.loads(tool_call.function.arguments)
            try:
                print(f"Trying to call function {function_name} with {function_args}")
                function_to_call(
                    **function_args,
                )
                print(f"Executing {function_name} was succesful!")
            except ValidationException:
                print(f"Validation Error concerning {function_name}!")
                # TODO: Feedback to GPT
                # Possibly a solution:
