from pydantic import BaseModel
import instructor
from openai import OpenAI
import streamlit as st
from enum import Enum


def describe_options(enum_class):
    options = [member.value for member in enum_class]
    return f"Available options: {', '.join(options)}"


def retrieve_model(prompt: str, model: BaseModel) -> BaseModel:
    if st.session_state.get("model") == "gpt-4o":
        client = instructor.patch(OpenAI())
        return client.chat.completions.create(
            model="gpt-4o",
            response_model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"You're part of a vehicle factory and returning the configuration parts for a vehicle as json.",
                },
                {"role": "user", "content": prompt},
            ],
        )
    else:
        client = OpenAI(
            base_url="https://api.siemens.com/llm/",
            api_key=st.session_state["mixtral_key"],
        )

        if issubclass(model, Enum):
            model_definiton = describe_options(model)
            json = client.chat.completions.create(
                model="mistral-7b-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": f"You're part of a vehicle factory and returning the configuration parts for a vehicle. ONLY return ONE exact option! {model_definiton} DO NOT ADD ANY ADDITIONAL INFORMATION!",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            print(json.choices[0].message.content)
            return model[json.choices[0].message.content.strip()]
        else:
            model_definiton = model.model_json_schema()
            json = client.chat.completions.create(
                model="mistral-7b-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": f"You're part of a vehicle factory and returning the configuration parts for a vehicle as json. "
                        + f"ONLY Return valid JSON from this definition {model_definiton}."
                        + "ONLY include the content of the repsective model."
                        + "DO NOT ADD ANY ADDITIONAL INFORMATION!",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            print(json.choices[0].message.content)
            return model.model_validate(json.choices[0].message.content.strip())
