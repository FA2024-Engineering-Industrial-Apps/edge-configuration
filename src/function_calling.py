from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
import json
from iem_model import AbstractAppConfig, Field, StringField

load_dotenv()

client = OpenAI()


# Look for default function signatures
class AuthenticationObject(AbstractAppConfig):
    username: StringField = StringField(
        name="username", description="the username of the user", value=None
    )
    email: StringField = StringField(
        name="email", description="The email of the user", value=None
    )

    def generate_prompt_string(self):
        return "Needs a username and a string"


dataObj = AuthenticationObject()


tools = dataObj.generate_tool_functions()

function_lib = {}

for item in tools:
    function_lib[item.name] = item.fct

tool_descriptions = [i.llm_description for i in tools]


messages = [
    {
        "role": "user",
        "content": "I want to update my name to 'Niclas' and email to 'mymy@py.co'",
    }
]


response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tool_descriptions,
    tool_choice="auto",  # auto is default, but we'll be explicit
)  # type: ignore


response_message = response.choices[0].message
tool_calls = response_message.tool_calls

for tool_call in tool_calls:
    function_name = tool_call.function.name
    function_to_call = function_lib[function_name]
    function_args = json.loads(tool_call.function.arguments)
    print(f"Function args {function_args}")
    function_response = function_to_call(
        function_args,
    )
    messages.append(
        {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": function_response,
        }
    )

print(dataObj)
