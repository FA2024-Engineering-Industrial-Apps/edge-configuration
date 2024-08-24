from pydantic import BaseModel
import instructor
from openai import OpenAI

def retrieve_model(prompt: str, model: BaseModel) -> BaseModel:
    client = instructor.patch(OpenAI())
    return client.chat.completions.create(
        model="gpt-4o",
        response_model=model,
        messages=[
            {
                "role": "system",
                "content": f"You're part of a vehicle factory and returning the configuration parts for a vehicle as json."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )