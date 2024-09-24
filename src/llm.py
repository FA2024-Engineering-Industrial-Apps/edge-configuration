from pydantic import BaseModel
import instructor
from openai import OpenAI
import streamlit as st
from enum import Enum
import json


def describe_options(enum_class):
    options = [member.value for member in enum_class]
    return f"Available options: {', '.join(options)}"


def retrieve_model(prompt: str, model: BaseModel, instructions: str) -> str:
    if st.session_state.get("model") == "gpt-4o":
        if model is not None and issubclass(model, Enum):
            client = OpenAI()
            model_definiton = describe_options(model)
            json_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"{instructions}",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return model[json_response.choices[0].message.content.strip()] 
        else:
            client = instructor.patch(OpenAI())
            return client.chat.completions.create(
                model="gpt-4o",
                response_model=model,
                messages=[
                    {
                        "role": "system",
                        "content": f"{instructions}",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            
    else:
        client = OpenAI(
            base_url="https://api.siemens.com/llm/",
            api_key=st.session_state["mixtral_key"],
        )

        if model is not None and issubclass(model, Enum):  # type: ignore
            model_definiton = describe_options(model)
            json_response = client.chat.completions.create(
                model="mistral-7b-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": f"{instructions}",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            print(json_response.choices[0].message.content)
            return model[json_response.choices[0].message.content.strip()]  # type: ignore
        else:
             # model_definiton = model.model_json_schema()
            response = client.chat.completions.create(
                model="mistral-7b-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": f"{instructions}"
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            # print(json_response.choices[0].message.content)
            return response.choices[0].message.content.strip()