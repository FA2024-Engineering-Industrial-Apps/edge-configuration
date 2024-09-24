from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
import json

load_dotenv()

client = OpenAI()


# Look for default function signatures
class AuthenticationObject(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None

    def update_username(self, name):
        self.username = name


dataObj = AuthenticationObject()

messages = [
    {
        "role": "user",
        "content": "I want to update my name to 'Niclas'",
    }
]


def generate_function_signatures():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "update_username",
                "description": "Update the username",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "the new username",
                        },
                    },
                    "required": ["name"],
                },
            },
        }
    ]
    return tools


def get_function_lib():
    return {"update_username": dataObj.update_username}


response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=generate_function_signatures(),
    tool_choice="auto",  # auto is default, but we'll be explicit
)  # type: ignore


response_message = response.choices[0].message
tool_calls = response_message.tool_calls

for tool_call in tool_calls:
    function_name = tool_call.function.name
    function_to_call = get_function_lib()[function_name]
    function_args = json.loads(tool_call.function.arguments)
    function_response = function_to_call(
        name=function_args.get("name"),
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
