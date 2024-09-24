from dotenv import load_dotenv
from pydantic import BaseModel
import instructor
from openai import OpenAI
import streamlit as st
from enum import Enum
import json

from data_extraction import DataExtractor
from iem_model import AbstractAppConfig


def describe_options(enum_class):
    options = [member.value for member in enum_class]
    return f"Available options: {', '.join(options)}"


def retrieve_model(prompt: str, model: AbstractAppConfig, instructions: str) -> str:
    if st.session_state.get("model") == "gpt-4o":
        load_dotenv()
        client = instructor.patch(OpenAI())
        data_extractor = DataExtractor(model)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"{instructions}",
                },
                {"role": "user", "content": prompt},
            ],
        )
        tool_response = data_extractor.update_data([
                {
                    "role": "system",
                    "content": f"{instructions}",
                },
                {"role": "user", "content": prompt},
            ])
        print(model)

        return response.choices[0].message.content.strip()

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
