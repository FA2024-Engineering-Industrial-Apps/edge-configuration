from dotenv import load_dotenv
from pydantic.dataclasses import dataclass
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
import os
from error_handling import LLMInteractionException
from history import History

from model.app_model import AppModel
from abc import ABC
from typing import List, Dict, Optional

load_dotenv()


@dataclass
class ResponseToolCallPair:
    response: Optional[str]
    tool_calls: Optional[List[ChatCompletionMessageToolCall]]


class LLM(ABC):
    client: OpenAI
    system_prompt: str
    model_name: str

    def send_request(self, messages: List[Dict]) -> ChatCompletion:
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,  # type: ignore
        )

    def handle_response(self, response: ChatCompletion) -> str:
        ret = response.choices[0].message.content
        if not ret:
            raise LLMInteractionException(f"{self.model_name} returned empty response")
        return ret

    def prompt(self, history: History) -> str:
        llmPromt = history.genPromtForLLM(n_oldAnswerResponsePairs=1)
        # print(f"llmPromt is: \n{llmPromt}\n\n")
        response: str = self.prompt_conversation(llmPromt)
        history.addPromt_withStrs("assistant", response)
        return response

    def prompt_conversation(self, input: List[Dict]) -> str:
        try:
            response = self.send_request(input)
            return self.handle_response(response)
        except Exception as e:
            raise LLMInteractionException(
                f"Error prompting {self.model_name}: {str(e)}"
            )

    def prompt_tool(self, input: List[Dict], tools: List[Dict]) -> ResponseToolCallPair:
        # calling GPT with the messanges and tool_descriptions / llm_descriptions of all functions
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=input,
            tools=tools,
            tool_choice="auto",
        )  # type: ignore

        # extracting the text respones and function calls answered by GPT
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        return ResponseToolCallPair(
            response=response_message.content, tool_calls=tool_calls
        )


class GPT4o(LLM):

    def __init__(self, system_prompt: str = ""):

        if os.environ.get("OPENAI_API_KEY") is None:
            raise LLMInteractionException("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI()
        self.system_prompt = system_prompt
        self.model_name = "gpt-4o-2024-08-06"


class GPTo1Mini(LLM):

    def __init__(self, system_prompt: str = ""):

        if os.environ.get("OPENAI_API_KEY") is None:
            raise LLMInteractionException("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI()
        self.system_prompt = system_prompt
        self.model_name = "gpt-4-turbo"


class Mistral7b(LLM):

    def __init__(self, system_prompt: str = ""):

        if os.environ.get("SIEMENS_LLM_KEY") is None:
            raise LLMInteractionException(
                "SIEMENS_LLM_KEY environment variable not set"
            )

        self.client = OpenAI(
            base_url="https://api.siemens.com/llm/",
            api_key=os.environ["SIEMENS_LLM_KEY"],
        )

        self.system_prompt = system_prompt
        self.model_name = "mistral-7b-instruct"


class Qwen25(LLM):

    def __init__(self, system_prompt: str = ""):
        self.client = OpenAI(
            base_url="http://workstation.ferienakademie.de:11434/v1",
            api_key="ollama",
        )

        self.system_prompt = system_prompt
        self.model_name = "qwen2.5:32b"


class Groq(LLM):

    def __init__(self, system_prompt: str = ""):
        self.client = OpenAI(
            base_url="http://workstation.ferienakademie.de:11434/v1",
            api_key="ollama",
        )

        self.system_prompt = system_prompt
        self.model_name = "llama3-groq-tool-use"


class Llama3(LLM):

    def __init__(self, system_prompt: str = ""):
        self.client = OpenAI(
            base_url="http://workstation.ferienakademie.de:11434/v1",
            api_key="ollama",
        )

        self.system_prompt = system_prompt
        self.model_name = "llama3.1"


class Gemma2(LLM):

    def __init__(self, system_prompt: str = ""):
        self.client = OpenAI(
            base_url="http://workstation.ferienakademie.de:11434/v1",
            api_key="ollama",
        )

        self.system_prompt = system_prompt
        self.model_name = "gemma2:27b"
