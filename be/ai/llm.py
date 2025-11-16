import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

def respond(prompt: str) -> str:
    completion = client.chat.completions.create(
    extra_body={},
    model="openrouter/sherlock-dash-alpha",
    messages=[
                {
                    "role": "user",
                    "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    #   {
                    #     "type": "image_url",
                    #     "image_url": {
                    #       "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                    #     }
                    #   }
                    ]
                }
                ]
    )
    return completion.choices[0].message.content

# print(respond("what is 1+1?"))