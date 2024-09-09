from pydantic import BaseModel
import instructor
from openai import OpenAI
import streamlit as st
from enum import Enum
import json


def describe_options(enum_class):
    options = [member.value for member in enum_class]
    return f"Available options: {', '.join(options)}"


def retrieve_model(prompt: str, model: BaseModel, instructions: str) -> BaseModel:
    if st.session_state.get("model") == "gpt-4o":
        client = instructor.patch(OpenAI())
        return client.chat.completions.create(
            model="gpt-4o",
            response_model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"{instructions}. Return it as valid json according to this model {model.model_json_schema()}.",
                },
                {"role": "user", "content": prompt},
            ],
        )
    else:
        client = OpenAI(
            base_url="https://api.siemens.com/llm/",
            api_key=st.session_state["mixtral_key"],
        )

        if issubclass(model, Enum):  # type: ignore
            model_definiton = describe_options(model)
            json_response = client.chat.completions.create(
                model="mistral-7b-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": f"{instructions}. ONLY return ONE exact option! {model_definiton} DO NOT ADD ANY ADDITIONAL INFORMATION!",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            print(json_response.choices[0].message.content)
            return model[json_response.choices[0].message.content.strip()]  # type: ignore
        else:
            model_definiton = model.model_json_schema()
            json_response = client.chat.completions.create(
                model="mistral-7b-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": f"{instructions}. Return it as valid json."
                        + f"ONLY Return valid JSON from this definition {model_definiton}."
                        + "ONLY include the fields of the respective model."
                        + "DO NOT include the model name."
                        + "DO NOT ADD ANY ADDITIONAL INFORMATION!",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            print(json_response.choices[0].message.content)
            return model.model_validate(
                json.loads(json_response.choices[0].message.content.strip())
            )
