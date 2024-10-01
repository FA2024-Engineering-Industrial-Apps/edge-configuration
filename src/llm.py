from dotenv import load_dotenv
from pydantic.dataclasses import dataclass
import instructor
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
import os
import streamlit as st
from enum import Enum
import json
from error_handling import LLMInteractionException

from data_extraction import DataExtractor
from iem_model import AbstractAppConfig
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

load_dotenv()


def describe_options(enum_class):
    options = [member.value for member in enum_class]
    return f"Available options: {', '.join(options)}"


def retrieve_model(prompt: str, model: AbstractAppConfig, history: list) -> str:
    if st.session_state.get("model") == "gpt-4o":
        load_dotenv()
        client = instructor.patch(OpenAI())
        data_extractor = DataExtractor(model)
        system_prompt = history[0]
        messages = [system_prompt]
        for element in history[-3:]:
            if element == system_prompt:
                continue
            messages.append(element)
        messages.append({"role": "user", "content": prompt})
        # print(messages)
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        data_extractor.update_data(messages)
        
        print("The new state of the model:\n", model, "\n")
        history.append(
            {
                "role": "system",
                "content": "The current configuration is: "
                + model.generate_prompt_string(),
            }
        )

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
            # print(json_response.choices[0].message.content)
            return model[json_response.choices[0].message.content.strip()]  # type: ignore
        else:
            # model_definiton = model.model_json_schema()
            response = client.chat.completions.create(
                model="mistral-7b-instruct",
                messages=[
                    {"role": "system", "content": f"{instructions}"},
                    {"role": "user", "content": prompt},
                ],
            )
            # print(json_response.choices[0].message.content)
            return response.choices[0].message.content.strip()
